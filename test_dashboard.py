"""Checks for step 5 (dashboard backend + hooks in step4_heart_secagg.py). Plain script, no pytest. Prints ALL OK at the end.
Run: .venv\\Scripts\\python.exe test_dashboard.py     (takes a few minutes: it runs short real simulations)

Covers: a) hook equivalence, b) API happy path + SSE, c) 422 / 404 / 409, d) inspector checks on captured data,
        e) stop leaves no child process behind.
Uses fastapi.testclient (httpx is installed in the venv).
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
BASE_ENV = {"NOISE": "1.0", "SEED": "0", "NUM_ROUNDS": "3", "PYTHONIOENCODING": "utf-8"}
tmp = Path(tempfile.mkdtemp(prefix="dashboard_test_"))


def run_step4(**env):
    """Run step4 as a subprocess (it reads its settings from env at import time). Returns the RESULT dict."""
    e = {**os.environ, **BASE_ENV, **{k: str(v) for k, v in env.items()}}
    out = subprocess.run([sys.executable, str(HERE / "step4_heart_secagg.py")], env=e, capture_output=True, text=True, cwd=HERE, timeout=900)
    return parse_result(out.stdout, out.stderr, out.returncode)


def parse_result(stdout, stderr="", code=0):
    lines = [l for l in stdout.splitlines() if l.startswith("RESULT ")]
    assert code == 0 and lines, f"run failed (exit {code}):\n{stdout[-1500:]}\n{stderr[-1500:]}"
    return json.loads(lines[-1][len("RESULT "):])


# ---------------------------------------------------------------- a) hook equivalence
# SECAGG=0 is deterministic, so hooks on/off must match EXACTLY. SECAGG=1 uses flwr's unseeded stochastic rounding
# (not bit-reproducible, see CLAUDE.md), so there epsilon must match exactly and accuracy within 0.02 (a few test rows).
off0 = run_step4(SECAGG=0)
on0 = run_step4(SECAGG=0, EVENTS_FILE=tmp / "ev0.jsonl", INSPECT_DIR=tmp / "insp0")
for k in ("fed_acc", "fed_f1", "fed_per_hospital_acc", "epsilon_per_hospital"):
    assert off0[k] == on0[k], (k, off0[k], on0[k])
# max |w| differed at the 1e-7 level in one hooks-off run vs two others (float32 run-to-run jitter, not the hooks): allow 1e-5
assert abs(off0["max_abs_weight"] - on0["max_abs_weight"]) < 1e-5, (off0["max_abs_weight"], on0["max_abs_weight"])
print(f"a) OK  SECAGG=0, hooks on == hooks off exactly: acc {on0['fed_acc']:.6f}, F1 {on0['fed_f1']:.6f}, eps {on0['epsilon_per_hospital']}")
off1 = run_step4(SECAGG=1)

# ---------------------------------------------------------------- API
from fastapi.testclient import TestClient  # noqa: E402

import dashboard.server as server  # noqa: E402

server.RUNS_DIR = tmp / "runs"
GOOD = {"noise": 1.0, "strategy": "fedavg", "secagg": True, "rounds": 3, "seed": 0}


def parse_sse(lines):
    events, ev = [], None
    for l in lines:
        if l.startswith("event: "):
            ev = l[7:]
        elif l.startswith("data: "):
            events.append((ev, json.loads(l[6:])))
    return events


with TestClient(server.app) as c:
    # ---- c) validation
    bad = [
        {**GOOD, "noise": -0.1}, {**GOOD, "noise": 5.1}, {**GOOD, "noise": "abc"}, {**GOOD, "strategy": "fedsgd"},
        {**GOOD, "rounds": 0}, {**GOOD, "rounds": 31}, {**GOOD, "rounds": 1.5}, {**GOOD, "seed": 100}, {**GOOD, "seed": -1},
        {**GOOD, "secagg": "yes"}, {**GOOD, "extra": 1}, {k: v for k, v in GOOD.items() if k != "noise"},
    ]
    for body in bad:
        r = c.post("/api/runs", json=body)
        assert r.status_code == 422, (body, r.status_code, r.text)
    r = c.post("/api/runs", content='{"noise": NaN, "strategy": "fedavg", "secagg": true}', headers={"content-type": "application/json"})
    assert r.status_code == 422, r.text
    assert c.post("/api/runs", content="not json", headers={"content-type": "application/json"}).status_code == 422
    assert c.get("/api/runs/current").json() == {"status": "idle"}
    print(f"c) OK  {len(bad) + 2} invalid bodies -> 422, nothing started")
    # path traversal / unknown ids never reach the filesystem
    for url in ("/api/replays/..%2F..%2Fstep4_heart_secagg", "/api/replays/..x", "/api/replays/a.b", "/api/inspect/a.b", "/api/inspect/x%2Fy",
                "/api/inspect/nope", "/api/runs/nope/events", "/api/replays/20250101-000000-abcdef"):
        assert c.get(url).status_code == 404, url
    assert c.post("/api/runs/nope/stop").status_code == 404
    assert c.get("/api/runs/current", headers={"host": "evil.example"}).status_code == 400  # DNS-rebinding guard
    stale = server.RUNS_DIR / "20200101-000000-aaaaaa"  # a run whose server died: meta.json still says "running"
    stale.mkdir(parents=True)
    (stale / "meta.json").write_text(json.dumps({"id": stale.name, "status": "running", "params": None}))
    assert server.run_status(stale.name)["status"] == "error"
    assert c.post(f"/api/runs/{stale.name}/stop").json()["stopped"] is False
    print("c) OK  path-traversal / unknown ids -> 404")

    # ---- b) happy path: start, 409 on second start, SSE until done
    r = c.post("/api/runs", json=GOOD)
    assert r.status_code == 201, r.text
    run_id = r.json()["id"]
    assert c.post("/api/runs", json=GOOD).status_code == 409
    assert c.get("/api/runs/current").json()["status"] == "running"
    print(f"c) OK  second start while running -> 409 (run {run_id})")
    with c.stream("GET", f"/api/runs/{run_id}/events") as resp:
        assert resp.headers["content-type"].startswith("text/event-stream")
        events = parse_sse(resp.iter_lines())
    kinds = [k for k, _ in events]
    assert kinds[0] == "run" and kinds[-1] == "done", kinds[:3] + kinds[-3:]
    assert events[-1][1]["exit_code"] == 0
    rounds = [e for k, e in events if k == "round"]
    assert [e["round"] for e in rounds] == [0, 1, 2, 3], [e["round"] for e in rounds]
    assert kinds.count("baseline") == 1 and kinds.count("inspect_ready") == 1
    stages = [e for k, e in events if k == "stage"]
    names = ["setup", "share_keys", "collect_masked_vectors", "unmask"]
    for n in names:
        assert sum(1 for s in stages if s["stage"] == n) == 4 * 3, (n, [s["stage"] for s in stages])  # 4 hospitals x 3 rounds
    assert all(s["plaintext_arrays_out"] == 0 for s in stages)  # nothing plain leaves a client (the global model coming IN is plain by design)
    assert all(s["bytes_out"] > 0 for s in stages if s["stage"] == "collect_masked_vectors")
    assert set(rounds[1]) >= {"acc", "f1", "per_hospital_acc", "epsilon", "max_abs_weight", "t", "total_rounds"}
    print(f"b) OK  SSE: {len(rounds)} round events, {len(stages)} stage events (4 stages x 4 hospitals x 3 rounds), done exit 0")
    # a stream opened after the run finished replays everything and ends with done
    with c.stream("GET", f"/api/runs/{run_id}/events") as resp:
        again = parse_sse(resp.iter_lines())
    assert [k for k, _ in again][-1] == "done" and len(again) == len(events)
    assert c.get("/api/runs/current").json()["status"] == "done"
    assert c.post("/api/runs/" + run_id + "/stop").json()["stopped"] is False  # nothing to stop

    # ---- hook equivalence, SECAGG=1: result of the API run (hooks on) vs hooks off
    on1 = parse_result((tmp / "runs" / run_id / "stdout.log").read_text(encoding="utf-8", errors="replace"))
    assert off1["epsilon_per_hospital"] == on1["epsilon_per_hospital"]
    d_acc, d_f1 = abs(off1["fed_acc"] - on1["fed_acc"]), abs(off1["fed_f1"] - on1["fed_f1"])
    assert d_acc <= 0.02 and d_f1 <= 0.02, (d_acc, d_f1)
    print(f"a) OK  SECAGG=1, hooks on vs off: epsilon identical, acc diff {d_acc:.4f}, F1 diff {d_f1:.4f} (limit 0.02; unseeded rounding)")

    # ---- d) inspector checks on the captured data
    ins = c.get(f"/api/inspect/{run_id}").json()
    assert ins["ready"] is True
    info = ins["info"]
    idir = tmp / "runs" / run_id / "insp"
    plain = np.load(idir / "plain.npy")
    masked = np.load(idir / "masked.npy")
    agg = np.load(idir / "aggregate.npy")
    meta = json.loads((idir / "plain_meta.json").read_text())
    import step3_heart_dp as s3  # noqa: E402

    n_params = sum(p.numel() for p in s3.Net().parameters())
    assert plain.size == n_params == meta["param_count"] == agg.size == 273, (plain.size, n_params, agg.size)
    # SecAgg+ prepends one slot (the example-count weight) to the parameter arrays, so the wire vector is n_params + 1 long
    assert masked.size == info["masked_len"] == n_params + 1, (masked.size, n_params)
    assert info["plaintext_arrays_out"] == 0 and info["hospital"] == 0 and info["round"] == 1
    body = masked[1:].astype(np.int64)
    # quantized plain update, as flwr computes it (secaggplus_mod._collect_masked_vectors), reduced mod 2**32 like the wire value
    q_ratio = round(meta["num_examples"] / info["max_weight"] * info["quant_range"])
    dq = q_ratio / info["quant_range"]
    pre = (np.clip(plain.astype(np.float64) * dq, -info["clipping_range"], info["clipping_range"]) + info["clipping_range"]) \
        * info["quant_range"] / (2 * info["clipping_range"])
    qplain = (np.round(pre).astype(np.int64) * q_ratio) % info["mod_range"]
    same = float((qplain == body).mean())
    assert same < 0.02, f"masked vector equals the quantized plain update in {same:.1%} of entries"
    # roughly uniform over [0, 2**32): chi-square, 16 equal bins, df = 15; 37.70 is the p = 0.001 critical value
    counts, _ = np.histogram(body, bins=16, range=(0, info["mod_range"]))
    exp = body.size / 16
    chi2 = float(((counts - exp) ** 2 / exp).sum())
    assert chi2 < 37.70, f"masked vector not uniform: chi2 {chi2:.1f} >= 37.70 (df 15, p 0.001)"
    assert abs(chi2 - ins["masked"]["chi2_16_bins"]) < 1e-6
    # contrast: the plain update is a narrow bell (most weights within +-1 of 0 although the range is +-8); the wire values span the whole range
    assert (np.abs(plain) < 1).mean() > 0.9 and body.min() < info["mod_range"] * 0.1 and body.max() > info["mod_range"] * 0.9
    assert np.abs(plain).max() < info["clipping_range"] and np.abs(agg).max() < info["clipping_range"]
    print(f"d) OK  masked len {masked.size} == {n_params} params + 1 weight slot; equal to quantized plain in {same:.1%} of entries; "
          f"chi2(16 bins) masked {chi2:.1f} < 37.70 ; plaintext arrays out = {info['plaintext_arrays_out']}")
    # contrast: with SecAgg off the same inspector sees the plain arrays leave the client
    info0 = json.loads((tmp / "insp0" / "inspect.json").read_text())
    assert info0["plaintext_arrays_out"] == 4 and "masked_len" not in info0, info0
    print(f"d) OK  SECAGG=0 contrast: plaintext arrays out = {info0['plaintext_arrays_out']} (so the 0 above is not a broken counter)")

    # ---- replays + sweeps
    reps = c.get("/api/replays").json()
    assert any(x["name"] == run_id and x["kind"] == "run" for x in reps)
    rep = c.get(f"/api/replays/{run_id}").json()
    assert rep["events"] and all("t" in e for e in rep["events"] if e["type"] in ("round", "stage"))
    sw = c.get("/api/sweeps")
    assert sw.status_code in (200, 503), sw.status_code
    print(f"b) OK  /api/replays lists the run ({len(rep['events'])} events); /api/sweeps -> {sw.status_code}")

    # ---- e) stop: no child process of the run remains
    def descendants(pid):
        try:
            import psutil
            return [p.pid for p in psutil.Process(pid).children(recursive=True)]
        except ImportError:
            pass
        if sys.platform == "win32":
            out = subprocess.run(["powershell", "-NoProfile", "-Command",
                                  "Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId | ConvertTo-Json"],
                                 capture_output=True, text=True).stdout
            rows = json.loads(out)
            pairs = [(r["ProcessId"], r["ParentProcessId"]) for r in rows]
        else:
            out = subprocess.run(["ps", "-eo", "pid=,ppid="], capture_output=True, text=True).stdout
            pairs = [tuple(map(int, l.split())) for l in out.splitlines() if l.strip()]
        found, todo = [], [pid]
        while todo:
            cur = todo.pop()
            kids = [p for p, pp in pairs if pp == cur and p not in found]
            found += kids
            todo += kids
        return found

    def alive(pid):
        if sys.platform == "win32":
            out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout
            return str(pid) in out.split()
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    r = c.post("/api/runs", json={**GOOD, "rounds": 30})
    assert r.status_code == 201, r.text
    stop_id = r.json()["id"]
    ev_file = tmp / "runs" / stop_id / "events.jsonl"
    t0 = time.time()
    while time.time() - t0 < 300:  # wait until Ray is up and round 0 was evaluated, i.e. the worker processes exist
        if ev_file.is_file() and '"round": 0' in ev_file.read_text(encoding="utf-8"):
            break
        time.sleep(1)
    else:
        raise AssertionError("run never reached round 0")
    time.sleep(3)
    proc_pid = server.manager.current.proc.pid
    kids = descendants(proc_pid)
    assert len(kids) >= 2, f"expected the run to have child processes (Ray), found {kids}"
    st = c.post(f"/api/runs/{stop_id}/stop").json()
    assert st["stopped"] is True and st["status"] == "stopped", st
    time.sleep(2)
    left = [p for p in kids + [proc_pid] if alive(p)]
    assert not left, f"processes still alive after stop: {left}"
    with c.stream("GET", f"/api/runs/{stop_id}/events") as resp:
        ev2 = parse_sse(resp.iter_lines())
    assert ev2[-1][0] == "stopped", ev2[-1]
    print(f"e) OK  stop: {len(kids)} descendant processes of the run, none alive after stop; SSE ends with 'stopped'")
    r = c.post("/api/runs", json={**GOOD, "rounds": 1})  # the lock was released: a new run can start
    assert r.status_code == 201
    assert c.post(f"/api/runs/{r.json()['id']}/stop").json()["stopped"] is True
    print("e) OK  a new run can start after a stop")

print("\nALL OK")
