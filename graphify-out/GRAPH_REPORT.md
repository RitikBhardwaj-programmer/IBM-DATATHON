# Graph Report - IBM DATATHON-tls  (2026-10-17)

## Corpus Check
- 30 files · ~56,417 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 27 file(s) not represented in the graph (top: .jsonl 9, (none) 5, .woff2 4)

## Summary
- 1325 nodes · 3091 edges · 72 communities (63 shown, 9 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 115 edges (avg confidence: 0.84)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c12622bb`
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
- draw
- n
- ae
- .isHorizontal
- updateElements
- ks
- I
- os
- qa
- CLAUDE.md
- i
- da
- Enum
- ._computeLabelSizes
- wi
- gen
- revalidate_static
- .parse
- .update
- On
- inspect_payload
- LocalDeployment
- RunManager
- de
- Track 2 AI Secured
- test_dashboard.py
- .notifyPlugins
- Opacus
- pa
- add
- .getParsed
- t
- .getDatasetMeta
- r
- start_run
- validation_error
- A
- O
- step3_heart_dp.py
- ln
- step6_heart_deploy.py
- Running the federation on IBM LinuxONE (s390x): runbook
- .configure
- step7_heart_attacks.py
- mn
- main
- .buildOrUpdateControllers
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

## Communities (72 total, 9 thin omitted)

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
Nodes (11): current_run(), get_inspect(), get_majority(), get_replay(), get_sweeps(), inspect_dir_for(), list_replays(), Step 5 dashboard backend: FastAPI + SSE. Starts step7_heart_attacks.py as a… (+3 more)

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
Cohesion: 0.05
Nodes (29): addControllers(), addElements(), addPlugins(), addScales(), afterEvent(), Bi(), dataset(), destroy() (+21 more)

### Community 16 - "en"
Cohesion: 0.07
Nodes (21): buildLookupTable(), determineDataLimits(), diff(), en, endOf(), format(), formats(), _generate() (+13 more)

### Community 17 - "4. Gotchas by area (symptom -> cause -> fix)"
Cohesion: 0.05
Nodes (38): 0. Read this first, 1.1 Timeline, 1.2 Improvement options for the event (pick at most two), 1. Solo 24-hour plan, with Claude as the team, 2.1 File map, 2.2 Design decisions and why, 2. Architecture we proved, 3. Results you can quote (+30 more)

### Community 18 - "zs"
Cohesion: 0.09
Nodes (5): buildTicks(), d(), ia(), Si(), zs

### Community 19 - "N"
Cohesion: 0.17
Nodes (4): afterDraw(), N(), _update(), W()

### Community 20 - "e"
Cohesion: 0.24
Nodes (8): be(), constructor(), describe(), jn(), override(), set(), ys(), e()

### Community 21 - "draw"
Cohesion: 0.11
Nodes (14): Aa(), beforeDatasetDraw(), beforeDatasetsDraw(), beforeDraw(), C(), draw(), ja, mt() (+6 more)

### Community 22 - "n"
Cohesion: 0.29
Nodes (7): fi(), Ha(), ht(), mi(), Na(), n(), yi()

### Community 23 - "ae"
Cohesion: 0.15
Nodes (6): ae, color(), ne(), oe(), re(), te()

### Community 24 - ".isHorizontal"
Cohesion: 0.11
Nodes (6): ct(), Es(), getPixelForTick(), getPixelForValue(), L(), Rs()

### Community 25 - "updateElements"
Cohesion: 0.24
Nodes (5): _calculateBarValuePixels(), getValueForPixel(), _s(), updateElements(), updateRangeFromParsed()

### Community 26 - "ks"
Cohesion: 0.05
Nodes (12): bs, getPlugin(), Ji, ki(), ks(), qi(), removeBox(), stop() (+4 more)

### Community 28 - "os"
Cohesion: 0.09
Nodes (7): as(), beforeUpdate(), initialize(), labelColor(), labelPointStyle(), os(), Ss()

### Community 29 - "qa"
Cohesion: 0.13
Nodes (8): _calculateBarIndexPixels(), _getStackCount(), _getStackIndex(), _getStacks(), label(), P(), qa, ua()

### Community 30 - "CLAUDE.md"
Cohesion: 0.19
Nodes (15): AI Secured track, Artifacts folder, Federated Learning Toolkit, Flower, IBM Z Datathon 2026 FL prep, Knowledge graph graphify-out, Non-IID simulated hospitals, Opacus (+7 more)

### Community 31 - "i"
Cohesion: 0.19
Nodes (5): gs, ii(), i(), ns(), us()

### Community 32 - "da"
Cohesion: 0.19
Nodes (5): da(), parseArrayData(), parseObjectData(), parsePrimitiveData(), resolveDataElementOptions()

### Community 33 - "Enum"
Cohesion: 0.60
Nodes (5): Agg, Attack, Strategy, Enum, str

### Community 34 - "._computeLabelSizes"
Cohesion: 0.50
Nodes (3): ee(), ie(), Le()

### Community 35 - "wi"
Cohesion: 0.12
Nodes (20): Ai(), average(), ca(), _e(), ft(), getCenterPoint(), c(), inRange() (+12 more)

### Community 36 - "gen"
Cohesion: 0.28
Nodes (9): check_run_id(), Status dict of a run: from memory if it is the current one, else from meta.json…, run_events(), gen(), run_status(), sse(), stderr_tail(), stop_run() (+1 more)

### Community 37 - "revalidate_static"
Cohesion: 0.50
Nodes (4): Static UI files are revalidated on every load (ETag), so an edited page or…, revalidate_static(), middleware, Request

### Community 38 - ".parse"
Cohesion: 0.14
Nodes (3): Ms(), Ps(), yt()

### Community 40 - "On"
Cohesion: 0.23
Nodes (3): afterUpdate(), An(), On

### Community 41 - "inspect_payload"
Cohesion: 0.18
Nodes (12): export_replay(), hist(), inspect_payload(), merged_events(), Complete JSON lines appended after `offset`. A half-written last line is left…, Per-hospital stage logs written by the inspector (one writer per file, so no…, All events of a finished run in time order: baseline + rounds + stages (+ final…, The 'what the server sees' data of one run: plain update, received masked… (+4 more)

### Community 42 - "LocalDeployment"
Cohesion: 0.06
Nodes (33): deploy_run_config(), The run's parameters as a `flwr run --run-config` string (keys of…, generate(), _key(), Create the TLS certificates for the step 6 deployment: a self-signed CA and one…, True if the existing server certificate has today's SAN list and is valid for…, Write the four files into `out` (created if needed). Returns `out`. Existing…, _still_good() (+25 more)

### Community 43 - "RunManager"
Cohesion: 0.22
Nodes (8): flwr_exe(), flwr_run_id(), kill_tree(), Flower's id of the run, read from the CLI's output ('Successfully started run…, Deploy mode: ask the SuperLink to stop the run (killing the CLI alone would…, Kill proc and all its descendants (Ray raylet/workers included)., RunManager, stop_flwr_run()

### Community 44 - "de"
Cohesion: 0.14
Nodes (8): de(), Et(), It(), jt(), ke(), numeric(), se(), Tt()

### Community 46 - "Track 2 AI Secured"
Cohesion: 0.29
Nodes (8): Federated learning privacy demo, Flower framework, Homomorphic encryption TenSEAL, IBM Secure Execution and pervasive encryption, Track 2 AI Secured, Homomorphic Encryption stretch goal, Three 2026 tracks, Track 2 AI Secured

### Community 47 - "test_dashboard.py"
Cohesion: 0.29
Nodes (4): parse_result(), Checks for step 5 (dashboard backend + hooks in step4_heart_secagg.py). Plain…, Run step4 as a subprocess (it reads its settings from env at import time).…, run_step4()

### Community 48 - ".notifyPlugins"
Cohesion: 0.26
Nodes (3): Ce(), ea(), running()

### Community 49 - "Opacus"
Cohesion: 0.29
Nodes (7): Differential privacy loan risk Opacus, Docker containerization, Flask or Streamlit demo, Prerequisites, IBM LinuxONE Docker, Opacus, Toolkit stack

### Community 51 - "add"
Cohesion: 0.22
Nodes (10): add(), ei(), Fe(), Ge(), je(), Qe(), ti(), Xt() (+2 more)

### Community 53 - ".getParsed"
Cohesion: 0.20
Nodes (3): getLabelAndValue(), getLabelForValue(), ma

### Community 54 - "t"
Cohesion: 0.17
Nodes (11): apply(), bt(), cs(), ds(), getRange(), hs(), _notify(), St() (+3 more)

### Community 57 - "r"
Cohesion: 0.11
Nodes (15): at(), dt(), r(), fa(), ga(), gt(), hi(), li() (+7 more)

### Community 58 - "start_run"
Cohesion: 0.40
Nodes (5): BaseModel, Why this combination cannot run, or None. Mirrors…, request_conflict(), RunRequest, start_run()

### Community 59 - "validation_error"
Cohesion: 0.67
Nodes (3): 422 without echoing the offending input: NaN/inf in the input would make the…, validation_error(), exception_handler

### Community 60 - "A"
Cohesion: 0.15
Nodes (11): A(), fs(), _getAnims(), H(), has(), j(), listen(), sa() (+3 more)

### Community 61 - "O"
Cohesion: 0.19
Nodes (9): Ci(), Di(), Fn(), He(), Is(), Nn(), O(), x() (+1 more)

### Community 62 - "step3_heart_dp.py"
Cohesion: 0.12
Nodes (22): baselines(), client_fn(), global_eval(), HospitalClient, make_loader(), Net, Context, no_grad (+14 more)

### Community 63 - "ln"
Cohesion: 0.25
Nodes (5): beforeLayout(), cn(), hn(), ln(), rn()

### Community 64 - "step6_heart_deploy.py"
Cohesion: 0.15
Nodes (17): load_all_hospitals(), load_hospital(), Clean one hospital's file and split it 75/25. All statistics come from THIS…, One dict per hospital; None for a missing file only when ALLOW_MISSING_DATA=1…, apply_run_config(), client_fn(), inspector_switch_mod(), main() (+9 more)

### Community 65 - "Running the federation on IBM LinuxONE (s390x): runbook"
Cohesion: 0.14
Nodes (13): 0. Before the event (on the laptop, today), 1. On the LinuxONE VM, 2. What was measured in the rehearsal (QEMU, laptop), 3. Problems met (symptom, cause, fix) and what to try first on the real VM, 4. Fallback if the Docker build fails or is too slow on the VM, 5. What to say to the judges (honest version), 6. Mixed-architecture rehearsal (laptop only), Build (native, no QEMU) (+5 more)

### Community 66 - ".configure"
Cohesion: 0.20
Nodes (6): addBox(), configure(), getMaxOverflow(), _refresh(), size(), start()

### Community 69 - "step7_heart_attacks.py"
Cohesion: 0.16
Nodes (18): epsilon_after(), finite_or_none(), get_parameters(), Opacus sets q = 1/len(loader) and runs len(loader) steps per epoch. Computed…, Deterministic epsilon of one hospital after `rounds` rounds (RDP accountant;…, sample_rate_and_steps(), emit_event(), global_eval() (+10 more)

### Community 70 - "mn"
Cohesion: 0.21
Nodes (8): bn(), getBasePixel(), kn(), mn(), pn(), sn(), xn(), yn

### Community 71 - "main"
Cohesion: 0.22
Nodes (7): attack_dir(), AttackHospitalClient, client_fn(), main(), Context, main, Step 4's main with this file's strategy (and global_eval).

### Community 72 - ".buildOrUpdateControllers"
Cohesion: 0.22
Nodes (3): ra(), remove(), ta()

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
- **97 isolated node(s):** `MARKERS`, `nf`, `registry`, `STAGE_IDX`, `STAGE_NAME` (+92 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 307 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `x()` connect `O` to `wi`, `app.js`, `chart.umd.min.js`, `en`, `t`, `ln`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `zs` connect `zs` to `._computeLabelSizes`, `.parse`, `chart.umd.min.js`, `en`, `qa`, `N`, `e`, `draw`, `.isHorizontal`, `r`, `ks`, `O`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `I()` connect `I` to `.update`, `.buildOrUpdateControllers`, `chart.umd.min.js`, `.notifyPlugins`, `O`, `N`, `draw`, `.getDatasetMeta`, `.isHorizontal`, `qa`, `i`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **What connects `MARKERS`, `nf`, `registry` to the rest of the system?**
  _97 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Z Datathon Playbook` be split into smaller, more focused modules?**
  _Cohesion score 0.09243697478991597 - nodes in this community are weakly interconnected._
- **Should `step2_heart_fedavg_fedprox.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12698412698412698 - nodes in this community are weakly interconnected._
- **Should `IBM HACKATHON LEARNING.txt` be split into smaller, more focused modules?**
  _Cohesion score 0.11494252873563218 - nodes in this community are weakly interconnected._