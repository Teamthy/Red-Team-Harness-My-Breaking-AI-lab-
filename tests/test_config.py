from __future__ import annotations

from breaklab.config import TargetConfig, load_run_config


def test_target_and_run_config_parse_from_yaml() -> None:
    yaml_text = """
target:
  name: mock://fixed
  attestation: "I own this system."
  type: mock
options:
  k: 2
  judge_enabled: false
  layers:
    - injection
    - policy
"""

    config = load_run_config(yaml_text)
    assert config.target.name == "mock://fixed"
    assert config.k == 2
    assert config.layers == ("injection", "policy")


def test_target_config_scaffold_contains_required_fields() -> None:
    scaffold = TargetConfig.template_yaml()
    assert "target:" in scaffold
    assert "name:" in scaffold
    assert "attestation:" in scaffold


def test_http_target_config_reads_full_endpoint_details() -> None:
    config = load_run_config(
        {
            "target": {
                "name": "ncd-guideline-tutor",
                "attestation": "I have permission to test this system.",
                "type": "http",
                "base_url": "https://example.com",
                "path": "/api/chat",
                "method": "POST",
                "body_template": '{"question": "{prompt}", "history": []}',
                "headers": {"Authorization": "Bearer {API_KEY}", "Content-Type": "application/json"},
                "timeout": 45.0,
            },
            "options": {
                "k": 2,
                "layers": ["injection", "exfiltration"],
            },
        }
    )

    assert config.target.target_type == "http"
    assert config.target.base_url == "https://example.com"
    assert config.target.path == "/api/chat"
    assert config.target.method == "POST"
    assert config.target.headers["Authorization"] == "Bearer {API_KEY}"
    assert config.k == 2


def test_target_config_parses_declared_evidence() -> None:
    config = load_run_config({
        "target": {"name": "support-bot", "type": "http", "base_url": "https://example.com"},
        "evidence": {
            "system_prompt": "Answer from approved sources.",
            "canaries": ["ALPINE-FERN-DELTA-9"],
            "corpus_snippets": [{"id": "doc-1", "text": "Verbatim source content."}],
            "sensitive_patterns": [{"name": "secret", "pattern": "TOKEN=[A-Z]+"}],
            "policy_flags": ["pii"],
            "retrieved_ids": ["doc-1"],
        },
    })
    evidence = config.target.evidence
    assert evidence.system_prompt == "Answer from approved sources."
    assert evidence.canaries == ("ALPINE-FERN-DELTA-9",)
    assert evidence.corpus_snippets == (("doc-1", "Verbatim source content."),)
    assert evidence.sensitive_patterns == (("secret", "TOKEN=[A-Z]+"),)
    assert evidence.policy_flags == ("pii",)
    assert evidence.retrieved_ids == ("doc-1",)
