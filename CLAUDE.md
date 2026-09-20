# IBM Z Datathon 2026 — Federated Learning prep

Goal: build a privacy-preserving federated learning demo (Flower + PyTorch, later Opacus DP and SecAgg+) for the "AI Secured: Innovation Without Exposure" track.

## Use the knowledge graph first
`graphify-out/` holds a knowledge graph of this folder. Before grepping or reading files, consult
`graphify-out/GRAPH_REPORT.md`, then use `graphify explain "<node>"` / `graphify path "A" "B"`.
After changing code run `graphify update .`; after changing docs/notes run `/graphify --update`.

## Layout
- `IBM HACKATHON LEARNING.txt` — learning progress summary (theory done; next is implementation).
- `step1_flower_fedavg.py` — Step 1: FedAvg, 3 non-IID simulated hospitals. Run with `.venv\Scripts\python.exe`.
- `artifacts/` — local copies of the three claude.ai artifacts (each `index.html`): Z Datathon Playbook, Corporate AI Circuit, Federated Learning Toolkit.
- `.venv/` — Python 3.14 venv (torch, flwr, ray, scikit-learn, pandas). Ignored by graphify via `.graphifyignore`.

## Teaching preference
Teach like a mentor: intuition -> simple example -> technical detail -> quiz -> implementation. Explain code in small pieces; don't dump big codebases. Don't re-teach completed theory (FedAvg, non-IID, FedProx, DP, SecAgg).
- `step2_heart_fedavg_fedprox.py` — Step 2: FedAvg vs FedProx on UCI Heart Disease with its 4 real hospitals. Sweep: `run_step2_sweep.sh` -> `results/step2_runs.jsonl`. Finding: FedProx ~ FedAvg; FedAvg ~ centralized.
- `data/heart_disease/` — NOT in git. Download the 4 files `processed.{cleveland,hungarian,switzerland,va}.data` from https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/
