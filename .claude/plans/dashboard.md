# Step 5: live privacy dashboard (approved 2026-10-09)

## Goal
One page where judges watch private federated learning happen: hospitals train, epsilon is spent, the server only receives noise-like masked vectors, plus the headline "within X% of centralized, without sharing patient data". Demo: live on the laptop with a replay fallback; LinuxONE/Docker-ready (no Windows-only code paths outside a guarded process-kill helper; HOST/PORT env).

## Stack (approved)
FastAPI + uvicorn (already in .venv) + plain HTML/CSS/JS + SSE for live updates. Chart.js 4.4.1 vendored as one file `dashboard/static/vendor/chart.umd.min.js` (MIT; approved), so it works offline. No other new dependency.

## Layout
1. LIVE RUN: controls (noise 0-5, FedAvg/FedProx, SecAgg on/off, rounds 1-30, default 15) + Start/Stop; global accuracy per round with dashed centralized line; epsilon per hospital; 4 hospital small charts; SecAgg+ stage strip (setup -> share keys -> masked upload -> unmask); payload-bytes counter.
2. WHAT THE SERVER SEES: one hospital, one round, REAL captured data: plain-update histogram (bell) | received masked vector (flat) | aggregate; badge "plaintext arrays in message: 0".
3. PRIVACY VS ACCURACY: from results/step3_runs.jsonl and step4_runs.jsonl via dashboard/sweeps.py: accuracy vs epsilon (log x), error bars over 5 seeds, centralized line, computed headline.
4. HOW IT WORKS + LIMITS: architecture diagram, threat model, limits (see CLAUDE.md Step 4 limits).

## Files
- `step4_heart_secagg.py`: optional hooks, no behaviour change when unset:
  - `EVENTS_FILE`: append one JSON line per round (round, acc, f1, per-hospital acc, epsilon per hospital, max_abs_weight, t), flushed.
  - `INSPECT_DIR`: an inspector client mod placed OUTSIDE secaggplus_mod (verify Flower mod order: which list position is outermost). Records per message: stage name (configs key "stage"), timestamp, payload bytes of arrays/bytes in/out. For hospital 0 at round `INSPECT_ROUND` (default 1): the plain update (from the client fit) and the masked vector (reply config record, key "masked_params" = list of bytes -> flwr.common.bytes_to_ndarray), and the count of plaintext arrays left in the outgoing message (secaggplus_mod clears array_records; expect 0).
- `dashboard/server.py`: FastAPI app. Routes: GET / (static), POST /api/runs (start; validated body; 409 if a run is active), POST /api/runs/{id}/stop, GET /api/runs/{id}/events (SSE: round events, stage events, done/error), GET /api/replays (list), GET /api/replays/{name} (events for replay), GET /api/sweeps (from dashboard/sweeps.py), GET /api/inspect/{id} (server-sees data). Run manager: one run at a time, subprocess with argument list (no shell), own process group; stop/crash/shutdown kill the whole tree (Windows `taskkill /T /F /PID`, POSIX os.killpg). Bind 127.0.0.1 by default; HOST/PORT env.
- `dashboard/sweeps.py` + `dashboard/test_sweeps.py` (Codex handoff).
- `dashboard/static/`: index.html, app.js, styles.css, vendor/chart.umd.min.js.
- `dashboard/replays/golden_run.jsonl`: one committed recorded live run (+ its inspect data) for the replay fallback.
- `test_dashboard.py` (plain script, prints ALL OK; pytest is not installed).
- `CLAUDE.md`: Layout + how to start the dashboard.

## Stages
1. Backend + hooks (Sonnet/medium session; Sonnet/high review subagent).
2. Live + sweep panels + replay (Sonnet/high session).
3. Server-sees + limits panels, visual polish: projector 1366x768, large fonts, high contrast, dark/light, phone width without horizontal scroll (same session as 2; Codex read-only second-opinion review).
Then visual QA by the Opus planning session in the browser pane.

## Risks and the test for each
- Hooks change training numbers silently -> same seed with hooks on/off gives identical acc/F1/epsilon.
- Inspector captures the wrong message -> captured masked vector has the model's total parameter count, differs from the quantized plain update, and is roughly uniform over its range (chi-square or KS test); plaintext arrays in outgoing message == 0. Do NOT claim "masks cancel" on the page unless a test proves it on captured data.
- Orphan processes (Ray) after stop/crash -> test: after stop, no child process of the run remains.
- Bytes honesty -> label "array payload bytes (inspector), excludes framing".
- Epsilon colour bands are a rule of thumb (<1 strong, 1-10 moderate, >10 weak) -> label them so on the page.
- Live duration: Ray start ~10-20 s (estimate) + ~2 s/round (measured in step 4).

## Verification (acceptance criteria)
1. test_dashboard.py ALL OK: hook equivalence; API happy paths; 422 on bad input; 409 on second start; no orphans after stop; inspector checks.
2. dashboard/test_sweeps.py passes; sweep means equal an independent recomputation.
3. Real end-to-end live run in a browser; replay works without training.
4. Headline number computed from files and shown with its source.
5. Screenshots of each panel at 1366x768 and phone width; dark and light.
