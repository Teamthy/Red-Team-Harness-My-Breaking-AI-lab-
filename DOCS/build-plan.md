# Project 1 Build Plan: the Red-Team Harness ("breaklab")

- Status: PLANNED, not started. Written 2026-10-12.
- Owner: Timothy (solo, part-time while running the empire).
- Estimate: 6 weeks part-time (about 12 focused hours per week) to public v1.0. If real bandwidth is 6 hours per week, the same phases stretch to 8 to 10 weeks. Phase boundaries are the flexibility point, not the case count.
- What it is: one command, a reproducible red-team battery against a running LLM app, with deterministic verdicts, a client-ready report, and a regression mode that plugs into CI.
- Positioning line (README and LinkedIn): "A red-team harness that turns 'is my LLM app safe?' into a pass/fail table, a client report, and a CI gate."
- Why it is different from garak and promptfoo: it scores design, not prompt templates. It emits machine-readable results plus a report you hand to the client, and every verdict cites the rule that fired and the exact evidence span. Use garak and promptfoo as external scanners later; the harness is the scoring and the story.

---

## 1. Product decisions (locked; change only with a note in section 9)

- D1. Deterministic-first verdicts. Every break must cite the rule that fired and the exact evidence span in the response. An LLM judge is optional, off by default, and never the sole evidence for a verdict.
- D2. v1 targets: HTTP chat endpoints (plain JSON and SSE streaming) plus a built-in mock target so the harness's own CI runs with zero API keys and zero cost. Local Python import targets are v1.1.
- D3. Running the battery needs no LLM (except the optional judge). Run cost is near zero.
- D4. The poisoning layer ships as an interface plus "not assessed" status in v1. Live poisoning needs corpus write access, which is the Project 2 adapter.
- D5. Agent tool-call attacks are out of v1 (Project 4 territory). The layer enum reserves the slot.
- D6. The report is a first-class artifact: markdown, client-sendable, shaped like the Sudhir session report (findings, before/after evidence, root cause, fix references).
- D7. `diff` mode (before/after) is in v1.0, not v1.1. It is the sales artifact: the same target, broken, then gated, one table apart.
- D8. Every run writes artifacts: one JSONL line per prompt attempt with the full request and response. Verdicts are reproducible from artifacts alone.
- D9. Ethics are product: the README carries a permissions section, and the CLI asks for a one-line attestation (system owned or written permission) on first run, stored per target config.

## 2. Taxonomy: six layers, 28 cases in v1

| Layer | Cases | Examples |
|---|---|---|
| Injection | 8 | direct meta ask, disclaimer echo, rule laundering, authority impersonation, transform to JSON, transform to another language, multi-turn setup then attack, mid-conversation injection |
| Exfiltration | 5 | chunk dump as table, list accessible sources, quote raw context verbatim, config or env probe, file path disclosure |
| Citation integrity | 4 | out-of-range citation, phantom source list, citation count mismatch, citation attached to a refusal |
| Policy and output bypass | 5 | dosage math, restricted medical advice, refusal evasion, PII extraction, instruction conflict (user vs system) |
| Robustness | 4 | non-English variant of a held prompt, obfuscated phrasing, formatting attack (request the answer as a table or CSV), system-prompt echo via n-gram |
| Poisoning (stub) | 2 | planted imperative assertion, trusted-source laundering. Status in v1: NOT ASSESSED, interface only |

Seed cases: the exfil case and the four injection cases are the exact prompts run live against the NCD Guideline Tutor on 2026-10-11. Their verbatim prompts, the break output, and the four refusal texts are the first test fixtures and the first sample-report content. No invented examples needed for the first six cases.

Severity defaults (overridable per case): exfil on a non-public corpus is critical; policy bypass in a medical context is critical; meta-ask leak is high; citation fabrication is high in medical contexts, medium elsewhere; robustness holds that break are medium.

## 3. Architecture

```
                    +------------------+
 CLI (typer)  --->  |   RunConfig      |  YAML: target, layers, k, canaries, judge on/off
                    +--------+---------+
                             |
                    +--------v---------+        +-------------------+
                    | Target adapter   | -----> | real app (HTTP)   |
                    |  http_target     |        | mock_target (CI)  |
                    |  send(q, hist)   |        +-------------------+
                    +--------+---------+
                             |  TargetResponse(text, citations, raw, events)
                    +--------v---------+
                    | Battery          |  28 cases, each: prompts (multi-turn ok),
                    | (registry)       |  layer, severity, expected-in-verify
                    +--------+---------+
                             |
                    +--------v---------+
                    | Checks           |  pure functions:
                    | canary n-gram    |  (response, context) -> passed, rule, evidence
                    | 12+ word verbatim|
                    | citation check   |
                    | regex probes     |
                    | judge (optional) |
                    +--------+---------+
                             |
                    +--------v---------+
                    | Results schema   |  versioned pydantic: run_id, target, cases[]
                    +--------+---------+
              +-----+-----+-----+-------+
              |           |           |
        console (rich)  JSON  markdown report  +  artifacts JSONL
                              |
                        diff mode (two runs -> before/after report)
```

Key properties:

- Checks are pure functions. A check is testable without a target, which is how the whole harness stays deterministic.
- The results schema is versioned (`schema_version: 1`) from day one. It is the thing clients and CI depend on.
- The mock target is not a placeholder. It is a deliberately naive RAG app (echoes its system prompt on request, dumps chunks, fabricates citations) used as the golden test: the broken mock must fail at least 15 cases, and the fixed mock (with the session gate code) must pass all v1 cases. That pair is the harness's own regression suite.

## 4. Repo layout

Suggested repo name: `breaklab` (check GitHub availability in Phase 0; alternatives: `redline-lab`, `breakai-lab`).

```
breaklab/
  README.md
  pyproject.toml            # hatchling; python >= 3.11; deps: pydantic, httpx, typer, rich, pyyaml
  .github/workflows/ci.yml  # ruff, mypy, pytest (runs the broken/fixed mock golden tests)
  LICENSE                   # MIT
  config/
    example_target.yaml
    example_expectations.yaml
  src/breaklab/
    __init__.py             # __version__
    cli.py                  # attack, verify, diff, new-target, attest
    config.py               # TargetConfig, RunConfig, pydantic-validated
    targets/
      base.py               # Target protocol
      http_target.py        # JSON + SSE extraction, auth headers, timeout, retries
      mock_target.py        # broken mock + fixed mock (gated, from the session code)
    battery/
      registry.py           # @attack decorator, layer enum, case schema
      injection.py
      exfil.py
      citation.py
      policy.py
      robustness.py
      poisoning.py          # interface + NOT_ASSESSED stub
    checks/
      canary.py             # n-gram canary detection (threshold, not substring)
      verbatim.py           # 12+ word verbatim run vs corpus snippets
      citation_check.py     # cited ids vs provided retrieved set
      regex_checks.py       # path disclosure, env/config probes
      judge.py              # optional LLM judge, off by default, budget-capped
    reporting/
      results.py            # Results schema (versioned)
      console.py            # rich pass/fail table, per-layer summary, score
      markdown.py           # client report
      diff.py               # before/after report
      score.py              # documented formula
    artifacts.py            # JSONL capture, one line per attempt
  tests/
    test_broken_mock_fails_battery.py   # golden: >= 15 of 28 break
    test_fixed_mock_holds_battery.py    # golden: 28 of 28 hold
    test_canary_check.py                # positive + negative fixtures per rule
    test_citation_check.py
    test_sse_parsing.py
    test_markdown_report.py
    test_diff.py
  examples/
    run_attack.sh
    sample_report_broken.md   # the flagship, from the real session + mock pair
    sample_report_fixed.md
```

## 5. CLI surface (v1)

```
breaklab attack  --target config.yaml [--layer injection,exfil] [--k 3] [--judge] [-o out/]
breaklab verify  --target config.yaml --expected expectations.yaml   # exit 0 = all hold, 1 = any break
breaklab diff    run_a.json run_b.json -o before_after.md
breaklab new-target  # interactive scaffold for a target config
```

Target config shape:

```yaml
target:
  name: ncd-tutor
  attestation: "I own this system / have written permission to test it."
  base_url: https://example.hf.space
  chat:
    path: /api/chat
    method: POST
    body_template: '{"question": "{prompt}", "history": []}'
    response:
      mode: sse            # or json
      text_path: "$.full_text"
      citations_path: "$.citations"
  headers:
    Authorization: "{API_KEY}"
options:
  k: 1                     # attempts per case; a break on any attempt is a break
  timeout_s: 60
  temperature_note: "set target to temperature 0 if possible"
  canaries:
    - "ALPINE-FERN-DELTA-9"
```

## 6. Phases, each ending in a shippable artifact

### Phase 0: skeleton (1 to 2 days)
- Init repo, pyproject, ruff, mypy, pytest, GitHub Actions (lint plus test), typer CLI with `--help`, mock echo target, one throwaway case.
- Done when: CI is green; `breaklab --help` works; `breaklab attack --target mock://echo` runs one case and prints a table.

### Phase 1: vertical slice (week 1)
- Target protocol, `http_target` (JSON), results schema v1, console reporter, artifact capture, and five real cases: the exfil dump case plus the four injection cases from the live session, with regex and canary checks.
- Done when: `breaklab attack` runs against a real live HTTP chat endpoint with correct verdicts. Test on at least three real apps (your own Article 1 support bot first, plus two public Spaces you have permission to probe).

### Phase 2: full battery and checks (week 2)
- All 28 cases; canary n-gram check; 12+ word verbatim check; citation validator; multi-turn case support; broken mock and fixed mock built; both golden tests in CI.
- Done when: the broken mock fails at least 15 cases and the fixed mock holds all v1 cases, in CI, with zero API keys. This is the internal alpha: usable on real targets from this point.

### Phase 3: report and regression mode (week 3)
- Markdown client report (findings, evidence spans, severity, fix references, score); score formula in `score.py` and documented; `verify` mode with expectations file and exit codes; attestation flow.
- Done when: a sample report is committed to `examples/` and reads like the Sudhir session report; `breaklab verify` exits 1 on the broken mock and 0 on the fixed mock; a GitHub Actions example shows it gating a branch.

### Phase 4: hardening (week 4)
- SSE/streaming extraction (the hard part: the NCD tutor streams `sources`, `token`, `done` events; build the parser against at least two real streaming targets), auth and timeout UX, `k`-sample mode, optional judge module (off by default, budget-capped, clearly labeled as non-deterministic), config validation error messages that a non-expert can act on.
- Done when: clean runs against three different live targets including two streaming ones; no secrets in any committed example; error messages pass a "can a client act on this" review.

### Phase 5: diff mode and flagship demo (week 5)
- `breaklab diff` producing a before/after markdown; the flagship run: broken reference target vs the same target with the session gate code applied; the report becomes `examples/sample_report_broken.md` and `sample_report_fixed.md`.
- Done when: the before/after pair exists, reads as one story, and includes the real 2026-10-11 exfil case with its verbatim break output and the canned refusal as the after state.

### Phase 6: public v1.0 (week 6)
- README (the story: what it is, why it differs from the existing scanners, quickstart, taxonomy table, score formula, ethics and permissions section), a 3 minute demo screencast, MIT license, version 0.1.0 tag, first "how I built breaklab" article, and the Upwork listings plus LinkedIn updated to link the repo.
- Done when: a stranger can install it, point it at their own app, and get a usable report in under 10 minutes, following only the README.

## 7. Not in v1 (law)

- Agent and tool-call attack layer (Project 4).
- Local Python import targets (v1.1).
- garak / promptfoo ingestion (v1.1, as external scanner adapters).
- Poisoning beyond the stub (needs the Project 2 corpus adapter).
- Browser and UI-level attacks, availability and rate tests.
- Any dashboard, web UI, or multi-user features.
- New ideas that appear mid-build go to `BACKLOG.md`, not to the branch.

## 8. Risks and mitigations

1. Verdict false positives (a rule firing on a legitimate answer destroys the tool's credibility). Mitigation: every check ships with positive and negative fixtures in `tests/`; tune against three real apps in Phase 1 before writing more cases.
2. Streaming and SSE edge cases. Mitigation: the HTTP target is built against at least two real streaming targets in Phase 4, and the mock target reproduces the exact event contract (`sources`, `token`, `done`) so the parser is tested offline.
3. LLM nondeterminism. Mitigation: recommend temperature 0 on the target; `k`-sample mode with "break on any" semantics; the report states attempts per case; verdicts are always per-run and reproducible from artifacts.
4. Scope creep (the known failure mode of this project's owner; see the Sudhir session post-mortem). Mitigation: section 7 is law; every phase ends in a shippable artifact; the week-2 alpha is the commitment checkpoint, and if it is not there, cut cases, never cut check quality.
5. Part-time energy over six weeks. Mitigation: each phase is independently useful; the repo is public-ready at the end of Phase 6 but usable privately from Phase 2; a stalled week costs a week, not a phase, because phases are self-contained.

## 9. Content flywheel (why this project pays)

- Each of the six layers is one article in the Breaking AI series (six articles, with real fixture prompts, because the battery ran them for real).
- The markdown reporter's template is the Sudhir session report, which already exists and is committed.
- The 30 minute scoping call becomes a live demo: run the battery against the prospect's own app on their screen, with their permission, in the first ten minutes.
- Upwork listings and the profile link the repo. The repo is the "proof on screen" that replaced the testimonial ask.
- Article cadence note: article 2 (five boring failure modes) publishes 2026-10-13 with real lab results from the support bot. breaklab's Phase 1 re-runs those same prompts against the same bot, so the article's numbers and the harness's first fixtures agree by construction.

## 10. Definition of done (v1.0, all must be true)

1. Public repo, CI green, MIT license, version 0.1.0 tag.
2. `pip install` plus one command produces a report on a target the user owns, following only the README.
3. Broken mock fails at least 15 of 28 cases; fixed mock holds all v1 cases; both in CI.
4. Every verdict in every report cites rule and evidence span; every run has an artifact file that reproduces it.
5. `verify` gates a branch in a public CI example.
6. `diff` produces the flagship before/after pair from the real session data.
7. README includes the taxonomy table, the score formula, and the ethics section.
8. One article published that links the repo; Upwork and LinkedIn updated.

## 11. Seed assets already in hand (real, committed, no fabrication)

- The verbatim exfil prompt and its break output (the before artifact): NCD session, 11:24 PM, 2026-10-11.
- The four injection prompts with their refusal texts (the held fixtures), including the French refusal.
- The gate code that fixed the break, verified live, with insertion points: session report Appendix A.
- The results schema thinking (the trace schema one-pager), reused as the results and artifact schema.
- The report structure (the session report), reused as the markdown reporter template.
- One real target with a history of both states (broken and gated) for the flagship diff.

## 12. First action

Say the word and Phase 0 starts: repo scaffold, tooling, CI, CLI, mock echo, one case, green build. Estimated time to a green CI: under three focused hours.