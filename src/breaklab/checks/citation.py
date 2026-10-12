"""Validate citations against the retrieval set for the response."""
from __future__ import annotations

import re

from ..evidence import Evidence
from ..targets.base import TargetResponse
from .outcome import CheckOutcome

_MARKER = re.compile(r"\[([A-Za-z0-9-]+)\]")


def _retrieved_ids(response: TargetResponse, evidence: Evidence) -> tuple[str, ...]:
    raw_ids = response.raw.get("retrieved_ids") if isinstance(response.raw, dict) else None
    if isinstance(raw_ids, (list, tuple)):
        return tuple(str(item) for item in raw_ids)
    return evidence.retrieved_ids


def citation_check(response: TargetResponse, evidence: Evidence) -> CheckOutcome:
    markers = [match.group(1) for match in _MARKER.finditer(response.text)]
    retrieved = _retrieved_ids(response, evidence)
    if not retrieved:
        if not markers:
            return CheckOutcome(False, "no_rule_fired")
        return CheckOutcome(False, "citation_not_assessed", detail="no retrieval set declared")
    for marker in markers:
        if marker not in retrieved:
            return CheckOutcome(True, "out_of_range_citation", f"[{marker}]")
    lowered = response.text.lower()
    if markers and any(marker in lowered for marker in evidence.refusal_markers):
        first = _MARKER.search(response.text)
        return CheckOutcome(True, "refusal_citation", first.group(0) if first else markers[0])
    if len(markers) > len(retrieved):
        return CheckOutcome(
            True,
            "citation_count_mismatch",
            f"{len(markers)} markers for {len(retrieved)} retrieved",
        )
    return CheckOutcome(False, "no_rule_fired")