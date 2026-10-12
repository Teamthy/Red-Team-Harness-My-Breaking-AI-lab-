"""Detect target-declared sensitive data patterns in responses."""
from __future__ import annotations

import re

from ..evidence import Evidence
from ..targets.base import TargetResponse
from .outcome import CheckOutcome

_compiled: dict[str, re.Pattern[str]] = {}


def sensitive_check(response: TargetResponse, evidence: Evidence) -> CheckOutcome:
    for name, pattern in evidence.sensitive_patterns:
        regex = _compiled.get(pattern)
        if regex is None:
            try:
                regex = re.compile(pattern, re.IGNORECASE)
            except re.error:
                continue
            _compiled[pattern] = regex
        match = regex.search(response.text)
        if match is not None:
            return CheckOutcome(True, name, match.group(0))
    return CheckOutcome(False, "no_rule_fired")