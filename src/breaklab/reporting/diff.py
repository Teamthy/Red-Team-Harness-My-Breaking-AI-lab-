from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _normalize_cases(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        cases = payload.get("cases", [])
        if isinstance(cases, list):
            return [item for item in cases if isinstance(item, dict)]

    raise ValueError("Run payload must be a dict or list of case results.")


def _summary_for_cases(cases: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "total": len(cases),
        "passes": sum(1 for item in cases if bool(item.get("passed", False))),
        "failures": sum(1 for item in cases if not bool(item.get("passed", False))),
    }


def _load_run_file(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    raw = file_path.read_text(encoding="utf-8")
    if not raw.strip():
        return {"target_name": file_path.stem, "cases": [], "summary": {"total": 0, "passes": 0, "failures": 0}}

    if file_path.suffix.lower() == ".jsonl":
        rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
        return {
            "target_name": file_path.stem,
            "cases": rows,
            "summary": _summary_for_cases(rows),
        }

    data = json.loads(raw)
    if isinstance(data, list):
        return {"target_name": file_path.stem, "cases": data, "summary": _summary_for_cases(data)}
    if isinstance(data, dict):
        cases = _normalize_cases(data)
        summary = data.get("summary") or _summary_for_cases(cases)
        return {
            "target_name": data.get("target_name", file_path.stem),
            "cases": cases,
            "summary": summary,
        }

    raise ValueError(f"Unsupported run payload in {path!s}.")


def render_diff_report(before: dict[str, Any], after: dict[str, Any]) -> str:
    before_cases = _normalize_cases(before)
    after_cases = _normalize_cases(after)
    before_map = {str(item.get("case", "")): item for item in before_cases if item.get("case")}
    after_map = {str(item.get("case", "")): item for item in after_cases if item.get("case")}

    all_cases = sorted(set(before_map) | set(after_map))
    before_summary = before.get("summary") or _summary_for_cases(before_cases)
    after_summary = after.get("summary") or _summary_for_cases(after_cases)

    lines = [
        "# Before/After Diff",
        "",
        f"**Before target:** {before.get('target_name', 'unknown')}",
        f"**After target:** {after.get('target_name', 'unknown')}",
        "",
        "## Summary",
        "",
        f"- Before passes: {before_summary.get('passes', 0)}",
        f"- Before failures: {before_summary.get('failures', 0)}",
        f"- After passes: {after_summary.get('passes', 0)}",
        f"- After failures: {after_summary.get('failures', 0)}",
        "",
        "## Changes",
        "",
        "| Case | Layer | Before | After | Delta |",
        "| --- | --- | --- | --- | --- |",
    ]

    changed = 0
    for case_name in all_cases:
        before_item = before_map.get(case_name, {})
        after_item = after_map.get(case_name, {})
        before_state = "PASS" if bool(before_item.get("passed", False)) else "FAIL"
        after_state = "PASS" if bool(after_item.get("passed", False)) else "FAIL"
        layer = after_item.get("layer") or before_item.get("layer") or "unknown"
        delta = f"{before_state} -> {after_state}"
        if before_state != after_state:
            changed += 1
        lines.append(f"| {case_name} | {layer} | {before_state} | {after_state} | {delta} |")

    lines.extend(["", f"- Changed cases: {changed}", ""])
    return "\n".join(lines) + "\n"
