"""Checks for step 8 (step 7's attackers in the Flower deployment). Plain script, no pytest. Takes about 10-15 minutes.
Run: .venv\\Scripts\\python.exe test_step8_deploy_attacks.py

One native deployment (run_step6_local.LocalDeployment: 1 SuperLink + 4 SuperNodes, each with only its own data file) serves all runs.
The reference is always step 7 as a SIMULATION with the same settings (step 7 == step 4 when there is no attack).
  a) attack=none, SECAGG=0, no attack-dir: same training result as step 7 (fed acc, F1, per-hospital acc, epsilon); MIA is skipped.
  b) labelflip by va, SECAGG=0: same training result AND the same attack fields (honest/attacker acc, both MIA AUCs) as step 7.
  c) boost by va + median, SECAGG=0: as b (the median defence runs in the deployment).
  d) flipboost by va, SECAGG=1: the run completes with all attack fields; the attacker's clip stats were written; MIA AUCs in [0, 1];
     honest accuracy within 0.03 of the simulation (SecAgg+ quantization is unseeded, so not bit-equal).
  e) median + SECAGG=1 is refused with step 7's message and gives no RESULT.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import run_step6_local as L  # noqa: E402

ROUNDS = 3
TRAIN_KEYS = ("fed_acc", "fed_f1", "fed_per_hospital_acc", "epsilon_per_hospital", "central_acc", "local_per_hospital_acc")
ATTACK_KEYS = ("honest_acc", "attacker_acc", "mia_n", "mia_auc_update", "mia_auc_global", "agg_over_range_rounds")
tmp = Path(tempfile.mkdtemp(prefix="step8_test_"))
failures = []


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    if not ok:
        failures.append(name)


def sim(tag, **env):
    """Step 7 as a simulation in a subprocess (settings are env vars read at import)."""
    d = tmp / f"sim_{tag}"
    d.mkdir(parents=True, exist_ok=True)
    e = {**os.environ, "NOISE": "1.0", "SEED": "0", "NUM_ROUNDS": str(ROUNDS), "PYTHONIOENCODING": "utf-8",
         "STEP7_ATTACK_DIR": str(d), **{k: str(v) for k, v in env.items()}}
    out = subprocess.run([sys.executable, str(HERE / "step7_heart_attacks.py")], env=e, capture_output=True, text=True, cwd=HERE, timeout=900)
    lines = [l for l in out.stdout.splitlines() if l.startswith("RESULT ")]
    assert out.returncode == 0 and lines, f"step7 {tag} failed:\n{out.stdout[-2000:]}\n{out.stderr[-2000:]}"
    return json.loads(lines[-1][len("RESULT "):])


def cfg(tag, attack_dir=True, **kw):
    c = {"rounds": ROUNDS, "noise": 1.0, "seed": 0, "strategy": "fedavg", "secagg": 0}
    if attack_dir:
        (tmp / f"dep_{tag}").mkdir(parents=True, exist_ok=True)
        c["attack-dir"] = (tmp / f"dep_{tag}").as_posix()
    c.update(kw)
    return c


def same(a, b, keys):
    diff = {k: (a.get(k), b.get(k)) for k in keys if json.dumps(a.get(k)) != json.dumps(b.get(k))}
    return not diff, diff


refs = {
    "a": sim("a", ATTACK="none", SECAGG=0, MIA=0),
    "b": sim("b", ATTACK="labelflip", SECAGG=0),
    "c": sim("c", ATTACK="boost", AGG="median", SECAGG=0),
    "d": sim("d", ATTACK="flipboost", SECAGG=1),
}
print("references (step 7 simulation) done")

with L.LocalDeployment() as dep:
    print(f"deployment work dir {dep.work}")
    res = {}
    res["a"] = L.parse_result(dep.run(cfg("a", attack_dir=False)))
    res["b"] = L.parse_result(dep.run(cfg("b", attack="labelflip")))
    res["c"] = L.parse_result(dep.run(cfg("c", attack="boost", agg="median")))
    res["d"] = L.parse_result(dep.run(cfg("d", attack="flipboost", secagg=1)))
    try:
        text_e = dep.run(cfg("e", agg="median", secagg=1), timeout=300)
    except RuntimeError as err:
        text_e = str(err)

ok, diff = same(res["a"], refs["a"], TRAIN_KEYS)
check("a) attack=none deployment == step 7 simulation (training)", ok, str(diff))
check("a) no attack-dir -> MIA skipped", res["a"]["mia_auc_update"] is None and res["a"]["attack"] == "none")

for t, label in (("b", "labelflip"), ("c", "boost + median")):
    ok, diff = same(res[t], refs[t], TRAIN_KEYS + ATTACK_KEYS)
    check(f"{t}) {label}: deployment == step 7 simulation (training + attack fields)", ok, str(diff))
check("c) the deployment used the median", res["c"]["agg"] == "median")

d = res["d"]
check("d) flipboost + SecAgg completes with the attack fields", d is not None and d["attack"] == "flipboost" and d["secagg"] == 1)
check("d) attacker clip stats written", d["max_scaled_attacker"] is not None, f"max_scaled {d['max_scaled_attacker']}")
check("d) MIA AUCs in [0, 1]", all(0 <= d[k] <= 1 for k in ("mia_auc_update", "mia_auc_global")))
check("d) honest accuracy close to the simulation", abs(d["honest_acc"] - refs["d"]["honest_acc"]) <= 0.03,
      f"deploy {d['honest_acc']:.3f} sim {refs['d']['honest_acc']:.3f}")

check("e) median + SecAgg refused", "RESULT {" not in text_e and "SecAgg+ hides exactly that" in text_e, text_e[-300:].replace("\n", " "))

print(f"\n{len(failures)} failure(s)" + (f": {failures}" if failures else ""))
sys.exit(1 if failures else 0)
