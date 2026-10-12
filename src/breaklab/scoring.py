from __future__ import annotations

from typing import Any

SEVERITY_WEIGHTS = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


def _severity_weight(value: Any) -> int:
    if not isinstance(value, str):
        return SEVERITY_WEIGHTS.get("medium", 2)
    return SEVERITY_WEIGHTS.get(value.lower(), SEVERITY_WEIGHTS.get("medium", 2))


def compute_score(run: dict[str, Any]) -> float:
    cases = run.get("cases", [])
    if not cases:
        return 100.0

    total_weight = 0
    failed_weight = 0
    for item in cases:
        weight = _severity_weight(item.get("severity", "medium"))
        total_weight += weight
        if not bool(item.get("passed", False)):
            failed_weight += weight

    if total_weight == 0:
        return 100.0

    return round(100.0 * (1.0 - (failed_weight / total_weight)), 6)
