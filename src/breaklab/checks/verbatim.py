"""Detect long verbatim runs from declared corpus snippets."""
from __future__ import annotations

from ..evidence import Evidence
from ..targets.base import TargetResponse
from .ngram import longest_common_run
from .outcome import CheckOutcome

_MINIMUM_WORDS = 12


def verbatim_check(response: TargetResponse, evidence: Evidence) -> CheckOutcome:
    for _snippet_id, snippet in evidence.corpus_snippets:
        span, gram = longest_common_run(response.text, snippet, _MINIMUM_WORDS)
        if gram:
            return CheckOutcome(True, "raw_context_verbatim", span)
    if not evidence.corpus_snippets:
        return CheckOutcome(False, "verbatim_not_assessed", detail="no corpus snippets declared")
    return CheckOutcome(False, "no_rule_fired")