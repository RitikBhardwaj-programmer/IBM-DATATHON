"""Checks for step 6 (Flower deployment mode, native on this machine). Plain script, no pytest. Takes several minutes.
Run: .venv\\Scripts\\python.exe test_step6_deploy.py

One deployment (1 SuperLink + 4 SuperNodes, each with only its own data file) serves all the runs below, one after the other.
  a) SECAGG=0 deployment == step 4 SECAGG=0 simulation (same seed/params): accuracy, F1, per-hospital accuracy, epsilon (diff < 1e-9);
     for FedAvg and FedProx. This is the gate: deployment mode must not change what is computed.
  b) SECAGG=1 deployment: aggregate within the SecAgg+ quantization bound of the SECAGG=0 deployment; same epsilon.
  c) dashboard hooks in deployment: 1 baseline event, rounds 0..N, stage files for 4 hospitals, inspect files, masked vector ~ uniform.
  d) after the deployment stops: no SuperLink / SuperNode / SuperExec / ServerApp / ClientApp process and no open port is left.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import run_step6_local as L  # noqa: E402

ROUNDS = 3
SIM_ENV = {"NOISE": "1.0", "SEED": "0", "NUM_ROUNDS": str(ROUNDS), "PYTHONIOENCODING": "utf-8"}
PROC_RE = r"flower-(superlink|supernode|superexec)|flwr-(serverapp|clientapp)"


def sim(**env):
    """Step 4 as a simulation, in a subprocess (its settings are env vars read at import)."""
    e = {**os.environ, **SIM_ENV, **{k: str(v) for k, v in env.items()}}
    out = subprocess.run([sys.executable, str(HERE / "step4_heart_secagg.py")], env=e, capture_output=True, text=True, cwd=HERE, timeout=900)
    lines = [l for l in out.stdout.splitlines() if l.startswith("RESULT ")]
    assert out.returncode == 0 and lines, f"step4 failed:\n{out.stdout[-2000:]}\n{out.stderr[-2000:]}"
    return json.loads(lines[-1][len("RESULT "):])


def stack_processes():
    """Command lines of Flower deployment processes alive on this machine."""
    if sys.platform == "win32":
        ps = ("Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match '%s' } | "
              "ForEach-Object { \"$($_.ProcessId) $($_.CommandLine)\" }" % PROC_RE)
        out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=60).stdout
    else:
        out = subprocess.run(["ps", "-eo", "pid,args"], capture_output=True, text=True, timeout=60).stdout
        out = "\n".join(l for l in out.splitlines() if re.search(PROC_RE, l) and "test_step6" not in l)
    return [l for l in out.splitlines() if l.strip()]


def cfg_for(tmp, tag, **kw):
    c = {"rounds": ROUNDS, "noise": 1.0, "seed": 0, "strategy": "fedavg", "secagg": 0, "debug-dir": str(tmp / tag)}
    c.update(kw)
    (tmp / tag).mkdir(parents=True, exist_ok=True)
    return c


assert not stack_processes(), f"a deployment is already running on this machine: {stack_processes()}"
tmp = Path(tempfile.mkdtemp(prefix="step6_test_"))
import step4_heart_secagg as s4  # noqa: E402  (loading data + defining apps only; for the quantization bound)

# ---- reference: step 4 simulation, SECAGG=0
ref = {"fedavg": sim(SECAGG=0, STRATEGY="fedavg"), "fedprox": sim(SECAGG=0, STRATEGY="fedprox", MU="0.1")}
print("reference (step 4 simulation, SECAGG=0) done")

with L.LocalDeployment(workdir=tmp / "deploy") as dep:
    # ---- a) SECAGG=0 deployment == simulation
    dep_off = {}
    for strat in ("fedavg", "fedprox"):
        text = dep.run(cfg_for(tmp, f"off_{strat}", strategy=strat, mu=0.1))
        r = L.parse_result(text)
        assert r is not None, text[-2000:]
        dep_off[strat] = r
        s = ref[strat]
        d_acc, d_f1 = abs(r["fed_acc"] - s["fed_acc"]), abs(r["fed_f1"] - s["fed_f1"])
        d_hosp = max(abs(a - b) for a, b in zip(r["fed_per_hospital_acc"], s["fed_per_hospital_acc"]))
        d_eps = max(abs(a - b) for a, b in zip(r["epsilon_per_hospital"], s["epsilon_per_hospital"]))
        d_base = max(abs(r["central_acc"] - s["central_acc"]), abs(r["central_f1"] - s["central_f1"]),
                     max(abs(a - b) for a, b in zip(r["local_per_hospital_acc"], s["local_per_hospital_acc"])))
        assert max(d_acc, d_f1, d_hosp, d_eps, d_base) < 1e-9, (strat, d_acc, d_f1, d_hosp, d_eps, d_base, r, s)
        print(f"a) OK  {strat}: deployment == simulation: acc {r['fed_acc']:.6f} (diff {d_acc:.1e}), F1 diff {d_f1:.1e}, "
              f"per-hospital diff {d_hosp:.1e}, epsilon diff {d_eps:.1e}, baselines diff {d_base:.1e}")
    pa = np.load(tmp / "off_fedavg" / "final_params.npz")
    pf = np.load(tmp / "off_fedprox" / "final_params.npz")
    assert max(float(np.abs(pa[k] - pf[k]).max()) for k in pa.files) > 1e-6, "FedProx run equals FedAvg run: mu did not reach the clients"

    # ---- b) + c) SECAGG=1 deployment with the dashboard hooks on
    ev, insp = tmp / "on" / "events.jsonl", tmp / "on" / "insp"
    text = dep.run(cfg_for(tmp, "on", secagg=1, **{"events-file": str(ev), "inspect-dir": str(insp), "inspect-round": 1}))
    r_on = L.parse_result(text)
    assert r_on is not None, text[-2000:]
    assert r_on["epsilon_per_hospital"] == dep_off["fedavg"]["epsilon_per_hospital"], "epsilon must not depend on SecAgg"
    d_acc = abs(r_on["fed_acc"] - dep_off["fedavg"]["fed_acc"])
    assert d_acc < 0.05, d_acc
    # strict bound, as in test_step4_secagg.py (b): ONE round, so the quantization error has not been fed back through training
    run1 = {}
    for sa in (0, 1):
        t1 = dep.run(cfg_for(tmp, f"one_{sa}", secagg=sa, rounds=1))
        run1[sa] = np.load(tmp / f"one_{sa}" / "final_params.npz")
    measured = max(float(np.abs(run1[1][k] - run1[0][k]).max()) for k in run1[1].files)
    cell, bound = s4.theoretical_quant_step()
    print(f"b) quantization cell (scaled domain) = {cell:.2e}; worst-case bound on aggregate = {bound:.2e}; "
          f"measured max |ON - OFF| after 1 round = {measured:.2e}")
    assert 0 < measured <= bound, "SecAgg differs from plain FedAvg by more than the quantization bound (or is identical = not applied)"
    print(f"b) OK  3-round SecAgg ON acc {r_on['fed_acc']:.4f} vs OFF {dep_off['fedavg']['fed_acc']:.4f}; epsilon identical")

    lines = [json.loads(l) for l in ev.read_text(encoding="utf-8").splitlines() if l.strip()]
    base = [e for e in lines if e["type"] == "baseline"]
    rounds = [e["round"] for e in lines if e["type"] == "round"]
    assert len(base) == 1 and base[0]["secagg"] == 1 and base[0]["rounds"] == ROUNDS, base
    assert rounds == list(range(0, ROUNDS + 1)), rounds
    assert lines[-1]["type"] == "done"
    stage_files = sorted(p.name for p in insp.glob("stages_h*.jsonl"))
    assert stage_files == [f"stages_h{i}.jsonl" for i in range(4)], stage_files
    for f in ("plain.npy", "plain_meta.json", "masked.npy", "inspect.json", "aggregate.npy"):
        assert (insp / f).is_file(), f"missing inspect file {f}"
    info = json.loads((insp / "inspect.json").read_text())
    assert info["secagg"] == 1 and info["masked_len"] == 274 and info["plaintext_arrays_out"] == 0, info
    masked = np.load(insp / "masked.npy")
    counts, _ = np.histogram(masked[1:], bins=16, range=(0, 2 ** 32))
    exp = (masked.size - 1) / 16
    chi2 = float(((counts - exp) ** 2 / exp).sum())
    assert chi2 < 37.70, f"masked vector not uniform: chi2 {chi2:.1f} (df 15, p 0.001)"
    plain = np.load(insp / "plain.npy")
    assert plain.size == 273 and not np.array_equal(plain.astype(np.float64), masked[1:].astype(np.float64))
    print(f"c) OK  1 baseline, rounds {rounds}, 4 stage files, inspect files present, masked len {masked.size}, chi2 {chi2:.1f} < 37.70, "
          f"plaintext arrays out = {info['plaintext_arrays_out']}")

# ---- d) nothing left behind
time.sleep(5)  # Flower's helper processes watch their parent and exit within a few seconds
left = stack_processes()
ports = [p for p in [L.CONTROL_PORT, L.FLEET_PORT] + [L.NODE_PORT0 + i for i in range(4)] if L.port_open(p)]
assert not left and not ports, f"survivors: {left}; open ports {ports}"
print("d) OK  no SuperLink / SuperNode / SuperExec / ServerApp / ClientApp process and no open port left")

print("ALL OK")
