"""Step 4: Step 3 (FedAvg / FedProx + Opacus DP-SGD on the 4 UCI Heart Disease hospitals) + Flower SecAgg+ (secure aggregation).

SecAgg+ hides each hospital's model update from the server: every client masks its (quantized) update with random masks
that cancel only when ALL updates are summed, so the server learns the sum and nothing about a single update.
DP (step 3) protects against what the *released model* leaks; SecAgg protects the updates *in transit and at the server*.

All model / DP / data code is imported from step3_heart_dp.py (single source of truth: the port cannot change DP or FedProx).
What is new here: the new-style `ServerApp` (`@app.main`) that runs `SecAggPlusWorkflow`, and a `secaggplus_mod` on the ClientApp.

Run one experiment (SECAGG=0 turns secure aggregation off, for comparison):
    SECAGG=1 STRATEGY=fedprox MU=0.1 NOISE=1.0 SEED=0 .venv\\Scripts\\python.exe step4_heart_secagg.py
Last line printed is `RESULT {json}`. All step-3 env vars still work (NOISE, CLIP, DELTA, STRATEGY, MU, SEED, NUM_ROUNDS, LOCAL_EPOCHS).
DEBUG_DIR (optional, used by test_step4_secagg.py): the server writes final_params.npz + round stats there, clients write
what they received (proximal_mu) and the max |weight| of their update before upload.

SecAgg+ number format (flwr secaggplus_mod): update * (num_examples / MAX_WEIGHT) is clipped to +-CLIPPING_RANGE, then quantized
to integers in [0, QUANT_RANGE]; the server sums and divides back. Anything beyond +-CLIPPING_RANGE would be silently clipped,
so the run asserts max |weight| stays below CLIPPING_RANGE.
"""
import json
import os
import time
from pathlib import Path

import numpy as np

import step3_heart_dp as s3  # data, Net, DP training, epsilon accountant, baselines (all unchanged)
from step3_heart_dp import (DATA, HOSPITALS, NUM_CLIENTS, NUM_ROUNDS, MU, STRATEGY, SEED, NOISE, CLIP, DELTA, LOCAL_EPOCHS,
                            Net, epsilon_after, finite_or_none, get_parameters, set_parameters, test, weighted_avg)

from flwr.app import Context
from flwr.client import ClientApp
from flwr.client.mod import secaggplus_mod
from flwr.common import ConfigRecord, bytes_to_ndarray, ndarrays_to_parameters
from flwr.server import ServerApp, ServerConfig
from flwr.server.compat.legacy_context import LegacyContext
from flwr.server.strategy import FedAvg, FedProx
from flwr.server.workflow import DefaultWorkflow, SecAggPlusWorkflow
from flwr.simulation import run_simulation

SECAGG = int(os.environ.get("SECAGG", 1))
NUM_SHARES = 4  # each client splits its secrets into 4 shares, one per client (itself included)
RECON_THRESHOLD = 3  # any 3 shares rebuild a secret (survives 1 dropout; needs < NUM_SHARES)
MAX_WEIGHT = 300.0  # >= the largest num_examples (cleveland train = 227); keeps num_examples / MAX_WEIGHT <= 1
CLIPPING_RANGE = 8.0
QUANT_RANGE = 2 ** 22  # flwr default quantization_range
DEBUG_DIR = os.environ.get("DEBUG_DIR")  # None in normal runs
# Dashboard hooks (step 5). Both unset = behaviour identical to before. They only observe; they never change what is trained or sent.
EVENTS_FILE = os.environ.get("EVENTS_FILE")  # server appends one JSON line per event ("baseline", "round")
INSPECT_DIR = os.environ.get("INSPECT_DIR")  # client mod writes what the server would see (stages_h<pid>.jsonl, inspect.json, *.npy)
INSPECT_ROUND = int(os.environ.get("INSPECT_ROUND", 1))  # round whose hospital-0 update / masked vector is captured in full
INSPECT_HOSPITAL = 0
MOD_RANGE = 2 ** 32  # SecAggPlusWorkflow default modulus_range


def debug_write(name, obj):
    if DEBUG_DIR:
        Path(DEBUG_DIR).mkdir(parents=True, exist_ok=True)
        (Path(DEBUG_DIR) / name).write_text(json.dumps(obj))


def emit_event(obj):
    """Append one JSON line to EVENTS_FILE and flush, so a reader sees it at once."""
    if EVENTS_FILE:
        try:
            with open(EVENTS_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(obj) + "\n")
                f.flush()
        except Exception as e:  # a hook must never take down a training run
            print(f"WARNING: could not write EVENTS_FILE: {e}")


def inspect_append(name, obj):
    Path(INSPECT_DIR).mkdir(parents=True, exist_ok=True)
    with open(Path(INSPECT_DIR) / name, "a", encoding="utf-8") as f:  # one small write per line: safe across client processes
        f.write(json.dumps(obj) + "\n")
        f.flush()


def inspect_save(name, data):
    """Write a file atomically (tmp + rename) so the dashboard server never reads half a file."""
    d = Path(INSPECT_DIR)
    d.mkdir(parents=True, exist_ok=True)
    tmp = d / (name + ".tmp")
    if isinstance(data, np.ndarray):
        with open(tmp, "wb") as f:
            np.save(f, data)
    else:
        tmp.write_text(json.dumps(data), encoding="utf-8")
    os.replace(tmp, d / name)


def _bytes_in_value(v):
    if isinstance(v, (bytes, bytearray)):
        return len(v)
    if isinstance(v, (list, tuple)):
        return sum(_bytes_in_value(x) for x in v)
    return 0


def payload_bytes(content):
    """(array payload bytes, bytes-typed config values) of a RecordDict. Excludes framing/headers and small scalars."""
    arrays = sum(len(a.data) for rec in content.array_records.values() for a in rec.values())
    cfg = sum(_bytes_in_value(v) for rec in content.config_records.values() for v in rec.values())
    return arrays, cfg


def n_arrays(content):
    return sum(len(rec) for rec in content.array_records.values())


def inspector_mod(msg, ctxt, call_next):
    """Client mod placed OUTSIDE secaggplus_mod (mods[0] is the outermost wrapper, see flwr.client.mod.utils.make_ffn).

    It sees the message the server sent and the reply the server will receive, i.e. what crosses the wire.
    It reads, never edits. The stage name must be read BEFORE call_next: secaggplus_mod pops it from the configs.
    """
    if msg.metadata.message_type != "train":
        return call_next(msg, ctxt)
    pid = int(ctxt.node_config["partition-id"])
    t0 = time.time()
    cfg_in = msg.content.config_records.get("secaggplus_configs")
    stage = str(cfg_in["stage"]) if cfg_in is not None and "stage" in cfg_in else "plain_fit"
    in_arrays, in_cfg = payload_bytes(msg.content)
    n_in = n_arrays(msg.content)

    rec = ctxt.state.config_records.get("inspector")  # per-node round counter (context state survives between messages)
    rnd = int(rec["round"]) if rec is not None else 0
    if stage in ("setup", "plain_fit"):  # a fit round starts with the setup stage (or is the only message when SecAgg is off)
        rnd += 1
        ctxt.state.config_records["inspector"] = ConfigRecord({"round": rnd})

    reply = call_next(msg, ctxt)

    try:  # observation only: a failure here must never fail the client's fit
        out_arrays, out_cfg = payload_bytes(reply.content)
        n_out = n_arrays(reply.content)
        inspect_append(f"stages_h{pid}.jsonl", {  # one file per hospital: concurrent appends from several processes lost lines on Windows
            "type": "stage", "t": t0, "t_end": time.time(), "hospital": pid, "round": rnd, "stage": stage,
            "bytes_in": in_arrays + in_cfg, "bytes_out": out_arrays + out_cfg,
            "array_bytes_in": in_arrays, "array_bytes_out": out_arrays, "plaintext_arrays_in": n_in, "plaintext_arrays_out": n_out,
        })
        if pid == INSPECT_HOSPITAL and rnd == INSPECT_ROUND and stage in ("collect_masked_vectors", "plain_fit"):
            info = {"round": rnd, "hospital": pid, "stage": stage, "secagg": SECAGG, "plaintext_arrays_out": n_out,
                    "bytes_out": out_arrays + out_cfg, "mod_range": MOD_RANGE, "quant_range": QUANT_RANGE,
                    "clipping_range": CLIPPING_RANGE, "max_weight": MAX_WEIGHT}
            out_cfgrec = reply.content.config_records.get("secaggplus_configs")
            if out_cfgrec is not None and "masked_params" in out_cfgrec:
                parts = [bytes_to_ndarray(b) for b in out_cfgrec["masked_params"]]
                masked = np.concatenate([a.ravel() for a in parts])
                info["masked_len"] = int(masked.size)
                info["masked_shapes"] = [list(a.shape) for a in parts]
                inspect_save("masked.npy", masked.astype(np.uint32))  # values are < 2**32
            inspect_save("inspect.json", info)  # written last: its presence means plain.npy + masked.npy are complete
    except Exception as e:
        print(f"WARNING: inspector_mod failed: {e!r}")
    return reply


# ---------------------------------------------------------------- client = step-3 hospital, wrapped by the SecAgg+ mod
class SecAggHospitalClient(s3.HospitalClient):
    def fit(self, parameters, config):
        params, n, metrics = super().fit(parameters, config)
        r = int(config.get("server_round", 0))
        debug_write(f"client_{self.pid}_r{r}.json", {
            "proximal_mu": float(config.get("proximal_mu", 0.0)),  # what the server actually sent
            "max_abs_update": max(float(np.abs(p).max()) for p in params),  # BEFORE masking: the clipping risk
        })
        if INSPECT_DIR and self.pid == INSPECT_HOSPITAL and r == INSPECT_ROUND:  # the plain update, BEFORE masking
            inspect_save("plain.npy", np.concatenate([p.ravel() for p in params]).astype(np.float32))
            inspect_save("plain_meta.json", {"round": r, "num_examples": int(n), "shapes": [list(p.shape) for p in params],
                                             "param_count": int(sum(p.size for p in params))})
        return params, n, metrics


def client_fn(context: Context):
    return SecAggHospitalClient(int(context.node_config["partition-id"])).to_client()


# `mods` wrap every message the client handles; secaggplus_mod runs the masking protocol on fit messages
# mods[0] is the OUTERMOST wrapper: inspector_mod goes first so it sees the already-masked reply.
client_app = ClientApp(client_fn=client_fn, mods=([inspector_mod] if INSPECT_DIR else []) + ([secaggplus_mod] if SECAGG else []))

# ---------------------------------------------------------------- server
history = []
stamps = []  # wall-clock time at each centralized evaluation (round 0 = start)
final_params = {}


def global_eval(server_round, parameters, config):
    """Same as step 3, plus: max |weight| of the aggregated model and a timestamp."""
    stamps.append(time.perf_counter())
    model = Net()
    set_parameters(model, parameters)
    per = [test(model, d["X_te"], d["y_te"]) for d in DATA]
    X = np.concatenate([d["X_te"] for d in DATA])
    y = np.concatenate([d["y_te"] for d in DATA])
    loss, acc, f1 = test(model, X, y)
    eps = [epsilon_after(len(d["y_tr"]), server_round) for d in DATA]
    max_abs = max(float(np.abs(p).max()) for p in parameters)
    if server_round > 0:
        assert max_abs < CLIPPING_RANGE, f"round {server_round}: max |weight| {max_abs:.2f} >= clipping_range {CLIPPING_RANGE}"
    if server_round > 0 and "params" in final_params:  # SecAgg+ halts silently if too many clients drop: model would not move
        assert any(not np.array_equal(a, b) for a, b in zip(final_params["params"], parameters)), f"round {server_round}: model unchanged"
    final_params["params"] = [np.array(p) for p in parameters]
    history.append({"round": server_round, "loss": loss, "acc": acc, "f1": f1, "max_abs_weight": max_abs,
                    "per_hospital_acc": [p[1] for p in per], "epsilon": eps})
    if INSPECT_DIR and server_round == INSPECT_ROUND:  # the aggregate the server obtains from the masked sum
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
    return FedProx(proximal_mu=MU, **kw) if STRATEGY == "fedprox" else FedAvg(**kw)


app = ServerApp()


@app.main()
def main(grid, context: Context) -> None:
    """Run the same FL loop as step 3, but the *fit* step (client training + aggregation) goes through SecAgg+ if SECAGG=1."""
    ctx = LegacyContext(context=context, config=ServerConfig(num_rounds=NUM_ROUNDS), strategy=make_strategy())
    if SECAGG:
        fit_workflow = SecAggPlusWorkflow(num_shares=NUM_SHARES, reconstruction_threshold=RECON_THRESHOLD,
                                          max_weight=MAX_WEIGHT, clipping_range=CLIPPING_RANGE, quantization_range=QUANT_RANGE)
        DefaultWorkflow(fit_workflow=fit_workflow)(grid, ctx)
    else:
        DefaultWorkflow()(grid, ctx)


def theoretical_quant_step():
    """Size of one quantization step in parameter units for the aggregated (weighted-average) model.

    Each client's scaled value v*(n/MAX_WEIGHT) in [-C, C] is mapped to an integer grid of QUANT_RANGE cells over width 2C,
    so one cell = 2C/QUANT_RANGE in the scaled domain. flwr rounds STOCHASTICALLY (up or down at random, unbiased), so the error
    per client is < 1 cell (not 1/2; float32 ulp adds ~0.125 cell, so use 1.125 for a strict bound, ours is practical). The server divides the sum by sum(n_i)/MAX_WEIGHT, so errors shrink by that factor
    but K clients add up: worst case = K * cell / sum(n/MAX_WEIGHT). Typical error is far smaller (random signs, ~sqrt(K)).
    """
    cell = 2 * CLIPPING_RANGE / QUANT_RANGE
    total_ratio = sum(len(d["y_tr"]) for d in DATA) / MAX_WEIGHT
    return cell, NUM_CLIENTS * cell / total_ratio


if __name__ == "__main__":
    local_acc, c_acc, c_f1 = s3.baselines()
    print(f"\nlocal-only per-hospital acc {[round(a, 2) for a in local_acc]} | centralized pooled acc {c_acc:.3f} F1 {c_f1:.3f}\n")
    emit_event({"type": "baseline", "central_acc": c_acc, "central_f1": c_f1, "local_per_hospital_acc": local_acc,
                "hospitals": HOSPITALS, "secagg": SECAGG, "strategy": STRATEGY, "noise": NOISE, "seed": SEED,
                "rounds": NUM_ROUNDS, "t": time.time()})
    print(f"secagg = {SECAGG} | strategy = {STRATEGY}" + (f" (mu={MU})" if STRATEGY == "fedprox" else "")
          + f" | seed {SEED} | noise {NOISE} clip {CLIP} delta {DELTA}")

    run_simulation(server_app=app, client_app=client_app, num_supernodes=NUM_CLIENTS)

    last = history[-1]
    eps = [finite_or_none(e) for e in last["epsilon"]]
    sec_per_round = (stamps[-1] - stamps[0]) / NUM_ROUNDS  # fits 1..N + evaluates 1..N-1 + round-0 setup; same offset ON and OFF
    if DEBUG_DIR:
        np.savez(Path(DEBUG_DIR) / "final_params.npz", *final_params["params"])
        debug_write("rounds.json", [{"round": h["round"], "max_abs_weight": h["max_abs_weight"], "acc": h["acc"]} for h in history])
    print("RESULT " + json.dumps({
        "secagg": SECAGG, "strategy": STRATEGY, "mu": MU if STRATEGY == "fedprox" else 0.0, "seed": SEED,
        "noise": NOISE, "clip": CLIP, "delta": DELTA,
        "fed_acc": last["acc"], "fed_f1": last["f1"], "fed_per_hospital_acc": last["per_hospital_acc"],
        "epsilon_per_hospital": eps, "epsilon_max": None if any(e is None for e in eps) else max(eps),
        "max_abs_weight": max(h["max_abs_weight"] for h in history), "sec_per_round": sec_per_round,
        "local_per_hospital_acc": local_acc, "central_acc": c_acc, "central_f1": c_f1,
    }))
