# Graph Report - IBM DATATHON  (2026-10-10)

## Corpus Check
- 22 files · ~37,482 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: .jsonl 8, .woff2 4, .npy 3)

## Summary
- 1147 nodes · 2800 edges · 59 communities (46 shown, 13 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 108 edges (avg confidence: 0.84)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `70844ac1`
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
- xs
- .isHorizontal
- N
- zs
- r
- i
- ae
- O
- .getMinMax
- ks
- I
- os
- qa
- CLAUDE.md
- gs
- da
- .configure
- ._handleEvent
- wi
- gen
- f
- .getDataset
- .render
- z
- inspect_payload
- updateElements
- RunManager
- .constructor
- .stop
- Track 2 AI Secured
- test_dashboard.py
- .notifyPlugins
- Opacus
- t
- .update
- e
- .getDatasetMeta
- revalidate_static
- ._update
- RunRequest
- validation_error

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
- `IBM LinuxONE Docker` --conceptually_related_to--> `LinuxONE Community Cloud`  [INFERRED]
  IBM HACKATHON LEARNING.txt → artifacts/z-datathon-playbook/index.html
- `Three 2026 tracks` --conceptually_related_to--> `Track 1 Real-Time AI`  [INFERRED]
  IBM HACKATHON LEARNING.txt → artifacts/z-datathon-playbook/index.html
- `Step 1 FedAvg script` --conceptually_related_to--> `FedAvg`  [INFERRED]
  CLAUDE.md → IBM HACKATHON LEARNING.txt
- `SecAgg+` --conceptually_related_to--> `Flower SecAgg+`  [INFERRED]
  CLAUDE.md → IBM HACKATHON LEARNING.txt

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Single FL training round flow** — artifacts_federated_learning_toolkit_index_round, artifacts_federated_learning_toolkit_index_dpsgd, artifacts_federated_learning_toolkit_index_secagg, artifacts_federated_learning_toolkit_index_flower, artifacts_federated_learning_toolkit_index_dashboard [EXTRACTED 0.95]
- **Four-layer improvement stack over FedAvg** — artifacts_federated_learning_toolkit_index_dpsgd, artifacts_federated_learning_toolkit_index_secagg, artifacts_federated_learning_toolkit_index_fedprox, artifacts_federated_learning_toolkit_index_dashboard [EXTRACTED 1.00]
- **Comparable corporate hackathons** — artifacts_corporate_ai_circuit_index_call_for_code, artifacts_corporate_ai_circuit_index_google_solution_challenge, artifacts_corporate_ai_circuit_index_imagine_cup, artifacts_corporate_ai_circuit_index_nasa_space_apps_challenge [EXTRACTED 1.00]
- **Private FL stack: FL + DP + SecAgg** — ibm_hackathon_learning_federated_learning, ibm_hackathon_learning_differential_privacy, ibm_hackathon_learning_secure_aggregation [EXTRACTED 1.00]
- **2026 tracks** — artifacts_z_datathon_playbook_index_track_1_real_time_ai, artifacts_z_datathon_playbook_index_track_2_ai_secured, artifacts_z_datathon_playbook_index_track_3_wildcard [EXTRACTED 1.00]

## Communities (59 total, 13 thin omitted)

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
Cohesion: 0.05
Nodes (55): main, baselines(), client_fn(), epsilon_after(), finite_or_none(), get_parameters(), global_eval(), HospitalClient (+47 more)

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
Nodes (75): applyTrFilters(), attach(), attachCurrent(), axisTitle(), bandsPlugin, baseOptions(), boot(), buildHospitalCharts() (+67 more)

### Community 14 - "chart.umd.min.js"
Cohesion: 0.05
Nodes (28): addControllers(), addElements(), addPlugins(), addScales(), as(), beforeLayout(), cn(), destroy() (+20 more)

### Community 16 - "en"
Cohesion: 0.06
Nodes (22): add(), buildLookupTable(), buildTicks(), determineDataLimits(), diff(), en, endOf(), format() (+14 more)

### Community 17 - "xs"
Cohesion: 0.21
Nodes (5): bs, ki(), stop(), Xi(), xs

### Community 19 - "N"
Cohesion: 0.12
Nodes (15): A(), afterDraw(), afterEvent(), Ci(), Fn(), H(), j(), jn() (+7 more)

### Community 20 - "zs"
Cohesion: 0.10
Nodes (3): d(), Si(), zs

### Community 21 - "r"
Cohesion: 0.18
Nodes (12): Ai(), at(), r(), ft(), gt(), hi(), li(), logarithmic() (+4 more)

### Community 22 - "i"
Cohesion: 0.13
Nodes (22): ca(), draw(), fi(), Ge(), getMaxOverflow(), Gi(), Ha(), ht() (+14 more)

### Community 23 - "ae"
Cohesion: 0.08
Nodes (13): ae, color(), de(), Et(), It(), jt(), ke(), ne() (+5 more)

### Community 24 - "O"
Cohesion: 0.10
Nodes (14): ct(), ee(), Es(), getBasePixel(), getPixelForTick(), getPixelForValue(), ie(), Is() (+6 more)

### Community 25 - ".getMinMax"
Cohesion: 0.29
Nodes (3): _s(), updateRangeFromParsed(), ys()

### Community 27 - "I"
Cohesion: 0.15
Nodes (3): generateLabels(), I(), ya()

### Community 28 - "os"
Cohesion: 0.13
Nodes (4): labelColor(), labelPointStyle(), os(), Ss()

### Community 29 - "qa"
Cohesion: 0.15
Nodes (5): Fe(), He(), qa, ua(), Xt()

### Community 30 - "CLAUDE.md"
Cohesion: 0.19
Nodes (15): AI Secured track, Artifacts folder, Federated Learning Toolkit, Flower, IBM Z Datathon 2026 FL prep, Knowledge graph graphify-out, Non-IID simulated hospitals, Opacus (+7 more)

### Community 31 - "gs"
Cohesion: 0.09
Nodes (10): cs(), ds(), ei(), gs, hs(), Ji, qi(), ti() (+2 more)

### Community 32 - "da"
Cohesion: 0.20
Nodes (3): da(), parseArrayData(), parsePrimitiveData()

### Community 33 - ".configure"
Cohesion: 0.17
Nodes (7): addBox(), configure(), getScale(), Qs(), _refresh(), removeBox(), start()

### Community 35 - "wi"
Cohesion: 0.17
Nodes (11): average(), Bi(), dataset(), _e(), getCenterPoint(), inRange(), nearest(), Ni() (+3 more)

### Community 36 - "gen"
Cohesion: 0.22
Nodes (11): check_run_id(), Status dict of a run: from memory if it is the current one, else from meta.json…, Complete JSON lines appended after `offset`. A half-written last line is left…, read_new_lines(), run_events(), gen(), run_status(), sse() (+3 more)

### Community 37 - "f"
Cohesion: 0.10
Nodes (14): Aa(), bn(), C(), getDecimalForValue(), getValueForPixel(), kn(), mt(), f() (+6 more)

### Community 38 - ".getDataset"
Cohesion: 0.14
Nodes (5): beforeUpdate(), initialize(), Ms(), Ps(), yt()

### Community 40 - "z"
Cohesion: 0.18
Nodes (7): afterUpdate(), An(), Di(), Nn(), On, x(), z()

### Community 41 - "inspect_payload"
Cohesion: 0.22
Nodes (11): export_replay(), get_replay(), hist(), inspect_payload(), merged_events(), Per-hospital stage logs written by the inspector (one writer per file, so no…, All events of a finished run in time order: baseline + rounds + stages (+ final…, The 'what the server sees' data of one run: plain update, received masked… (+3 more)

### Community 42 - "updateElements"
Cohesion: 0.06
Nodes (19): _calculateBarIndexPixels(), dt(), fa(), ga(), getLabelAndValue(), getLabelForValue(), _getRuler(), _getStackCount() (+11 more)

### Community 43 - "RunManager"
Cohesion: 0.36
Nodes (3): kill_tree(), Kill proc and all its descendants (Ray raylet/workers included)., RunManager

### Community 44 - ".constructor"
Cohesion: 0.25
Nodes (5): ea(), fs(), ia(), sa(), xe()

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
Cohesion: 0.13
Nodes (17): apply(), beforeDatasetDraw(), beforeDatasetsDraw(), beforeDraw(), bt(), getRange(), index(), ka() (+9 more)

### Community 52 - ".update"
Cohesion: 0.27
Nodes (3): getController(), reset(), ta()

### Community 54 - "e"
Cohesion: 0.38
Nodes (6): be(), constructor(), describe(), override(), set(), e()

### Community 56 - "revalidate_static"
Cohesion: 0.50
Nodes (4): Static UI files are revalidated on every load (ETag), so an edited page or…, revalidate_static(), middleware, Request

### Community 58 - "RunRequest"
Cohesion: 0.67
Nodes (3): BaseModel, RunRequest, start_run()

### Community 59 - "validation_error"
Cohesion: 0.67
Nodes (3): 422 without echoing the offending input: NaN/inf in the input would make the…, validation_error(), exception_handler

## Knowledge Gaps
- **49 isolated node(s):** `MARKERS`, `nf`, `registry`, `STAGE_IDX`, `STAGE_NAME` (+44 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 216 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `x()` connect `z` to `app.js`, `chart.umd.min.js`, `N`, `t`, `O`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Why does `zs` connect `zs` to `f`, `updateElements`, `chart.umd.min.js`, `en`, `xs`, `.isHorizontal`, `e`, `O`, `qa`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Why does `I()` connect `I` to `.configure`, `._handleEvent`, `wi`, `.render`, `z`, `updateElements`, `.constructor`, `.stop`, `chart.umd.min.js`, `.notifyPlugins`, `.isHorizontal`, `t`, `.update`, `N`, `.getDatasetMeta`, `O`, `qa`, `gs`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **What connects `MARKERS`, `nf`, `registry` to the rest of the system?**
  _49 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Z Datathon Playbook` be split into smaller, more focused modules?**
  _Cohesion score 0.09243697478991597 - nodes in this community are weakly interconnected._
- **Should `step2_heart_fedavg_fedprox.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12698412698412698 - nodes in this community are weakly interconnected._
- **Should `IBM HACKATHON LEARNING.txt` be split into smaller, more focused modules?**
  _Cohesion score 0.11494252873563218 - nodes in this community are weakly interconnected._