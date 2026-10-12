from breaklab.battery import Battery, default_cases
from breaklab.targets.mock_target import BrokenMockTarget, FixedMockTarget


def test_default_battery_has_full_case_registry() -> None:
    cases = default_cases()
    assert len(cases) >= 28
    layers = {case.layer for case in cases}
    assert {"injection", "exfiltration", "citation", "policy", "robustness", "poisoning"}.issubset(layers)


def test_broken_mock_fails_a_majority_of_cases() -> None:
    broken = BrokenMockTarget()
    result = Battery(default_cases()).run(broken)
    assert result["summary"]["failures"] >= 15


def test_fixed_mock_holds_the_registry() -> None:
    fixed = FixedMockTarget()
    result = Battery(default_cases()).run(fixed)
    assert result["summary"]["failures"] == 0
