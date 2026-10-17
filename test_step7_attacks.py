"""Checks for step 7 (attacks). Plain script, no pytest. Each check runs a short real simulation in a subprocess
(steps 3/4/7 read their settings from env vars at import time, so one process = one config).
Run: .venv\\Scripts\\python.exe test_step7_attacks.py
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


def proc(script, debug_dir=None, **env):
    e = {**os.environ, **BASE_ENV, **{k: str(v) for k, v in env.items()}}
    if debug_dir:
        e["DEBUG_DIR"] = str(debug_dir)
    return subprocess.run([sys.executable, str(HERE / script)], env=e, capture_output=True, text=True, cwd=HERE, timeout=900)


def run(script, debug_dir=None, **env):
    out = proc(script, debug_dir, **env)
    lines = [l for l in out.stdout.splitlines() if l.startswith("RESULT ")]
    assert out.returncode == 0 and lines, f"{script} failed:\n{out.stdout[-2000:]}\n{out.stderr[-2000:]}"
    return json.loads(lines[-1][len("RESULT "):])


def params(debug_dir):
    z = np.load(debug_dir / "final_params.npz")
    return np.concatenate([z[k].ravel() for k in z.files])


tmp = Path(tempfile.mkdtemp(prefix="step7_test_"))
sys.path.insert(0, str(HERE))

# ---- a) ATTACK=none, AGG=fedavg reproduces step 4 exactly (SecAgg off and on)
clean = {}
for secagg in (0, 1):
    r4 = run("step4_heart_secagg.py", SECAGG=secagg)
    r7 = run("step7_heart_attacks.py", debug_dir=tmp / f"clean_{secagg}", SECAGG=secagg)
    for k in ("fed_acc", "fed_f1", "fed_per_hospital_acc", "epsilon_per_hospital", "central_acc", "local_per_hospital_acc"):
        assert r4[k] == r7[k], (secagg, k, r4[k], r7[k])
    clean[secagg] = r7
    print(f"a) OK  SECAGG={secagg}: step 7 (no attack) == step 4: acc {r7['fed_acc']:.6f}, F1, per-hospital acc, epsilon, baselines identical")

# ---- b) label flip by one hospital lowers the honest hospitals' accuracy (same seed, SecAgg on)
flip = run("step7_heart_attacks.py", debug_dir=tmp / "flip_1", SECAGG=1, ATTACK="labelflip")
print(f"b) honest-hospital acc: clean {clean[1]['honest_acc']:.3f} -> label flip {flip['honest_acc']:.3f}")
assert flip["honest_acc"] < clean[1]["honest_acc"], "label flip did not lower honest-hospital accuracy"
print("b) OK")

# ---- c) boost moves the aggregate further from the clean aggregate than label flip (SecAgg off: no clipping)
flip0 = run("step7_heart_attacks.py", debug_dir=tmp / "flip_0", SECAGG=0, ATTACK="labelflip")
boost = run("step7_heart_attacks.py", debug_dir=tmp / "boost_0", SECAGG=0, ATTACK="boost")
base = params(tmp / "clean_0")
d_flip = float(np.linalg.norm(params(tmp / "flip_0") - base))
d_boost = float(np.linalg.norm(params(tmp / "boost_0") - base))
print(f"c) ||aggregate - clean||: label flip {d_flip:.3f}, boost x10 {d_boost:.3f}; honest acc boost {boost['honest_acc']:.3f}")
assert d_boost > d_flip, "boost should move the aggregate more than label flip"
assert boost["clipped_rounds"] == 0, "nothing is clipped when SecAgg is off"
print("c) OK")

# ---- g) flip + boost (boosting a harmful direction) lowers honest accuracy more than label flip alone (same seed, SecAgg off)
fb = run("step7_heart_attacks.py", debug_dir=tmp / "flipboost_0", SECAGG=0, ATTACK="flipboost")
print(f"g) honest-hospital acc: clean {clean[0]['honest_acc']:.3f}, label flip {flip0['honest_acc']:.3f}, flip+boost x10 {fb['honest_acc']:.3f}")
assert fb["honest_acc"] < flip0["honest_acc"], "flip+boost did not lower honest-hospital accuracy more than label flip"
assert fb["clipped_rounds"] == 0, "nothing is clipped when SecAgg is off"
fb1 = run("step7_heart_attacks.py", debug_dir=tmp / "flipboost_1", SECAGG=1, ATTACK="flipboost")
print(f"g) with SecAgg+: honest acc {fb1['honest_acc']:.3f}, attacker update clipped in {fb1['clipped_rounds']} of {ROUNDS} rounds "
      f"(max scaled value {fb1['max_scaled_attacker']:.2f}, clipping range 8)")
print("g) OK")

# ---- d) the MIA scorer: AUC in [0,1], and ~0.5 when 'members' and 'non-members' come from the same rows
import step7_heart_attacks as s7  # safe: importing only loads data + defines apps (no simulation)

d0 = s7.DATA[0]
p0 = [np.asarray(p) for p in np.load(tmp / "clean_0" / "final_params.npz").values()]
aucs = []
for i in range(200):
    perm = np.random.default_rng(i).permutation(len(d0["y_te"]))
    a, b = perm[: len(perm) // 2], perm[len(perm) // 2:]
    auc, adv, n = s7.mia(p0, d0["X_te"][a], d0["y_te"][a], d0["X_te"][b], d0["y_te"][b], seed=i)
    assert 0.0 <= auc <= 1.0 and 0.0 <= adv <= 1.0
    aucs.append(auc)
print(f"d) MIA on two random halves of the same test set: mean AUC {np.mean(aucs):.3f} (sd {np.std(aucs):.3f}, 200 splits)")
assert abs(np.mean(aucs) - 0.5) < 0.02, "a coin-flip setting should average AUC 0.5"
r = clean[0]
assert all(0.0 <= r[k] <= 1.0 for k in ("mia_auc_update", "mia_adv_update", "mia_auc_global", "mia_adv_global"))
print("d) OK")

# ---- e) robust aggregation with SecAgg+ is refused (it needs the individual updates SecAgg+ hides)
for agg in ("median", "trimmed"):
    out = proc("step7_heart_attacks.py", SECAGG=1, AGG=agg)
    assert out.returncode != 0 and "SecAgg+ hides" in out.stderr, (agg, out.returncode, out.stderr[-500:])
print("e) OK  AGG=median/trimmed with SECAGG=1 refused with an explanation")

# ---- f) median and trimmed mean run; with 4 hospitals and beta 0.25 they are the same rule
med = run("step7_heart_attacks.py", debug_dir=tmp / "median", SECAGG=0, AGG="median")
trim = run("step7_heart_attacks.py", debug_dir=tmp / "trimmed", SECAGG=0, AGG="trimmed")
diff = float(np.abs(params(tmp / "median") - params(tmp / "trimmed")).max())
print(f"f) clean acc: fedavg {clean[0]['fed_acc']:.3f}, median {med['fed_acc']:.3f}, trimmed {trim['fed_acc']:.3f}; "
      f"max |median - trimmed| = {diff:.1e}")
assert diff < 1e-6, "with 4 clients, trimmed mean (beta 0.25) should equal the median"
print("f) OK")
print("\nALL STEP 7 CHECKS PASSED")
