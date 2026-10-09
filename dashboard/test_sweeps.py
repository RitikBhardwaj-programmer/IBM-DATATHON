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
    print("ALL OK")


if __name__ == "__main__":
    main()
