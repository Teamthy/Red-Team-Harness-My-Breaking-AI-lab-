from breaklab.battery import Battery
from breaklab.targets.mock_target import BrokenMockTarget, FixedMockTarget


def test_broken_mock_fails_27_cases_and_obfuscated_case_holds() -> None:
    result = Battery().run(BrokenMockTarget())
    assert result["summary"] == {"total": 28, "failures": 27, "passes": 1}
    held = [case["case"] for case in result["cases"] if case["passed"]]
    assert held == ["obfuscated_prompt"]


def test_fixed_mock_holds_all_cases() -> None:
    result = Battery().run(FixedMockTarget())
    assert result["summary"] == {"total": 28, "failures": 0, "passes": 28}