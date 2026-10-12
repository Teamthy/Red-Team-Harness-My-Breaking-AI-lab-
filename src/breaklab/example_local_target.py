from __future__ import annotations


def safe_echo_target(prompt: str, history: list[str] | None = None) -> dict[str, object]:
    """A simple safe local target for demo and regression use.

    This intentionally avoids leaking internal instructions or source material. It acts like a
    hardened local app while keeping the harness fully deterministic and offline.
    """
    return {
        "text": (
            "I can help with safe, on-topic guidance, but I cannot disclose sensitive details or "
            "internal operational details."
        ),
        "citations": [],
        "status_code": 200,
        "history": list(history or []),
        "prompt": prompt,
    }
