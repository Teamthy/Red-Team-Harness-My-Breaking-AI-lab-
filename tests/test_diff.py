from __future__ import annotations

from breaklab.reporting.diff import render_diff_report


def test_render_diff_report_highlights_case_status_changes() -> None:
    before = {
        "target_name": "broken-target",
        "cases": [
            {"case": "prompt_leak", "layer": "injection", "passed": False, "rule": "system_prompt_echo"},
            {"case": "safe_case", "layer": "policy", "passed": True, "rule": "no_rule_fired"},
        ],
    }
    after = {
        "target_name": "fixed-target",
        "cases": [
            {"case": "prompt_leak", "layer": "injection", "passed": True, "rule": "no_rule_fired"},
            {"case": "safe_case", "layer": "policy", "passed": True, "rule": "no_rule_fired"},
        ],
    }

    report = render_diff_report(before, after)

    assert "# Before/After Diff" in report
    assert "prompt_leak" in report
    assert "FAIL -> PASS" in report
    assert "Summary" in report
