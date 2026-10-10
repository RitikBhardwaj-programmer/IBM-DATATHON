"""Step 6: Step 4 (FedAvg/FedProx + Opacus DP + Flower SecAgg+) as a Flower DEPLOYMENT: one SuperLink + one SuperNode per hospital.

Step 4 ran inside `flwr.simulation` (Ray, one process, env-var config). Ray has no s390x wheels, so it cannot run on IBM LinuxONE.
Deployment mode needs no Ray: every hospital is its own long-running SuperNode process/container that sees ONLY its own data file.

What changes versus step 4 is only how the run is wired, never what is computed:
  * Parameters travel as Flower *run_config* (long-running SuperNodes cannot get per-run env vars). `apply_run_config` copies them
    into the step-3 / step-4 module globals on both sides, so all model, DP, SecAgg and hook code is reused unchanged.
  * The `ServerApp` (below) is step 4's `__main__` as a Flower app: baselines FIRST (they consume the torch RNG; the initial model is
    drawn after them, exactly as in step 4), then the strategy and the same workflows.
  * The ClientApp mods are always installed and switch themselves on/off from run_config (SecAgg on/off, inspector on/off).

Start (see run_step6_local.py for a native launcher, deploy/docker-compose.yml for containers):
    flwr run . local --run-config "noise=1.0 strategy=\\"fedprox\\" secagg=1 rounds=3"
The last log line of the ServerApp is `RESULT {json}` (same format as step 4).
Demo limits (be honest): the ServerApp process holds all four files to compute the non-private baselines and the pooled test score
(evaluation only, never used for training). Real SuperNodes hold only their own file. Transport is insecure gRPC (no TLS) in the demo.
"""
import json
import time
from pathlib import Path

import numpy as np
import torch

import step3_heart_dp as s3
import step4_heart_secagg as s4

from flwr.app import Context
from flwr.client import ClientApp
from flwr.client.mod import secaggplus_mod
from flwr.server import ServerApp, ServerConfig
from flwr.server.compat.legacy_context import LegacyContext
from flwr.server.workflow import DefaultWorkflow, SecAggPlusWorkflow

_applied = {"seed": None}
s3_import_seed = s3.SEED  # seed the hospital split was made with at import (from the env SEED)


def _opt(value):
    """run_config has no None: an empty string means 'not set'."""
    return value if value else None


def apply_run_config(cfg):
    """Set the step-3 / step-4 module globals from a Flower run_config (keys as in pyproject.toml). Safe to call repeatedly."""
    seed = int(cfg["seed"])
    for mod in (s3, s4):  # step 4 did `from step3 import NOISE, ...`: its functions read ITS copies, step 3's read THEIRS
        mod.NOISE = float(cfg["noise"])
        mod.CLIP = float(cfg["clip"])
        mod.DELTA = float(cfg["delta"])
        mod.STRATEGY = str(cfg["strategy"])
        mod.MU = float(cfg["mu"])
        mod.SEED = seed
        mod.NUM_ROUNDS = int(cfg["rounds"])
        mod.LOCAL_EPOCHS = int(cfg["local-epochs"])
    s4.SECAGG = int(cfg["secagg"])
    s4.EVENTS_FILE = _opt(str(cfg["events-file"]))
    s4.INSPECT_DIR = _opt(str(cfg["inspect-dir"]))
    s4.INSPECT_ROUND = int(cfg["inspect-round"])
    s4.DEBUG_DIR = _opt(str(cfg["debug-dir"]))
    if _applied["seed"] != seed:
        if _applied["seed"] is not None or seed != s3_import_seed:  # the split depends on SEED (random_state): reload only if it changed
            s3.DATA[:] = s3.load_all_hospitals()  # in place: step 4 holds a reference to the same list
        torch.manual_seed(seed)  # step 3 seeds at import with the env SEED; do the same for the run's seed
        _applied["seed"] = seed



# ---------------------------------------------------------------- client side
def inspector_switch_mod(msg, ctxt, call_next):
    """Step 4's inspector_mod, active only when the run's config has an inspect-dir (it needs a folder to write to)."""
    apply_run_config(ctxt.run_config)
    if not s4.INSPECT_DIR:
        return call_next(msg, ctxt)
    return s4.inspector_mod(msg, ctxt, call_next)


def secagg_switch_mod(msg, ctxt, call_next):
    """secaggplus_mod only when this run uses SecAgg+. The server's SecAggPlusWorkflow decides the same from the same run_config."""
    apply_run_config(ctxt.run_config)
    if not s4.SECAGG:
        return call_next(msg, ctxt)
    return secaggplus_mod(msg, ctxt, call_next)


def client_fn(context: Context):
    apply_run_config(context.run_config)
    pid = int(context.node_config["partition-id"])
    assert s3.DATA[pid] is not None, f"hospital {pid} ({s3.HOSPITALS[pid]}): no data file in DATA_DIR={s3.DATA_DIR}"
    return s4.SecAggHospitalClient(pid).to_client()


# mods[0] is the OUTERMOST wrapper: the inspector goes first so it sees the already-masked reply (see step4 inspector_mod).
client_app = ClientApp(client_fn=client_fn, mods=[inspector_switch_mod, secagg_switch_mod])

# ---------------------------------------------------------------- server side
app = ServerApp()


@app.main()
def main(grid, context: Context) -> None:
    apply_run_config(context.run_config)
    s4.history.clear()
    s4.stamps.clear()
    s4.final_params.clear()

    # SAME ORDER AS step4 __main__: baselines first (they draw from the torch RNG), THEN the initial model inside make_strategy().
    local_acc, c_acc, c_f1 = s3.baselines()
    print(f"\nlocal-only per-hospital acc {[round(a, 2) for a in local_acc]} | centralized pooled acc {c_acc:.3f} F1 {c_f1:.3f}\n")
    s4.emit_event({"type": "baseline", "central_acc": c_acc, "central_f1": c_f1, "local_per_hospital_acc": local_acc,
                   "hospitals": s3.HOSPITALS, "secagg": s4.SECAGG, "strategy": s4.STRATEGY, "noise": s4.NOISE, "seed": s4.SEED,
                   "rounds": s4.NUM_ROUNDS, "t": time.time()})
    print(f"secagg = {s4.SECAGG} | strategy = {s4.STRATEGY}" + (f" (mu={s4.MU})" if s4.STRATEGY == "fedprox" else "")
          + f" | seed {s4.SEED} | noise {s4.NOISE} clip {s4.CLIP} delta {s4.DELTA}")

    ctx = LegacyContext(context=context, config=ServerConfig(num_rounds=s4.NUM_ROUNDS), strategy=s4.make_strategy())
    if s4.SECAGG:
        fit_workflow = SecAggPlusWorkflow(num_shares=s4.NUM_SHARES, reconstruction_threshold=s4.RECON_THRESHOLD,
                                          max_weight=s4.MAX_WEIGHT, clipping_range=s4.CLIPPING_RANGE, quantization_range=s4.QUANT_RANGE)
        DefaultWorkflow(fit_workflow=fit_workflow)(grid, ctx)
    else:
        DefaultWorkflow()(grid, ctx)

    last = s4.history[-1]
    eps = [s3.finite_or_none(e) for e in last["epsilon"]]
    sec_per_round = (s4.stamps[-1] - s4.stamps[0]) / s4.NUM_ROUNDS
    if s4.DEBUG_DIR:
        np.savez(Path(s4.DEBUG_DIR) / "final_params.npz", *s4.final_params["params"])
        s4.debug_write("rounds.json", [{"round": h["round"], "max_abs_weight": h["max_abs_weight"], "acc": h["acc"]} for h in s4.history])
    result = {
        "secagg": s4.SECAGG, "strategy": s4.STRATEGY, "mu": s4.MU if s4.STRATEGY == "fedprox" else 0.0, "seed": s4.SEED,
        "noise": s4.NOISE, "clip": s4.CLIP, "delta": s4.DELTA,
        "fed_acc": last["acc"], "fed_f1": last["f1"], "fed_per_hospital_acc": last["per_hospital_acc"],
        "epsilon_per_hospital": eps, "epsilon_max": None if any(e is None for e in eps) else max(eps),
        "max_abs_weight": max(h["max_abs_weight"] for h in s4.history), "sec_per_round": sec_per_round,
        "local_per_hospital_acc": local_acc, "central_acc": c_acc, "central_f1": c_f1,
    }
    s4.debug_write("result.json", result)
    print("RESULT " + json.dumps(result))
    s4.emit_event({"type": "done", "t": time.time()})
