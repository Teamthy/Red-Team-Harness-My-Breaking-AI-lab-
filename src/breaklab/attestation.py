from __future__ import annotations

import json
from pathlib import Path


def _state_path(base_dir: str | Path | None = None) -> Path:
    root = Path(base_dir) if base_dir is not None else Path.cwd()
    return root / ".breaklab" / "attestations.json"


def _load_store(base_dir: str | Path | None = None) -> dict[str, str]:
    path = _state_path(base_dir)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if isinstance(data, dict):
        clean: dict[str, str] = {}
        for key, value in data.items():
            if isinstance(value, str):
                clean[key] = value
        return clean
    return {}


def get_attestation(target_name: str, base_dir: str | Path | None = None) -> str | None:
    store = _load_store(base_dir)
    return store.get(target_name)


def set_attestation(target_name: str, attestation: str, base_dir: str | Path | None = None) -> str:
    path = _state_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    store = _load_store(base_dir)
    store[target_name] = attestation.strip()
    path.write_text(json.dumps(store, indent=2, sort_keys=True), encoding="utf-8")
    return store[target_name]


def ensure_attestation(
    target_name: str,
    attestation: str | None = None,
    base_dir: str | Path | None = None,
) -> str | None:
    existing = get_attestation(target_name, base_dir=base_dir)
    if existing:
        return existing
    if attestation is not None:
        return set_attestation(target_name, attestation, base_dir=base_dir)
    return None
