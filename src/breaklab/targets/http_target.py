from __future__ import annotations

import json
from typing import Any

import httpx

from .base import TargetResponse


class HTTPTarget:
    def __init__(
        self,
        base_url: str,
        path: str = "/api/chat",
        method: str = "POST",
        body_template: str | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
        client: httpx.Client | None = None,
        stream: bool = False,
        response_mode: str = "json",
        sse_options: dict[str, Any] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.path = path if path.startswith("/") else f"/{path}"
        self.method = method.upper()
        self.body_template = body_template or '{"question": "{prompt}", "history": {history}}'
        self.timeout = timeout
        self.headers = headers or {"Content-Type": "application/json"}
        self.stream = stream
        self.response_mode = response_mode.lower()
        self.sse_options = sse_options or {
            "text_field": "content",
            "status_field": "done",
            "citations_field": "citations",
        }
        self._client = client or httpx.Client(timeout=timeout, headers=self.headers)

    def _build_payload(self, prompt: str, history: list[str] | None = None) -> dict[str, Any]:
        history_payload = list(history or [])
        try:
            payload = json.loads(self.body_template)
            payload["question"] = prompt
            payload["history"] = history_payload
            return payload
        except json.JSONDecodeError:
            return {
                "question": prompt,
                "history": history_payload,
            }

    def _extract_text(self, payload: Any) -> str:
        if isinstance(payload, dict):
            for key in ("full_text", "output", "answer", "message", "response", "text"):
                value = payload.get(key)
                if isinstance(value, str):
                    return value
                if isinstance(value, dict):
                    nested = value.get("content")
                    if isinstance(nested, str):
                        return nested
        if isinstance(payload, list):
            return "\n".join(str(item) for item in payload)
        return str(payload)

    def _extract_citations(self, payload: Any) -> list[str]:
        if isinstance(payload, dict):
            for key in ("citations", "sources", "references"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [str(item) for item in value]
                if isinstance(value, str):
                    return [value]
        return []

    def _parse_sse_payload(self, raw_text: str) -> tuple[str, list[str], dict[str, Any]]:
        chunks: list[str] = []
        citations: list[str] = []
        parsed: dict[str, Any] = {}
        current: list[str] = []
        pending_event: str | None = None

        for line in raw_text.splitlines():
            if not line.strip():
                if current:
                    payload = "\n".join(current)
                    current = []
                    if payload:
                        try:
                            message = json.loads(payload)
                        except json.JSONDecodeError:
                            message = payload
                        if isinstance(message, dict):
                            text_field = self.sse_options.get("text_field", "content")
                            content_value = message.get(text_field)
                            if isinstance(content_value, str):
                                chunks.append(content_value)
                            citations_value = message.get(self.sse_options.get("citations_field", "citations"))
                            if isinstance(citations_value, list):
                                citations.extend(str(item) for item in citations_value)
                            elif isinstance(citations_value, str):
                                citations.append(citations_value)
                            if "done" in message or self.sse_options.get("status_field") in message:
                                parsed = message
                            if pending_event is not None:
                                parsed.setdefault("event", pending_event)
                        else:
                            chunks.append(str(message))
                continue

            if line.startswith(":"):
                continue
            if line.startswith("event:"):
                pending_event = line.split(":", 1)[1].strip()
                continue
            if line.startswith("data:"):
                current.append(line.split(":", 1)[1].strip())

        if current:
            payload = "\n".join(current)
            try:
                message = json.loads(payload)
            except json.JSONDecodeError:
                message = payload
            if isinstance(message, dict):
                text_field = self.sse_options.get("text_field", "content")
                content_value = message.get(text_field)
                if isinstance(content_value, str):
                    chunks.append(content_value)
                citations_value = message.get(self.sse_options.get("citations_field", "citations"))
                if isinstance(citations_value, list):
                    citations.extend(str(item) for item in citations_value)
                elif isinstance(citations_value, str):
                    citations.append(citations_value)
                if "done" in message or self.sse_options.get("status_field") in message:
                    parsed = message
            else:
                chunks.append(str(message))

        return "".join(chunks), citations, parsed

    def send(self, prompt: str, history: list[str] | None = None) -> TargetResponse:
        payload = self._build_payload(prompt, history)
        response = self._client.request(
            self.method,
            f"{self.base_url}{self.path}",
            json=payload,
            headers=self.headers,
        )
        response.raise_for_status()

        if self.stream or self.response_mode == "sse":
            data = response.text
            text, citations, parsed = self._parse_sse_payload(data)
            return TargetResponse(text=text, citations=citations, raw=parsed or {"raw": data}, status_code=response.status_code)

        data = response.json()
        text = self._extract_text(data)
        citations = self._extract_citations(data)
        return TargetResponse(text=text, citations=citations, raw=data, status_code=response.status_code)
