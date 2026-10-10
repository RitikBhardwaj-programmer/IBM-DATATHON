"""Step 6 native launcher (Windows or Linux, no Docker): 1 SuperLink + 4 SuperNodes as separate processes, then `flwr run`.

Each SuperNode gets its OWN data folder holding only its hospital's file (DATA_DIR + ALLOW_MISSING_DATA=1): the same isolation
that docker-compose.yml gives with bind mounts. The SuperLink (and so the ServerApp it spawns) sees the whole data folder,
because the demo's ServerApp computes the non-private baselines and the pooled test score (see step6_heart_deploy.py).

Use:   .venv\\Scripts\\python.exe run_step6_local.py noise=1.0 strategy=fedprox secagg=1 rounds=3 seed=0
Keys are the run_config keys of pyproject.toml; unset keys keep the defaults there. Prints the ServerApp's `RESULT {json}` line.
Everything is killed at the end (also on Ctrl+C or a crash): SuperLink, SuperExec, ServerApp, SuperNodes, ClientApps.
"""
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOSPITALS = ["cleveland", "hungarian", "switzerland", "va"]
CONTROL_PORT = 9093  # SuperLink Runtime + Control HTTP API (flwr run talks to it). 8000 is the default but the dashboard uses it.
FLEET_PORT = 9092  # SuperLink Fleet API (SuperNodes connect here)
NODE_PORT0 = 9094  # SuperNode i serves its Runtime API on NODE_PORT0 + i
BIN = Path(sys.executable).parent  # venv Scripts/bin: flower-superlink spawns `flower-superexec` by name, so it must be on PATH


def exe(name):
    """Full path of a venv console script (Windows Popen looks the name up on the PARENT's PATH, not on env=)."""
    return str(BIN / (name + (".exe" if sys.platform == "win32" else "")))


def kill_tree(proc):
    """Kill proc and its descendants (pattern of dashboard/server.py). POSIX: the group, because we start every child in a new session."""
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True, timeout=30)
        else:
            os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, subprocess.TimeoutExpired):
        pass
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        pass


def toml_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return repr(v)  # keeps the decimal point: the override must have the default's type (float)
    if isinstance(v, int):
        return str(v)
    return json.dumps(str(v))  # a JSON string is also a valid TOML basic string


def run_config_arg(cfg):
    return " ".join(f"{k}={toml_value(v)}" for k, v in cfg.items())


def port_open(port):
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


class LocalDeployment:
    """Context manager: starts the SuperLink and 4 SuperNodes; `run(cfg)` submits one run and waits for it."""

    def __init__(self, workdir=None, data_dir=None):
        self.work = Path(workdir) if workdir else Path(tempfile.mkdtemp(prefix="step6-"))
        self.data_dir = Path(data_dir) if data_dir else ROOT / "data" / "heart_disease"
        self.procs = []
        self.logs = self.work / "logs"

    def _env(self, **extra):
        env = {**os.environ, "PATH": str(BIN) + os.pathsep + os.environ.get("PATH", ""), "FLWR_HOME": str(self.work / "flwr_home"),
               "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
        env.update(extra)
        return env

    def _spawn(self, name, cmd, env):
        kw = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if sys.platform == "win32" else {"start_new_session": True}
        out = open(self.logs / f"{name}.log", "wb")
        try:  # cwd = work dir, NOT the repo: the apps must be imported from the shipped FAB, never from the repo checkout
            p = subprocess.Popen(cmd, cwd=str(self.work), env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT, **kw)
        finally:
            out.close()
        self.procs.append(p)
        return p

    def __enter__(self):
        try:
            self.logs.mkdir(parents=True, exist_ok=True)
            busy = [p for p in [CONTROL_PORT, FLEET_PORT] + [NODE_PORT0 + i for i in range(4)] if port_open(p)]
            if busy:
                raise RuntimeError(f"ports already in use: {busy} (is another deployment running?)")
            (self.work / "flwr_home").mkdir(exist_ok=True)  # own Flower config: the user's ~/.flwr is never touched
            (self.work / "flwr_home" / "config.toml").write_text(
                f'[superlink]\ndefault = "step6"\n\n[superlink.step6]\naddress = "127.0.0.1:{CONTROL_PORT}"\ninsecure = true\n', encoding="utf-8")
            self._spawn("superlink", [exe("flower-superlink"), "--insecure", "--disable-runtime-dependency-installation",
                                      "--host", "127.0.0.1", "--port", str(CONTROL_PORT), "--fleet-api-address", f"127.0.0.1:{FLEET_PORT}"],
                        self._env(DATA_DIR=str(self.data_dir)))
            for i, name in enumerate(HOSPITALS):
                d = self.work / f"data_{name}"  # this SuperNode's whole world: one file
                d.mkdir(exist_ok=True)
                shutil.copy2(self.data_dir / f"processed.{name}.data", d / f"processed.{name}.data")
                self._spawn(f"supernode-{i}", [exe("flower-supernode"), "--insecure", "--superlink", f"127.0.0.1:{FLEET_PORT}",
                                               "--node-config", f"partition-id={i} num-partitions={len(HOSPITALS)}",
                                               "--port", str(NODE_PORT0 + i)],
                            self._env(DATA_DIR=str(d), ALLOW_MISSING_DATA="1"))
            self._wait_ready()
            return self
        except BaseException:
            self.close()
            raise

    def _wait_ready(self, timeout=90):
        """SuperLink answers on the control port and all 4 SuperNodes are connected (they log it)."""
        t0 = time.time()
        while time.time() - t0 < timeout:
            for p in self.procs:
                if p.poll() is not None:
                    raise RuntimeError(f"a process exited early (code {p.returncode}); see {self.logs}")
            if port_open(CONTROL_PORT) and all(port_open(NODE_PORT0 + i) for i in range(4)):
                time.sleep(3)  # let the SuperNodes finish registering with the SuperLink
                return
            time.sleep(0.5)
        raise RuntimeError(f"deployment not ready after {timeout}s; see {self.logs}")

    def run(self, cfg, timeout=900):
        """Submit one run (`flwr run --stream`) and return its combined log text. Raises on non-zero exit or timeout."""
        cmd = [exe("flwr"), "run", str(ROOT), "step6", "--stream",
               "--run-config", run_config_arg(cfg)]
        res = subprocess.run(cmd, cwd=str(self.work), env=self._env(), capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=timeout)
        text = res.stdout + "\n" + res.stderr
        (self.logs / "flwr_run.log").write_text(text, encoding="utf-8")
        if res.returncode != 0:
            raise RuntimeError(f"flwr run failed (exit {res.returncode}):\n{text[-3000:]}")
        return text

    def close(self):
        for p in reversed(self.procs):
            kill_tree(p)
        self.procs = []

    def __exit__(self, *exc):
        self.close()


def parse_result(text):
    for line in reversed(text.splitlines()):
        if "RESULT {" in line:
            return json.loads(line[line.index("RESULT ") + 7:])
    return None


def main(argv):
    cfg = {}
    for a in argv:
        k, _, v = a.partition("=")
        try:
            cfg[k] = json.loads(v)  # numbers / true / false; keep a decimal point yourself for floats (noise=1.0)
        except ValueError:
            cfg[k] = v
    with LocalDeployment() as dep:
        print(f"work dir {dep.work} (logs in {dep.logs})")
        text = dep.run(cfg)
    print(text)
    res = parse_result(text)
    print("RESULT " + json.dumps(res) if res else "no RESULT line found")
    return 0 if res else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
