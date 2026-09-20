"""Step 2: FedAvg vs FedProx on the UCI Heart Disease data, using its 4 REAL hospitals as clients.

No simulated split: Cleveland, Hungarian, Switzerland and VA Long Beach each become one client.
Their differences (disease rate 36%-93%, age, sex mix, missing measurements) are natural non-IID.

Run one experiment:
    STRATEGY=fedavg  SEED=0 .venv\\Scripts\\python.exe step2_heart_fedavg_fedprox.py
    STRATEGY=fedprox MU=0.1 SEED=0 .venv\\Scripts\\python.exe step2_heart_fedavg_fedprox.py
Last line printed is `RESULT {json}` so a runner can collect many runs.
"""
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
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
LR = 0.05

HOSPITALS = ["cleveland", "hungarian", "switzerland", "va"]
NUM_CLIENTS = len(HOSPITALS)
DATA_DIR = Path(__file__).parent / "data" / "heart_disease"
COLS = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"]
NUMERIC = ["age", "sex", "fbs", "exang", "trestbps", "chol", "thalach", "oldpeak"]

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


DATA = [load_hospital(h) for h in HOSPITALS]
N_FEATURES = DATA[0]["X_tr"].shape[1]
for h, d in zip(HOSPITALS, DATA):
    print(f"{h:12s} train {len(d['y_tr']):3d} (disease {d['y_tr'].mean():.2f}) | test {len(d['y_te']):3d} (disease {d['y_te'].mean():.2f})")


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


def train(model, loader, epochs, mu=0.0):
    """Local SGD. If mu > 0 (FedProx) add  mu/2 * ||w - w_global||^2  to the loss: a rubber band to the global model."""
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


@torch.no_grad()
def test(model, X, y):
    model.eval()
    logits = model(torch.from_numpy(X))
    loss = nn.BCEWithLogitsLoss()(logits, torch.from_numpy(y)).item()
    pred = (logits > 0).int().numpy()
    return loss, float((pred == y).mean()), float(f1_score(y, pred, zero_division=0))


def make_loader(X, y):
    return DataLoader(TensorDataset(torch.from_numpy(X), torch.from_numpy(y)), batch_size=16, shuffle=True)


# ---------------------------------------------------------------- Flower client = one real hospital
class HospitalClient(NumPyClient):
    def __init__(self, pid):
        self.d = DATA[pid]
        self.model = Net()
        self.loader = make_loader(self.d["X_tr"], self.d["y_tr"])

    def get_parameters(self, config):
        return get_parameters(self.model)

    def fit(self, parameters, config):  # LEARN
        set_parameters(self.model, parameters)
        train(self.model, self.loader, LOCAL_EPOCHS, mu=float(config.get("proximal_mu", 0.0)))
        return get_parameters(self.model), len(self.d["y_tr"]), {}

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
    history.append({"round": server_round, "loss": loss, "acc": acc, "f1": f1, "per_hospital_acc": [p[1] for p in per]})
    if server_round % 5 == 0 or server_round == NUM_ROUNDS:
        print(f"round {server_round:2d} | pooled test loss {loss:.3f} acc {acc:.3f} F1 {f1:.3f} | per-hospital acc {[round(p[1], 2) for p in per]}")
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
    )
    strategy = FedProx(proximal_mu=MU, **kw) if STRATEGY == "fedprox" else FedAvg(**kw)
    return ServerAppComponents(strategy=strategy, config=ServerConfig(num_rounds=NUM_ROUNDS))


# ---------------------------------------------------------------- baselines
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


if __name__ == "__main__":
    local_acc, c_acc, c_f1 = baselines()
    print(f"\nlocal-only per-hospital acc {[round(a, 2) for a in local_acc]} | centralized pooled acc {c_acc:.3f} F1 {c_f1:.3f}\n")
    print(f"strategy = {STRATEGY}" + (f" (mu={MU})" if STRATEGY == "fedprox" else "") + f" | seed {SEED}")

    run_simulation(
        server_app=ServerApp(server_fn=server_fn),
        client_app=ClientApp(client_fn=client_fn),
        num_supernodes=NUM_CLIENTS,
    )
    last = history[-1]
    print("RESULT " + json.dumps({
        "strategy": STRATEGY, "mu": MU if STRATEGY == "fedprox" else 0.0, "seed": SEED,
        "fed_acc": last["acc"], "fed_f1": last["f1"], "fed_per_hospital_acc": last["per_hospital_acc"],
        "local_per_hospital_acc": local_acc, "central_acc": c_acc, "central_f1": c_f1,
    }))
