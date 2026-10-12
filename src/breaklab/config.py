from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml


@dataclass(slots=True)
class TargetConfig:
    name: str = "mock://echo"
    attestation: str = "I own this system or have written permission to test it."
    target_type: Literal["mock", "http", "python"] = "mock"
    base_url: str | None = None
    path: str = "/api/chat"
    method: str = "POST"
    body_template: str = '{"question": "{prompt}", "history": []}'
    headers: dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0
    stream: bool = False
    response_mode: str = "json"
    sse: dict[str, Any] = field(default_factory=dict)
    module: str | None = None
    callable_name: str | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> TargetConfig:
        target_data = data.get("target", data)
        chat_data = target_data.get("chat", {}) if isinstance(target_data, dict) else {}
        target_type = str(target_data.get("type", target_data.get("target_type", "mock")))

        if target_type == "python":
            module_name = str(target_data.get("module") or target_data.get("callable_module") or "")
            callable_name = str(target_data.get("callable") or target_data.get("callable_name") or "")
            target_name = str(target_data.get("name") or f"python://{module_name}:{callable_name}")
            return cls(
                name=target_name,
                attestation=str(target_data.get("attestation", cls.attestation)),
                target_type="python",
                module=module_name,
                callable_name=callable_name,
            )

        if target_type == "http" or target_data.get("base_url") or target_data.get("path") or chat_data:
            sse_cfg = dict(target_data.get("sse") or chat_data.get("sse") or {})
            base_url = str(target_data.get("base_url") or chat_data.get("base_url") or target_data.get("name") or "https://example.com")
            return cls(
                name=str(target_data.get("name", base_url)),
                attestation=str(target_data.get("attestation", cls.attestation)),
                target_type="http",
                base_url=base_url,
                path=str(target_data.get("path") or chat_data.get("path") or "/api/chat"),
                method=str(target_data.get("method") or chat_data.get("method") or "POST").upper(),
                body_template=str(target_data.get("body_template") or chat_data.get("body_template") or '{"question": "{prompt}", "history": []}'),
                headers=dict(target_data.get("headers") or chat_data.get("headers") or {"Content-Type": "application/json"}),
                timeout=float(target_data.get("timeout") or chat_data.get("timeout") or 30.0),
                stream=bool(target_data.get("stream") or target_data.get("response_mode") == "sse" or bool(chat_data.get("stream"))),
                response_mode=str(target_data.get("response_mode") or ("sse" if sse_cfg else "json")),
                sse=sse_cfg,
            )

        return cls(
            name=str(target_data.get("name", "mock://echo")),
            attestation=str(target_data.get("attestation", cls.attestation)),
            target_type=target_type,
        )

    @classmethod
    def template_yaml(cls) -> str:
        return """target:
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
"""


@dataclass(slots=True)
class RunConfig:
    target: TargetConfig = field(default_factory=TargetConfig)
    k: int = 1
    judge_enabled: bool = False
    layers: tuple[str, ...] = ("injection",)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> RunConfig:
        target_cfg = TargetConfig.from_mapping(data)
        options = data.get("options", {})
        layers = tuple(options.get("layers", ["injection"]))
        return cls(
            target=target_cfg,
            k=int(options.get("k", 1)),
            judge_enabled=bool(options.get("judge_enabled", False)),
            layers=layers,
        )

    @classmethod
    def from_path(cls, path: str | Path) -> RunConfig:
        raw = Path(path).read_text(encoding="utf-8")
        data = yaml.safe_load(raw) or {}
        return cls.from_mapping(data)


def load_run_config(source: str | Path | dict[str, Any]) -> RunConfig:
    if isinstance(source, dict):
        return RunConfig.from_mapping(source)
    if isinstance(source, (str, Path)):
        path = Path(source)
        if path.exists():
            return RunConfig.from_path(path)
        return RunConfig.from_mapping(yaml.safe_load(str(source)) or {})
    raise TypeError("Unsupported config source type")
