"""Step 5 dashboard backend: FastAPI + SSE. Starts step4_heart_secagg.py as a subprocess and streams what it writes.

Start:  .venv\\Scripts\\python.exe -m dashboard.server        (HOST=127.0.0.1 PORT=8000 by default; set HOST=0.0.0.0 in Docker)

Training code is never imported here: the child process gets EVENTS_FILE / INSPECT_DIR (see step4_heart_secagg.py) and this
server tails those files. One run at a time. Stop, crash and server shutdown kill the child's whole process tree (Ray workers too).
"""
import asyncio
import importlib
import json
import os
import re
import secrets
import signal
import subprocess
import sys
import threading
import time
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parent.parent
DASH = Path(__file__).resolve().parent
RUNS_DIR = DASH / "runs"
REPLAYS_DIR = DASH / "replays"
STATIC_DIR = DASH / "static"
TRAIN_SCRIPT = ROOT / "step4_heart_secagg.py"
INSPECT_ROUND = 1
RUN_ID_RE = re.compile(r"\d{8}-\d{6}-[0-9a-f]{6}")  # ids are generated here; anything else is rejected before touching the disk
NAME_RE = re.compile(r"[A-Za-z0-9_-]{1,64}")  # always used with fullmatch ($ would accept a trailing newline)


# ---------------------------------------------------------------- request model
class Strategy(str, Enum):
    fedavg = "fedavg"
    fedprox = "fedprox"


class RunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    noise: float = Field(ge=0, le=5, strict=True)
    strategy: Strategy
    secagg: bool = Field(strict=True)
    rounds: int = Field(default=15, ge=1, le=30, strict=True)
    seed: int = Field(default=0, ge=0, le=99, strict=True)


# ---------------------------------------------------------------- process-tree kill
def kill_tree(proc):
    """Kill proc and all its descendants (Ray raylet/workers included)."""
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True, timeout=30)
        else:
            os.killpg(proc.pid, signal.SIGKILL)  # start_new_session=True made the child its own group leader: pgid == pid
    except (ProcessLookupError, PermissionError, subprocess.TimeoutExpired):
        pass
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        pass


# ---------------------------------------------------------------- run manager
class Run:
    def __init__(self, params):
        self.id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(3)
        self.params = params
        self.dir = RUNS_DIR / self.id
        self.status = "running"  # running | done | error | stopped
        self.exit_code = None
        self.stop_requested = False
        self.started = time.time()
        self.finished = None
        self.proc = None

    def meta(self):
        return {"id": self.id, "params": self.params, "status": self.status, "exit_code": self.exit_code,
                "started": self.started, "finished": self.finished}


class RunManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.current = None

    def start(self, params):
        with self.lock:
            if self.current is not None and self.current.status == "running":
                raise RuntimeError("a run is already active")
            run = Run(params)
            run.dir.mkdir(parents=True, exist_ok=False)
            (run.dir / "insp").mkdir()
            env = {
                **os.environ,
                "SECAGG": "1" if params["secagg"] else "0", "STRATEGY": params["strategy"], "MU": "0.1",
                "NOISE": repr(float(params["noise"])), "NUM_ROUNDS": str(params["rounds"]), "SEED": str(params["seed"]),
                "EVENTS_FILE": str(run.dir / "events.jsonl"), "INSPECT_DIR": str(run.dir / "insp"),
                "INSPECT_ROUND": str(INSPECT_ROUND), "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1",
            }
            kw = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if sys.platform == "win32" else {"start_new_session": True}
            out = open(run.dir / "stdout.log", "wb")
            err = open(run.dir / "stderr.log", "wb")
            try:
                run.proc = subprocess.Popen([sys.executable, str(TRAIN_SCRIPT)], cwd=str(ROOT), env=env,
                                            stdin=subprocess.DEVNULL, stdout=out, stderr=err, **kw)
            finally:
                out.close()
                err.close()
            self.current = run
            threading.Thread(target=self._watch, args=(run,), daemon=True).start()
            self._write_meta(run)
            return run

    def _watch(self, run):
        code = run.proc.wait()
        with self.lock:
            run.exit_code = code
            run.finished = time.time()
            run.status = "stopped" if run.stop_requested and code != 0 else ("done" if code == 0 else "error")
            self._write_meta(run)
        if sys.platform != "win32":
            kill_tree(run.proc)  # POSIX: the group may still hold Ray daemons. Windows: taskkill /T needs a live parent, so it cannot help here

    @staticmethod
    def _write_meta(run):
        (run.dir / "meta.json").write_text(json.dumps(run.meta()), encoding="utf-8")

    def stop(self, run_id):
        with self.lock:
            run = self.current
            if run is None or run.id != run_id or run.status != "running":
                return False
            run.stop_requested = True
        kill_tree(run.proc)
        for _ in range(50):  # the watcher thread records the final status; wait for it so callers see "stopped"
            if run.status != "running":
                break
            time.sleep(0.1)
        return True

    def shutdown(self):
        run = self.current
        if run is not None and run.status == "running":
            run.stop_requested = True
            kill_tree(run.proc)
            with self.lock:
                if run.status == "running":  # the watcher thread may not have run yet
                    run.status, run.exit_code, run.finished = "stopped", run.proc.poll(), time.time()
                    self._write_meta(run)


manager = RunManager()


def run_status(run_id):
    """Status dict of a run: from memory if it is the current one, else from meta.json on disk."""
    cur = manager.current
    if cur is not None and cur.id == run_id:
        return cur.meta()
    f = RUNS_DIR / run_id / "meta.json"
    if f.is_file():
        m = json.loads(f.read_text(encoding="utf-8"))
        if m.get("status") == "running":  # not the current run: the server that owned it died
            m.update(status="error", note="interrupted")
        return m
    if (RUNS_DIR / run_id).is_dir():  # server died mid-run
        return {"id": run_id, "status": "error", "exit_code": None, "params": None, "note": "interrupted"}
    return None


def check_run_id(run_id):
    if not RUN_ID_RE.fullmatch(run_id):
        raise HTTPException(404, "unknown run")
    st = run_status(run_id)
    if st is None:
        raise HTTPException(404, "unknown run")
    return st


# ---------------------------------------------------------------- file helpers
def read_new_lines(path, offset):
    """Complete JSON lines appended after `offset`. A half-written last line is left for the next call. Missing file = nothing yet."""
    try:
        with open(path, "rb") as f:
            f.seek(offset)
            data = f.read()
    except FileNotFoundError:
        return [], offset
    end = data.rfind(b"\n")
    if end < 0:
        return [], offset
    out = []
    for line in data[:end].split(b"\n"):
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out, offset + end + 1


def read_jsonl(path):
    return read_new_lines(path, 0)[0]


def stage_files(insp_dir):
    """Per-hospital stage logs written by the inspector (one writer per file, so no lost lines)."""
    return sorted(Path(insp_dir).glob("stages_h*.jsonl"))


def stderr_tail(run_dir, n=25, max_chars=3000):
    try:
        text = (run_dir / "stderr.log").read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""
    return "\n".join(text.splitlines()[-n:])[-max_chars:]


def merged_events(run_dir, meta=None):
    """All events of a finished run in time order: baseline + rounds + stages (+ final status). This is what a replay plays back."""
    ev = read_jsonl(run_dir / "events.jsonl")
    for f in stage_files(run_dir / "insp"):
        ev += read_jsonl(f)
    ev.sort(key=lambda e: e.get("t", 0))
    return ev


def sse(event, obj):
    return f"event: {event}\ndata: {json.dumps(obj)}\n\n"


def hist(values, lo, hi, bins):
    counts, edges = np.histogram(values, bins=bins, range=(lo, hi))
    return {"edges": [float(e) for e in edges], "counts": [int(c) for c in counts]}


def inspect_payload(insp_dir):
    """The 'what the server sees' data of one run: plain update, received masked vector, aggregate, with histograms."""
    info_f = insp_dir / "inspect.json"
    if not info_f.is_file():
        return {"ready": False}
    info = json.loads(info_f.read_text(encoding="utf-8"))
    res = {"ready": True, "info": info}
    plain = np.load(insp_dir / "plain.npy") if (insp_dir / "plain.npy").is_file() else None
    masked = np.load(insp_dir / "masked.npy") if (insp_dir / "masked.npy").is_file() else None
    agg = np.load(insp_dir / "aggregate.npy") if (insp_dir / "aggregate.npy").is_file() else None
    if plain is not None:
        lim = float(max(np.abs(plain).max(), 1e-9))
        res["plain"] = {"values": plain.tolist(), "hist": hist(plain, -lim, lim, 24), "count": int(plain.size)}
    if masked is not None:
        body = masked[1:]  # masked[0] is the example-count slot that SecAgg+ prepends; the rest are the model parameters
        mod = info["mod_range"]
        counts, _ = np.histogram(body, bins=16, range=(0, mod))
        expected = body.size / 16
        res["masked"] = {"values": masked.astype(np.int64).tolist(), "hist": hist(body, 0, mod, 24), "count": int(masked.size),
                         "chi2_16_bins": float(((counts - expected) ** 2 / expected).sum()), "chi2_df": 15,
                         "chi2_p001_threshold": 37.70}
    if agg is not None:
        lim = float(max(np.abs(agg).max(), 1e-9))
        res["aggregate"] = {"values": agg.tolist(), "hist": hist(agg, -lim, lim, 24), "count": int(agg.size)}
    stages = [e for f in stage_files(insp_dir) for e in read_jsonl(f)
              if e.get("hospital") == info["hospital"] and e.get("round") == info["round"]]
    res["stages"] = stages
    return res


def inspect_dir_for(name):
    """Resolve a run id or replay name to its inspect folder. Only ids/names matching strict patterns reach the filesystem."""
    if RUN_ID_RE.fullmatch(name):
        d = RUNS_DIR / name / "insp"
    elif NAME_RE.fullmatch(name):
        d = REPLAYS_DIR / name
    else:
        raise HTTPException(404, "unknown run or replay")
    if not d.is_dir():
        raise HTTPException(404, "unknown run or replay")
    return d


def export_replay(run_id, name):
    """Freeze a finished run into dashboard/replays/<name>.jsonl (+ <name>/ with its inspect files)."""
    import shutil
    if not NAME_RE.fullmatch(name) or not RUN_ID_RE.fullmatch(run_id):
        raise ValueError("bad name or id")
    src = RUNS_DIR / run_id
    meta = json.loads((src / "meta.json").read_text(encoding="utf-8"))
    REPLAYS_DIR.mkdir(exist_ok=True)
    lines = [{"type": "meta", "params": meta["params"], "source_run": run_id, "status": meta["status"], "t": meta["started"]}]
    lines += merged_events(src)
    lines.append({"type": "done" if meta["status"] == "done" else meta["status"], "exit_code": meta["exit_code"], "t": meta["finished"]})
    (REPLAYS_DIR / f"{name}.jsonl").write_text("\n".join(json.dumps(l) for l in lines) + "\n", encoding="utf-8")
    dst = REPLAYS_DIR / name
    dst.mkdir(exist_ok=True)
    for f in (src / "insp").iterdir():
        if f.suffix in (".json", ".npy", ".jsonl"):
            shutil.copy2(f, dst / f.name)


# ---------------------------------------------------------------- app
@asynccontextmanager
async def lifespan(_app):
    RUNS_DIR.mkdir(exist_ok=True)
    yield
    manager.shutdown()


app = FastAPI(title="Federated privacy dashboard", lifespan=lifespan)
# No authentication: anyone who can reach the port can start/stop runs. Default = loopback only, and the Host header is checked
# (DNS rebinding). For Docker/LinuxONE set HOST=0.0.0.0 and ALLOWED_HOSTS to the names you serve (default "*" in that case).
_loopback = os.environ.get("HOST", "127.0.0.1") in ("127.0.0.1", "localhost", "::1")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=os.environ.get(
    "ALLOWED_HOSTS", "localhost,127.0.0.1,[::1],testserver" if _loopback else "*").split(","))


@app.exception_handler(RequestValidationError)
async def validation_error(_req, exc):
    """422 without echoing the offending input: NaN/inf in the input would make the default handler's JSON encoding fail (500)."""
    return JSONResponse({"detail": [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]}, status_code=422)


@app.post("/api/runs", status_code=201)
def start_run(req: RunRequest):
    try:
        run = manager.start({"noise": req.noise, "strategy": req.strategy.value, "secagg": req.secagg,
                             "rounds": req.rounds, "seed": req.seed})
    except RuntimeError:
        raise HTTPException(409, "a run is already active; stop it first")
    return run.meta()


@app.get("/api/runs/current")
def current_run():
    cur = manager.current
    return cur.meta() if cur is not None else {"status": "idle"}


@app.post("/api/runs/{run_id}/stop")
def stop_run(run_id: str):
    st = check_run_id(run_id)
    stopped = manager.stop(run_id)
    return {"id": run_id, "stopped": stopped, "was": st["status"], "status": run_status(run_id)["status"]}


@app.get("/api/runs/{run_id}/events")
async def run_events(run_id: str, request: Request):
    check_run_id(run_id)
    d = RUNS_DIR / run_id

    async def gen():
        offsets = {"events.jsonl": 0}
        inspect_sent = False
        last_ping = time.monotonic()
        yield sse("run", run_status(run_id))
        while True:
            st = run_status(run_id)
            finished = st["status"] != "running"  # decided BEFORE the drain, so everything written before the end is still sent
            for f in stage_files(d / "insp"):
                offsets.setdefault(f"insp/{f.name}", 0)
            for rel in list(offsets):
                lines, offsets[rel] = read_new_lines(d / rel, offsets[rel])
                for obj in lines:
                    yield sse(obj.get("type", "message"), obj)
            if not inspect_sent and (d / "insp" / "inspect.json").is_file() and (d / "insp" / "aggregate.npy").is_file():
                inspect_sent = True
                yield sse("inspect_ready", {"type": "inspect_ready", "id": run_id})
            if finished:
                if st["status"] == "error":
                    yield sse("run_error", {"type": "run_error", "exit_code": st.get("exit_code"), "stderr_tail": stderr_tail(d)})
                elif st["status"] == "stopped":
                    yield sse("stopped", {"type": "stopped", "exit_code": st.get("exit_code")})
                else:
                    yield sse("done", {"type": "done", "exit_code": st.get("exit_code")})
                return
            if await request.is_disconnected():
                return
            if time.monotonic() - last_ping > 15:
                last_ping = time.monotonic()
                yield ": ping\n\n"
            await asyncio.sleep(0.25)

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/api/replays")
def list_replays():
    items = []
    if REPLAYS_DIR.is_dir():
        for f in sorted(REPLAYS_DIR.glob("*.jsonl")):
            if NAME_RE.fullmatch(f.stem):
                items.append({"name": f.stem, "kind": "replay", "has_inspect": (REPLAYS_DIR / f.stem).is_dir()})
    if RUNS_DIR.is_dir():
        for d in sorted(RUNS_DIR.iterdir(), reverse=True):
            if RUN_ID_RE.fullmatch(d.name) and (d / "meta.json").is_file():
                m = json.loads((d / "meta.json").read_text(encoding="utf-8"))
                if m.get("status") == "done":
                    items.append({"name": d.name, "kind": "run", "params": m.get("params"), "has_inspect": (d / "insp" / "inspect.json").is_file()})
    return items


@app.get("/api/replays/{name}")
def get_replay(name: str):
    if RUN_ID_RE.fullmatch(name):
        d = RUNS_DIR / name
        if not (d / "meta.json").is_file():
            raise HTTPException(404, "unknown replay")
        return {"name": name, "events": merged_events(d)}
    if not NAME_RE.fullmatch(name) or not (REPLAYS_DIR / f"{name}.jsonl").is_file():
        raise HTTPException(404, "unknown replay")
    return {"name": name, "events": read_jsonl(REPLAYS_DIR / f"{name}.jsonl")}


@app.get("/api/inspect/{name}")
def get_inspect(name: str):
    return inspect_payload(inspect_dir_for(name))


@app.get("/api/sweeps")
def get_sweeps():
    try:
        mod = importlib.import_module("dashboard.sweeps")
    except ModuleNotFoundError as e:
        if e.name != "dashboard.sweeps":
            raise
        return JSONResponse({"detail": "dashboard/sweeps.py is not available yet"}, status_code=503)
    return mod.to_json(ROOT / "results")


# static UI last, so /api/* wins. check_dir=False: the folder may be created after import in odd setups.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True, check_dir=False), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", 8000)),
                timeout_graceful_shutdown=3)  # open SSE streams would otherwise block shutdown (and the child kill) forever
