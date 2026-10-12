from typer.testing import CliRunner

from breaklab.cli import app, attack_target

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "attack" in result.stdout.lower()


def test_attack_target_mock_echo_holds_without_declared_evidence() -> None:
    result = attack_target("mock://echo")
    assert result["summary"]["total"] == 28
    assert result["summary"]["failures"] == 0


def test_verify_mock_echo_passes() -> None:
    result = runner.invoke(app, ["verify", "--target", "mock://echo"])
    assert result.exit_code == 0
    assert "Verification passed" in result.stdout


def test_new_target_template_scaffold(tmp_path) -> None:
    result = runner.invoke(app, ["new-target", "--template", "fastapi-sse", "--path", str(tmp_path / "example_target.yaml")])
    assert result.exit_code == 0, result.stdout
    contents = (tmp_path / "example_target.yaml").read_text(encoding="utf-8")
    assert "fastapi-chat-sse" in contents
    assert "response_mode: sse" in contents


def test_new_target_list_templates() -> None:
    result = runner.invoke(app, ["new-target", "--list-templates"])
    assert result.exit_code == 0, result.stdout
    assert "fastapi-sse" in result.stdout.lower()
    assert "openai-compatible" in result.stdout.lower()


def test_score_command_reports_weighted_score(tmp_path) -> None:
    artifact = tmp_path / "demo_run.json"
    artifact.write_text(
        '{"target_name": "demo", "cases": [{"case": "a", "passed": false, "severity": "critical"}, {"case": "b", "passed": true, "severity": "high"}], "summary": {"total": 2, "passes": 1, "failures": 1}}',
        encoding="utf-8",
    )
    result = runner.invoke(app, ["score", str(artifact)])
    assert result.exit_code == 0, result.stdout
    assert "42.857143" in result.stdout
