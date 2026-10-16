"""Step 7: Step 4 (FedAvg / FedProx + Opacus DP-SGD + Flower SecAgg+ on the 4 UCI Heart Disease hospitals) + two attackers.

Attackers (one per direction of threat):
  * Integrity: one MALICIOUS HOSPITAL (ATTACKER) poisons its update every round.
      ATTACK=labelflip  trains on flipped labels (sick <-> healthy), same DP, same seed formula.
      ATTACK=boost      sends global + BOOST * (local - global): its update counts BOOST times more in the average.
  * Privacy: an HONEST-BUT-CURIOUS SERVER runs a loss-threshold membership inference attack (MIA, Yeom et al. 2018)
    after training: "was this patient in hospital MIA_HOSPITAL's training set?" Members = that hospital's train rows,
    non-members = its test rows (balanced, seeded subsample). Score = -loss (members tend to have lower loss).
    Two targets: (a) that hospital's own update in the last round (what the server sees when SECAGG=0),
                 (b) the final global model (all the server gets when SECAGG=1).

Defence against poisoning: AGG=median (Flower FedMedian) or AGG=trimmed (FedTrimmedAvg, TRIM_BETA). Both need every
hospital's update in the clear, which SecAgg+ hides by design, so AGG != fedavg with SECAGG=1 is refused.
With 4 hospitals, trimmed mean with beta 0.25 cuts 1 from each end = the mean of the middle 2 = np.median: the same rule.
Both ignore num_examples (unweighted), so they differ from FedAvg even with no attacker.

All model / DP / data / SecAgg code is imported from step 3 and step 4 unchanged. ATTACK=none + AGG=fedavg reproduces step 4
exactly (same seed -> same accuracy, F1, per-hospital accuracy, epsilon); the MIA runs after training with its own RNG.

Run one experiment:
    ATTACK=labelflip SECAGG=1 NOISE=1.0 SEED=0 .venv\\Scripts\\python.exe step7_heart_attacks.py
    ATTACK=boost AGG=median SECAGG=0 NOISE=1.0 SEED=0 .venv\\Scripts\\python.exe step7_heart_attacks.py
Env: ATTACK (none|labelflip|boost, default none), ATTACKER (hospital id, default 3 = va), BOOST (default 10.0),
     AGG (fedavg|median|trimmed, default fedavg), TRIM_BETA (default 0.25), MIA (0/1, default 1),
     MIA_HOSPITAL (default 0 = cleveland: largest test set; must differ from ATTACKER, else the run is refused),
     plus every step 3 / step 4 env var and hook.

Output schema (dashboard step 5 hooks still work):
  EVENTS_FILE gets, after the last "round" line, one line
    {"type": "attack", "attack", "attacker", "attacker_name", "boost", "agg", "secagg", "noise", "seed", "rounds",
     "mia_hospital", "mia_hospital_name", "mia_n", "mia_auc_update", "mia_adv_update", "mia_auc_global", "mia_adv_global",
     "honest_acc", "attacker_acc", "clipped_rounds", "max_scaled_attacker", "agg_over_range_rounds", "t"}
  The last stdout line is `RESULT {json}`: every step 4 RESULT key, plus the same attack fields (without "type"/"t").
  mia_* are null when MIA=0. mia_adv_* uses the best threshold chosen on the same rows it scores, so it is optimistic
  (well above 0 even with no leak); AUC is the number to quote. clipped_rounds counts rounds where the attacker's scaled update
  reached SecAgg+'s +-CLIPPING_RANGE (approximate: same scaling as secaggplus_mod, >= instead of >; 0 when SECAGG=0).
  agg_over_range_rounds counts rounds whose aggregate has a weight beyond +-CLIPPING_RANGE; it only matters with SECAGG=1.
  honest_acc = mean accuracy of the hospitals other than ATTACKER, also when ATTACK=none (same hospitals in every comparison).
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import roc_auc_score, roc_curve

import step3_heart_dp as s3
import step4_heart_secagg as s4  # importing only loads data + defines apps (no simulation)
from step3_heart_dp import (DATA, HOSPITALS, NUM_CLIENTS, NUM_ROUNDS, MU, STRATEGY, SEED, NOISE, CLIP, DELTA, LOCAL_EPOCHS,
                            Net, epsilon_after, finite_or_none, get_parameters, set_parameters, test, weighted_avg)
from step4_heart_secagg import (SECAGG, NUM_SHARES, RECON_THRESHOLD, MAX_WEIGHT, CLIPPING_RANGE, QUANT_RANGE, DEBUG_DIR,
                                INSPECT_DIR, INSPECT_ROUND, emit_event, inspect_save, inspector_mod, debug_write)

from flwr.app import Context
from flwr.client import ClientApp
from flwr.client.mod import secaggplus_mod
from flwr.common import ndarrays_to_parameters
from flwr.server import ServerApp, ServerConfig
from flwr.server.compat.legacy_context import LegacyContext
from flwr.server.strategy import FedAvg, FedMedian, FedProx, FedTrimmedAvg
from flwr.server.workflow import DefaultWorkflow, SecAggPlusWorkflow
from flwr.simulation import run_simulation

ATTACK = os.environ.get("ATTACK", "none")
ATTACKER = int(os.environ.get("ATTACKER", 3))
BOOST = float(os.environ.get("BOOST", 10.0))
AGG = os.environ.get("AGG", "fedavg")
TRIM_BETA = float(os.environ.get("TRIM_BETA", 0.25))  # flwr cuts int(beta * 4): 0.2 would cut nothing with 4 hospitals
MIA = int(os.environ.get("MIA", 1))
MIA_HOSPITAL = int(os.environ.get("MIA_HOSPITAL", 0))
# Side channel from the clients to this process (simulation only): the MIA hospital's last update + the attacker's clip stats.
# The main process creates it before the simulation starts; clients read it at fit time (they inherit the environment).
ATTACK_DIR_ENV = "STEP7_ATTACK_DIR"


def config_error():
    """Return an error message for an invalid or contradictory configuration, or None."""
    if ATTACK not in ("none", "labelflip", "boost"):
        return f"ATTACK must be none, labelflip or boost (got {ATTACK!r})"
    if AGG not in ("fedavg", "median", "trimmed"):
        return f"AGG must be fedavg, median or trimmed (got {AGG!r})"
    if not 0 <= ATTACKER < NUM_CLIENTS or not 0 <= MIA_HOSPITAL < NUM_CLIENTS:
        return f"ATTACKER and MIA_HOSPITAL must be hospital ids 0..{NUM_CLIENTS - 1}"
    if MIA and ATTACK != "none" and ATTACKER == MIA_HOSPITAL:
        return "MIA_HOSPITAL must not be the ATTACKER: a poisoned update says nothing about an honest hospital's privacy"
    if AGG != "fedavg" and SECAGG:
        return (f"AGG={AGG} needs every hospital's update in the clear, and SecAgg+ hides exactly that (the server only gets "
                f"the sum). Use SECAGG=0 with AGG={AGG}, or AGG=fedavg with SECAGG=1.")
    if AGG != "fedavg" and STRATEGY == "fedprox":
        return "STRATEGY=fedprox is a FedAvg variant; use it with AGG=fedavg"
    return None


_err = config_error()
if _err:
    sys.exit(f"ERROR: {_err}")


def attack_dir():
    d = os.environ.get(ATTACK_DIR_ENV)
    return Path(d) if d else None


# ---------------------------------------------------------------- membership inference (the curious server)
@torch.no_grad()
def example_losses(params, X, y):
    """Per-example BCE loss of the model with these parameters."""
    model = Net()
    set_parameters(model, params)
    model.eval()
    return nn.BCEWithLogitsLoss(reduction="none")(model(torch.from_numpy(X)), torch.from_numpy(y)).numpy()


def mia(params, X_in, y_in, X_out, y_out, seed):
    """Loss-threshold membership inference. Returns (AUC, advantage, n per side).

    Balanced: n = min(#members, #non-members) rows from each side (seeded), so a coin flip scores AUC 0.5.
    AUC: chance a random member gets a lower loss than a random non-member. Advantage: best threshold's TPR - FPR.
    """
    rng = np.random.default_rng(seed)
    n = min(len(y_in), len(y_out))
    i_in = rng.choice(len(y_in), n, replace=False)
    i_out = rng.choice(len(y_out), n, replace=False)
    scores = -np.concatenate([example_losses(params, X_in[i_in], y_in[i_in]), example_losses(params, X_out[i_out], y_out[i_out])])
    labels = np.concatenate([np.ones(n), np.zeros(n)])
    fpr, tpr, _ = roc_curve(labels, scores)
    return float(roc_auc_score(labels, scores)), float(np.max(tpr - fpr)), int(n)


# ---------------------------------------------------------------- client = step-4 hospital; one of them may be malicious
class AttackHospitalClient(s4.SecAggHospitalClient):
    def __init__(self, pid):
        super().__init__(pid)
        if ATTACK == "labelflip" and pid == ATTACKER:
            self.d = {**self.d, "y_tr": (1 - self.d["y_tr"]).astype(np.float32)}  # train rows only; test labels stay true

    def fit(self, parameters, config):
        params, n, metrics = super().fit(parameters, config)
        r = int(config.get("server_round", 0))
        out = attack_dir()
        if ATTACK == "boost" and self.pid == ATTACKER:
            params = [(g + BOOST * (p - g)).astype(np.float32) for p, g in zip(params, parameters)]
        if out and self.pid == ATTACKER and ATTACK != "none":
            max_scaled = max(float(np.abs(p).max()) for p in params) * n / MAX_WEIGHT  # what secaggplus_mod compares to the clip
            with open(out / "attacker.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps({"round": r, "max_scaled": max_scaled, "clipped": bool(SECAGG and max_scaled >= CLIPPING_RANGE)}) + "\n")
        if out and MIA and self.pid == MIA_HOSPITAL and r == NUM_ROUNDS:  # the update the server would see with SECAGG=0
            np.savez(out / "mia_update.npz", *params)
        return params, n, metrics


def client_fn(context: Context):
    return AttackHospitalClient(int(context.node_config["partition-id"])).to_client()


client_app = ClientApp(client_fn=client_fn, mods=([inspector_mod] if INSPECT_DIR else []) + ([secaggplus_mod] if SECAGG else []))

# ---------------------------------------------------------------- server
history = []
stamps = []
final_params = {}


def global_eval(server_round, parameters, config):
    """Step 4's global_eval. Only difference: under an attack, an aggregate beyond +-CLIPPING_RANGE is recorded, not asserted."""
    stamps.append(time.perf_counter())
    model = Net()
    set_parameters(model, parameters)
    per = [test(model, d["X_te"], d["y_te"]) for d in DATA]
    X = np.concatenate([d["X_te"] for d in DATA])
    y = np.concatenate([d["y_te"] for d in DATA])
    loss, acc, f1 = test(model, X, y)
    eps = [epsilon_after(len(d["y_tr"]), server_round) for d in DATA]
    max_abs = max(float(np.abs(p).max()) for p in parameters)
    if server_round > 0 and ATTACK == "none":
        assert max_abs < CLIPPING_RANGE, f"round {server_round}: max |weight| {max_abs:.2f} >= clipping_range {CLIPPING_RANGE}"
    if server_round > 0 and "params" in final_params:  # SecAgg+ halts silently if too many clients drop: model would not move
        assert any(not np.array_equal(a, b) for a, b in zip(final_params["params"], parameters)), f"round {server_round}: model unchanged"
    final_params["params"] = [np.array(p) for p in parameters]
    history.append({"round": server_round, "loss": loss, "acc": acc, "f1": f1, "max_abs_weight": max_abs,
                    "per_hospital_acc": [p[1] for p in per], "epsilon": eps})
    if INSPECT_DIR and server_round == INSPECT_ROUND:
        inspect_save("aggregate.npy", np.concatenate([np.asarray(p).ravel() for p in parameters]).astype(np.float32))
    emit_event({"type": "round", "round": server_round, "total_rounds": NUM_ROUNDS, "acc": acc, "f1": f1, "loss": finite_or_none(loss),
                "per_hospital_acc": [p[1] for p in per], "epsilon": [finite_or_none(e) for e in eps],
                "max_abs_weight": finite_or_none(max_abs), "t": time.time()})
    if server_round % 5 == 0 or server_round == NUM_ROUNDS:
        print(f"round {server_round:2d} | pooled test loss {loss:.3f} acc {acc:.3f} F1 {f1:.3f} | max|w| {max_abs:.2f} | "
              f"per-hospital acc {[round(p[1], 2) for p in per]} | eps {[round(e, 2) for e in eps]}")
    return loss, {"accuracy": acc, "f1": f1}


def make_strategy():
    kw = dict(
        fraction_fit=1.0, fraction_evaluate=1.0,
        min_fit_clients=NUM_CLIENTS, min_evaluate_clients=NUM_CLIENTS, min_available_clients=NUM_CLIENTS,
        initial_parameters=ndarrays_to_parameters(get_parameters(Net())),
        evaluate_fn=global_eval, evaluate_metrics_aggregation_fn=weighted_avg,
        on_fit_config_fn=lambda r: {"server_round": r},
    )
    if AGG == "median":
        return FedMedian(**kw)
    if AGG == "trimmed":
        return FedTrimmedAvg(beta=TRIM_BETA, **kw)
    return FedProx(proximal_mu=MU, **kw) if STRATEGY == "fedprox" else FedAvg(**kw)


app = ServerApp()


@app.main()
def main(grid, context: Context) -> None:
    """Step 4's main with this file's strategy (and global_eval)."""
    ctx = LegacyContext(context=context, config=ServerConfig(num_rounds=NUM_ROUNDS), strategy=make_strategy())
    if SECAGG:
        fit_workflow = SecAggPlusWorkflow(num_shares=NUM_SHARES, reconstruction_threshold=RECON_THRESHOLD,
                                          max_weight=MAX_WEIGHT, clipping_range=CLIPPING_RANGE, quantization_range=QUANT_RANGE)
        DefaultWorkflow(fit_workflow=fit_workflow)(grid, ctx)
    else:
        DefaultWorkflow()(grid, ctx)


def attack_summary(out):
    """Attack fields for the "attack" event and the RESULT line (reads the side channel written by the clients)."""
    last = history[-1]
    honest = [a for i, a in enumerate(last["per_hospital_acc"]) if i != ATTACKER]
    rows = [json.loads(l) for l in (out / "attacker.jsonl").read_text(encoding="utf-8").splitlines()] if (out / "attacker.jsonl").exists() else []
    res = {"attack": ATTACK, "attacker": ATTACKER, "attacker_name": HOSPITALS[ATTACKER], "boost": BOOST if ATTACK == "boost" else None,
           "agg": AGG, "secagg": SECAGG, "noise": NOISE, "seed": SEED, "rounds": NUM_ROUNDS,
           "mia_hospital": MIA_HOSPITAL, "mia_hospital_name": HOSPITALS[MIA_HOSPITAL], "mia_n": None,
           "mia_auc_update": None, "mia_adv_update": None, "mia_auc_global": None, "mia_adv_global": None,
           "honest_acc": float(np.mean(honest)), "attacker_acc": last["per_hospital_acc"][ATTACKER],
           "clipped_rounds": sum(r["clipped"] for r in rows), "max_scaled_attacker": max((r["max_scaled"] for r in rows), default=None),
           "agg_over_range_rounds": sum(h["max_abs_weight"] >= CLIPPING_RANGE for h in history if h["round"] > 0)}
    if MIA:
        d = DATA[MIA_HOSPITAL]
        z = np.load(out / "mia_update.npz")
        update = [z[k] for k in z.files]
        mia_seed = SEED * 1_000_000 + 999  # own RNG: the MIA never touches the training RNG streams
        res["mia_auc_update"], res["mia_adv_update"], res["mia_n"] = mia(update, d["X_tr"], d["y_tr"], d["X_te"], d["y_te"], mia_seed)
        res["mia_auc_global"], res["mia_adv_global"], _ = mia(final_params["params"], d["X_tr"], d["y_tr"], d["X_te"], d["y_te"], mia_seed)
    return res


if __name__ == "__main__":
    out = Path(os.environ.get(ATTACK_DIR_ENV) or tempfile.mkdtemp(prefix="step7_"))
    out.mkdir(parents=True, exist_ok=True)
    os.environ[ATTACK_DIR_ENV] = str(out)  # before run_simulation, so the client processes inherit it
    for name in ("attacker.jsonl", "mia_update.npz"):  # a reused dir must not leak an older run's rows
        (out / name).unlink(missing_ok=True)

    local_acc, c_acc, c_f1 = s3.baselines()
    print(f"\nlocal-only per-hospital acc {[round(a, 2) for a in local_acc]} | centralized pooled acc {c_acc:.3f} F1 {c_f1:.3f}\n")
    emit_event({"type": "baseline", "central_acc": c_acc, "central_f1": c_f1, "local_per_hospital_acc": local_acc,
                "hospitals": HOSPITALS, "secagg": SECAGG, "strategy": STRATEGY, "noise": NOISE, "seed": SEED,
                "rounds": NUM_ROUNDS, "attack": ATTACK, "attacker": ATTACKER, "agg": AGG, "t": time.time()})
    print(f"secagg = {SECAGG} | strategy = {STRATEGY}" + (f" (mu={MU})" if STRATEGY == "fedprox" else "")
          + f" | agg {AGG} | attack {ATTACK}" + (f" by {HOSPITALS[ATTACKER]}" if ATTACK != "none" else "")
          + f" | seed {SEED} | noise {NOISE} clip {CLIP} delta {DELTA}")

    run_simulation(server_app=app, client_app=client_app, num_supernodes=NUM_CLIENTS)

    last = history[-1]
    eps = [finite_or_none(e) for e in last["epsilon"]]
    sec_per_round = (stamps[-1] - stamps[0]) / NUM_ROUNDS
    if DEBUG_DIR:
        np.savez(Path(DEBUG_DIR) / "final_params.npz", *final_params["params"])
        debug_write("rounds.json", [{"round": h["round"], "max_abs_weight": h["max_abs_weight"], "acc": h["acc"]} for h in history])
    summary = attack_summary(out)
    emit_event({"type": "attack", **summary, "t": time.time()})
    print(f"attack {ATTACK} | honest-hospital acc {summary['honest_acc']:.3f} | MIA on {HOSPITALS[MIA_HOSPITAL]}: "
          f"update AUC {summary['mia_auc_update']} global AUC {summary['mia_auc_global']}")
    print("RESULT " + json.dumps({
        "secagg": SECAGG, "strategy": STRATEGY, "mu": MU if STRATEGY == "fedprox" else 0.0, "seed": SEED,
        "noise": NOISE, "clip": CLIP, "delta": DELTA,
        "fed_acc": last["acc"], "fed_f1": last["f1"], "fed_per_hospital_acc": last["per_hospital_acc"],
        "epsilon_per_hospital": eps, "epsilon_max": None if any(e is None for e in eps) else max(eps),
        "max_abs_weight": max(h["max_abs_weight"] for h in history), "sec_per_round": sec_per_round,
        "local_per_hospital_acc": local_acc, "central_acc": c_acc, "central_f1": c_f1,
        "local_epochs": LOCAL_EPOCHS, **summary,
    }))
