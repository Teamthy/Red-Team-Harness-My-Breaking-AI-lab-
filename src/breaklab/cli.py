from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import typer
import yaml
from rich.console import Console
from rich.table import Table

from .artifacts import ArtifactWriter
from .battery import Battery
from .config import RunConfig, TargetConfig, load_run_config
from .reporting.diff import _load_run_file, render_diff_report
from .reporting.markdown import render_markdown_report
from .results import CaseResult, RunResult
from .targets.http_target import HTTPTarget
from .targets.mock_target import BrokenMockTarget, FixedMockTarget, MockEchoTarget
from .targets.python_target import PythonTarget

app = typer.Typer(add_completion=False, no_args_is_help=True)


def _attestation_path(base_dir: str | Path | None = None) -> Path:
    root = Path(base_dir) if base_dir is not None else Path.cwd()
    return root / ".breaklab" / "attestations.json"


def _load_attestations(base_dir: str | Path | None = None) -> dict[str, str]:
    path = _attestation_path(base_dir)
    if not path.exists():
        return {}
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    return {str(key): str(value) for key, value in payload.items() if isinstance(value, str)}


def get_attestation(target_name: str, base_dir: str | Path | None = None) -> str | None:
    return _load_attestations(base_dir).get(target_name)


def set_attestation(target_name: str, attestation: str, base_dir: str | Path | None = None) -> str:
    store = _load_attestations(base_dir)
    store[target_name] = attestation.strip()
    path = _attestation_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(store, sort_keys=True), encoding="utf-8")
    return store[target_name]


def ensure_attestation(target_name: str, attestation: str | None = None, base_dir: str | Path | None = None) -> str | None:
    existing = get_attestation(target_name, base_dir=base_dir)
    if existing:
        return existing
    if attestation is not None:
        return set_attestation(target_name, attestation, base_dir=base_dir)
    return None


def _build_target(target: str | TargetConfig) -> Any:
    if isinstance(target, TargetConfig):
        if target.target_type == "http":
            return HTTPTarget(
                base_url=target.base_url or target.name,
                path=target.path,
                method=target.method,
                body_template=target.body_template,
                headers=target.headers,
                timeout=target.timeout,
                stream=target.stream,
                response_mode=target.response_mode,
                sse_options=target.sse,
            )
        if target.target_type == "python":
            return PythonTarget(target.name or f"python://{target.module}:{target.callable_name}")
        target_name = target.name
    else:
        target_name = target

    if target_name.startswith("python://") or ":" in target_name and target_name.split(":", 1)[0].replace(".", "").replace("_", "").isalnum():
        try:
            return PythonTarget(target_name)
        except (ImportError, AttributeError, ValueError, TypeError):
            pass

    if target_name == "mock://echo":
        return MockEchoTarget(target_name)
    if target_name == "mock://broken":
        return BrokenMockTarget(target_name)
    if target_name == "mock://fixed":
        return FixedMockTarget(target_name)
    if target_name.startswith("mock://"):
        return MockEchoTarget(target_name)
    if target_name.startswith(("http://", "https://")):
        return HTTPTarget(base_url=target_name)
    raise typer.BadParameter(
        f"Unsupported target '{target_name}'. Supported targets include mock://* and http(s)://* URLs."
    )


def attack_target(
    target_name: str = "mock://echo",
    layer: str | None = None,
    k: int = 1,
    config_path: str | None = None,
    judge_enabled: bool = False,
    attestation: str | None = None,
) -> dict[str, Any]:
    config: RunConfig | None = None
    if config_path is not None:
        config = load_run_config(config_path)
        target_name = config.target.base_url or config.target.name
        if layer is None and config.layers:
            layer = ",".join(config.layers)
        if k == 1:
            k = config.k
        if judge_enabled is False:
            judge_enabled = config.judge_enabled
        if attestation is None and config.target.attestation:
            attestation = config.target.attestation

    if attestation:
        ensure_attestation(target_name, attestation)

    target = _build_target(config.target if config is not None else target_name)
    battery = Battery()
    if layer:
        if "," in layer:
            selected = {item.strip() for item in layer.split(",") if item.strip()}
            battery = Battery([case for case in battery.cases if case.layer in selected])
        else:
            battery = Battery([case for case in battery.cases if case.layer == layer])

    run_result = battery.run(target, judge_enabled=judge_enabled)
    cases = [
        CaseResult(
            case=item["case"],
            layer=item["layer"],
            passed=bool(item["passed"]),
            rule=str(item["rule"]),
            evidence=str(item["evidence"]),
            severity=str(item["severity"]),
            attempts=int(item["attempts"]),
        )
        for item in run_result["cases"]
    ]
    result = RunResult(target_name=target_name, cases=cases)
    artifact_dir = Path("artifacts")
    ArtifactWriter(artifact_dir).write_run(result)
    return result.to_dict()


def verify_expectations(result: dict[str, Any], expectation_path: str | Path) -> bool:
    content = Path(expectation_path).read_text(encoding="utf-8")
    data = yaml.safe_load(content) or {}
    expected = data.get("expected")
    if expected is None:
        raise typer.BadParameter(f"No 'expected' list found in {expectation_path}.")

    result_map = {case["case"]: case["passed"] for case in result.get("cases", [])}
    for item in expected:
        case_name = item.get("case")
        if case_name not in result_map:
            raise typer.BadParameter(f"Expected case '{case_name}' was not in the run results.")
        if result_map[case_name] != bool(item.get("pass")):
            return False
    return True


@app.callback()
def main() -> None:
    """Breaklab CLI entry point."""


@app.command()
def attack(
    target: str = typer.Option("mock://echo", "--target", "-t", help="Target adapter to run."),
    layer: Annotated[str | None, typer.Option("--layer")] = None,
    k: int = typer.Option(1, "--k", min=1),
    config: str | None = typer.Option(None, "--config", "-c", help="Path to a YAML run config file."),
    judge: bool = typer.Option(False, "--judge", help="Enable the optional judge as a secondary unsafe-response check."),
    attestation: str | None = typer.Option(None, "--attestation", "-a", help="One-line permission statement to store for this target."),
) -> None:
    """Run the battery against a target."""
    result = attack_target(target, layer=layer, k=k, config_path=config, judge_enabled=judge, attestation=attestation)
    console = Console()
    table = Table(title=f"Breaklab attack: {target}")
    table.add_column("Case", style="cyan")
    table.add_column("Layer", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Rule", style="yellow")

    for item in result["cases"]:
        status = "FAIL" if not item["passed"] else "PASS"
        table.add_row(item["case"], item["layer"], status, item["rule"])

    console.print(table)
    console.print(
        f"Summary: {result['summary']['passes']} pass, {result['summary']['failures']} fail"
    )


@app.command()
def verify(
    target: str = typer.Option("mock://echo", "--target", "-t", help="Target adapter to verify."),
    layer: Annotated[str | None, typer.Option("--layer")] = None,
    k: int = typer.Option(1, "--k", min=1),
    expected: str | None = typer.Option(None, "--expected", "-e", help="YAML file with expected pass/fail per case."),
    report: bool = typer.Option(False, "--report", help="Emit a markdown report for the verification run."),
    config: str | None = typer.Option(None, "--config", "-c", help="Path to a YAML run config file."),
    judge: bool = typer.Option(False, "--judge", help="Enable the optional judge as a secondary unsafe-response check."),
    attestation: str | None = typer.Option(None, "--attestation", "-a", help="One-line permission statement to store for this target."),
) -> None:
    """Verify the target passes the current battery and exit with a failing code on breakage."""
    result = attack_target(target, layer=layer, k=k, config_path=config, judge_enabled=judge, attestation=attestation)

    if expected is not None and not verify_expectations(result, expected):
        typer.secho("Verification failed: expected results do not match the run.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if result["summary"]["failures"] > 0:
        typer.secho(
            f"Verification failed: {result['summary']['failures']} case(s) broke.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    if report:
        typer.echo(render_markdown_report(result))

    typer.secho("Verification passed: all checked cases held.", fg=typer.colors.GREEN)


@app.command()
def diff(
    before: str = typer.Argument(..., help="Path to the pre-change run artifact or JSON result file."),
    after: str = typer.Argument(..., help="Path to the post-change run artifact or JSON result file."),
    output: str | None = typer.Option(None, "--output", "-o", help="Optional path to write the markdown diff report."),
) -> None:
    """Render a before/after markdown diff report from two run artifacts."""
    before_payload = _load_run_file(before)
    after_payload = _load_run_file(after)
    report = render_diff_report(before_payload, after_payload)

    if output is not None:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(report, encoding="utf-8")

    typer.echo(report)


@app.command()
def new_target(path: str = typer.Option("config/example_target.yaml", "--path", "-p", help="Where to write the target config template.")) -> None:
    """Scaffold a new target config YAML file."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(TargetConfig.template_yaml(), encoding="utf-8")
    typer.secho(f"Target config scaffold written to {output}", fg=typer.colors.GREEN)


@app.command()
def attest(
    target: str = typer.Argument(..., help="Target name or URL to store the attestation for."),
    attestation: str | None = typer.Option(None, "--attestation", "-a", help="One-line permission statement to save."),
) -> None:
    """Persist a one-line attestation for a target."""
    finalized = attestation or get_attestation(target)
    if finalized is None:
        raise typer.BadParameter("An attestation string is required. Pass --attestation or store one first.")
    stored = set_attestation(target, finalized)
    typer.secho(f"Saved attestation for {target}: {stored}", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
