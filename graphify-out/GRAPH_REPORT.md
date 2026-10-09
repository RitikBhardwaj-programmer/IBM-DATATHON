# Graph Report - IBM DATATHON  (2026-10-09)

## Corpus Check
- 11 files · ~16,292 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: .jsonl 3, (none) 2, .flag 2)

## Summary
- 262 nodes · 461 edges · 11 communities (7 shown, 4 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 36 edges (avg confidence: 0.82)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f5bca50f`
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
- step3_heart_dp.py
- run_step3_sweep.sh
- test_step4_secagg.py

## God Nodes (most connected - your core abstractions)
1. `Z Datathon Playbook` - 40 edges
2. `Corporate AI Circuit` - 23 edges
3. `Net` - 12 edges
4. `Federated Learning Toolkit` - 9 edges
5. `Flower (flwr)` - 8 edges
6. `HospitalClient` - 7 edges
7. `Net` - 7 edges
8. `HospitalClient` - 7 edges
9. `test()` - 7 edges
10. `HospitalClient` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Learning progression days 1-10` --semantically_similar_to--> `Four-week roadmap`  [INFERRED] [semantically similar]
  IBM HACKATHON LEARNING.txt → artifacts/z-datathon-playbook/index.html
- `make_strategy()` --indirect_call--> `weighted_avg()`  [INFERRED]
  step4_heart_secagg.py → step3_heart_dp.py
- `IBM LinuxONE Docker` --conceptually_related_to--> `Docker containerization`  [INFERRED]
  IBM HACKATHON LEARNING.txt → artifacts/z-datathon-playbook/index.html
- `Federated Learning` --conceptually_related_to--> `Federated learning privacy demo`  [EXTRACTED]
  IBM HACKATHON LEARNING.txt → artifacts/z-datathon-playbook/index.html
- `Flower` --conceptually_related_to--> `Flower framework`  [EXTRACTED]
  IBM HACKATHON LEARNING.txt → artifacts/z-datathon-playbook/index.html

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Single FL training round flow** — artifacts_federated_learning_toolkit_index_round, artifacts_federated_learning_toolkit_index_dpsgd, artifacts_federated_learning_toolkit_index_secagg, artifacts_federated_learning_toolkit_index_flower, artifacts_federated_learning_toolkit_index_dashboard [EXTRACTED 0.95]
- **Four-layer improvement stack over FedAvg** — artifacts_federated_learning_toolkit_index_dpsgd, artifacts_federated_learning_toolkit_index_secagg, artifacts_federated_learning_toolkit_index_fedprox, artifacts_federated_learning_toolkit_index_dashboard [EXTRACTED 1.00]
- **Comparable corporate hackathons** — artifacts_corporate_ai_circuit_index_call_for_code, artifacts_corporate_ai_circuit_index_google_solution_challenge, artifacts_corporate_ai_circuit_index_imagine_cup, artifacts_corporate_ai_circuit_index_nasa_space_apps_challenge [EXTRACTED 1.00]
- **Private FL stack: FL + DP + SecAgg** — ibm_hackathon_learning_federated_learning, ibm_hackathon_learning_differential_privacy, ibm_hackathon_learning_secure_aggregation [EXTRACTED 1.00]
- **2026 tracks** — artifacts_z_datathon_playbook_index_track_1_real_time_ai, artifacts_z_datathon_playbook_index_track_2_ai_secured, artifacts_z_datathon_playbook_index_track_3_wildcard [EXTRACTED 1.00]

## Communities (11 total, 4 thin omitted)

### Community 0 - "Z Datathon Playbook"
Cohesion: 0.08
Nodes (44): Depth on familiar problem or narrow problem, Accessibility copilot, Autism Screening, Big-endian PyTorch issue, Breast Cancer Detection, COBOL modernization copilot, Creativity and novelty, Datathon Oct 17-18 (+36 more)

### Community 1 - "step2_heart_fedavg_fedprox.py"
Cohesion: 0.13
Nodes (20): baselines(), client_fn(), global_eval(), HospitalClient, load_hospital(), make_loader(), Net, Context (+12 more)

### Community 2 - "IBM HACKATHON LEARNING.txt"
Cohesion: 0.07
Nodes (50): Differential privacy loan risk Opacus, Flask or Streamlit demo, AI Secured track, Artifacts folder, Federated Learning Toolkit, Flower, IBM Z Datathon 2026 FL prep, Knowledge graph graphify-out (+42 more)

### Community 3 - "Federated Learning Toolkit"
Cohesion: 0.09
Nodes (28): Build on Flower, Communication cost / quantization, Live Streamlit dashboard layer, Datasets: MedMNIST / Credit Card Fraud, Federated Learning Toolkit, Docker / LinuxONE deployment, DP-SGD via Opacus layer, Epsilon/delta privacy budget (+20 more)

### Community 5 - "step1_flower_fedavg.py"
Cohesion: 0.14
Nodes (16): client_fn(), dirichlet_partition(), global_eval(), HospitalClient, Net, Context, no_grad, NumPyClient (+8 more)

### Community 6 - "Corporate AI Circuit"
Cohesion: 0.18
Nodes (22): Accessibility built by someone who needs it, Alpha-Eye, ATTI, Call for Code, Corporate AI Circuit, Crowded food security, Crowded health diagnosis, FARMISTAR (+14 more)

### Community 8 - "step3_heart_dp.py"
Cohesion: 0.07
Nodes (42): baselines(), client_fn(), epsilon_after(), finite_or_none(), get_parameters(), global_eval(), HospitalClient, load_hospital() (+34 more)

## Knowledge Gaps
- **26 isolated node(s):** `run_step2_sweep.sh script`, `PYTHONIOENCODING`, `run_step3_sweep.sh script`, `PYTHONIOENCODING`, `run_step4_sweep.sh script` (+21 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 61 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Z Datathon Playbook` connect `Z Datathon Playbook` to `IBM HACKATHON LEARNING.txt`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `Artifacts folder` connect `IBM HACKATHON LEARNING.txt` to `Z Datathon Playbook`, `Corporate AI Circuit`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `Corporate AI Circuit` connect `Corporate AI Circuit` to `Z Datathon Playbook`, `IBM HACKATHON LEARNING.txt`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **What connects `run_step2_sweep.sh script`, `PYTHONIOENCODING`, `run_step3_sweep.sh script` to the rest of the system?**
  _26 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Z Datathon Playbook` be split into smaller, more focused modules?**
  _Cohesion score 0.07610993657505286 - nodes in this community are weakly interconnected._
- **Should `step2_heart_fedavg_fedprox.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12698412698412698 - nodes in this community are weakly interconnected._
- **Should `IBM HACKATHON LEARNING.txt` be split into smaller, more focused modules?**
  _Cohesion score 0.0693815987933635 - nodes in this community are weakly interconnected._