# Backlog

This file holds ideas intentionally out of scope for the completed local v1.0 implementation. New ideas belong here instead of widening the release scope.

## Already built

- Evidence-driven echo, canary, verbatim, sensitive-pattern, citation, and opt-in policy checks.
- 28-case battery with independent k attempts and multi-turn histories.
- Broken, fixed, and harmless mock targets; anonymized fixture provenance and regression tests.
- HTTP JSON/SSE and local Python target adapters, report generation, scoring, and diff mode.
- Target templates, permission attestation, and CI smoke coverage.

## High-priority next ideas

### 1. Optional LLM judge backend
- Add a budget-capped judge mode behind a flag.
- Keep the default deterministic path as the primary source of truth.
- Goal: use an LLM only as supplemental evidence, never as the sole verdict source.

### 2. Poisoning corpus adapter
- Build a Project 2 adapter that can read or write a controlled poisoning corpus.
- Keep poisoning at NOT_ASSESSED until the corpus layer is validated.
- Goal: enable the poisoning layer with explicit permissions and storage controls.

### 3. Gate pattern narrowing
- The bundled mock gate is intentionally broad and can refuse benign list/source requests.
- Narrow the intent patterns and add explicit false-positive fixtures before using a similar gate on high-traffic routes.

### 4. Browser and UI-level probes
- Extend the harness to support browser automation and UI-level prompts.
- Keep behind a separate adapter and explicit permission checks.
- Goal: test front-end AI experiences without mixing them with API-level red-teaming.

## Medium-priority ideas

- Add custom case sets and target-specific expected results as first-class files.
- Add per-layer dashboards for case drift and false-positive tuning.
- Add a richer sample artifact library for client-facing demos.
- Add a Windows CI lane alongside Ubuntu.

## Deferred / out of scope for v1

- Agent and tool-call attacks
- Real-target live validation until authorized targets and evidence are supplied
- Multi-user dashboards or web UI
- garak / promptfoo integration as a first-class scanner adapter
- Browser-only or app-UI automation beyond the explicit target adapter model

## Notes

This backlog is intentionally separate from the active milestone work so the project stays deterministic, scoped, and shippable.
