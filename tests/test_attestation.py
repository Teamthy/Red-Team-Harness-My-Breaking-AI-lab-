from __future__ import annotations

from breaklab.attestation import get_attestation, set_attestation


def test_attestation_round_trip(tmp_path) -> None:
    target = "python://breaklab.example_local_target:safe_echo_target"
    statement = "I own this system or have written permission to test it."

    set_attestation(target, statement, base_dir=tmp_path)
    saved = get_attestation(target, base_dir=tmp_path)

    assert saved == statement
