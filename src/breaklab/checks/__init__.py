"""Deterministic checks dispatched by name from battery cases."""
from __future__ import annotations

from collections.abc import Callable

from ..evidence import Evidence
from ..targets.base import TargetResponse
from .canary import canary_check
from .citation import citation_check
from .echo import echo_check
from .outcome import CheckOutcome
from .policy import policy_check
from .sensitive import sensitive_check
from .verbatim import verbatim_check

Check = Callable[[TargetResponse, Evidence], CheckOutcome]
CHECKS: dict[str, Check] = {
    "canary": canary_check,
    "echo": echo_check,
    "verbatim": verbatim_check,
    "sensitive": sensitive_check,
    "citation": citation_check,
    "policy": policy_check,
}

__all__ = [
    "CHECKS", "CheckOutcome", "Evidence", "TargetResponse", "canary_check",
    "citation_check", "echo_check", "policy_check", "sensitive_check", "verbatim_check",
]