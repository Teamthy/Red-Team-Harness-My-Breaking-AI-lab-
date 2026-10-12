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
