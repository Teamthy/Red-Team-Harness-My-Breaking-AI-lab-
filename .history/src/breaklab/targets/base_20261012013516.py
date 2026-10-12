from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class TargetResponse:
    text: str
    citations: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
    status_code: int = 200


class TargetAdapter(Protocol):
    def send(self, prompt: str, history: list[str] | None = None) -> TargetResponse:
        ...
