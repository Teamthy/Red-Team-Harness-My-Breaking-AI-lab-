from __future__ import annotations

import importlib
from collections.abc import Callable, Sequence
from typing import Any

from .base import TargetResponse


class PythonTarget:
    """Call a Python function as a local target adapter.

    Supported target strings:
    - python://module:function
    - python://module.function
    - module:function
    - module.function
    """

    def __init__(self, target_name: str = "python://module:function") -> None:
        self.name = target_name
        self._callable = self._resolve_callable(target_name)

    def _resolve_callable(self, target_name: str) -> Callable[..., Any]:
        ref = target_name.removeprefix("python://")

        if ":" in ref:
            module_name, attr_path = ref.split(":", 1)
        elif "." in ref:
            module_name, attr_path = ref.rsplit(".", 1)
        else:
            raise ValueError(
                "Python targets must be formatted as 'python://module:callable' or 'python://module.callable'."
            )

        module = importlib.import_module(module_name)
        obj: Any = module
        for part in attr_path.split("."):
            obj = getattr(obj, part)

        if not callable(obj):
            raise TypeError(f"Resolved target '{target_name}' is not callable: {obj!r}")

        return obj

    def send(self, prompt: str, history: Sequence[str] | None = None) -> TargetResponse:
        result = self._callable(prompt, list(history or []))

        if isinstance(result, TargetResponse):
            return result
        if isinstance(result, dict):
            text = str(
                result.get("text")
                or result.get("answer")
                or result.get("response")
                or result.get("full_text")
                or result.get("output")
                or ""
            )
            citations = result.get("citations") or result.get("sources") or []
            raw = {key: value for key, value in result.items()}
            status_code = int(result.get("status_code", 200))
            return TargetResponse(
                text=text,
                citations=[str(item) for item in citations],
                raw=raw,
                status_code=status_code,
            )
        if isinstance(result, str):
            return TargetResponse(text=result, raw={"prompt": prompt, "history": list(history or [])})

        text_value = getattr(result, "text", None)
        if text_value is not None:
            citations_value = getattr(result, "citations", None) or getattr(result, "sources", None) or []
            raw_value = getattr(result, "raw", {})
            status_code = getattr(result, "status_code", 200)
            return TargetResponse(
                text=str(text_value),
                citations=[str(item) for item in citations_value],
                raw=dict(raw_value) if isinstance(raw_value, dict) else {"payload": raw_value},
                status_code=int(status_code),
            )

        return TargetResponse(
            text=str(result),
            raw={"prompt": prompt, "history": list(history or [])},
            status_code=200,
        )
