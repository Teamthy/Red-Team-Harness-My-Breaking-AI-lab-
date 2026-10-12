from __future__ import annotations

import sys
import types

from breaklab.config import TargetConfig
from breaklab.targets.python_target import PythonTarget


def test_python_target_resolves_callable_and_returns_target_response() -> None:
    module = types.ModuleType("local_python_target")

    def local_handler(prompt: str, history: list[str] | None = None) -> dict[str, object]:
        return {
            "text": f"Echo: {prompt}",
            "citations": ["doc-1", "doc-2"],
            "history": list(history or []),
        }

    module.local_handler = local_handler
    sys.modules[module.__name__] = module

    target = PythonTarget("python://local_python_target:local_handler")
    response = target.send("hello there", ["previous prompt"])

    assert response.text == "Echo: hello there"
    assert response.citations == ["doc-1", "doc-2"]
    assert response.raw["history"] == ["previous prompt"]


def test_target_config_parses_python_target() -> None:
    config = TargetConfig.from_mapping(
        {
            "target": {
                "name": "python://local_python_target:local_handler",
                "type": "python",
                "module": "local_python_target",
                "callable": "local_handler",
            }
        }
    )

    assert config.target_type == "python"
    assert config.module == "local_python_target"
    assert config.callable_name == "local_handler"
