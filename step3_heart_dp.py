"""Step 3: Step 2 (FedAvg / FedProx on the 4 real UCI Heart Disease hospitals) + differential privacy (Opacus DP-SGD).

Every hospital trains locally with DP-SGD: per-example gradient clipping (CLIP) + Gaussian noise (NOISE * CLIP) + Poisson sampling.
Each round is a fresh run of DP-SGD from the global model, so epsilon composes over rounds. We compute it per hospital
with an RDP accountant (see `epsilon_after`). Guarantee unit: one patient record in one hospital's training set.

Run one experiment:
    STRATEGY=fedavg  NOISE=1.0 SEED=0 .venv\\Scripts\\python.exe step3_heart_dp.py
    STRATEGY=fedprox MU=0.1 NOISE=1.0 SEED=0 .venv\\Scripts\\python.exe step3_heart_dp.py
Last line printed is `RESULT {json}` so a runner can collect many runs.

Differences from step 2 even at NOISE=0 (unavoidable with Opacus):
  * Poisson sampling: each step samples every row independently with prob q = 1/len(loader); batch size varies
    (expected n/len(loader) ~ 16 or less) instead of fixed shuffled batches of 16. Step count per epoch is the same.
  * Per-example clipping to norm CLIP changes the gradient whenever an example's gradient is larger than CLIP.
  * FedProx pull is applied as a separate update after the optimizer step (see `train_dp`), not as a loss term.
    For plain SGD the two are equal to first order in LR: w -= LR * (grad + mu * (w - w_global)).
DELTA: 1e-5 is below 1/n_train for every hospital (smallest train set ~ 92 rows => 1/n ~ 1e-2), so the usual rule delta < 1/n holds.
"""
import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from opacus import PrivacyEngine
from opacus.accountants import RDPAccountant
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset

from flwr.client import ClientApp, NumPyClient
from flwr.common import Context, ndarrays_to_parameters
from flwr.server import ServerApp, ServerAppComponents, ServerConfig
from flwr.server.strategy import FedAvg, FedProx
from flwr.simulation import run_simulation

STRATEGY = os.environ.get("STRATEGY", "fedavg")
MU = float(os.environ.get("MU", 0.1))  # FedProx strength; ignored for fedavg
SEED = int(os.environ.get("SEED", 0))
NUM_ROUNDS = int(os.environ.get("NUM_ROUNDS", 20))
LOCAL_EPOCHS = int(os.environ.get("LOCAL_EPOCHS", 5))
NOISE = float(os.environ.get("NOISE", 1.0))  # noise_multiplier: noise std = NOISE * CLIP. 0 = no noise
CLIP = float(os.environ.get("CLIP", 1.0))  # max_grad_norm: per-example gradient clipping bound
DELTA = float(os.environ.get("DELTA", 1e-5))
LR = 0.05

HOSPITALS = ["cleveland", "hungarian", "switzerland", "va"]
NUM_CLIENTS = len(HOSPITALS)
DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).parent / "data" / "heart_disease"))
# Deployment mode (step 6): a SuperNode container holds ONLY its own hospital's file. ALLOW_MISSING_DATA=1 lets such a process
# import this module; the other hospitals' entries in DATA are then None (and are never touched by that hospital's client).
ALLOW_MISSING_DATA = os.environ.get("ALLOW_MISSING_DATA") == "1"
COLS = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"]
NUMERIC = ["age", "sex", "fbs", "exang", "trestbps", "chol", "thalach", "oldpeak"]
BATCH = 16

torch.manual_seed(SEED)


# ---------------------------------------------------------------- data (one dict per hospital)
def load_hospital(name):
    """Clean one hospital's file and split it 75/25. All statistics come from THIS hospital's train rows only."""
    d = pd.read_csv(DATA_DIR / f"processed.{name}.data", header=None, names=COLS, na_values="?")
    d.loc[d.chol == 0, "chol"] = np.nan  # 0 mg/dl is a missing-value code, not a measurement
    d.loc[d.trestbps == 0, "trestbps"] = np.nan
    y = (d.num > 0).astype("float32").to_numpy()  # any heart disease vs none

    d["restecg"] = d.restecg.fillna(0)
    onehot = pd.concat(
        [pd.get_dummies(pd.Categorical(d.cp, categories=[1, 2, 3, 4]), prefix="cp"),
         pd.get_dummies(pd.Categorical(d.restecg, categories=[0, 1, 2]), prefix="ecg")], axis=1
    ).astype("float32")
    num = d[NUMERIC].astype("float32")  # ca, thal, slope dropped: 50-99% missing at some hospitals

    tr, te = train_test_split(np.arange(len(d)), test_size=0.25, stratify=y, random_state=SEED)
    mean = num.iloc[tr].mean()  # NaN-aware; NaN if a column is entirely missing in train
    std = num.iloc[tr].std().replace(0, 1)
    num = ((num - mean) / std).fillna(0.0)  # standardise, then missing -> 0 (= this hospital's mean)
    X = np.concatenate([num.to_numpy(), onehot.to_numpy()], axis=1).astype("float32")
    return {"X_tr": X[tr], "y_tr": y[tr], "X_te": X[te], "y_te": y[te]}


def load_all_hospitals():
    """One dict per hospital; None for a missing file only when ALLOW_MISSING_DATA=1 (otherwise a missing file is an error)."""
    return [load_hospital(h) if (not ALLOW_MISSING_DATA or (DATA_DIR / f"processed.{h}.data").exists()) else None for h in HOSPITALS]


DATA = load_all_hospitals()
N_FEATURES = next(d for d in DATA if d is not None)["X_tr"].shape[1]
for h, d in zip(HOSPITALS, DATA):
    if d is not None:
        print(f"{h:12s} train {len(d['y_tr']):3d} (disease {d['y_tr'].mean():.2f}) | test {len(d['y_te']):3d} (disease {d['y_te'].mean():.2f})")
assert all(DELTA < 1 / len(d["y_tr"]) for d in DATA if d is not None), "DELTA must be smaller than 1/n_train for every hospital"


# ---------------------------------------------------------------- model + PyTorch helpers
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(N_FEATURES, 16), nn.ReLU(), nn.Linear(16, 1))

    def forward(self, x):
        return self.net(x).squeeze(1)  # logits


def get_parameters(model):
    return [v.cpu().numpy() for v in model.state_dict().values()]


def set_parameters(model, params):
    keys = model.state_dict().keys()
    model.load_state_dict({k: torch.tensor(v) for k, v in zip(keys, params)}, strict=True)


def make_loader(X, y):
    return DataLoader(TensorDataset(torch.from_numpy(X), torch.from_numpy(y)), batch_size=BATCH, shuffle=True)


def train(model, loader, epochs, mu=0.0):
    """Non-private local SGD (step-2 code), used only by the centralized / local-only baselines."""
    global_w = [p.detach().clone() for p in model.parameters()]
    opt = torch.optim.SGD(model.parameters(), lr=LR)
    loss_fn = nn.BCEWithLogitsLoss()
    model.train()
    for _ in range(epochs):
        for xb, yb in loader:
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            if mu > 0:
                loss = loss + (mu / 2) * sum(((p - g) ** 2).sum() for p, g in zip(model.parameters(), global_w))
            loss.backward()
            opt.step()


def train_dp(model, X, y, epochs, mu, noise, clip, seed):
    """DP-SGD local training. Returns the PrivacyEngine (its accountant has this one call's privacy spend).

    FedProx is NOT a loss term here: Opacus builds per-example gradients from layer hooks, so a loss term that is not a
    per-example function of the batch would be dropped or mis-scaled. Instead, after each noisy optimizer step we pull the
    weights toward w_global: p -= LR*mu*(p - w_global). For SGD this equals adding mu*(w - w_global) to the gradient, and
    it touches only public data (w_global) and the already-privatised weights, so it is post-processing: DP still holds.
    """
    gen = torch.Generator().manual_seed(seed)  # drives the Gaussian noise only (Opacus does not use it for the sampler)
    global_w = [p.detach().clone() for p in model.parameters()]
    opt = torch.optim.SGD(model.parameters(), lr=LR)
    engine = PrivacyEngine(accountant="rdp")  # opacus default is PRV; we use RDP to match epsilon_after
    dp_model, dp_opt, dp_loader = engine.make_private(
        module=model, optimizer=opt, data_loader=make_loader(X, y),
        noise_multiplier=noise, max_grad_norm=clip, poisson_sampling=True, noise_generator=gen,
    )
    # make_private leaves the Poisson sampler on the global RNG; give it its own seeded generator for reproducibility.
    dp_loader.batch_sampler.generator = torch.Generator().manual_seed(seed + 1)
    loss_fn = nn.BCEWithLogitsLoss()
    dp_model.train()
    for _ in range(epochs):
        for xb, yb in dp_loader:
            dp_opt.zero_grad()
            loss_fn(dp_model(xb), yb).backward()
            dp_opt.step()
            if mu > 0:
                with torch.no_grad():  # the same tensors as dp_model's parameters
                    for p, g in zip(model.parameters(), global_w):
                        p -= LR * mu * (p - g)
    return engine, len(dp_loader)


def sample_rate_and_steps(n_train):
    """Opacus sets q = 1/len(loader) and runs len(loader) steps per epoch. Computed here without needing a client."""
    n_batches = math.ceil(n_train / BATCH)
    return 1 / n_batches, n_batches


def epsilon_after(n_train, rounds, noise=None, delta=None, epochs=None):
    """Deterministic epsilon of one hospital after `rounds` rounds (RDP accountant; composition over all rounds).

    No state is kept between rounds or processes: the spend is fully determined by (noise, q, total steps).
    """
    noise = NOISE if noise is None else noise
    delta = DELTA if delta is None else delta
    epochs = LOCAL_EPOCHS if epochs is None else epochs
    if noise <= 0 or rounds == 0:
        return math.inf if noise <= 0 else 0.0
    q, steps_per_epoch = sample_rate_and_steps(n_train)
    acc = RDPAccountant()
    acc.history = [(noise, q, rounds * epochs * steps_per_epoch)]
    return float(acc.get_epsilon(delta))


@torch.no_grad()
def test(model, X, y):
    model.eval()
    logits = model(torch.from_numpy(X))
    loss = nn.BCEWithLogitsLoss()(logits, torch.from_numpy(y)).item()
    pred = (logits > 0).int().numpy()
    return loss, float((pred == y).mean()), float(f1_score(y, pred, zero_division=0))


# ---------------------------------------------------------------- Flower client = one real hospital
class HospitalClient(NumPyClient):
    def __init__(self, pid):
        self.pid = pid
        self.d = DATA[pid]
        self.model = Net()

    def get_parameters(self, config):
        return get_parameters(self.model)

    def fit(self, parameters, config):  # LEARN (privately)
        model = Net()  # fresh module each round: Opacus attaches hooks to the module it wraps
        set_parameters(model, parameters)
        server_round = int(config.get("server_round", 0))
        seed = SEED * 1_000_000 + self.pid * 1_000 + server_round  # reproducible, distinct per run/hospital/round
        train_dp(model, self.d["X_tr"], self.d["y_tr"], LOCAL_EPOCHS, float(config.get("proximal_mu", 0.0)), NOISE, CLIP, seed)
        self.model = model
        return get_parameters(model), len(self.d["y_tr"]), {}

    def evaluate(self, parameters, config):  # MEASURE on this hospital's held-out test rows
        set_parameters(self.model, parameters)
        loss, acc, f1 = test(self.model, self.d["X_te"], self.d["y_te"])
        return loss, len(self.d["y_te"]), {"accuracy": acc, "f1": f1}


def client_fn(context: Context):
    return HospitalClient(int(context.node_config["partition-id"])).to_client()


# ---------------------------------------------------------------- Flower server
history = []  # one dict per round, filled by global_eval


def global_eval(server_round, parameters, config):
    """Score the current global model on every hospital's test set (reporting only, simulation-side)."""
    model = Net()
    set_parameters(model, parameters)
    per = [test(model, d["X_te"], d["y_te"]) for d in DATA]
    X = np.concatenate([d["X_te"] for d in DATA])
    y = np.concatenate([d["y_te"] for d in DATA])
    loss, acc, f1 = test(model, X, y)
    eps = [epsilon_after(len(d["y_tr"]), server_round) for d in DATA]  # spend after `server_round` completed rounds
    history.append({"round": server_round, "loss": loss, "acc": acc, "f1": f1,
                    "per_hospital_acc": [p[1] for p in per], "epsilon": eps})
    if server_round % 5 == 0 or server_round == NUM_ROUNDS:
        print(f"round {server_round:2d} | pooled test loss {loss:.3f} acc {acc:.3f} F1 {f1:.3f} | "
              f"per-hospital acc {[round(p[1], 2) for p in per]} | eps {[round(e, 2) for e in eps]}")
    return loss, {"accuracy": acc, "f1": f1}


def weighted_avg(metrics):
    total = sum(n for n, _ in metrics)
    return {k: sum(n * m[k] for n, m in metrics) / total for k in ("accuracy", "f1")}


def server_fn(context: Context):
    kw = dict(
        fraction_fit=1.0, fraction_evaluate=1.0,
        min_fit_clients=NUM_CLIENTS, min_evaluate_clients=NUM_CLIENTS, min_available_clients=NUM_CLIENTS,
        initial_parameters=ndarrays_to_parameters(get_parameters(Net())),
        evaluate_fn=global_eval, evaluate_metrics_aggregation_fn=weighted_avg,
        on_fit_config_fn=lambda r: {"server_round": r},
    )
    strategy = FedProx(proximal_mu=MU, **kw) if STRATEGY == "fedprox" else FedAvg(**kw)
    return ServerAppComponents(strategy=strategy, config=ServerConfig(num_rounds=NUM_ROUNDS))


# ---------------------------------------------------------------- baselines (non-private)
def baselines():
    """Local-only: each hospital trains alone. Centralized: pool every hospital's train rows (ignores privacy)."""
    epochs = NUM_ROUNDS * LOCAL_EPOCHS
    local = []
    for d in DATA:
        m = Net()
        train(m, make_loader(d["X_tr"], d["y_tr"]), epochs)
        local.append(test(m, d["X_te"], d["y_te"])[1])
    c = Net()
    Xtr = np.concatenate([d["X_tr"] for d in DATA])
    ytr = np.concatenate([d["y_tr"] for d in DATA])
    train(c, make_loader(Xtr, ytr), epochs)
    Xte = np.concatenate([d["X_te"] for d in DATA])
    yte = np.concatenate([d["y_te"] for d in DATA])
    _, cacc, cf1 = test(c, Xte, yte)
    return local, cacc, cf1


def finite_or_none(x):
    return None if math.isinf(x) else x  # JSON has no infinity; None means "no DP guarantee" (NOISE=0)


if __name__ == "__main__":
    local_acc, c_acc, c_f1 = baselines()
    print(f"\nlocal-only per-hospital acc {[round(a, 2) for a in local_acc]} | centralized pooled acc {c_acc:.3f} F1 {c_f1:.3f}\n")
    print(f"strategy = {STRATEGY}" + (f" (mu={MU})" if STRATEGY == "fedprox" else "")
          + f" | seed {SEED} | noise {NOISE} clip {CLIP} delta {DELTA}")

    run_simulation(
        server_app=ServerApp(server_fn=server_fn),
        client_app=ClientApp(client_fn=client_fn),
        num_supernodes=NUM_CLIENTS,
    )
    last = history[-1]
    eps = [finite_or_none(e) for e in last["epsilon"]]
    print("RESULT " + json.dumps({
        "strategy": STRATEGY, "mu": MU if STRATEGY == "fedprox" else 0.0, "seed": SEED,
        "noise": NOISE, "clip": CLIP, "delta": DELTA,
        "fed_acc": last["acc"], "fed_f1": last["f1"], "fed_per_hospital_acc": last["per_hospital_acc"],
        "epsilon_per_hospital": eps, "epsilon_max": None if any(e is None for e in eps) else max(eps),
        "local_per_hospital_acc": local_acc, "central_acc": c_acc, "central_f1": c_f1,
    }))
