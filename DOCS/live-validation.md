# Live validation workflow

This document covers the external validation path for the harness when a real target is available.

## Scope

Use this workflow only against targets you own or have explicit written permission to test.

## Required inputs

You need:

- a real HTTP or SSE chat endpoint
- a valid target config file
- an attestation string that matches your permission
- the evidence block populated from the target's actual system prompt, served corpus snippets, retrieval IDs, canaries, sensitive data patterns, and applicable policy flags. Checks without declared evidence report `*_not_assessed`; they do not infer safety from prompt wording.
- a clean environment with the project installed

## Example HTTP validation

```bash
breaklab verify --config config/target_templates/openai_compatible_chat.yaml --report
```

For a local FastAPI app:

```bash
breaklab verify --config config/target_templates/fastapi_chat.yaml --report
```

## Example SSE validation

```bash
breaklab verify --config config/target_templates/fastapi_sse_chat.yaml --report
```

## Validation checklist for each real target

1. Confirm the target is permissioned and documented.
2. Update the config with the real `base_url`, `path`, headers, and auth values; source evidence from the target implementation rather than guessing.
3. Keep `judge_enabled` set to `false` unless you intentionally want supplemental judge evidence.
4. Run the verification path in a controlled environment.
5. Save the artifact and markdown output in a timestamped location.
6. Record whether the result is a pass, a fail, or a partial/inconclusive run; retain not-assessed checks as unknowns.
7. Summarize the result in a client-ready report or issue thread.

## Minimum external coverage target

Before a public release, run at least:

- one real JSON chat endpoint
- one real SSE streaming endpoint
- one fixed mock baseline
- one local Python target baseline

This is the minimum external pattern needed to prove the harness works across both JSON and streaming surfaces while keeping the default CI path deterministic.

## Optional broader coverage

Once a real target exists, add more app-specific templates in the same pattern:

- OpenAI-compatible endpoint
- FastAPI chat endpoint
- streaming endpoint with `event: data` and `done` semantics
- internal service wrapped behind a proxy or gateway

Keep each new config as a copy of a working template, not as a custom branch of the core logic.
