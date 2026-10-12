# Breaklab

Breaklab is the Phase 0 skeleton for the red-team harness described in the project build plan.

This repository starts with the minimum viable structure for a reproducible LLM safety battery:

- a Typer CLI
- a mock target with no external API dependencies
- one deterministic attack case
- pytest coverage
- GitHub Actions CI

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
breaklab --help
breaklab attack --target mock://echo
```

If the `breaklab` command is not recognized in PowerShell on Windows, add the Python Scripts directory to your `PATH` or run it via:

```bash
python -m breaklab.cli --help
```

## Current status

This is the Phase 0 proof-of-life build. It is intentionally small and intentionally deterministic.

## License

MIT
