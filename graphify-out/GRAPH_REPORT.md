# Graph Report - IBM DATATHON  (2026-10-09)

## Corpus Check
- 8 files · ~14,354 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .jsonl 2, .flag 1)

## Summary
- 242 nodes · 421 edges · 10 communities (8 shown, 2 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 34 edges (avg confidence: 0.81)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3dc6abd1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Z Datathon Playbook
- step2_heart_fedavg_fedprox.py
- IBM HACKATHON LEARNING.txt
- Federated Learning Toolkit
- CLAUDE.md
- step1_flower_fedavg.py
- Corporate AI Circuit
- run_step2_sweep.sh
- step3_heart_dp.py
- run_step3_sweep.sh

## God Nodes (most connected - your core abstractions)
1. `Z Datathon Playbook` - 40 edges
2. `Corporate AI Circuit` - 23 edges
3. `Net` - 9 edges
4. `Federated Learning Toolkit` - 9 edges
5. `Flower (flwr)` - 8 edges
6. `HospitalClient` - 7 edges
7. `Net` - 7 edges
8. `HospitalClient` - 7 edges
9. `HospitalClient` - 7 edges
10. `global_eval()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Learning progression days 1-10` --semantically_similar_to--> `Four-week roadmap`  [INFERRED] [semantically similar]
  IBM HACKATHON LEARNING.txt → artifacts/z-datathon-playbook/index.html
- `Three 2026 tracks` --conceptually_related_to--> `Track 1 Real-Time AI`  [INFERRED]
  IBM HACKATHON LEARNING.txt → artifacts/z-datathon-playbook/index.html
- `IBM LinuxONE Docker` --conceptually_related_to--> `Docker containerization`  [INFERRED]
  IBM HACKATHON LEARNING.txt → artifacts/z-datathon-playbook/index.html
- `Judging dimensions` --conceptually_related_to--> `Judging rubric 2025`  [EXTRACTED]
  IBM HACKATHON LEARNING.txt → artifacts/z-datathon-playbook/index.html
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

## Communities (10 total, 2 thin omitted)

### Community 0 - "Z Datathon Playbook"
Cohesion: 0.08
Nodes (41): Depth on familiar problem or narrow problem, Accessibility copilot, Autism Screening, Big-endian PyTorch issue, Breast Cancer Detection, COBOL modernization copilot, Creativity and novelty, Datathon Oct 17-18 (+33 more)

### Community 1 - "step2_heart_fedavg_fedprox.py"
Cohesion: 0.13
Nodes (20): baselines(), client_fn(), global_eval(), HospitalClient, load_hospital(), make_loader(), Net, Context (+12 more)

### Community 2 - "IBM HACKATHON LEARNING.txt"
Cohesion: 0.10
Nodes (34): Non-IID simulated hospitals, Step 1 FedAvg script, Classification metrics, Client drift, Communication efficiency, Convergence, Dashboard, Datathon architecture (+26 more)

### Community 3 - "Federated Learning Toolkit"
Cohesion: 0.09
Nodes (28): Build on Flower, Communication cost / quantization, Live Streamlit dashboard layer, Datasets: MedMNIST / Credit Card Fraud, Federated Learning Toolkit, Docker / LinuxONE deployment, DP-SGD via Opacus layer, Epsilon/delta privacy budget (+20 more)

### Community 4 - "CLAUDE.md"
Cohesion: 0.14
Nodes (19): Differential privacy loan risk Opacus, Flask or Streamlit demo, AI Secured track, Artifacts folder, Federated Learning Toolkit, Flower, IBM Z Datathon 2026 FL prep, Knowledge graph graphify-out (+11 more)

### Community 5 - "step1_flower_fedavg.py"
Cohesion: 0.14
Nodes (16): client_fn(), dirichlet_partition(), global_eval(), HospitalClient, Net, Context, no_grad, NumPyClient (+8 more)

### Community 6 - "Corporate AI Circuit"
Cohesion: 0.18
Nodes (22): Accessibility built by someone who needs it, Alpha-Eye, ATTI, Call for Code, Corporate AI Circuit, Crowded food security, Crowded health diagnosis, FARMISTAR (+14 more)

### Community 8 - "step3_heart_dp.py"
Cohesion: 0.09
Nodes (28): baselines(), client_fn(), epsilon_after(), global_eval(), HospitalClient, load_hospital(), make_loader(), Net (+20 more)

## Knowledge Gaps
- **24 isolated node(s):** `run_step2_sweep.sh script`, `PYTHONIOENCODING`, `run_step3_sweep.sh script`, `PYTHONIOENCODING`, `Autism Screening` (+19 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 55 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Z Datathon Playbook` connect `Z Datathon Playbook` to `CLAUDE.md`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Why does `Artifacts folder` connect `CLAUDE.md` to `Z Datathon Playbook`, `Corporate AI Circuit`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `Corporate AI Circuit` connect `Corporate AI Circuit` to `Z Datathon Playbook`, `CLAUDE.md`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **What connects `run_step2_sweep.sh script`, `PYTHONIOENCODING`, `run_step3_sweep.sh script` to the rest of the system?**
  _24 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Z Datathon Playbook` be split into smaller, more focused modules?**
  _Cohesion score 0.08170731707317073 - nodes in this community are weakly interconnected._
- **Should `step2_heart_fedavg_fedprox.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12698412698412698 - nodes in this community are weakly interconnected._
- **Should `IBM HACKATHON LEARNING.txt` be split into smaller, more focused modules?**
  _Cohesion score 0.09915966386554621 - nodes in this community are weakly interconnected._