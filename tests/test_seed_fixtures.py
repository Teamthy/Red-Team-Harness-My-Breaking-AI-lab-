"""Pin anonymized live-session fixture invariants and mock correspondence."""
from __future__ import annotations

import json
import re
from pathlib import Path

from breaklab.battery import default_cases
from breaklab.targets.mock_target import BROKEN_EXFIL_TABLE, CANNED_EXFIL, SNIPPET_A1C

FIXDIR = Path(__file__).resolve().parent / "fixtures" / "guideline_rag"
FORBIDDEN = ("client-name", "ncd", "huggingface", "hugging face", "2026", "10-11", "10/11")


def _load(name: str) -> str:
    return (FIXDIR / name).read_text(encoding="utf-8")


def test_fixture_files_exist() -> None:
    for name in (
        "broken_exfil_response.txt", "fixed_exfil_response.txt", "cases.json",
        "corpus_snippets.json", "system_prompt.txt", "withstand_refusals.json", "PROVENANCE.md",
    ):
        assert (FIXDIR / name).exists(), name


def test_fixture_pack_has_no_client_identifiers_or_machine_paths() -> None:
    for path in FIXDIR.iterdir():
        body = path.read_text(encoding="utf-8").lower()
        assert not any(term in body for term in FORBIDDEN), path.name
        for match in re.findall(r"/(?:home|var|etc|opt)/[\w./-]+", body):
            assert match.startswith(("/home/app", "/var/lib/app")), (path.name, match)


def test_broken_and_fixed_captured_responses_match_mock() -> None:
    assert _load("broken_exfil_response.txt").strip() == BROKEN_EXFIL_TABLE
    assert _load("fixed_exfil_response.txt").strip() == CANNED_EXFIL
    assert SNIPPET_A1C in BROKEN_EXFIL_TABLE


def test_fixture_seed_prompts_are_in_registry() -> None:
    data = json.loads(_load("cases.json"))
    registry = {case.name: case for case in default_cases()}
    for fixture in data["cases"]:
        assert fixture["prompt"] == registry[fixture["name"]].prompt
        assert fixture["seed_from_session"] is True


def test_corpus_fixture_matches_mock_evidence() -> None:
    data = json.loads(_load("corpus_snippets.json"))
    snippets = {item["id"]: item["text"] for item in data["snippets"]}
    assert snippets["6"] == SNIPPET_A1C