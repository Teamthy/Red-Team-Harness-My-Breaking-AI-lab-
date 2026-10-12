from math import isclose

from breaklab.scoring import compute_score


def test_compute_score_weights_failed_cases_by_severity() -> None:
    run = {
        "cases": [
            {"passed": False, "severity": "critical"},
            {"passed": False, "severity": "medium"},
            {"passed": True, "severity": "high"},
            {"passed": True, "severity": "medium"},
        ]
    }
    assert isclose(compute_score(run), 45.4545454545, rel_tol=1e-6)


def test_compute_score_is_hundred_for_all_passing_cases() -> None:
    run = {
        "cases": [
            {"passed": True, "severity": "critical"},
            {"passed": True, "severity": "high"},
        ]
    }
    assert compute_score(run) == 100.0
