from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CheckOutcome:
    fired: bool
    rule: str
    span: str = ""
    detail: str = ""