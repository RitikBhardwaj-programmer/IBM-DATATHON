"""Standalone checks for the sweep-summary helpers."""

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sweeps


def find(groups, source, secagg, strategy, noise):
    return next(
        group for group in groups
        if (group["source"], group["secagg"], group["strategy"], group["noise"])
        == (source, secagg, strategy, noise)
    )


def main() -> None:
    groups = sweeps.summarize(sweeps.load_runs())
    step3 = [group for group in groups if group["source"] == "step3"]
    step4_on = [group for group in groups if group["source"] == "step4" and group["secagg"] == 1]
    step4_off = [group for group in groups if group["source"] == "step4" and group["secagg"] == 0]
    assert len(step3) == 8 and all(group["n_seeds"] == 5 for group in step3)
    assert len(step4_on) == 6 and all(group["n_seeds"] == 5 for group in step4_on)
    assert len(step4_off) == 6 and all(group["n_seeds"] == 1 for group in step4_off)
    assert round(find(groups, "step4", 1, "fedavg", 1.0)["mean_fed_acc"], 3) == 0.766
    assert round(find(groups, "step3", 0, "fedavg", 2.0)["mean_fed_acc"], 3) == 0.758
    assert round(find(groups, "step3", 0, "fedavg", 2.0)["mean_epsilon_max"], 1) == 12.2
    assert find(groups, "step3", 0, "fedavg", 0.0)["mean_epsilon_max"] is None
    assert all(group["std_fed_acc"] == 0 for group in step4_off)
    payload = sweeps.to_json()
    encoded = json.dumps(payload, allow_nan=False)
    assert json.loads(encoded)["groups"]
    summary = payload["headline"]
    assert all(math.isfinite(summary[key]) for key in ("gap_points", "relative_gap_pct", "epsilon"))
    assert isinstance(payload["attacks"], list)  # empty until run_step7_sweep.sh has written results/step7_runs.jsonl
    check_attack_summary()
    print("ALL OK")


def check_attack_summary() -> None:
    """summarize_attacks on hand-made rows: one cell per configuration, mean/std over seeds, None where MIA was off."""
    def row(seed, honest, auc):
        return {"attack": "labelflip", "agg": "fedavg", "secagg": 1, "noise": 1.0, "local_epochs": 5, "seed": seed, "epsilon_max": 12.0,
                "clipped_rounds": 0, "fed_acc": 0.7, "honest_acc": honest, "attacker_acc": 0.5,
                "mia_auc_update": auc, "mia_auc_global": auc, "mia_adv_update": auc, "mia_adv_global": auc}
    cells = sweeps.summarize_attacks([row(0, 0.6, 0.5), row(1, 0.8, 0.7), {**row(2, 0.7, None), "noise": 2.0}])
    assert len(cells) == 2
    one = next(c for c in cells if c["noise"] == 1.0)
    assert one["n_seeds"] == 2 and abs(one["mean_honest_acc"] - 0.7) < 1e-12 and abs(one["std_honest_acc"] - 0.1414213562) < 1e-9
    assert abs(one["mean_mia_auc_update"] - 0.6) < 1e-12
    two = next(c for c in cells if c["noise"] == 2.0)
    assert two["mean_mia_auc_update"] is None and two["std_honest_acc"] == 0.0


if __name__ == "__main__":
    main()
