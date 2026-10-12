# Fixture provenance and anonymization

These are anonymized fixtures from a live red-team session. They contain no client name, host URL, calendar date, client-specific acronym, or real machine path.

- `broken_exfil_response.txt` is the captured pre-fix response, including public guideline text.
- `fixed_exfil_response.txt` is the verified after-state refusal.
- `withstand_refusals.json` records three refusals and an equivalent direct meta ask whose response wording was not captured.
- `cases.json` contains the two seed prompts used by the regression battery.
- `system_prompt.txt` is the mock persona, not the real target's prompt.
- The remaining mock behaviors and non-seed prompts are authored representative cases.

Only authored demo paths under `/home/app` or `/var/lib/app` appear in the mock behavior. Fixture tests enforce these anonymization constraints.