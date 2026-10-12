"""Independent k attempts and accumulated multi-turn history."""
from __future__ import annotations

from collections.abc import Sequence

from breaklab.battery import Battery, CaseDefinition
from breaklab.evidence import Evidence
from breaklab.targets.base import TargetResponse


class _CounterTarget:
    def __init__(self, break_on: int | None = None) -> None:
        self.evidence = Evidence(canaries=("ALPINE-FERN-DELTA-9",))
        self.break_on = break_on
        self.sends = 0
        self.histories: list[list[str]] = []

    def send(self, prompt: str, history: Sequence[str] | None = None) -> TargetResponse:
        self.sends += 1
        self.histories.append(list(history or []))
        text = "ALPINE-FERN-DELTA-9" if self.sends == self.break_on else "I can help with your question."
        return TargetResponse(text=text)


CASE = CaseDefinition("probe", "injection", "high", ("probe?",), ("canary",))


def test_k_records_the_attempt_that_breaks() -> None:
    item = Battery([CASE]).run(_CounterTarget(break_on=2), k=3)["cases"][0]
    assert item["passed"] is False and item["attempts"] == 2


def test_k_records_all_attempts_when_held() -> None:
    target = _CounterTarget()
    item = Battery([CASE]).run(target, k=3)["cases"][0]
    assert item["passed"] is True and item["attempts"] == 3
    assert target.sends == 3


def test_k_defaults_to_one_attempt() -> None:
    target = _CounterTarget()
    Battery([CASE]).run(target)
    assert target.sends == 1


def test_history_accumulates_between_turns() -> None:
    case = CaseDefinition("mt", "injection", "high", ("t1", "t2", "t3"), ("canary",))
    target = _CounterTarget()
    Battery([case]).run(target)
    assert target.histories == [[], ["t1"], ["t1", "t2"]]


def test_history_resets_for_each_attempt() -> None:
    case = CaseDefinition("mt", "injection", "high", ("t1", "t2"), ("canary",))
    target = _CounterTarget()
    Battery([case]).run(target, k=2)
    assert target.histories == [[], ["t1"], [], ["t1"]]