from typer.testing import CliRunner

from breaklab.cli import app, attack_target


runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "attack" in result.stdout.lower()


def test_attack_target_mock_echo() -> None:
    result = attack_target("mock://echo")
    assert result["summary"]["total"] == 1
    assert result["summary"]["failures"] == 1
    assert result["cases"][0]["passed"] is False
    assert result["cases"][0]["rule"] == "system_prompt_echo"


def test_verify_mock_echo_fails() -> None:
    result = runner.invoke(app, ["verify", "--target", "mock://echo"])
    assert result.exit_code == 1
    assert "Verification failed" in result.stdout
