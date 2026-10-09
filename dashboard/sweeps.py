"""Load and summarize the DP and secure-aggregation sweep results."""

import json
from pathlib import Path
from statistics import mean, stdev
from typing import Any


Run = dict[str, Any]
Group = dict[str, Any]


def load_runs(results_dir: str | Path = "results") -> list[Run]:
    """Load step 3 and 4 JSONL files, adding their source metadata."""
    runs: list[Run] = []
    for source in ("step3", "step4"):
        path = Path(results_dir) / f"{source}_runs.jsonl"
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    run = json.loads(line)
                    run["source"] = source
                    run["secagg"] = 0 if source == "step3" else run["secagg"]
                    runs.append(run)
    return runs


def _sample_std(values: list[float]) -> float:
    return 0.0 if len(values) == 1 else stdev(values)


def _mean_or_none(values: list[float | None]) -> float | None:
    return None if any(value is None for value in values) else mean(values)  # type: ignore[arg-type]


def summarize(runs: list[Run]) -> list[Group]:
    """Group runs by sweep configuration and calculate their summary values."""
    buckets: dict[tuple[str, int, str, float], list[Run]] = {}
    for run in runs:
        key = (run["source"], run["secagg"], run["strategy"], run["noise"])
        buckets.setdefault(key, []).append(run)

    groups: list[Group] = []
    for (source, secagg, strategy, noise), members in sorted(buckets.items()):
        per_hospital = list(zip(*(run["fed_per_hospital_acc"] for run in members)))
        group: Group = {
            "source": source,
            "secagg": secagg,
            "strategy": strategy,
            "noise": noise,
            "n_seeds": len(members),
            "mean_fed_acc": mean(run["fed_acc"] for run in members),
            "std_fed_acc": _sample_std([run["fed_acc"] for run in members]),
            "mean_fed_f1": mean(run["fed_f1"] for run in members),
            "std_fed_f1": _sample_std([run["fed_f1"] for run in members]),
            "mean_central_acc": mean(run["central_acc"] for run in members),
            "std_central_acc": _sample_std([run["central_acc"] for run in members]),
            "mean_epsilon_max": _mean_or_none([run["epsilon_max"] for run in members]),
            "mean_fed_per_hospital_acc": [mean(scores) for scores in per_hospital],
        }
        if source == "step4":
            group["mean_sec_per_round"] = mean(run["sec_per_round"] for run in members)
        groups.append(group)
    return groups


def _finite(value: object) -> bool:
    return isinstance(value, (int, float)) and value == value and abs(value) != float("inf")


def _json_safe(value: Any) -> Any:
    """Replace non-finite floats with JSON's null equivalent."""
    if isinstance(value, float) and not _finite(value):
        return None
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    return value


def headline(groups: list[Group]) -> dict[str, Any]:
    """Compare the most private (lowest finite epsilon) group with its baseline.

    Picking the lowest epsilon, not the highest accuracy, keeps the headline honest:
    it reports the privacy level we would defend, not the best-looking number.
    Ties on epsilon go to the more accurate strategy.
    """
    private = [group for group in groups if _finite(group["mean_epsilon_max"])]
    secured = [group for group in private if group["secagg"] == 1]
    candidates = secured or [group for group in private if group["source"] == "step3"]
    if not candidates:
        return {"gap_points": None, "relative_gap_pct": None, "epsilon": None, "source": None}
    best = min(candidates, key=lambda group: (group["mean_epsilon_max"], -group["mean_fed_acc"]))
    central, fed = best["mean_central_acc"], best["mean_fed_acc"]
    return {
        "gap_points": (central - fed) * 100,
        "relative_gap_pct": (central - fed) / central * 100 if central else None,
        "epsilon": best["mean_epsilon_max"],
        "source": (
            f"{best['source']}_runs.jsonl: secagg={best['secagg']}, "
            f"strategy={best['strategy']}, noise={best['noise']}"
        ),
    }


def to_json(results_dir: str | Path = "results") -> dict[str, Any]:
    """Return loaded runs, grouped summaries, and headline values for an API."""
    runs = load_runs(results_dir)
    groups = summarize(runs)
    return _json_safe({"runs": runs, "groups": groups, "headline": headline(groups)})
