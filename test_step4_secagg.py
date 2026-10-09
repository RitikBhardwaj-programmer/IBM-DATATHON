"""Checks for step 4 (SecAgg+). Plain script, no pytest. Each check runs a short real simulation in a subprocess
(step 3 / step 4 read their settings from env vars at import time, so one process = one config).
Run: .venv\\Scripts\\python.exe test_step4_secagg.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ROUNDS = "3"
BASE_ENV = {"NOISE": "1.0", "SEED": "0", "NUM_ROUNDS": ROUNDS, "PYTHONIOENCODING": "utf-8"}


def run(script, debug_dir=None, **env):
    e = {**os.environ, **BASE_ENV, **{k: str(v) for k, v in env.items()}}
    if debug_dir:
        e["DEBUG_DIR"] = str(debug_dir)
    out = subprocess.run([sys.executable, str(HERE / script)], env=e, capture_output=True, text=True, cwd=HERE, timeout=900)
    lines = [l for l in out.stdout.splitlines() if l.startswith("RESULT ")]
    assert out.returncode == 0 and lines, f"{script} failed:\n{out.stdout[-2000:]}\n{out.stderr[-2000:]}"
    return json.loads(lines[-1][len("RESULT "):])


tmp = Path(tempfile.mkdtemp(prefix="step4_test_"))
sys.path.insert(0, str(HERE))

# ---- a) SECAGG=0 port reproduces step 3 (same seed, same DP, same FedAvg)
for strat, mu in (("fedavg", 0.0), ("fedprox", 0.1)):
    r3 = run("step3_heart_dp.py", STRATEGY=strat, MU=mu)
    r4_off = run("step4_heart_secagg.py", debug_dir=tmp / f"off_{strat}", SECAGG=0, STRATEGY=strat, MU=mu)
    d_acc = abs(r3["fed_acc"] - r4_off["fed_acc"])
    d_f1 = abs(r3["fed_f1"] - r4_off["fed_f1"])
    d_hosp = max(abs(a - b) for a, b in zip(r3["fed_per_hospital_acc"], r4_off["fed_per_hospital_acc"]))
    assert d_acc < 1e-9 and d_f1 < 1e-9 and d_hosp < 1e-9, (strat, d_acc, d_f1, d_hosp)
    assert r3["epsilon_per_hospital"] == r4_off["epsilon_per_hospital"]
    print(f"a) OK  {strat}: port == step 3: acc {r4_off['fed_acc']:.6f} (diff {d_acc:.1e}), F1 diff {d_f1:.1e}, per-hospital diff {d_hosp:.1e}, epsilon identical")

# ---- b) one round, SecAgg ON vs OFF, same seed: aggregated parameters agree within quantization error
run("step4_heart_secagg.py", debug_dir=tmp / "b_off", SECAGG=0, STRATEGY="fedavg", NUM_ROUNDS=1)
run("step4_heart_secagg.py", debug_dir=tmp / "b_on", SECAGG=1, STRATEGY="fedavg", NUM_ROUNDS=1)
import step4_heart_secagg as s4  # safe: importing only loads data + defines apps (no simulation)

on = np.load(tmp / "b_on" / "final_params.npz")
off = np.load(tmp / "b_off" / "final_params.npz")
measured = max(float(np.abs(on[k] - off[k]).max()) for k in on.files)
cell, bound = s4.theoretical_quant_step()
print(f"b) quantization cell (scaled domain) = {cell:.2e}; worst-case bound on aggregate = {bound:.2e}; "
      f"measured max |ON - OFF| = {measured:.2e}")
assert 0 < measured <= bound, "SecAgg differs from plain FedAvg by more than the quantization bound (or is identical = not applied)"
print("b) OK")

r4_on = run("step4_heart_secagg.py", debug_dir=tmp / "on", SECAGG=1, STRATEGY="fedavg")

# ---- c) max |weight| stays inside the clipping range, every round (aggregate and each client's own update)
rounds = json.loads((tmp / "on" / "rounds.json").read_text())
agg_max = max(r["max_abs_weight"] for r in rounds)
client_max = max(json.loads(p.read_text())["max_abs_update"] for p in (tmp / "on").glob("client_*_r*.json"))
assert agg_max < s4.CLIPPING_RANGE and client_max < s4.CLIPPING_RANGE
print(f"c) OK  max|w| aggregate {agg_max:.3f}, client updates {client_max:.3f} < clipping_range {s4.CLIPPING_RANGE}")

# ---- d) FedProx proximal_mu reaches the clients through the SecAgg+ workflow
run("step4_heart_secagg.py", debug_dir=tmp / "prox", SECAGG=1, STRATEGY="fedprox", MU="0.1")
files = sorted((tmp / "prox").glob("client_*_r*.json"))
mus = {json.loads(p.read_text())["proximal_mu"] for p in files}
assert len(files) == 4 * int(ROUNDS) and mus == {0.1}, (len(files), mus)
fedavg_mus = {json.loads(p.read_text())["proximal_mu"] for p in (tmp / "on").glob("client_*_r*.json")}
assert fedavg_mus == {0.0}
print(f"d) OK  proximal_mu seen by {len(files)} client fits under SecAgg+ = {mus}; fedavg clients saw {fedavg_mus}")

print("ALL OK")
