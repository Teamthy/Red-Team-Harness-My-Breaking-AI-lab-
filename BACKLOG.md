# Backlog

This file holds ideas that are useful but intentionally out of scope for the current v1 milestone. New ideas should be recorded here instead of adding scope to the active branch.

## High-priority next ideas

### 1. Local Python import target adapter
- Add a target adapter for Python modules and package-level functions.
- Use it to run the harness against locally imported app code instead of only HTTP and mock targets.
- Goal: support a local function-level safety gate for internal services.

### 2. Real-world target connectors
- Add a small library of target config templates for common app stacks.
- Include examples for OpenAI-compatible endpoints, FastAPI server wrappers, and SSE chat backends.
- Goal: lower the friction for non-expert users testing their own app.

### 3. Optional LLM judge backend
- Add a budget-capped judge mode behind a flag.
- Keep the default deterministic path as the primary source of truth.
- Goal: use an LLM only as supplemental evidence, never as the sole verdict source.

### 4. Poisoning corpus adapter
- Build a Project 2 adapter that can read or write a controlled poisoning corpus.
- Keep poisoning at NOT_ASSESSED until the corpus layer is validated.
- Goal: enable the poisoning layer with explicit permissions and storage controls.

### 5. Browser and UI-level probes
- Extend the harness to support browser automation and UI-level prompts.
- Keep behind a separate adapter and explicit permission checks.
- Goal: test front-end AI experiences without mixing them with API-level red-teaming.

## Medium-priority ideas

- Add richer score normalization and severity weighting.
- Add per-layer dashboards for case drift and false-positive tuning.
- Add support for custom case sets and target-specific expected results.
- Add a richer sample artifact library for client-facing demos.

## Deferred / out of scope for v1

- Agent and tool-call attacks
- Local Python import targets in the main harness path
- Multi-user dashboards or web UI
- garak / promptfoo integration as a first-class scanner adapter
- Browser-only or app-UI automation beyond the explicit target adapter model

## Notes

This backlog is intentionally separate from the active milestone work so the project stays deterministic, scoped, and shippable.
