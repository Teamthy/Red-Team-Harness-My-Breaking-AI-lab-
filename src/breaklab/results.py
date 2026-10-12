from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CaseResult:
    case: str
    layer: str
    passed: bool
    rule: str = "no_rule_fired"
    evidence: str = ""
    severity: str = "medium"
    attempts: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "case": self.case,
            "layer": self.layer,
            "passed": self.passed,
            "rule": self.rule,
            "evidence": self.evidence,
            "severity": self.severity,
            "attempts": self.attempts,
        }


@dataclass(slots=True)
class RunResult:
    target_name: str
    cases: list[CaseResult] = field(default_factory=list)
    schema_version: int = 1

    def __post_init__(self) -> None:
        if not self.cases:
            self.cases = []

    def to_dict(self) -> dict[str, Any]:
        summary = {
            "total": len(self.cases),
            "passes": sum(1 for case in self.cases if case.passed),
            "failures": sum(1 for case in self.cases if not case.passed),
        }
        return {
            "schema_version": self.schema_version,
            "target_name": self.target_name,
            "cases": [case.to_dict() for case in self.cases],
            "summary": summary,
        }
