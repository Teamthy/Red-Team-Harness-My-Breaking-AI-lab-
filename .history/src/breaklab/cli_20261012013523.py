from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .battery import Battery
from .targets.mock_target import MockEchoTarget

app = typer.Typer(add_completion=False, no_args_is_help=True)


def attack_target(target_name: str = "mock://echo", layer: str | None = None, k: int = 1) -> dict[str, object]:
    if not target_name.startswith("mock://"):
        raise typer.BadParameter(
            f"Unsupported target '{target_name}'. Only mock:// targets are available in this Phase 0 scaffold."
        )

    target = MockEchoTarget(target_name)
    battery = Battery()
    if layer:
        battery = Battery([case for case in battery.cases if case.layer == layer])

    if k > 1:
        # Phase 0 intentionally keeps single-attempt semantics.
        # The same structure can later be extended to repeated sampling.
        pass

    return battery.run(target)


@app.callback()
def main() -> None:
    """Breaklab CLI entry point."""


@app.command()
def attack(
    target: str = typer.Option("mock://echo", "--target", "-t", help="Target adapter to run."),
    layer: Annotated[str | None, typer.Option("--layer")] = None,
    k: int = typer.Option(1, "--k", min=1),
) -> None:
    """Run the battery against a target."""
    result = attack_target(target, layer=layer, k=k)
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
) -> None:
    """Verify the target passes the current battery and exit with a failing code on breakage."""
    result = attack_target(target, layer=layer, k=k)
    if result["summary"]["failures"] > 0:
        typer.secho(
            f"Verification failed: {result['summary']['failures']} case(s) broke.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    typer.secho("Verification passed: all checked cases held.", fg=typer.colors.GREEN)


@app.command()
def diff() -> None:
    """Placeholder for before/after diff mode; to be implemented in later phases."""
    typer.echo("Diff mode is not implemented in this Phase 0 skeleton.")


@app.command()
def new_target() -> None:
    """Placeholder for scaffolding a new target config."""
    typer.echo("Target scaffolding is not implemented in this Phase 0 skeleton.")


if __name__ == "__main__":
    app()
