# Graph Report - IBM DATATHON  (2026-10-10)

## Corpus Check
- 27 files · ~43,686 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 23 file(s) not represented in the graph (top: .jsonl 8, (none) 4, .woff2 4)

## Summary
- 1219 nodes · 2914 edges · 76 communities (58 shown, 18 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 109 edges (avg confidence: 0.84)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `571b2c8f`
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
- wi
- zs
- N
- d
- r
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
- ._update
- ja
- add
- gen
- va
- .getDataset
- .update
- z
- inspect_payload
- LocalDeployment
- RunManager
- se
- .constructor
- Track 2 AI Secured
- test_dashboard.py
- .notifyPlugins
- Opacus
- t
- .buildOrUpdateControllers
- updateElements
- e
- .getDatasetMeta
- ks
- fa
- RunRequest
- validation_error
- .initialize
- A
- step3_heart_dp.py
- ._computeLabelItems
- step6_heart_deploy.py
- Running the federation on IBM LinuxONE (s390x): runbook
- Net
- _each
- C
- global_eval
- sn
- .getLabels
- load_all_hospitals
- test_step4_secagg.py
- zero-exposure-heart

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
- `make_strategy()` --indirect_call--> `weighted_avg()`  [INFERRED]
  step4_heart_secagg.py → step3_heart_dp.py
- `IBM LinuxONE Docker` --conceptually_related_to--> `LinuxONE Community Cloud`  [INFERRED]
  IBM HACKATHON LEARNING.txt → artifacts/z-datathon-playbook/index.html
- `Three 2026 tracks` --conceptually_related_to--> `Track 1 Real-Time AI`  [INFERRED]
  IBM HACKATHON LEARNING.txt → artifacts/z-datathon-playbook/index.html
- `Step 1 FedAvg script` --conceptually_related_to--> `FedAvg`  [INFERRED]
  CLAUDE.md → IBM HACKATHON LEARNING.txt

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Single FL training round flow** — artifacts_federated_learning_toolkit_index_round, artifacts_federated_learning_toolkit_index_dpsgd, artifacts_federated_learning_toolkit_index_secagg, artifacts_federated_learning_toolkit_index_flower, artifacts_federated_learning_toolkit_index_dashboard [EXTRACTED 0.95]
- **Four-layer improvement stack over FedAvg** — artifacts_federated_learning_toolkit_index_dpsgd, artifacts_federated_learning_toolkit_index_secagg, artifacts_federated_learning_toolkit_index_fedprox, artifacts_federated_learning_toolkit_index_dashboard [EXTRACTED 1.00]
- **Comparable corporate hackathons** — artifacts_corporate_ai_circuit_index_call_for_code, artifacts_corporate_ai_circuit_index_google_solution_challenge, artifacts_corporate_ai_circuit_index_imagine_cup, artifacts_corporate_ai_circuit_index_nasa_space_apps_challenge [EXTRACTED 1.00]
- **Private FL stack: FL + DP + SecAgg** — ibm_hackathon_learning_federated_learning, ibm_hackathon_learning_differential_privacy, ibm_hackathon_learning_secure_aggregation [EXTRACTED 1.00]
- **2026 tracks** — artifacts_z_datathon_playbook_index_track_1_real_time_ai, artifacts_z_datathon_playbook_index_track_2_ai_secured, artifacts_z_datathon_playbook_index_track_3_wildcard [EXTRACTED 1.00]

## Communities (76 total, 18 thin omitted)

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
Cohesion: 0.16
Nodes (16): _bytes_in_value(), client_fn(), debug_write(), inspect_append(), inspect_save(), inspector_mod(), n_arrays(), payload_bytes() (+8 more)

### Community 10 - "server.py"
Cohesion: 0.19
Nodes (13): current_run(), get_inspect(), get_majority(), get_sweeps(), inspect_dir_for(), list_replays(), Step 5 dashboard backend: FastAPI + SSE. Starts step4_heart_secagg.py as a…, Resolve a run id or replay name to its inspect folder. Only ids/names matching… (+5 more)

### Community 11 - "sweeps.py"
Cohesion: 0.13
Nodes (21): Any, Run, _finite(), headline(), _json_safe(), load_runs(), _mean_or_none(), Load and summarize the DP and secure-aggregation sweep results. (+13 more)

### Community 12 - "Step 5: live privacy dashboard (approved 2026-10-09)"
Cohesion: 0.22
Nodes (8): Files, Goal, Layout, Risks and the test for each, Stack (approved), Stages, Step 5: live privacy dashboard (approved 2026-10-09), Verification (acceptance criteria)

### Community 13 - "app.js"
Cohesion: 0.07
Nodes (79): applyTrFilters(), attach(), attachCurrent(), axisTitle(), backedText(), bandsPlugin, baseOptions(), boot() (+71 more)

### Community 14 - "chart.umd.min.js"
Cohesion: 0.06
Nodes (20): as(), Bi(), dataset(), destroy(), get(), getController(), getScale(), Gi() (+12 more)

### Community 16 - "en"
Cohesion: 0.11
Nodes (12): buildLookupTable(), diff(), en, endOf(), _generate(), getDecimalForValue(), _getTimestampsForTable(), initOffsets() (+4 more)

### Community 19 - "N"
Cohesion: 0.18
Nodes (7): afterDraw(), afterEvent(), Fn(), hn(), N(), rn(), x()

### Community 21 - "r"
Cohesion: 0.22
Nodes (9): Ai(), r(), ft(), gt(), hi(), li(), logarithmic(), numeric() (+1 more)

### Community 22 - "i"
Cohesion: 0.16
Nodes (16): ca(), fi(), Ha(), ht(), ii(), c(), i(), m() (+8 more)

### Community 23 - "ae"
Cohesion: 0.12
Nodes (8): ae, color(), ee(), ie(), ne(), oe(), re(), te()

### Community 24 - ".isHorizontal"
Cohesion: 0.22
Nodes (4): ct(), Is(), ln(), Rs()

### Community 26 - "_update"
Cohesion: 0.08
Nodes (12): beforeLayout(), bs, cn(), Ji, ki(), qi(), removeBox(), stop() (+4 more)

### Community 27 - "I"
Cohesion: 0.16
Nodes (4): beforeDatasetsDraw(), generateLabels(), I(), vn()

### Community 28 - "os"
Cohesion: 0.16
Nodes (3): labelColor(), labelPointStyle(), os()

### Community 29 - "qa"
Cohesion: 0.18
Nodes (5): He(), ka(), qa, ua(), v()

### Community 30 - "CLAUDE.md"
Cohesion: 0.19
Nodes (15): AI Secured track, Artifacts folder, Federated Learning Toolkit, Flower, IBM Z Datathon 2026 FL prep, Knowledge graph graphify-out, Non-IID simulated hospitals, Opacus (+7 more)

### Community 31 - "de"
Cohesion: 0.11
Nodes (10): cs(), de(), ds(), gs, hs(), St(), ti(), us() (+2 more)

### Community 32 - "da"
Cohesion: 0.15
Nodes (5): beforeDatasetDraw(), beforeDraw(), da(), kn(), wn()

### Community 33 - "._update"
Cohesion: 0.25
Nodes (4): getMaxOverflow(), getPlugin(), size(), vs()

### Community 35 - "add"
Cohesion: 0.15
Nodes (13): add(), average(), _e(), ei(), _getAnims(), getCenterPoint(), has(), listen() (+5 more)

### Community 36 - "gen"
Cohesion: 0.20
Nodes (12): check_run_id(), Status dict of a run: from memory if it is the current one, else from meta.json…, Static UI files are revalidated on every load (ETag), so an edited page or…, revalidate_static(), run_events(), gen(), run_status(), sse() (+4 more)

### Community 38 - ".getDataset"
Cohesion: 0.14
Nodes (4): Ms(), Ps(), Ss(), yt()

### Community 39 - ".update"
Cohesion: 0.20
Nodes (6): addBox(), configure(), k(), _refresh(), reset(), start()

### Community 40 - "z"
Cohesion: 0.19
Nodes (6): afterUpdate(), An(), Ci(), Di(), On, z()

### Community 41 - "inspect_payload"
Cohesion: 0.18
Nodes (13): export_replay(), get_replay(), hist(), inspect_payload(), merged_events(), Complete JSON lines appended after `offset`. A half-written last line is left…, Per-hospital stage logs written by the inspector (one writer per file, so no…, All events of a finished run in time order: baseline + rounds + stages (+ final… (+5 more)

### Community 42 - "LocalDeployment"
Cohesion: 0.10
Nodes (19): exe(), kill_tree(), LocalDeployment, main(), parse_result(), port_open(), Step 6 native launcher (Windows or Linux, no Docker): 1 SuperLink + 4…, SuperLink answers on the control port and all 4 SuperNodes are connected (they… (+11 more)

### Community 43 - "RunManager"
Cohesion: 0.18
Nodes (10): deploy_run_config(), flwr_exe(), flwr_run_id(), kill_tree(), Flower's id of the run, read from the CLI's output ('Successfully started run…, Deploy mode: ask the SuperLink to stop the run (killing the CLI alone would…, Kill proc and all its descendants (Ray raylet/workers included)., The run's parameters as a `flwr run --run-config` string (keys of… (+2 more)

### Community 44 - "se"
Cohesion: 0.22
Nodes (7): Et(), It(), jt(), ke(), se(), Tt(), Xt()

### Community 45 - ".constructor"
Cohesion: 0.17
Nodes (5): ea(), fs(), ra(), sa(), xe()

### Community 46 - "Track 2 AI Secured"
Cohesion: 0.29
Nodes (8): Federated learning privacy demo, Flower framework, Homomorphic encryption TenSEAL, IBM Secure Execution and pervasive encryption, Track 2 AI Secured, Homomorphic Encryption stretch goal, Three 2026 tracks, Track 2 AI Secured

### Community 47 - "test_dashboard.py"
Cohesion: 0.29
Nodes (4): parse_result(), Checks for step 5 (dashboard backend + hooks in step4_heart_secagg.py). Plain…, Run step4 as a subprocess (it reads its settings from env at import time).…, run_step4()

### Community 49 - "Opacus"
Cohesion: 0.29
Nodes (7): Differential privacy loan risk Opacus, Docker containerization, Flask or Streamlit demo, Prerequisites, IBM LinuxONE Docker, Opacus, Toolkit stack

### Community 51 - "t"
Cohesion: 0.33
Nodes (6): bt(), Ge(), getRange(), _notify(), t(), vi()

### Community 53 - "updateElements"
Cohesion: 0.06
Nodes (25): _calculateBarIndexPixels(), _calculateBarValuePixels(), getBasePixel(), getLabelAndValue(), getLabelForValue(), getPixelForTick(), getPixelForValue(), _getRuler() (+17 more)

### Community 54 - "e"
Cohesion: 0.28
Nodes (8): apply(), be(), constructor(), describe(), jn(), override(), set(), e()

### Community 55 - ".getDatasetMeta"
Cohesion: 0.18
Nodes (3): afterDatasetsUpdate(), onClick(), W()

### Community 57 - "fa"
Cohesion: 0.18
Nodes (6): at(), dt(), fa(), ga(), lt(), nt()

### Community 58 - "RunRequest"
Cohesion: 0.50
Nodes (4): BaseModel, RunRequest, start_run(), post

### Community 59 - "validation_error"
Cohesion: 0.67
Nodes (3): 422 without echoing the offending input: NaN/inf in the input would make the…, validation_error(), exception_handler

### Community 61 - "A"
Cohesion: 0.20
Nodes (12): A(), draw(), Fe(), H(), j(), je(), Nn(), O() (+4 more)

### Community 62 - "step3_heart_dp.py"
Cohesion: 0.15
Nodes (18): baselines(), client_fn(), epsilon_after(), global_eval(), Context, no_grad, Step 3: Step 2 (FedAvg / FedProx on the 4 real UCI Heart Disease hospitals) +…, Non-private local SGD (step-2 code), used only by the centralized / local-only… (+10 more)

### Community 63 - "._computeLabelItems"
Cohesion: 0.25
Nodes (3): Es(), L(), Le()

### Community 64 - "step6_heart_deploy.py"
Cohesion: 0.19
Nodes (14): finite_or_none(), apply_run_config(), client_fn(), inspector_switch_mod(), main(), _opt(), Context, main (+6 more)

### Community 65 - "Running the federation on IBM LinuxONE (s390x): runbook"
Cohesion: 0.14
Nodes (13): 0. Before the event (on the laptop, today), 1. On the LinuxONE VM, 2. What was measured in the rehearsal (QEMU, laptop), 3. Problems met (symptom, cause, fix) and what to try first on the real VM, 4. Fallback if the Docker build fails or is too slow on the VM, 5. What to say to the judges (honest version), 6. Mixed-architecture rehearsal (laptop only), Build (native, no QEMU) (+5 more)

### Community 66 - "Net"
Cohesion: 0.19
Nodes (8): HospitalClient, make_loader(), Net, NumPyClient, DP-SGD local training. Returns the PrivacyEngine (its accountant has this one…, train_dp(), Checks for step 3. Run: .venv\\Scripts\\python.exe test_step3_dp.py, trained_weights()

### Community 67 - "_each"
Cohesion: 0.17
Nodes (12): addControllers(), addElements(), addPlugins(), addScales(), _each(), _exec(), getElement(), _getRegistryForType() (+4 more)

### Community 68 - "C"
Cohesion: 0.22
Nodes (8): Aa(), C(), format(), formats(), init(), la(), ot(), parse()

### Community 69 - "global_eval"
Cohesion: 0.22
Nodes (9): get_parameters(), emit_event(), global_eval(), main(), make_strategy(), main, Same as step 3, plus: max |weight| of the aggregated model and a timestamp., Run the same FL loop as step 3, but the *fit* step (client training +… (+1 more)

### Community 70 - "sn"
Cohesion: 0.29
Nodes (5): bn(), getValueForPixel(), pn(), sn(), yn

### Community 72 - ".getLabels"
Cohesion: 0.40
Nodes (3): buildTicks(), determineDataLimits(), ia()

### Community 73 - "load_all_hospitals"
Cohesion: 0.50
Nodes (4): load_all_hospitals(), load_hospital(), Clean one hospital's file and split it 75/25. All statistics come from THIS…, One dict per hospital; None for a missing file only when ALLOW_MISSING_DATA=1…

## Knowledge Gaps
- **62 isolated node(s):** `MARKERS`, `nf`, `registry`, `STAGE_IDX`, `STAGE_NAME` (+57 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 251 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `x()` connect `N` to `ja`, `z`, `app.js`, `chart.umd.min.js`, `A`, `e`, `qa`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `zs` connect `zs` to `ja`, `va`, `.getLabels`, `chart.umd.min.js`, `en`, `wi`, `.parse`, `d`, `updateElements`, `e`, `.isHorizontal`, `fa`, `_update`, `A`, `._computeLabelItems`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `I()` connect `I` to `.update`, `.bindResponsiveEvents`, `z`, `.constructor`, `chart.umd.min.js`, `.notifyPlugins`, `qa`, `N`, `.buildOrUpdateControllers`, `updateElements`, `.getDatasetMeta`, `.isHorizontal`, `_update`, `A`, `._computeLabelItems`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **What connects `MARKERS`, `nf`, `registry` to the rest of the system?**
  _62 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Z Datathon Playbook` be split into smaller, more focused modules?**
  _Cohesion score 0.09243697478991597 - nodes in this community are weakly interconnected._
- **Should `step2_heart_fedavg_fedprox.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12698412698412698 - nodes in this community are weakly interconnected._
- **Should `IBM HACKATHON LEARNING.txt` be split into smaller, more focused modules?**
  _Cohesion score 0.11494252873563218 - nodes in this community are weakly interconnected._