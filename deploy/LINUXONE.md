# Running the federation on IBM LinuxONE (s390x): runbook

Written from the rehearsal of 2026-10-10 (laptop, Docker Desktop, QEMU emulation of s390x). Everything marked **measured** was run;
everything marked **estimate** or **not verified** was not. The real LinuxONE VM is not available before 16 Oct.

## What runs where
One SuperLink container, four SuperNode containers (one per hospital, each mounts only its own data file) and the dashboard, all from
ONE image (`deploy/Dockerfile`). Flower deployment mode needs no Ray (Ray has no s390x wheels), so the same code runs on amd64 and s390x.

## 0. Before the event (on the laptop, today)
- The image, the compose file, the mixed-architecture override and this runbook are committed on `feature/step6-deploy`.
- Bring a copy of the repo and `data/heart_disease/` (4 files, not in git). Download URL in `CLAUDE.md`
  (`https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/`: `processed.{cleveland,hungarian,switzerland,va}.data`).

## 1. On the LinuxONE VM
Prerequisites: Docker Engine with the compose plugin (or Podman: see section 4), git, outbound HTTPS to `archive.ubuntu.com`/`ports.ubuntu.com`,
`pypi.org`, `files.pythonhosted.org` and `download.pytorch.org` during the build (the run itself needs no internet).

```bash
uname -m                      # must print s390x
git clone <repo url> && cd IBM-DATATHON && git checkout feature/step6-deploy   # or the merged branch
mkdir -p data/heart_disease && cd data/heart_disease
for h in cleveland hungarian switzerland va; do
  curl -fLO https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.$h.data
done
cd ../..
chmod a+r data/heart_disease/*.data       # the containers run as uid 1000
```

### Build (native, no QEMU)
```bash
time docker compose -f deploy/docker-compose.yml build
```
Expected: the long steps are compiling `grpcio` (C++) and `cryptography` (Rust) because PyPI has no s390x wheels for them.
**Measured under QEMU:** 174 min for the whole image. **Estimate** on native hardware: roughly 10 to 30 min (QEMU is commonly 5 to 15 times
slower than native for compiles; not measured). Start the build as soon as you have the VM. Build once, never `--no-cache`.

### Start and open the dashboard
```bash
docker compose -f deploy/docker-compose.yml up -d
docker compose -f deploy/docker-compose.yml ps          # superlink + 4 supernodes + dashboard Up
```
The dashboard listens on `127.0.0.1:8000` of the VM only (it has no login). From your laptop: `ssh -L 8000:127.0.0.1:8000 <user>@<vm>`, then open
http://127.0.0.1:8000. Set `DASHBOARD_PORT=8001` if 8000 is taken.

### Prove it is s390x and big-endian (for the judges)
```bash
docker compose -f deploy/docker-compose.yml exec superlink uname -m                                    # s390x
docker compose -f deploy/docker-compose.yml exec superlink python -c "import sys,platform;print(platform.machine(), sys.byteorder)"   # s390x big
docker compose -f deploy/docker-compose.yml exec supernode-1 ls /data                                  # only processed.hungarian.data
```
The inspector files written by an s390x container are big-endian: `head -c 100 /runs/<id>/insp/masked.npy` shows `'descr': '>u4'`.

### Smoke run
In the dashboard: Rounds 3, SecAgg on, Start. Or without a browser:
```bash
curl -s -X POST http://127.0.0.1:8000/api/runs -H 'Content-Type: application/json' \
     -d '{"noise":1.0,"strategy":"fedavg","secagg":true,"rounds":3,"seed":0}'
curl -s http://127.0.0.1:8000/api/runs/current
```
Check the run finished with all four hospitals: `docker compose -f deploy/docker-compose.yml logs | grep -E "Traceback|ClientApp raised"` must print nothing.
(SecAgg+ tolerates one dropped hospital by design, so a client that crashes does NOT fail the run: the per-hospital accuracy of that hospital just stays low.)

## 2. What was measured in the rehearsal (QEMU, laptop)
| Item | Result |
|---|---|
| `uname -m` in the container | `s390x` |
| `sys.byteorder`, `struct.pack('=I', 1)` | `big`, `00000001` |
| Image size | 3.6 GB (amd64: 3.17 GB) |
| Build, whole image under QEMU | 174 min 35 s: apt 5 min, torch 2.7 min, grpcio 141 min, cryptography 11.5 min, flwr + opacus 13 min (pycryptodome, httptools, uvloop compiled) |
| Versions on s390x | Python 3.12.3, torch 2.14.1+cpu, flwr 1.37.0, grpcio 1.84.0, cryptography 46.0.7, numpy 1.26.4, scipy 1.11.4, pandas 2.1.4, scikit-learn 1.4.1, opacus 1.6.0 |
| 1 round, all containers s390x (SecAgg on, noise 1.0, seed 0) | completed; about 9 min wall under QEMU (ServerApp baselines + 1 round); accuracy 0.7056, epsilon max 7.58 (matches the accountant: 4.73 for the 227-row hospital), masked vector 274 values, chi-square 17.9 < 37.70 |
| 1 round, MIXED (SuperLink + 3 SuperNodes amd64, hungarian SuperNode s390x) | completed, accuracy 0.7056 and per-hospital accuracy identical to the all-s390x run |

Not verified: speed on real LinuxONE; behaviour of the protobuf C extension on real hardware (see problem 2); more than 1 round on s390x.

## 3. Problems met (symptom, cause, fix) and what to try first on the real VM
1. **Build died after 14 min: `ReadTimeoutError ... files.pythonhosted.org`** while pip fetched build dependencies of `cryptography`.
   Cause: pip's default 15 s read timeout. Fix (in the Dockerfile): `PIP_DEFAULT_TIMEOUT=120 PIP_RETRIES=10`.
2. **`import flwr` segfaults (`google.protobuf.internal.builder`)**. Cause: protobuf 6.33.6 ships a prebuilt C extension (`google/_upb/_message.abi3.so`)
   for s390x, and it crashed under QEMU. Fix in the image: a `.pth` file sets `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` when
   `platform.machine() == "s390x"` (pure Python, correct on any byte order, slower). **Try first on the real VM:** build with the `.pth` removed or run
   `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=upb python -c "import flwr"` in a throw-away container; if it works natively the C extension is faster. Not tested on real hardware.
3. **`ImportError: libopenblas.so.0` on `import torch`**. Cause: the torch s390x wheel links OpenBLAS dynamically. Fix: apt `libopenblas0`.
4. **Python processes that import protobuf exit with `Segmentation fault` under QEMU** (even `import google.protobuf.descriptor_pb2`), after all
   output was written. Effect: the `flwr run --stream` CLI returns exit code -11 (the dashboard still shows the run as done, because it trusts the
   ServerApp's final `done` event); a QEMU container that crashes this way can hang while QEMU writes a core file (`docker kill` it). Long-running
   containers are not affected. Two root-cause attempts (upb off, pure Python on) did not remove it, so it is **unresolved**; it may be a QEMU-user
   artefact. Check on the real VM: `docker compose exec superlink python -c "import flwr"; echo $?` must print 0.
5. **Mixed amd64 + s390x: `ValueError: given numpy array has byte order different from the native byte order`** in the s390x ClientApp.
   Cause: Flower sends arrays with `np.save`, which records the byte order, so a little-endian server's weights reach a big-endian client
   non-native and `torch.tensor` refuses them. SecAgg+ hid it (one dropped hospital is allowed): the run "finished" with 3 hospitals and the
   missing hospital scored 0.42. Fix: `set_parameters` in `step3_heart_dp.py` converts to native byte order (no-op on one architecture); test: `test_step3_dp.py` check 5.
   After the fix the mixed run equals the all-s390x run.
6. **Flower telemetry / update check**: Flower sends usage telemetry and checks for updates by default. The image sets `FLWR_TELEMETRY_ENABLED=0` and
   `FLWR_DISABLE_UPDATE_CHECK=1` (a privacy demo should not phone home, and the VM may be offline).
7. **Port 8000 busy on the laptop**: use `DASHBOARD_PORT=8001`.
8. After Stop, a defunct (zombie) `flwr-serverapp` may remain in the SuperLink container until the next run. Harmless (parent does not reap it).

## 4. Fallback if the Docker build fails or is too slow on the VM
- Build `grpcio` and `cryptography` wheels once, then reuse: in a `python:3.12-slim`/`ubuntu:24.04` s390x container run
  `pip wheel grpcio grpcio-health-checking cryptography -w /wheels` (env of the Dockerfile) and install with `pip install --find-links /wheels`.
- No containers at all: on the VM install the same apt packages as the Dockerfile (python3-venv, python3-numpy, python3-scipy, python3-pandas,
  python3-sklearn, libopenblas0, build-essential, libssl-dev, libffi-dev, zlib1g-dev, libc-ares-dev, rustc, cargo), create the venv with
  `--system-site-packages`, run the three `pip install` lines of the Dockerfile, `export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python`,
  then `python run_step6_local.py rounds=3 secagg=1 noise=1.0` (starts SuperLink + 4 SuperNodes as processes, each with only its own data file).
- Podman: `podman compose` accepts the same file; the shared volume `runs` and the `init: true` flag are supported.

## 5. What to say to the judges (honest version)
- The federated training runs as five separate containers on an IBM LinuxONE (s390x, big-endian) VM; hospital data never leaves its container;
  updates are masked with SecAgg+ and the training is differentially private (Opacus).
- Limits: the SuperLink container also holds all four files because its ServerApp computes the non-private baselines and the pooled test score
  (evaluation only); the `/runs` volume is the demo's inspector channel; gRPC is insecure (no TLS) and the dashboard has no login; SecAgg+ hides one
  update only inside the sum (3 colluding parties out of 4 reveal the fourth); the QEMU rehearsal says nothing about LinuxONE speed.

## 6. Mixed-architecture rehearsal (laptop only)
```bash
docker compose -f deploy/docker-compose.yml build                                        # amd64 image
docker buildx build --platform linux/s390x -f deploy/Dockerfile -t zero-exposure-fl:s390x --load .   # s390x image (needs QEMU: docker run --privileged --rm tonistiigi/binfmt --install s390x)
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.mixed.yml up -d --no-build
```
