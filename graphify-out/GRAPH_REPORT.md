# Graph Report - IBM DATATHON  (2026-10-10)

## Corpus Check
- 22 files · ~37,981 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: .jsonl 8, .woff2 4, .npy 3)

## Summary
- 1151 nodes · 2808 edges · 66 communities (54 shown, 12 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 108 edges (avg confidence: 0.84)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `127c77ac`
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
- z
- zs
- N
- d
- r
- i
- ae
- getPixelForValue
- .getMinMax
- ks
- I
- os
- qa
- CLAUDE.md
- t
- da
- .configure
- .getLabels
- wi
- gen
- _calculateBarValuePixels
- .buildOrUpdateElements
- .update
- .isHorizontal
- inspect_payload
- .getParsed
- RunManager
- de
- .stop
- Track 2 AI Secured
- test_dashboard.py
- .notifyPlugins
- Opacus
- .getSortedVisibleDatasetMetas
- .buildOrUpdateControllers
- pa
- e
- .getDatasetMeta
- revalidate_static
- fa
- RunRequest
- validation_error
- .getDataset
- A
- Ji
- ._resolveTickFontOptions
- updateElements
- _getAnims

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

## Communities (66 total, 12 thin omitted)

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
Nodes (79): applyTrFilters(), attach(), attachCurrent(), axisTitle(), backedText(), bandsPlugin, baseOptions(), boot() (+71 more)

### Community 14 - "chart.umd.min.js"
Cohesion: 0.06
Nodes (21): addControllers(), addElements(), addPlugins(), addScales(), destroy(), _each(), ei(), _exec() (+13 more)

### Community 16 - "en"
Cohesion: 0.07
Nodes (25): add(), bn(), buildLookupTable(), diff(), en, endOf(), format(), formats() (+17 more)

### Community 17 - "z"
Cohesion: 0.19
Nodes (9): An(), Ci(), Di(), Fe(), Ge(), He(), Nn(), z() (+1 more)

### Community 19 - "N"
Cohesion: 0.15
Nodes (8): afterDraw(), afterEvent(), Fn(), hn(), jn(), N(), rn(), x()

### Community 21 - "r"
Cohesion: 0.22
Nodes (9): Ai(), r(), ft(), gt(), hi(), li(), logarithmic(), numeric() (+1 more)

### Community 22 - "i"
Cohesion: 0.10
Nodes (27): Aa(), as(), C(), ca(), draw(), fi(), ga(), Gi() (+19 more)

### Community 23 - "ae"
Cohesion: 0.15
Nodes (6): ae, color(), ne(), oe(), re(), te()

### Community 24 - "getPixelForValue"
Cohesion: 0.17
Nodes (7): ct(), Es(), getPixelForTick(), getPixelForValue(), _getRuler(), L(), Rs()

### Community 25 - ".getMinMax"
Cohesion: 0.25
Nodes (3): _s(), updateRangeFromParsed(), ys()

### Community 26 - "ks"
Cohesion: 0.06
Nodes (14): beforeLayout(), bs, cn(), getPlugin(), ki(), ks(), qi(), stop() (+6 more)

### Community 27 - "I"
Cohesion: 0.15
Nodes (4): generateLabels(), I(), W(), ya()

### Community 28 - "os"
Cohesion: 0.14
Nodes (3): labelColor(), labelPointStyle(), os()

### Community 29 - "qa"
Cohesion: 0.16
Nodes (6): ka(), label(), P(), qa, ua(), v()

### Community 30 - "CLAUDE.md"
Cohesion: 0.19
Nodes (15): AI Secured track, Artifacts folder, Federated Learning Toolkit, Flower, IBM Z Datathon 2026 FL prep, Knowledge graph graphify-out, Non-IID simulated hospitals, Opacus (+7 more)

### Community 31 - "t"
Cohesion: 0.15
Nodes (11): apply(), bt(), cs(), ds(), gs, hs(), _notify(), St() (+3 more)

### Community 32 - "da"
Cohesion: 0.19
Nodes (5): da(), parseArrayData(), parseObjectData(), parsePrimitiveData(), resolveDataElementOptions()

### Community 33 - ".configure"
Cohesion: 0.15
Nodes (8): addBox(), configure(), getMaxOverflow(), getScale(), Qs(), _refresh(), size(), start()

### Community 34 - ".getLabels"
Cohesion: 0.14
Nodes (7): buildTicks(), determineDataLimits(), Ha(), ja, g(), Na(), ws()

### Community 35 - "wi"
Cohesion: 0.20
Nodes (12): average(), Bi(), dataset(), _e(), getCenterPoint(), inRange(), nearest(), Ni() (+4 more)

### Community 36 - "gen"
Cohesion: 0.22
Nodes (11): check_run_id(), Status dict of a run: from memory if it is the current one, else from meta.json…, Complete JSON lines appended after `offset`. A half-written last line is left…, read_new_lines(), run_events(), gen(), run_status(), sse() (+3 more)

### Community 37 - "_calculateBarValuePixels"
Cohesion: 0.18
Nodes (3): _calculateBarValuePixels(), getValueForPixel(), mt()

### Community 38 - ".buildOrUpdateElements"
Cohesion: 0.20
Nodes (3): Ms(), Ps(), yt()

### Community 39 - ".update"
Cohesion: 0.20
Nodes (3): k(), removeBox(), reset()

### Community 40 - ".isHorizontal"
Cohesion: 0.17
Nodes (3): afterUpdate(), ln(), On

### Community 41 - "inspect_payload"
Cohesion: 0.22
Nodes (11): export_replay(), get_replay(), hist(), inspect_payload(), merged_events(), Per-hospital stage logs written by the inspector (one writer per file, so no…, All events of a finished run in time order: baseline + rounds + stages (+ final…, The 'what the server sees' data of one run: plain update, received masked… (+3 more)

### Community 42 - ".getParsed"
Cohesion: 0.20
Nodes (3): getLabelAndValue(), getLabelForValue(), ma

### Community 43 - "RunManager"
Cohesion: 0.36
Nodes (3): kill_tree(), Kill proc and all its descendants (Ray raylet/workers included)., RunManager

### Community 44 - "de"
Cohesion: 0.12
Nodes (10): de(), Et(), It(), jt(), ke(), rt(), se(), Tt() (+2 more)

### Community 46 - "Track 2 AI Secured"
Cohesion: 0.29
Nodes (8): Federated learning privacy demo, Flower framework, Homomorphic encryption TenSEAL, IBM Secure Execution and pervasive encryption, Track 2 AI Secured, Homomorphic Encryption stretch goal, Three 2026 tracks, Track 2 AI Secured

### Community 47 - "test_dashboard.py"
Cohesion: 0.29
Nodes (4): parse_result(), Checks for step 5 (dashboard backend + hooks in step4_heart_secagg.py). Plain…, Run step4 as a subprocess (it reads its settings from env at import time).…, run_step4()

### Community 48 - ".notifyPlugins"
Cohesion: 0.21
Nodes (5): Ce(), ea(), ia(), oa(), running()

### Community 49 - "Opacus"
Cohesion: 0.29
Nodes (7): Differential privacy loan risk Opacus, Docker containerization, Flask or Streamlit demo, Prerequisites, IBM LinuxONE Docker, Opacus, Toolkit stack

### Community 51 - ".getSortedVisibleDatasetMetas"
Cohesion: 0.28
Nodes (8): beforeDatasetDraw(), beforeDatasetsDraw(), beforeDraw(), getRange(), index(), vi(), vn(), wn()

### Community 54 - "e"
Cohesion: 0.24
Nodes (9): be(), constructor(), describe(), get(), me(), override(), route(), set() (+1 more)

### Community 56 - "revalidate_static"
Cohesion: 0.50
Nodes (4): Static UI files are revalidated on every load (ETag), so an edited page or…, revalidate_static(), middleware, Request

### Community 57 - "fa"
Cohesion: 0.20
Nodes (5): at(), dt(), fa(), lt(), nt()

### Community 58 - "RunRequest"
Cohesion: 0.67
Nodes (3): BaseModel, RunRequest, start_run()

### Community 59 - "validation_error"
Cohesion: 0.67
Nodes (3): 422 without echoing the offending input: NaN/inf in the input would make the…, validation_error(), exception_handler

### Community 60 - ".getDataset"
Cohesion: 0.18
Nodes (3): beforeUpdate(), initialize(), Ss()

### Community 61 - "A"
Cohesion: 0.29
Nodes (9): A(), H(), Is(), j(), je(), O(), Qe(), U() (+1 more)

### Community 63 - "._resolveTickFontOptions"
Cohesion: 0.29
Nodes (3): ee(), ie(), Le()

### Community 64 - "updateElements"
Cohesion: 0.36
Nodes (5): _calculateBarIndexPixels(), _getStackCount(), _getStackIndex(), _getStacks(), updateElements()

### Community 65 - "_getAnims"
Cohesion: 0.50
Nodes (3): _getAnims(), has(), listen()

## Knowledge Gaps
- **50 isolated node(s):** `MARKERS`, `nf`, `registry`, `STAGE_IDX`, `STAGE_NAME` (+45 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 217 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `x()` connect `N` to `.getLabels`, `.isHorizontal`, `app.js`, `chart.umd.min.js`, `z`, `A`, `qa`, `t`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `zs` connect `zs` to `.getLabels`, `_calculateBarValuePixels`, `chart.umd.min.js`, `en`, `z`, `.parse`, `d`, `e`, `getPixelForValue`, `fa`, `ks`, `A`, `._resolveTickFontOptions`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `I()` connect `I` to `.configure`, `wi`, `.update`, `.isHorizontal`, `.getParsed`, `.stop`, `chart.umd.min.js`, `.notifyPlugins`, `z`, `.getSortedVisibleDatasetMetas`, `.buildOrUpdateControllers`, `A`, `.getDatasetMeta`, `getPixelForValue`, `.getMinMax`, `ks`, `qa`, `t`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **What connects `MARKERS`, `nf`, `registry` to the rest of the system?**
  _50 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Z Datathon Playbook` be split into smaller, more focused modules?**
  _Cohesion score 0.09243697478991597 - nodes in this community are weakly interconnected._
- **Should `step2_heart_fedavg_fedprox.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12698412698412698 - nodes in this community are weakly interconnected._
- **Should `IBM HACKATHON LEARNING.txt` be split into smaller, more focused modules?**
  _Cohesion score 0.11494252873563218 - nodes in this community are weakly interconnected._