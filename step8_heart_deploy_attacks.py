"""Step 8: Step 7 (malicious hospital, curious server, median defence) as a Flower DEPLOYMENT, so the attacks run on IBM LinuxONE.

Step 7 runs only as a simulation (Ray), and Ray has no s390x wheels. Step 6 showed how to run step 4 as a deployment (1 SuperLink +
1 SuperNode per hospital) without changing what is computed. Step 8 does the same for step 7, reusing steps 3, 4, 6 and 7 unchanged:
  * `apply_run_config` = step 6's (step 3 / step 4 globals) + the attack keys and the step-3/4 values that step 7 imported BY VALUE
    (`from step3_heart_dp import NOISE, ...` gives step 7 its own copies, read by its functions).
  * Client = step 7's AttackHospitalClient behind step 6's switch mods. Server = step 6's order (baselines first: same torch RNG
    order as the simulation) with step 7's strategy (FedAvg / FedProx / FedMedian / FedTrimmedAvg), global_eval and attack summary.
  * Step 7's client -> server side channel (the attacker's clip stats and the MIA hospital's last update) is the folder
    `attack-dir` on the volume all containers share (the dashboard uses <run dir>/attack). Without it the run still trains and
    attacks; it only skips the membership test (mia=0) and the clip stats.

Run (native, no Docker): .venv\\Scripts\\python.exe run_step6_local.py rounds=3 secagg=1 attack=labelflip attack-dir=C:/tmp/a
attack=none agg=fedavg is step 6 exactly (and so step 4); any attack equals step 7's simulation with the same settings.
The last ServerApp log line is `RESULT {json}` with step 7's keys; the events file gets step 7's "attack" event before "done".
Demo limits: as step 6 (the ServerApp holds all 4 files for evaluation and the MIA); the MIA reads the honest hospital's update from
the shared folder, standing in for what the server receives when SecAgg+ is off (as in step 7).
"""
import json
import os
import tempfile
import time
from pathlib import Path

import numpy as np

import step3_heart_dp as s3
import step4_heart_secagg as s4
import step6_heart_deploy as s6
import step7_heart_attacks as s7

from flwr.app import Context
from flwr.client import ClientApp
from flwr.server import ServerApp, ServerConfig
from flwr.server.compat.legacy_context import LegacyContext
from flwr.server.workflow import DefaultWorkflow, SecAggPlusWorkflow

SIDE_FILES = ("attacker.jsonl", "mia_update.npz")


def apply_run_config(cfg):
    """Step 6's apply_run_config, then step 7's settings. Raises ValueError on a combination step 7 refuses."""
    s6.apply_run_config(cfg)
    for name in ("NOISE", "CLIP", "DELTA", "STRATEGY", "MU", "SEED", "NUM_ROUNDS", "LOCAL_EPOCHS"):
        setattr(s7, name, getattr(s3, name))
    for name in ("SECAGG", "INSPECT_DIR", "INSPECT_ROUND", "DEBUG_DIR"):
        setattr(s7, name, getattr(s4, name))
    s7.ATTACK = str(cfg["attack"])
    s7.ATTACKER = int(cfg["attacker"])
    s7.BOOST = float(cfg["boost"])
    s7.AGG = str(cfg["agg"])
    s7.TRIM_BETA = float(cfg["trim-beta"])
    s7.MIA_HOSPITAL = int(cfg["mia-hospital"])
    attack_dir = s6._opt(str(cfg["attack-dir"]))
    s7.MIA = int(cfg["mia"]) if attack_dir else 0  # the membership test needs the honest hospital's update from the shared folder
    if attack_dir:
        os.environ[s7.ATTACK_DIR_ENV] = attack_dir  # step 7's clients and summary find the side channel through this variable
    else:
        os.environ.pop(s7.ATTACK_DIR_ENV, None)
    err = s7.config_error()
    if err:
        raise ValueError(err)


# ---------------------------------------------------------------- client side
def client_fn(context: Context):
    apply_run_config(context.run_config)
    pid = int(context.node_config["partition-id"])
    assert s3.DATA[pid] is not None, f"hospital {pid} ({s3.HOSPITALS[pid]}): no data file in DATA_DIR={s3.DATA_DIR}"
    return s7.AttackHospitalClient(pid).to_client()


# Same mods and order as step 6 (they only need the step 3 / step 4 settings).
client_app = ClientApp(client_fn=client_fn, mods=[s6.inspector_switch_mod, s6.secagg_switch_mod])

# ---------------------------------------------------------------- server side
app = ServerApp()


@app.main()
def main(grid, context: Context) -> None:
    apply_run_config(context.run_config)
    for state in (s7.history, s7.stamps, s7.final_params):
        state.clear()
    out = s7.attack_dir()
    if out:
        out.mkdir(parents=True, exist_ok=True)
        for name in SIDE_FILES:  # a reused folder must not leak an older run's rows (step 7 does the same)
            (out / name).unlink(missing_ok=True)

    # SAME ORDER AS step 6 / step 7 __main__: baselines first (they draw from the torch RNG), THEN the strategy's initial model.
    local_acc, c_acc, c_f1 = s3.baselines()
    print(f"\nlocal-only per-hospital acc {[round(a, 2) for a in local_acc]} | centralized pooled acc {c_acc:.3f} F1 {c_f1:.3f}\n")
    s4.emit_event({"type": "baseline", "central_acc": c_acc, "central_f1": c_f1, "local_per_hospital_acc": local_acc,
                   "hospitals": s3.HOSPITALS, "secagg": s7.SECAGG, "strategy": s7.STRATEGY, "noise": s7.NOISE, "seed": s7.SEED,
                   "rounds": s7.NUM_ROUNDS, "attack": s7.ATTACK, "attacker": s7.ATTACKER, "agg": s7.AGG, "t": time.time()})
    print(f"secagg = {s7.SECAGG} | strategy = {s7.STRATEGY}" + (f" (mu={s7.MU})" if s7.STRATEGY == "fedprox" else "")
          + f" | agg {s7.AGG} | attack {s7.ATTACK}" + (f" by {s3.HOSPITALS[s7.ATTACKER]}" if s7.ATTACK != "none" else "")
          + f" | seed {s7.SEED} | noise {s7.NOISE} clip {s7.CLIP} delta {s7.DELTA}")

    ctx = LegacyContext(context=context, config=ServerConfig(num_rounds=s7.NUM_ROUNDS), strategy=s7.make_strategy())
    if s7.SECAGG:
        fit_workflow = SecAggPlusWorkflow(num_shares=s4.NUM_SHARES, reconstruction_threshold=s4.RECON_THRESHOLD,
                                          max_weight=s4.MAX_WEIGHT, clipping_range=s4.CLIPPING_RANGE, quantization_range=s4.QUANT_RANGE)
        DefaultWorkflow(fit_workflow=fit_workflow)(grid, ctx)
    else:
        DefaultWorkflow()(grid, ctx)

    history = s7.history
    last = history[-1]
    eps = [s3.finite_or_none(e) for e in last["epsilon"]]
    sec_per_round = (s7.stamps[-1] - s7.stamps[0]) / s7.NUM_ROUNDS
    if s7.DEBUG_DIR:
        np.savez(Path(s7.DEBUG_DIR) / "final_params.npz", *s7.final_params["params"])
        s4.debug_write("rounds.json", [{"round": h["round"], "max_abs_weight": h["max_abs_weight"], "acc": h["acc"]} for h in history])
    # attack_summary reads the side files from a folder; without attack-dir there are none (MIA is off, so it reads nothing)
    summary = s7.attack_summary(out if out else Path(tempfile.mkdtemp(prefix="step8_")))
    s4.emit_event({"type": "attack", **summary, "t": time.time()})
    print(f"attack {s7.ATTACK} | honest-hospital acc {summary['honest_acc']:.3f} | MIA on {s3.HOSPITALS[s7.MIA_HOSPITAL]}: "
          f"update AUC {summary['mia_auc_update']} global AUC {summary['mia_auc_global']}")
    result = {
        "secagg": s7.SECAGG, "strategy": s7.STRATEGY, "mu": s7.MU if s7.STRATEGY == "fedprox" else 0.0, "seed": s7.SEED,
        "noise": s7.NOISE, "clip": s7.CLIP, "delta": s7.DELTA,
        "fed_acc": last["acc"], "fed_f1": last["f1"], "fed_per_hospital_acc": last["per_hospital_acc"],
        "epsilon_per_hospital": eps, "epsilon_max": None if any(e is None for e in eps) else max(eps),
        "max_abs_weight": max(h["max_abs_weight"] for h in history), "sec_per_round": sec_per_round,
        "local_per_hospital_acc": local_acc, "central_acc": c_acc, "central_f1": c_f1,
        "local_epochs": s7.LOCAL_EPOCHS, **summary,
    }
    s4.debug_write("result.json", result)
    print("RESULT " + json.dumps(result))
    s4.emit_event({"type": "done", "t": time.time()})
