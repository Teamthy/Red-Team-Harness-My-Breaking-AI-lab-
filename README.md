# Breaklab

Breaklab is a deterministic red-team harness for LLM apps. It runs a repeatable battery of safety checks against a target, records artifact-level evidence, and produces a report you can hand to a client or gate in CI.

This repo already includes the working core: mock targets, real HTTP and SSE target support, battery execution, YAML config loading, markdown reporting, and before/after diff generation.

## What it does

- Runs a fixed battery of adversarial cases against a target
- Works against mock targets for zero-cost CI validation
- Supports HTTP JSON endpoints and SSE streaming chat endpoints
- Captures one artifact record per prompt attempt
- Produces a pass/fail summary and a markdown client report
- Supports diff mode to compare a broken run against a fixed run

## Quick start

From the repo root:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
breaklab --help
```

Run the built-in mock target:

```bash
breaklab attack --target mock://echo
breaklab attack --target mock://broken
breaklab attack --target mock://fixed
```

Verify the target against the current battery:

```bash
breaklab verify --target mock://fixed
breaklab verify --target mock://broken
```

Generate a markdown report:

```bash
breaklab verify --target mock://fixed --report
```

Compare a broken run to a fixed run and emit a client-ready markdown diff:

```bash
breaklab diff artifacts/20261012T013253Z-mock_broken.jsonl artifacts/20261012T013302Z-mock_fixed.jsonl -o examples/mock_diff_report.md
```

## Real target configuration

Scaffold a config:

```bash
breaklab new-target --path config/example_target.yaml
```

Example YAML:

```yaml
target:
  name: my-http-chat
  attestation: "I own this system or have written permission to test it."
  type: http
  base_url: https://api.example.com
  path: /api/chat
  method: POST
  body_template: '{"question": "{prompt}", "history": []}'
  headers:
    Authorization: "Bearer {API_KEY}"
    Content-Type: application/json
  timeout: 45.0
options:
  k: 1
  judge_enabled: false
  layers:
    - injection
    - exfiltration
```

Then run it with:

```bash
breaklab attack --config config/example_target.yaml
breaklab verify --config config/example_target.yaml --report
```

## Built-in demo targets

The project ships with deterministic mock targets that are useful for local development and CI:

- `mock://echo` — harmless echo target
- `mock://broken` — intentionally weak target that fails the battery
- `mock://fixed` — hardened target that passes the battery

These are the regression anchors for the harness itself.

## Target templates

The project now includes a small library of real-world target configs for common app patterns:

- `config/target_templates/openai_compatible_chat.yaml` — OpenAI-compatible JSON chat API
- `config/target_templates/fastapi_chat.yaml` — local FastAPI JSON chat endpoint
- `config/target_templates/fastapi_sse_chat.yaml` — local FastAPI SSE streaming endpoint

Use them as a starting point, then replace the example `base_url`, auth values, and routes with the target you own or have explicit permission to test.

```bash
breaklab verify --config config/target_templates/openai_compatible_chat.yaml
breaklab verify --config config/target_templates/fastapi_chat.yaml
breaklab verify --config config/target_templates/fastapi_sse_chat.yaml --report
```

## Sample artifacts

Two example markdown reports are committed under the `examples/` directory:

- `examples/sample_report_broken.md`
- `examples/sample_report_fixed.md`

These demonstrate the before/after story for a broken target and the repaired target.

## Release readiness

The project is now structured for a clean public handoff:

- version metadata is already present in `pyproject.toml`
- the repo has a working CI smoke path in `.github/workflows/ci.yml`
- the harness already has a documented mock and Python-based regression lane
- the diff report and sample artifacts are committed for client-facing review

See [DOCS/release-readiness.md](DOCS/release-readiness.md) for the full release checklist.

## Live validation and public release

When you have a real target ready, use the external validation checklist in [DOCS/live-validation.md](DOCS/live-validation.md) and the release flow in [DOCS/release-readiness.md](DOCS/release-readiness.md).

This keeps the external validation path separate from the deterministic CI path while still giving you a concrete public-release checklist.

## Project status

This repository is in a working, verified state with the core functionality in place:

- Typer CLI
- HTTP + SSE target adapters
- YAML config support
- Run artifact capture
- Markdown reporting
- Diff report generation
- Golden mock regression checks

## Ethics and permissions

Breaklab is explicitly designed for authorized testing only. Every target config includes an attestation field and the project expects the user to confirm they own the target or have written permission to exercise it.

## License

MIT
