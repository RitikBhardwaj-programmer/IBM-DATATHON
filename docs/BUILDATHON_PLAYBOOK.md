# Zero Exposure: buildathon playbook (IBM Z Datathon 2026)

Everything we learned while building steps 1 to 6, written for the event window **17 Oct 10:00 to 18 Oct 23:59 IST** (about 38 h; called a 24-hour datathon).
One person builds; Claude sessions are the team. Labels on facts: **measured** (we ran it), **sourced** (a page or file says so),
**estimate** (own arithmetic, assumptions stated), **unverified** (not run yet). Sources are repo files unless marked *vault*
(`C:\Users\DELL\Brain\Memory\IBM DATATHON\`).

---

## 0. Read this first

| What | When (IST) | Status on 2026-10-11 |
|---|---|---|
| Registration closes (all members registered, leader files the team form, 4-6 members) | 15 Oct, 23:59 | Leader registered; teammates not yet |
| Abstract (problem + approach) on Hack2Skill | FAQ says 5 Oct, timeline says "To Be Announced" | **Not submitted.** Draft is in the chat of 2026-10-10 |
| "Get Your LinuxONE System Ready" session, **mandatory for every participant** | 16 Oct, 19:15-20:30 | - |
| Event (code must be built in this window) | 17 Oct 10:00 to 18 Oct 23:59 | - |
| Submission: working demo, repo link, short description, pitch deck | before 18 Oct 23:59 | - |

Source: *vault* `datathon-2026-rules` (read from hack2skill.com/event/datathon-2026 on 2026-10-10).

**Rule risk, stated once:** the FAQ says the solution must be built during 17-18 Oct and forbids "continuation hacks" and re-using
prior personal projects as the core. Steps 1-6 were built before the event. You chose to keep this repo and check the rule yourself;
ask the organisers on Discord or stemprograms@sstarsfoundation.org if unsure.

**The five things that matter most**
1. Get the LinuxONE VM on 16 Oct and start the Docker build **at once**. Under QEMU it took 174 min (measured); native speed is unverified.
2. A working demo beats an ambitious unfinished one (sourced: playbook artifact). Freeze features at 18 Oct 18:00.
3. Show it **running on s390x** on screen: `uname -m`, `sys.byteorder = big`, the per-hospital data mounts.
4. Say the limits before the judges find them (section 6.4). Honesty is part of the privacy story.
5. Keep the golden replay ready: the dashboard works with no training at all.

---

## 1. Solo 24-hour plan, with Claude as the team

You are the only builder. Claude sessions do the parallel work; you decide, check and present.
The plan assumes the code from steps 1-6 is the base and the event time goes to LinuxONE, hardening and the pitch.

### 1.1 Timeline

| When (IST) | You | Claude | Checkpoint (go / fallback) |
|---|---|---|---|
| **16 Oct 19:15-20:30** | Attend the mandatory session; get VM credentials | - | Can you SSH in? |
| 16 Oct 20:30 | Run the pre-checks in section 5.1; start the build | Main session watches the build log | `uname -m` = s390x. Build starts. If no Docker: native fallback (5.4) |
| 16 Oct night | **Sleep.** The build runs alone | - | - |
| **17 Oct 08:45** | Global kick-off (sourced: Hack2Skill timeline) | - | - |
| 17 Oct 10:00-12:00 | Build finished? `compose up`, smoke run, proof commands (5.2, 5.3) | Main session (Opus): read logs with you | All 4 hospitals in the logs, no `ClientApp raised`. Else fix or use the laptop amd64 compose |
| 17 Oct 12:00-13:00 | Pick at most **two** improvements (1.2); approve their plans | Opus plans them (plan mode, routing card) | Plans written and approved |
| 17 Oct 13:00-20:00 | Review, answer questions, test | Two Sonnet build sessions in parallel, **one writer per set of files** | Each stage has a test that passes |
| 17 Oct 20:00-22:00 | Run the full demo on LinuxONE; record screen as backup | Review subagent + Codex read-only review | Fix Blocker/High findings only |
| 17 Oct 22:00-06:00 | **Sleep** (6 h minimum) | Nothing runs unattended that writes code | - |
| 18 Oct 07:00-12:00 | Pitch deck (6.2) and demo script (6.3) | Claude drafts slides and speaker notes from this file | Deck complete |
| 18 Oct 12:00-18:00 | Rehearse the 5-min demo twice; record the video | Opus visual QA of the dashboard | Rehearsal under 5 min |
| **18 Oct 18:00** | **Feature freeze.** Only bug fixes after this | - | Tag the repo (`git tag event-final`) |
| 18 Oct 18:00-21:00 | Submit early: demo link/video, repo, description, deck | Claude checks the submission list (6.5) | Submitted **before 21:00**; 3 h buffer |
| 18 Oct 23:59 | Deadline | - | - |

### 1.2 Improvement options for the event (pick at most two)

Each one closes a stated limit (section 6.4). Effort figures are **estimates**.

| Option | Closes this limit | Effort (estimate) | Risk |
|---|---|---|---|
| **DONE 17 Oct:** TLS on gRPC (`deploy/gen_certs.py`, `certs` compose service; CLAUDE.md "Step 6 TLS") | "gRPC is insecure" | 2-3 h | Certificate paths in 5 containers |
| Federated evaluation (each hospital scores its own test rows) so the SuperLink holds no hospital files | "SuperLink holds all four files" | 3-4 h | Pooled F1 is not a weighted mean of per-hospital F1: the headline metric changes |
| Dashboard login (basic auth) and a public demo URL | "No login, loopback only" | 1-2 h | Exposing the VM: keep it short-lived |
| One slide + design note: IBM Secure Execution for the SuperLink | Z-specific hardening | 1 h (no code) | Only claim what you ran |

Do not start a third option. A finished demo with one improvement beats two half-done ones.

---

## 2. Architecture we proved

```
  hospital containers (SuperNodes)             server container (SuperLink)            browser
 +-------------------------------+         +-------------------------------+     +---------------+
 | cleveland  /data: own file    |--+      | ServerApp:                    |     | dashboard     |
 | hungarian  /data: own file    |--+----->|  baselines (eval only)        |---->| FastAPI + SSE |
 | switzerland /data: own file   |--+ gRPC |  SecAgg+ -> sum only          |     | 127.0.0.1:8000|
 | va          /data: own file   |--+      |  FedAvg / FedProx             |     +---------------+
 +-------------------------------+         +-------------------------------+
   each: local training with DP-SGD             sees masked vectors, then the SUM
   (clip + noise), then SecAgg+ mask            writes events + inspector files to /runs
```

### 2.1 File map

| File | Role |
|---|---|
| `step3_heart_dp.py` | Data (4 UCI files, 75/25 stratified split by `SEED`), model `Net`, DP-SGD with Opacus, RDP epsilon. Env `DATA_DIR`, `ALLOW_MISSING_DATA` |
| `step4_heart_secagg.py` | SecAgg+ (`SecAggPlusWorkflow(num_shares=4, reconstruction_threshold=3, max_weight=300, clipping_range=8)`), inspector mod, simulation entry point |
| `step6_heart_deploy.py` | Same as step 4 in deployment mode: `apply_run_config`, ServerApp runs baselines first, ends with `RESULT` + `done` |
| `pyproject.toml` | Flower app components and run_config keys (floats need a decimal point) |
| `run_step6_local.py` | Native run, no Docker: SuperLink + 4 SuperNodes as processes |
| `deploy/Dockerfile`, `deploy/docker-compose.yml` | One image for every role; one container per hospital; dashboard `MODE=deploy` |
| `deploy/docker-compose.mixed.yml` | amd64 SuperLink + s390x hungarian SuperNode (laptop rehearsal) |
| `deploy/LINUXONE.md` | Full LinuxONE runbook (section 5 is the summary) |
| `dashboard/` | Live dashboard; `replays/golden_run.jsonl` is the no-training fallback |

### 2.2 Design decisions and why

| Decision | Why |
|---|---|
| Flower **deployment mode**, not simulation | Ray has no s390x wheels (sourced: PyPI, 2026-10-10). Deployment also gives separate processes per hospital |
| Parameters as Flower **run_config**, not env | SuperNodes are long-running; env cannot change per run. `apply_run_config` copies values into step 3 **and** step 4 module globals |
| ServerApp runs `s3.baselines()` **before** building the strategy | Same torch RNG order as the simulation; gives exact equality (section 3) |
| Each SuperNode mounts **only its own** data file | The privacy story in one command: `ls /data` |
| One image for all roles, `ubuntu:24.04`, numpy/scipy/pandas/sklearn from apt | PyPI has no s390x wheels for them; apt has prebuilt s390x packages |
| torch from `download.pytorch.org/whl/cpu` | The only place with s390x torch wheels (sourced) |
| `set_parameters` converts arrays to native byte order | Big-endian clients reject little-endian arrays (section 4.6) |
| Light theme default, IBM Plex, gold = locked, teal = model | Dashboard redesign, PR #5 |

---

## 3. Results you can quote

| Claim | Number | Label | Source |
|---|---|---|---|
| Headline: privacy costs little accuracy | Federated 76.02% vs centralized 77.84%, gap 1.8 points (2.3%), within the ±2.0-point seed spread; FedProx, DP noise 2, SecAgg on, 5 seeds, ε ≈ 12.2 | measured | dashboard `/api/sweeps` (from `results/step3_runs.jsonl`, `step4_runs.jsonl`) |
| Step 2: plain federated learning | accuracy 0.778; FedProx ≈ FedAvg; FedAvg ≈ centralized | measured | CLAUDE.md |
| Step 3: DP cost | accuracy 0.767 (noise 0) to 0.758-0.760 (noise 2); max ε 12 at noise 2, 166 at noise 0.5 | measured | CLAUDE.md |
| Step 4: SecAgg+ costs no accuracy | 0.766 at noise 1, 0.758 at noise 2 (5 seeds); same ε; quantization error ~4e-6 | measured | CLAUDE.md |
| Step 4: SecAgg+ time cost | +0.4-0.5 s per round (2.0-2.6 s vs 1.5-2.1 s) | measured | CLAUDE.md |
| Golden run (dashboard default view) | 76.6% after 15 rounds; centralized 80.5%; worst-case ε 30.8; noise 1.0, FedAvg, seed 0, one run | measured | `dashboard/replays/golden_run.jsonl` |
| The server sees noise | masked vector of 274 uint32 values; chi-square uniformity test passes | measured | `test_dashboard.py`, CLAUDE.md |
| Step 6: deployment = simulation | SECAGG=0: accuracy, F1, per-hospital accuracy, ε, baselines identical (diff 0.0), FedAvg and FedProx, 3 rounds, seed 0 | measured | CLAUDE.md |
| Step 6: SecAgg+ error | 3.75e-6 vs bound 6.64e-6 after 1 round, same ε | measured | CLAUDE.md |
| s390x works (QEMU) | 1 round, all containers s390x: accuracy 0.7056, max ε 7.58, chi-square 17.9 < 37.70 | measured (emulated) | `deploy/LINUXONE.md` |
| Mixed amd64 + s390x | same accuracy (0.7056) and per-hospital accuracy as all-s390x | measured (emulated) | `deploy/LINUXONE.md` |
| Build cost on s390x | 174 min 35 s under QEMU (grpcio 141 min); image 3.6 GB | measured (emulated) | `deploy/LINUXONE.md` |
| Native LinuxONE build time | roughly 10-30 min | **estimate** (QEMU commonly 5-15x slower) | `deploy/LINUXONE.md` |
| Step 7: one label-flipping hospital | honest hospitals 76.3% -> 66.9% (FedAvg, noise 1, SecAgg on or off, 5 seeds) | measured | `results/step7_runs.jsonl` |
| Step 7: median vs label flip | 71.8% (wins back about half), only possible with SecAgg off; clean median 77.8% vs FedAvg 76.3% | measured | `results/step7_runs.jsonl` |
| Step 7: boost x10 of an honest update | 77.1%: no harm (it only gives va more weight) | measured | `results/step7_runs.jsonl` |
| Step 7: flip + boost x10 (boosts a harmful update) | honest hospitals 76.3% -> 42.8% (FedAvg, noise 1, SecAgg on or off, 5 seeds); median 71.4%; SecAgg+ clipped it in 0 of 300 rounds (max scaled value 2.58 < 8) | measured | `results/step7_runs.jsonl` |
| Step 7: membership inference | AUC 49-50% (coin flip) in every config, even no DP; 53.2% ± 2.6 when overfit (50 local epochs, no DP) | measured | `results/step7_runs.jsonl` |

Say "one run" or "mean of 5 seeds" every time. The design review flagged the headline (5-seed mean) next to a single run as a contradiction.

---

## 4. Gotchas by area (symptom -> cause -> fix)

### 4.1 Flower SecAgg+ (*vault* `flwr-secaggplus-gotchas`)
| Symptom | Cause | Fix |
|---|---|---|
| The error bound of 1/2 cell is wrong | Flower uses stochastic rounding | Use K·cell/Σ(n/max_weight) |
| Model silently stops changing after 2 of 4 dropouts | Threshold is 3; the workflow only logs "Secure aggregation halted" | Assert the model changes every round |
| SECAGG=1 is not bit-reproducible per seed | The quantizer uses unseeded `np.random` | Compare SecAgg runs statistically, not exactly |
| Values beyond ±8 after scaling | Silently clipped | Assert max\|w\| < 8 |

### 4.2 Inspector mod (*vault* `flwr-inspector-mod-gotchas`)
| Symptom | Cause | Fix |
|---|---|---|
| The mod never sees the masked reply | `mods[0]` is the OUTERMOST mod | Put the observer before `secaggplus_mod` |
| The stage name is missing | `secaggplus_mod` pops `"stage"` | Read it before `call_next` |
| Length check fails | The masked vector has a +1 example-count slot (273 → 274) | Expect params + 1 |
| A hospital drops silently | An exception inside a mod (for example a missing folder) | Create folders first; grep logs |

### 4.3 Opacus and epsilon (*vault* `opacus-default-accountant-prv`)
| Symptom | Cause | Fix |
|---|---|---|
| ε does not match the hand formula | Opacus 1.6 `PrivacyEngine()` defaults to the PRV accountant | Pass `accountant="rdp"` |
| ε resets every round | Flower recreates the client each round | Compute ε statelessly from the round history |
| FedProx term lost | Opacus per-sample hooks | Apply prox after `opt.step()`: `p -= LR*mu*(p - w_global)` |
| Results change between identical runs | Unseeded Poisson sampler (found in review) | Seed the sampler |

### 4.4 Flower deployment mode (*vault* `flwr-deployment-gotchas`)
| Symptom | Cause | Fix |
|---|---|---|
| `flwr run` cannot find the federation | Flower 1.37 reads `$FLWR_HOME/config.toml`, not pyproject federations | `[superlink.<name>] address = "host:port"` plus `root-certificates = "<ca.crt>"` (TLS) or `insecure = true`; set `FLWR_HOME` to a scratch folder |
| Port clash with the dashboard | SuperLink Control/Runtime API defaults to `--port 8000` | Use 9093; Fleet API is 9092; each SuperNode on one host needs its own `--port` |
| With TLS, a SuperNode or the CLI retries forever | The SuperLink certificate lacks the name the client dials (Flower's own `flower-superexec` dials 127.0.0.1) | `deploy/gen_certs.py` SANs: `superlink`, `localhost`, `127.0.0.1`, `::1`; CLI uses `root-certificates = ...` instead of `insecure = true` |
| A gRPC probe of port 9093 fails even with TLS working | The Control API on `--port` is HTTP in Flower 1.37; only the Fleet API (9092) is gRPC | Probe 9093 with HTTPS, 9092 with gRPC (`test_step6_deploy.py` e) |
| `flower-superexec` not found (Windows) | SuperLink spawns it by name | Venv Scripts on PATH; full path for every console script |
| The repo's modules load instead of the FAB | cwd is the repo | Run `flower-*` from outside the repo; `fab-include` keeps the FAB to 3 modules |
| SuperLink runs `uv sync` | Runtime dependency install is on | `--disable-runtime-dependency-installation` |
| A run_config override is rejected | Type must match the default | Floats need a decimal point (`noise=1.0`); empty string = unset |
| Flower phones home | Telemetry and update check are on by default | `FLWR_TELEMETRY_ENABLED=0 FLWR_DISABLE_UPDATE_CHECK=1` |
| Results differ from the simulation | Settings copied into only one module, or wrong RNG order | `apply_run_config` on step 3 and step 4 globals; baselines before the strategy |
| A zombie `flwr-serverapp` after Stop | The parent does not reap it | Harmless; it goes at the next run |

### 4.5 Docker
| Symptom | Cause | Fix |
|---|---|---|
| Build dies after 14 min with `ReadTimeoutError` | pip's 15 s read timeout | `PIP_DEFAULT_TIMEOUT=120 PIP_RETRIES=10` |
| A small fix re-runs a 2-hour compile | Layer cache | Each long compile in its own RUN; new apt packages in a late layer |
| Orphan processes after Stop | No init process in the container | `init: true` in compose reaps killed processes; a defunct `flwr-serverapp` can still show in the SuperLink until the next run (4.4, harmless) |
| Containers cannot read the data | They run as uid 1000 | `chmod a+r data/heart_disease/*.data` |
| Port 8000 busy | Another app | `DASHBOARD_PORT=8001` |
| `/data` paths mangled in Git Bash | MSYS path conversion | `MSYS_NO_PATHCONV=1`, `cygpath -m` |

### 4.6 s390x, QEMU, big-endian, protobuf (`deploy/LINUXONE.md`)
| Symptom | Cause | Fix |
|---|---|---|
| `pip install torch` fails on s390x | PyPI has no s390x torch | `--index-url https://download.pytorch.org/whl/cpu` |
| Long builds | No s390x wheels for grpcio, cryptography, numpy, scipy, pandas, scikit-learn, pycryptodome, httptools, uvloop | apt for numpy/scipy/pandas/sklearn; grpcio + cryptography compile (Rust needed for cryptography) |
| `ImportError: libopenblas.so.0` | The torch s390x wheel links OpenBLAS dynamically | apt `libopenblas0` |
| `import flwr` segfaults | protobuf 6.33 upb C extension under QEMU | `.pth` sets `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` on s390x. **Test the C extension on the real VM** (5.1) |
| Process exits with `Segmentation fault` (-11) after its work | Unresolved; maybe QEMU only | Long-running containers are fine. A hung QEMU container: `docker kill`, `--ulimit core=0` |
| Mixed run: one hospital scores 0.42, run "succeeds" | Little-endian arrays reach a big-endian client; SecAgg+ tolerates 1 dropout | Fixed in `set_parameters`. **Always** grep logs for `ClientApp raised` and check per-hospital accuracy |

### 4.7 Dashboard and Chart.js (*vault* `dashboard-ui-gotchas`)
| Symptom | Cause | Fix |
|---|---|---|
| "Maximum call stack size exceeded" | `s.ticks = s.ticks \|\| {}` on a Chart.js 4 options proxy | `if (!s.ticks) s.ticks = {}` |
| `this._fn is not a function` | Animated first draw + colours set after `new Chart()` | `Chart.defaults.animation = false` |
| A needle at x≈0 draws at ~10% | Bar chart on a linear axis pads half a bar | `offset: false` |
| Old JS/CSS after an edit | Browser cache | Server sends `Cache-Control: no-cache` for static files |
| `@ibm/plex` download 403 | Package over 150 MB for jsdelivr | `@ibm/plex-sans@1.1.0`, `@ibm/plex-mono@2.5.0` |
| Judges see two different accuracies | Headline = 5-seed mean, rail = one run | Label both sources on the page (done) |
| Sticky console hides controls | KPIs + long banner + help text | Status pill beside the heading, SecAgg above Averaging, short banner |

### 4.8 Windows shell and tools
| Symptom | Cause | Fix |
|---|---|---|
| `codex.ps1 cannot be loaded` | PowerShell execution policy | Use `/c/Users/DELL/AppData/Roaming/npm/codex.cmd` from Git Bash |
| Codex: `helper_unknown_error: setup refresh had errors` | Elevated sandbox from the desktop app | Add `-c 'windows.sandbox="unelevated"'` |
| `UnicodeEncodeError` on print | Console is cp1252 | `PYTHONIOENCODING=utf-8` |
| Orphan check lists Edge as a child | Windows reuses PIDs | Rerun; not a real leak |

### 4.9 Browser-pane QA (Claude desktop)
| Symptom | Cause | Fix |
|---|---|---|
| Screenshots blank, cropped or behind the scroll position | Hidden pane pauses rendering | DOM checks (`scrollWidth`, `getBoundingClientRect`); copy canvases into a fixed overlay to inspect them |
| KPIs show "–" after a run | `requestAnimationFrame` paused in a hidden pane | Take a screenshot to force a frame; not a bug |
| `preview_start {name}` fails: port busy | Another chat holds the port | `preview_start {url}` |

---

## 5. LinuxONE day-0 summary (full version: `deploy/LINUXONE.md`)

### 5.0 Done on 17 Oct (measured; session notes: `docs/linuxone_session/NOTES.md`)
- Registration: event code **SSF2026**; image `Ubuntu24.04-Datathon`, flavor `AI_LAB` (3 vCPU, 7.8 GB RAM, 50 GB); quota 1 server.
- Docker is not pre-installed: `sudo apt-get install -y docker.io docker-compose-v2`. `lscpu` shows the `nnpa` flag (Telum AI accelerator).
- Native build: **17 min 47 s** (QEMU: 174 min). 3-round SecAgg run ~3 min; RAM in use 2.3 GB of 7.8 GB with all 6 containers.
- The interpreter-exit segfault also happens on real hardware: `import flwr` prints, then exits 139; the dashboard shows `exit_code -11`
  although the run finished (all rounds + `done` in the events file). Judge success by the events file.
- Step 8 (written 17 Oct, PR #14): attacks + median defence now run in the deployment; flip+boost ran live on LinuxONE (honest acc 0.413).
- Laptop tunnel: Windows reserves ports 7911-8010, so `-L 8000:...` fails with `bind ... Permission denied`. Use `-L 8800:127.0.0.1:8000`
  and http://127.0.0.1:8800.

### 5.1 Pre-checks, right after you get the VM
```bash
uname -m                                   # must print s390x
docker compose version                     # or podman compose
```
After the build:
```bash
docker compose -f deploy/docker-compose.yml exec superlink python -c "import flwr"; echo $?   # must print 0
```
Try the faster protobuf C extension in a throw-away container: `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=upb python -c "import flwr"`.
If it works natively, remove the `.pth` for speed. (Unverified on real hardware.)

### 5.2 Build and start
Clone, fetch the 4 data files and `chmod a+r` them (commands in `deploy/LINUXONE.md` section 1), then:
```bash
time docker compose -f deploy/docker-compose.yml build      # once; never --no-cache
docker compose -f deploy/docker-compose.yml up -d
docker compose -f deploy/docker-compose.yml ps -a           # certs Exited (0); superlink + 4 supernodes + dashboard Up
```
TLS fallback if SuperNodes never join: `docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.insecure.yml up -d` (say "TLS off").
Open the dashboard from the laptop: `ssh -L 8800:127.0.0.1:8000 <user>@<vm>`, then http://127.0.0.1:8800 (8000 is reserved on this Windows laptop).

### 5.3 Proof for the judges
```bash
docker compose -f deploy/docker-compose.yml exec superlink uname -m          # s390x
docker compose -f deploy/docker-compose.yml exec superlink python -c "import sys,platform;print(platform.machine(), sys.byteorder)"   # s390x big
docker compose -f deploy/docker-compose.yml exec supernode-1 ls /data        # only processed.hungarian.data
docker compose -f deploy/docker-compose.yml exec supernode-1 ls /tls         # only ca.crt: the hospital holds no key
docker compose -f deploy/docker-compose.yml logs | grep -E "Traceback|ClientApp raised"   # must print nothing
```
`head -c 100 /runs/<id>/insp/masked.npy` shows `'descr': '>u4'`: the masked vector was written big-endian.

### 5.4 Fallbacks, in order
1. Build slow or failing: prebuild wheels once (`pip wheel grpcio grpcio-health-checking cryptography -w /wheels`), then `pip install --find-links /wheels`.
2. No Docker on the VM: apt packages + venv `--system-site-packages` + the Dockerfile's pip lines, `export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python`, then `python run_step6_local.py rounds=3 secagg=1 noise=1.0`.
3. Podman: `podman compose` takes the same file.
4. VM unusable: run the amd64 compose on the laptop and show the recorded s390x rehearsal (section 3). Say clearly that it is the rehearsal.
5. No training possible at all: the dashboard's golden replay.

### 5.5 Not verified yet
The protobuf C extension on real hardware; a 20-round run on LinuxONE (3 rounds measured);
an independent review of step 6 by the planning session (PR #6 merged before it); a long run of `test_step6_deploy.py` (~15 min) after the merge.

---

## 6. Pitch and judging

### 6.1 What the judges score
- **2026 FAQ** (sourced): innovation and creativity, technical implementation and complexity, relevance and impact (AI for Good),
  **why IBM Z is the right platform**, scalability and feasibility, presentation clarity.
- **2025 playbook** (sourced, older): value to community, creativity/novelty, technical design ("actual use of ML on Z, not just Python hosted somewhere").

### 6.2 Winning and losing patterns (playbook artifact)
| Winners did | Losers did | Our answer |
|---|---|---|
| One narrow problem, a named beneficiary, a number | Generic Kaggle classifiers; **heart disease is listed among datasets judges see several times every year** | The novelty is not the classifier: it is training across 4 real hospitals with DP + SecAgg+ on LinuxONE, with zero records shared |
| A single strong result as a number | Model bake-offs with mediocre accuracy | "Within 1.8 points of a centralized model (5-seed mean), at ε ≈ 12, without sharing patient data" |
| Actually deployed on LinuxONE, screen-shotable | IBM Z only on a slide | Live s390x proof commands (5.3) |
| Hit a platform snag and solved it (a past team: big-endian PyTorch) | Found platform problems too late | Our big-endian bug: a hospital silently dropped in a mixed run; found and fixed (4.6) |
| A complete, working demo | A notebook with no demo | Dashboard + golden replay fallback |

### 6.3 Five-minute demo script
1. **(30 s) Problem.** Hospitals cannot pool patient data (HIPAA, GDPR, India's DPDP Act 2023); small hospitals train weak models alone.
2. **(30 s) Idea.** The model travels, the data stays. Three layers: federated learning, differential privacy, secure aggregation.
3. **(60 s) LinuxONE proof.** Terminal: `uname -m` → s390x, `sys.byteorder` → big, `ls /data` in a hospital container shows only its own file.
4. **(90 s) Live run.** Dashboard: Start; accuracy climbs toward the centralized line; ε per hospital grows; the stage strip shows setup → share keys → masked upload → unmask.
5. **(45 s) What the server sees.** The hero strip and panel 2: 273 readable values become noise across 0…2³²; only the sum is recoverable.
6. **(30 s) Result.** The trade-off chart and the headline number, labelled "mean of 5 seeds".
6b. **(optional, 45 s) Attacks panel.** One label-flipping hospital costs the others ~9 points; the median wins back half, but only if SecAgg+ is off: a server that cannot see single updates can neither leak them nor catch the liar. Say that the membership attack fails (coin flip) even without DP on this small model.
7. **(15 s) Limits + next step.** Three limits (6.4) and the Secure Execution hardening slide (TLS is already on: say it in step 3).

### 6.4 Honest limits (say them)
- Threat model: honest-but-curious server. With 4 hospitals, 3 colluding with the server reveal the 4th's update.
- SecAgg+ hides single updates, not what the released model leaks; that is why DP is also needed. ε is large (12 at noise 2) because the hospitals are small.
- The SuperLink container holds all four files for the non-private baselines and the pooled test score (evaluation only).
- The `/runs` volume is the demo's inspector channel; the dashboard has no login.
- TLS encrypts every link between containers (not the loopback SuperNode -> ClientApp hop inside each hospital container) but uses a self-made demo CA and authenticates only the SuperLink: the CA is public, so TLS alone does not stop an unknown SuperNode from joining (Flower's `--enable-supernode-auth` would; not used).
- Values beyond ±8 after scaling are clipped; the run asserts they stay below 8.
- ε colour bands (<1 strong, 1-10 moderate, >10 weak) are a rule of thumb, not a standard.
- Step 7: SecAgg+ and robust aggregation exclude each other, so with SecAgg+ on we have no defence against a poisoning hospital (and cannot tell which one cheated). The membership attack fails even without DP, so the demo does not show DP stopping it; at ε ≈ 12 the DP guarantee itself is weak. Plain boost amplifies an honest update and does no harm; flip + boost amplifies a harmful one and cuts honest accuracy to 42.8%, and SecAgg+'s clipping range (±8) does not catch it.
- IBM Z security features (Secure Execution, pervasive encryption, Crypto Express) are **production hardening we did not implement**, unless you implement one during the event.

### 6.5 Why IBM Z / LinuxONE (honest framing)
- The theme "AI Secured: Innovation Without Exposure" nearly describes federated learning (playbook).
- It really runs on s390x, big-endian, and we fixed a real cross-architecture bug (measured).
- Five isolated containers on one consolidated, secure platform: the deployment shape regulated institutions use (inference).
- Next steps on Z: IBM Secure Execution for the aggregator; Crypto Express / pervasive encryption for keys and data at rest (sourced as Z features; not implemented).
- Gap: we have no measured scalability number. Do not invent one; say "4 hospitals tested; the protocol is designed for many".

### 6.6 Submission checklist
- [ ] Working demo: live URL or screen recording of the LinuxONE run (record it on 17 Oct evening as a backup)
- [ ] Repo link (public or shared with judges); `README.md` says how to run it (added 2026-10-11; update its results if you add new ones)
- [ ] Short description (reuse the abstract)
- [ ] Pitch deck: problem, beneficiary, approach, LinuxONE proof, result number, limits, next steps
- [ ] Submitted before 21:00 IST on 18 Oct

---

## 7. Working with Claude (what worked)

### 7.1 The loop
```
Opus plan (plan mode + routing card)  ->  Sonnet build session(s)  ->  review subagent + Codex read-only review
        ->  Opus visual / numbers QA in the browser pane  ->  fix Blocker/High  ->  PR
```
Codex review and Opus visual QA found different classes of bugs (code races vs misleading charts): keep both for user-facing work
(*vault* `Chats/2026-10-08 Token budget routing`).

### 7.2 Routing-card outcomes
| Step | Card | What happened |
|---|---|---|
| 3 (DP) | held | Sonnet built it with no retries; the Opus plan pre-empted 2 quiet failures; review found an unseeded sampler |
| 4 (SecAgg+) | held | Planned quiet-failure tests ran; review found a too-tight bound and a silent stall |
| 5 (dashboard) | held | Codex built `sweeps.py` in parallel; Codex review: 6 real findings (111.6k ChatGPT tokens); Opus QA: 4 more |
| 5 (redesign) | held | design-review agent: 0 blockers, 5 High (all fixed); Codex: no regressions (this session's record, 2026-10-10; commits `70844ac`, `127c77a`) |
| 6 (deploy) | not recorded | PR merged before the planning session's independent check |
| 7 (attacks) | changed mid-way | Planned as 2 Claude cloud sessions; the user moved it back to the laptop (local data and venv, no install). Opus review: 2 real bugs (attacker = MIA target; headline stuck on a partial sweep), 8 nits, all fixed. The sweep died once when the session ended; `RESUME=1` added |

### 7.3 Rules for every brief
- State the **honesty rule**: report what ran and its output; never claim a check passed without running it. (A Codex brief that asked for "best accuracy" produced cherry-picking.)
- Tell the worker how to self-check, and "if something is missing, say what and stop; never mock or guess".
- Name the gate test (for example "deployment must equal simulation, diff < 1e-9; never loosen the tolerance").
- After starting a session, check its model and effort with `get_session` (one session ran at medium though proposed at high).
- One writer per set of files; read-only work can run in parallel.
- Commit often; after a PR merge check `git log origin/main..branch` for commits that missed the merge.

### 7.4 Cost
- Input tokens dominate (~97% in a 40-turn session, toy estimate). Keep contexts small; start fresh sessions per phase.
- A cheap model that fails quietly costs more than a strong one that gets it right first time.
- Codex runs on the ChatGPT plan, not Claude tokens: use it for read-only reviews and self-contained modules. On this PC:
  `/c/Users/DELL/AppData/Roaming/npm/codex.cmd exec -s read-only -c 'windows.sandbox="unelevated"' "$(cat brief.txt)"`.
- Cloud threads and claude.ai Projects ignore `~/.claude`: put the rules in the repo `CLAUDE.md`.

---

## 8. Open items before 17 Oct
- [ ] Teammates registered (4 minimum) and on the team form by 15 Oct 23:59
- [ ] Abstract submitted (draft from 2026-10-10)
- [ ] Every member booked for the 16 Oct session
- [ ] Run `test_step6_deploy.py` once on `main` (~15 min) and record the result
- [ ] Pitch deck skeleton and the abstract text ready to paste
- [x] Repo `README.md` (problem, how to run on the laptop and on LinuxONE, results, limits)
- [ ] Laptop: amd64 image built, golden replay checked, data files copied to a USB stick
