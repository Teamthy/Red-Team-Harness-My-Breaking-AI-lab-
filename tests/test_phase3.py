from __future__ import annotations

from pathlib import Path

import yaml

from breaklab.reporting.markdown import render_markdown_report
from breaklab.results import CaseResult, RunResult


def test_render_markdown_report_includes_failures_and_summary() -> None:
    run = RunResult(
        target_name="mock://broken",
        cases=[
            CaseResult(case="prompt_leak", layer="injection", passed=False, rule="system_prompt_echo", evidence="system prompt leaked"),
            CaseResult(case="safe_case", layer="policy", passed=True, rule="no_rule_fired", evidence="safe answer"),
        ],
    )

    markdown = render_markdown_report(run.to_dict())
    assert "# Breaklab Report" in markdown
    assert "prompt_leak" in markdown
    assert "Summary" in markdown
    assert "2" in markdown


def test_verify_expected_yaml_matches_results(tmp_path: Path) -> None:
    expectations_path = tmp_path / "expectations.yaml"
    expectations_path.write_text(
        yaml.safe_dump({
            "expected": [
                {"case": "prompt_leak", "pass": False},
                {"case": "safe_case", "pass": True},
            ]
        }),
        encoding="utf-8",
    )

    run = RunResult(
        target_name="mock://broken",
        cases=[
            CaseResult(case="prompt_leak", layer="injection", passed=False, rule="system_prompt_echo", evidence="leak"),
            CaseResult(case="safe_case", layer="policy", passed=True, rule="no_rule_fired", evidence="safe"),
        ],
    )

    expected = yaml.safe_load(expectations_path.read_text(encoding="utf-8"))
    matched = all(
        any(item["case"] == case.case and item["pass"] == case.passed for item in expected["expected"])
        for case in run.cases
    )

    assert matched is True
