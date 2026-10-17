# Graph Report - IBM DATATHON  (2026-10-17)

## Corpus Check
- 33 files · ~57,255 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 26 file(s) not represented in the graph (top: .jsonl 9, (none) 4, .woff2 4)

## Summary
- 1333 nodes · 3098 edges · 65 communities (57 shown, 8 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 115 edges (avg confidence: 0.84)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `85ba0036`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Z Datathon Playbook
- step2_heart_fedavg_fedprox.py
- IBM HACKATHON LEARNING.txt
- Federated Learning Toolkit
- run_step4_sweep.sh
- step1_flower_fedavg.py
- Corporate AI Circuit
- run_step2_sweep.sh
- step4_heart_secagg.py
- run_step3_sweep.sh
- server.py
- sweeps.py
- Step 5: live privacy dashboard (approved 2026-10-09)
- app.js
- chart.umd.min.js
- en
- 4. Gotchas by area (symptom -> cause -> fix)
- zs
- N
- e
- C
- i
- ae
- .isHorizontal
- .getMinMax
- _update
- I
- os
- qa
- CLAUDE.md
- de
- da
- ks
- Event improvement 1: TLS on gRPC (step 6 deployment)
- _e
- gen
- inspect_payload
- .parse
- .initialize
- z
- inspect_payload
- LocalDeployment
- RunManager
- r
- Track 2 AI Secured
- test_dashboard.py
- Opacus
- pa
- updateElements
- t
- P
- start_run
- validation_error
- step3_heart_dp.py
- step6_heart_deploy.py
- Running the federation on IBM LinuxONE (s390x): runbook
- ._update
- step7_heart_attacks.py
- mn
- main
- example_losses
- zero-exposure-heart
- run_step7_sweep.sh
- test_step7_attacks.py

## God Nodes (most connected - your core abstractions)
1. `I()` - 75 edges
2. `zs` - 73 edges
3. `os()` - 56 edges
4. `Z Datathon Playbook` - 40 edges
5. `N()` - 35 edges
6. `d()` - 28 edges
7. `updateElements()` - 24 edges
8. `en` - 24 edges
9. `A()` - 23 edges
10. `Corporate AI Circuit` - 23 edges

## Surprising Connections (you probably didn't know these)
- `Learning progression days 1-10` --semantically_similar_to--> `Four-week roadmap`  [INFERRED] [semantically similar]
  IBM HACKATHON LEARNING.txt → artifacts/z-datathon-playbook/index.html
- `example_losses()` --uses--> `Net`  [INFERRED]
  step7_heart_attacks.py → step3_heart_dp.py
- `make_strategy()` --indirect_call--> `weighted_avg()`  [INFERRED]
  step4_heart_secagg.py → step3_heart_dp.py
- `make_strategy()` --indirect_call--> `weighted_avg()`  [INFERRED]
  step7_heart_attacks.py → step3_heart_dp.py
- `IBM LinuxONE Docker` --conceptually_related_to--> `LinuxONE Community Cloud`  [INFERRED]
  IBM HACKATHON LEARNING.txt → artifacts/z-datathon-playbook/index.html

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Single FL training round flow** — artifacts_federated_learning_toolkit_index_round, artifacts_federated_learning_toolkit_index_dpsgd, artifacts_federated_learning_toolkit_index_secagg, artifacts_federated_learning_toolkit_index_flower, artifacts_federated_learning_toolkit_index_dashboard [EXTRACTED 0.95]
- **Four-layer improvement stack over FedAvg** — artifacts_federated_learning_toolkit_index_dpsgd, artifacts_federated_learning_toolkit_index_secagg, artifacts_federated_learning_toolkit_index_fedprox, artifacts_federated_learning_toolkit_index_dashboard [EXTRACTED 1.00]
- **Comparable corporate hackathons** — artifacts_corporate_ai_circuit_index_call_for_code, artifacts_corporate_ai_circuit_index_google_solution_challenge, artifacts_corporate_ai_circuit_index_imagine_cup, artifacts_corporate_ai_circuit_index_nasa_space_apps_challenge [EXTRACTED 1.00]
- **Private FL stack: FL + DP + SecAgg** — ibm_hackathon_learning_federated_learning, ibm_hackathon_learning_differential_privacy, ibm_hackathon_learning_secure_aggregation [EXTRACTED 1.00]
- **2026 tracks** — artifacts_z_datathon_playbook_index_track_1_real_time_ai, artifacts_z_datathon_playbook_index_track_2_ai_secured, artifacts_z_datathon_playbook_index_track_3_wildcard [EXTRACTED 1.00]

## Communities (65 total, 8 thin omitted)

### Community 0 - "Z Datathon Playbook"
Cohesion: 0.09
Nodes (35): Depth on familiar problem or narrow problem, Accessibility copilot, Autism Screening, Big-endian PyTorch issue, Breast Cancer Detection, COBOL modernization copilot, Creativity and novelty, Datathon Oct 17-18 (+27 more)

### Community 1 - "step2_heart_fedavg_fedprox.py"
Cohesion: 0.13
Nodes (20): baselines(), client_fn(), global_eval(), HospitalClient, load_hospital(), make_loader(), Net, Context (+12 more)

### Community 2 - "IBM HACKATHON LEARNING.txt"
Cohesion: 0.11
Nodes (29): Classification metrics, Client drift, Communication efficiency, Convergence, Dashboard, Datathon architecture, Differential Privacy, DP-SGD (+21 more)

### Community 3 - "Federated Learning Toolkit"
Cohesion: 0.09
Nodes (28): Build on Flower, Communication cost / quantization, Live Streamlit dashboard layer, Datasets: MedMNIST / Credit Card Fraud, Federated Learning Toolkit, Docker / LinuxONE deployment, DP-SGD via Opacus layer, Epsilon/delta privacy budget (+20 more)

### Community 5 - "step1_flower_fedavg.py"
Cohesion: 0.14
Nodes (16): client_fn(), dirichlet_partition(), global_eval(), HospitalClient, Net, Context, no_grad, NumPyClient (+8 more)

### Community 6 - "Corporate AI Circuit"
Cohesion: 0.18
Nodes (22): Accessibility built by someone who needs it, Alpha-Eye, ATTI, Call for Code, Corporate AI Circuit, Crowded food security, Crowded health diagnosis, FARMISTAR (+14 more)

### Community 8 - "step4_heart_secagg.py"
Cohesion: 0.12
Nodes (19): _bytes_in_value(), client_fn(), debug_write(), inspect_append(), inspector_mod(), main(), make_strategy(), n_arrays() (+11 more)

### Community 10 - "server.py"
Cohesion: 0.23
Nodes (12): Agg, Attack, current_run(), get_majority(), get_sweeps(), list_replays(), Step 5 dashboard backend: FastAPI + SSE. Starts step7_heart_attacks.py as a…, Accuracy of always answering the more common label, per hospital test set. Same… (+4 more)

### Community 11 - "sweeps.py"
Cohesion: 0.11
Nodes (27): Any, Run, _finite(), headline(), _json_safe(), load_attack_runs(), load_runs(), _mean_or_none() (+19 more)

### Community 12 - "Step 5: live privacy dashboard (approved 2026-10-09)"
Cohesion: 0.22
Nodes (8): Files, Goal, Layout, Risks and the test for each, Stack (approved), Stages, Step 5: live privacy dashboard (approved 2026-10-09), Verification (acceptance criteria)

### Community 13 - "app.js"
Cohesion: 0.06
Nodes (89): applyTrFilters(), atkCell(), atkNoise(), attach(), attachCurrent(), ATTACK_NAME, ATTACKS, axisTitle() (+81 more)

### Community 14 - "chart.umd.min.js"
Cohesion: 0.04
Nodes (38): addControllers(), addElements(), addPlugins(), addScales(), afterEvent(), as(), beforeLayout(), cn() (+30 more)

### Community 16 - "en"
Cohesion: 0.07
Nodes (18): add(), buildLookupTable(), determineDataLimits(), diff(), en, endOf(), format(), formats() (+10 more)

### Community 17 - "4. Gotchas by area (symptom -> cause -> fix)"
Cohesion: 0.05
Nodes (38): 0. Read this first, 1.1 Timeline, 1.2 Improvement options for the event (pick at most two), 1. Solo 24-hour plan, with Claude as the team, 2.1 File map, 2.2 Design decisions and why, 2. Architecture we proved, 3. Results you can quote (+30 more)

### Community 18 - "zs"
Cohesion: 0.08
Nodes (5): buildTicks(), d(), ia(), Si(), zs

### Community 19 - "N"
Cohesion: 0.17
Nodes (4): afterDraw(), Fn(), jn(), N()

### Community 20 - "e"
Cohesion: 0.24
Nodes (9): be(), constructor(), describe(), f(), ot(), override(), ri(), set() (+1 more)

### Community 21 - "C"
Cohesion: 0.18
Nodes (7): Aa(), C(), getDecimalForValue(), mt(), parse(), va(), xa()

### Community 22 - "i"
Cohesion: 0.22
Nodes (11): fi(), Ha(), ht(), ii(), i(), m(), mi(), Na() (+3 more)

### Community 23 - "ae"
Cohesion: 0.08
Nodes (16): ae, color(), ee(), Et(), ie(), It(), jt(), ke() (+8 more)

### Community 24 - ".isHorizontal"
Cohesion: 0.10
Nodes (14): A(), configure(), ct(), Es(), getPixelForTick(), getPixelForValue(), H(), Is() (+6 more)

### Community 25 - ".getMinMax"
Cohesion: 0.29
Nodes (3): _s(), updateRangeFromParsed(), ys()

### Community 26 - "_update"
Cohesion: 0.09
Nodes (10): bs, Ji, ki(), qi(), removeBox(), stop(), Ui(), _update() (+2 more)

### Community 27 - "I"
Cohesion: 0.05
Nodes (21): addBox(), afterDatasetsUpdate(), beforeDatasetsDraw(), Bi(), Ce(), dataset(), ea(), generateLabels() (+13 more)

### Community 28 - "os"
Cohesion: 0.12
Nodes (4): labelColor(), labelPointStyle(), os(), Ss()

### Community 29 - "qa"
Cohesion: 0.12
Nodes (6): He(), ka(), qa, ua(), v(), wi()

### Community 30 - "CLAUDE.md"
Cohesion: 0.19
Nodes (15): AI Secured track, Artifacts folder, Federated Learning Toolkit, Flower, IBM Z Datathon 2026 FL prep, Knowledge graph graphify-out, Non-IID simulated hospitals, Opacus (+7 more)

### Community 31 - "de"
Cohesion: 0.15
Nodes (6): de(), ei(), gs, ti(), ve(), Ye()

### Community 32 - "da"
Cohesion: 0.19
Nodes (5): da(), parseArrayData(), parseObjectData(), parsePrimitiveData(), resolveDataElementOptions()

### Community 34 - "Event improvement 1: TLS on gRPC (step 6 deployment)"
Cohesion: 0.25
Nodes (7): Event improvement 1: TLS on gRPC (step 6 deployment), Facts checked in the installed Flower 1.37 (not from memory), Files (worktree `../IBM DATATHON-tls`, branch `feature/grpc-tls` from origin/main; the flip+boost session owns this checkout), Goal, Risks, Routing card, Verification

### Community 35 - "_e"
Cohesion: 0.15
Nodes (13): average(), ca(), _e(), getCenterPoint(), c(), inRange(), nearest(), Ni() (+5 more)

### Community 36 - "gen"
Cohesion: 0.25
Nodes (9): check_run_id(), Status dict of a run: from memory if it is the current one, else from meta.json…, Static UI files are revalidated on every load (ETag), so an edited page or…, revalidate_static(), run_events(), run_status(), stop_run(), middleware (+1 more)

### Community 37 - "inspect_payload"
Cohesion: 0.33
Nodes (6): get_inspect(), hist(), inspect_dir_for(), inspect_payload(), The 'what the server sees' data of one run: plain update, received masked…, Resolve a run id or replay name to its inspect folder. Only ids/names matching…

### Community 38 - ".parse"
Cohesion: 0.13
Nodes (3): Ms(), Ps(), yt()

### Community 40 - "z"
Cohesion: 0.13
Nodes (14): afterUpdate(), An(), Ci(), Di(), draw(), Fe(), Ge(), je() (+6 more)

### Community 41 - "inspect_payload"
Cohesion: 0.18
Nodes (13): export_replay(), get_replay(), merged_events(), Complete JSON lines appended after `offset`. A half-written last line is left…, Per-hospital stage logs written by the inspector (one writer per file, so no…, All events of a finished run in time order: baseline + rounds + stages (+ final…, Freeze a finished run into dashboard/replays/<name>.jsonl (+ <name>/ with its…, read_jsonl() (+5 more)

### Community 42 - "LocalDeployment"
Cohesion: 0.07
Nodes (31): generate(), _key(), Create the TLS certificates for the step 6 deployment: a self-signed CA and one…, True if the existing server certificate has today's SAN list and is valid for…, Write the four files into `out` (created if needed). Returns `out`. Existing…, _still_good(), _write_cert(), _write_key() (+23 more)

### Community 43 - "RunManager"
Cohesion: 0.18
Nodes (10): deploy_run_config(), flwr_exe(), flwr_run_id(), kill_tree(), The run's parameters as a `flwr run --run-config` string (keys of…, Flower's id of the run, read from the CLI's output ('Successfully started run…, Deploy mode: ask the SuperLink to stop the run (killing the CLI alone would…, Kill proc and all its descendants (Ray raylet/workers included). (+2 more)

### Community 44 - "r"
Cohesion: 0.17
Nodes (12): Ai(), beforeDatasetDraw(), beforeDraw(), r(), ft(), gt(), hi(), li() (+4 more)

### Community 46 - "Track 2 AI Secured"
Cohesion: 0.29
Nodes (8): Federated learning privacy demo, Flower framework, Homomorphic encryption TenSEAL, IBM Secure Execution and pervasive encryption, Track 2 AI Secured, Homomorphic Encryption stretch goal, Three 2026 tracks, Track 2 AI Secured

### Community 47 - "test_dashboard.py"
Cohesion: 0.29
Nodes (4): parse_result(), Checks for step 5 (dashboard backend + hooks in step4_heart_secagg.py). Plain…, Run step4 as a subprocess (it reads its settings from env at import time).…, run_step4()

### Community 49 - "Opacus"
Cohesion: 0.29
Nodes (7): Differential privacy loan risk Opacus, Docker containerization, Flask or Streamlit demo, Prerequisites, IBM LinuxONE Docker, Opacus, Toolkit stack

### Community 53 - "updateElements"
Cohesion: 0.13
Nodes (10): _calculateBarIndexPixels(), getLabelAndValue(), getLabelForValue(), _getRuler(), _getStackCount(), _getStackIndex(), _getStacks(), ma (+2 more)

### Community 54 - "t"
Cohesion: 0.20
Nodes (12): apply(), bt(), cs(), ds(), getRange(), hs(), _notify(), pt() (+4 more)

### Community 57 - "P"
Cohesion: 0.12
Nodes (10): at(), dt(), fa(), ga(), label(), lt(), nt(), P() (+2 more)

### Community 58 - "start_run"
Cohesion: 0.33
Nodes (6): BaseModel, Why this combination cannot run, or None. Mirrors…, request_conflict(), RunRequest, start_run(), post

### Community 59 - "validation_error"
Cohesion: 0.67
Nodes (3): 422 without echoing the offending input: NaN/inf in the input would make the…, validation_error(), exception_handler

### Community 62 - "step3_heart_dp.py"
Cohesion: 0.12
Nodes (22): baselines(), client_fn(), global_eval(), HospitalClient, make_loader(), Net, Context, no_grad (+14 more)

### Community 64 - "step6_heart_deploy.py"
Cohesion: 0.15
Nodes (17): load_all_hospitals(), load_hospital(), Clean one hospital's file and split it 75/25. All statistics come from THIS…, One dict per hospital; None for a missing file only when ALLOW_MISSING_DATA=1…, apply_run_config(), client_fn(), inspector_switch_mod(), main() (+9 more)

### Community 65 - "Running the federation on IBM LinuxONE (s390x): runbook"
Cohesion: 0.14
Nodes (13): 0. Before the event (on the laptop, today), 1. On the LinuxONE VM, 2. What was measured in the rehearsal (QEMU, laptop), 3. Problems met (symptom, cause, fix) and what to try first on the real VM, 4. Fallback if the Docker build fails or is too slow on the VM, 5. What to say to the judges (honest version), 6. Mixed-architecture rehearsal (laptop only), Build (native, no QEMU) (+5 more)

### Community 66 - "._update"
Cohesion: 0.25
Nodes (4): getMaxOverflow(), getPlugin(), size(), vs()

### Community 69 - "step7_heart_attacks.py"
Cohesion: 0.16
Nodes (18): epsilon_after(), finite_or_none(), get_parameters(), Opacus sets q = 1/len(loader) and runs len(loader) steps per epoch. Computed…, Deterministic epsilon of one hospital after `rounds` rounds (RDP accountant;…, sample_rate_and_steps(), emit_event(), global_eval() (+10 more)

### Community 70 - "mn"
Cohesion: 0.18
Nodes (10): bn(), _calculateBarValuePixels(), getBasePixel(), getValueForPixel(), kn(), mn(), pn(), sn() (+2 more)

### Community 71 - "main"
Cohesion: 0.22
Nodes (7): attack_dir(), AttackHospitalClient, client_fn(), main(), Context, main, Step 4's main with this file's strategy (and global_eval).

### Community 73 - "example_losses"
Cohesion: 0.29
Nodes (7): attack_summary(), example_losses(), mia(), no_grad, Per-example BCE loss of the model with these parameters., Loss-threshold membership inference. Returns (AUC, advantage, n per side).…, Attack fields for the "attack" event and the RESULT line (reads the side…

### Community 76 - "run_step7_sweep.sh"
Cohesion: 0.60
Nodes (4): has_row(), one(), PYTHONIOENCODING, run_step7_sweep.sh script

### Community 77 - "test_step7_attacks.py"
Cohesion: 0.50
Nodes (3): proc(), Checks for step 7 (attacks). Plain script, no pytest. Each check runs a short…, run()

## Knowledge Gaps
- **103 isolated node(s):** `MARKERS`, `nf`, `registry`, `STAGE_IDX`, `STAGE_NAME` (+98 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 314 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `x()` connect `z` to `app.js`, `chart.umd.min.js`, `N`, `t`, `.isHorizontal`, `qa`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `zs` connect `zs` to `.parse`, `chart.umd.min.js`, `en`, `pa`, `N`, `e`, `C`, `.isHorizontal`, `P`, `_update`, `qa`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `I()` connect `I` to `z`, `chart.umd.min.js`, `.isHorizontal`, `P`, `_update`, `qa`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **What connects `MARKERS`, `nf`, `registry` to the rest of the system?**
  _103 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Z Datathon Playbook` be split into smaller, more focused modules?**
  _Cohesion score 0.09243697478991597 - nodes in this community are weakly interconnected._
- **Should `step2_heart_fedavg_fedprox.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12698412698412698 - nodes in this community are weakly interconnected._
- **Should `IBM HACKATHON LEARNING.txt` be split into smaller, more focused modules?**
  _Cohesion score 0.11494252873563218 - nodes in this community are weakly interconnected._