# Step 8: attackers + median defence in the step 6 deployment (runs on LinuxONE)

## Goal
Today the step 7 attacks (labelflip, boost, flipboost, curious-server MIA) and the median/trimmed defence run only in simulation
(Ray), and Ray has no s390x wheels. The dashboard refuses them in `MODE=deploy` (`dashboard/server.py:85`). Make them run in the
deployment (SuperLink + 4 SuperNode containers), so the attack demo runs live on LinuxONE. Written during the event (17 Oct).

## Approach: reuse step 7 unchanged, wire it like step 6 wired step 4
- NEW `step8_heart_deploy_attacks.py` (~120 lines): a Flower app (ServerApp + ClientApp) that imports step 3/4/6/7.
  - `apply_run_config(cfg)`: calls step 6's version, then copies the attack keys into step 7's module globals
    (`ATTACK, ATTACKER, BOOST, AGG, TRIM_BETA, MIA, MIA_HOSPITAL`) and the shared ones step 7 imported by value
    (`NUM_ROUNDS, MU, STRATEGY, SEED, NOISE, CLIP, DELTA, LOCAL_EPOCHS, SECAGG, INSPECT_DIR, INSPECT_ROUND, DEBUG_DIR`).
    Runs `s7.config_error()` and raises on a bad combination (e.g. median + SecAgg).
  - Side channel: step 7 clients write `attacker.jsonl` / `mia_update.npz` to `$STEP7_ATTACK_DIR`. In deployment that dir is
    `<run dir>/attack` on the shared `/runs` volume (new run_config key `attack-dir`; apply sets the env var in each process).
  - Client: step 6's two switch mods + `s7.AttackHospitalClient(pid)`.
  - Server: step 6's `main` order (baselines first: same torch RNG order) with `s7.make_strategy()` / `s7.global_eval`,
    then `s7.attack_summary`, the `attack` event and the same `RESULT` line as step 7.
- `pyproject.toml`: components -> step 8; `fab-include` += step7 + step8; new config keys
  `attack="none" attacker=3 boost=10.0 agg="fedavg" trim-beta=0.25 mia=1 mia-hospital=0 attack-dir=""`.
- `dashboard/server.py`: drop the deploy-mode refusal; `deploy_run_config` passes the attack keys and `attack-dir`;
  the attack card reads the `attack` event as in sim mode (check it does).
- `deploy/Dockerfile`: COPY step7/step8 if files are copied one by one (check). Rebuild = only the last layers.
- Step 6 stays as it is (no edits): step 8 with `attack=none agg=fedavg` must equal step 6.

## Verification (tests derived from the goal)
1. `test_step8_deploy_attacks.py` (native launcher, like `test_step6_deploy.py`):
   a. attack=none, agg=fedavg, secagg=0 -> equals step 6 deployment exactly (acc, F1, per-hospital, epsilon).
   b. attack=labelflip, secagg=1, 3 rounds, seed 0 -> equals step 7 SIMULATION with the same env exactly (fed_acc, honest_acc,
      per-hospital acc, epsilon); within the SecAgg quantization bound if not bit-equal.
   c. agg=median, secagg=0 -> runs and matches step 7 sim; agg=median + secagg=1 -> refused with step 7's message.
   d. MIA fields present and in [0, 1].
2. Dashboard in deploy mode (laptop Docker, amd64): an attack run shows the attack card; then the same on the LinuxONE VM.

## Risks
- Step 7 reads module globals at call time but imported some by value: a missed copy = silent wrong config. Test b catches it.
- `s7.global_eval` asserts `max_abs < CLIPPING_RANGE` only when attack=none (as in sim): same behaviour.
- The MIA side channel (honest hospital's last update written to a shared volume) only stands in for what the server sees with
  SecAgg off; say so in the demo, as in step 7.
- VM is on `feature/step7-attacks`; main now has TLS (needs `deploy/gen_certs.py` before `compose up`). Move the VM to the new
  branch after merge and follow `deploy/LINUXONE.md`.

## Not in scope
Attack sweeps on LinuxONE; new attack types; TLS changes.

## Routing card
| Phase | Agent | Model | Effort | Why |
|---|---|---|---|---|
| Explore | main session (done) | opus | - | step 6/7, dashboard and Flower's Ray import already read |
| Build step8 + pyproject + dashboard + Dockerfile | main session | opus | medium | context is loaded; a missed global copy fails quietly |
| Tests (~15-20 min of runs) | background Bash | - | - | runtime, not tokens |
| Review of the diff | Codex read-only, in parallel with the tests | n/a | - | independent eyes on ChatGPT quota |
| Deploy on the VM | main session | opus | low | commands only |
Codex handoffs: review (`codex exec -s read-only`), after the build.
Antigravity handoffs: none.
Switch needed: none.
