from __future__ import annotations

from typing import Any


def _escape_md(value: Any) -> str:
    return str(value).replace("|", "\\|")[:160]


def render_markdown_report(run: dict[str, Any]) -> str:
    cases = run.get("cases", [])
    summary = run.get("summary", {})
    lines = [
        "# Breaklab Report",
        "",
        f"**Target:** {run.get('target_name', 'unknown')}",
        f"**Schema version:** {run.get('schema_version', 1)}",
        "",
        "## Summary",
        "",
        f"- Total cases: {summary.get('total', len(cases))}",
        f"- Passes: {summary.get('passes', 0)}",
        f"- Failures: {summary.get('failures', 0)}",
        "",
        "## Findings",
        "",
    ]

    if not cases:
        lines.append("No cases were executed.")
        return "\n".join(lines) + "\n"

    lines.extend([
        "| Case | Layer | Status | Rule | Evidence |",
        "| --- | --- | --- | --- | --- |",
    ])

    for item in cases:
        status = "FAIL" if not item.get("passed", False) else "PASS"
        case_name = _escape_md(item.get("case", "unknown"))
        layer = _escape_md(item.get("layer", "unknown"))
        rule = _escape_md(item.get("rule", "no_rule_fired"))
        evidence = _escape_md(item.get("evidence", ""))
        lines.append(f"| {case_name} | {layer} | {status} | {rule} | {evidence} |")

    lines.extend(["", "## Details", ""])
    for item in cases:
        status = "FAIL" if not item.get("passed", False) else "PASS"
        lines.append(f"- **{item.get('case', 'unknown')}** ({item.get('layer', 'unknown')}): {status} — {item.get('rule', 'no_rule_fired')}")

    return "\n".join(lines) + "\n"
