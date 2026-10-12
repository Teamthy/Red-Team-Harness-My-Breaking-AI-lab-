from dataclasses import dataclass, field
from typing import Literal


@dataclass(slots=True)
class TargetConfig:
    name: str = "mock://echo"
    attestation: str = "I own this system or have written permission to test it."
    target_type: Literal["mock", "http"] = "mock"


@dataclass(slots=True)
class RunConfig:
    target: TargetConfig = field(default_factory=TargetConfig)
    k: int = 1
    judge_enabled: bool = False
    layers: tuple[str, ...] = ("injection",)
