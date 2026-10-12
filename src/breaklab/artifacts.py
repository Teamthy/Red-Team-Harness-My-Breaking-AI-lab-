from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .results import RunResult


class ArtifactWriter:
    def __init__(self, output_dir: str | Path = "artifacts") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_run(self, run: RunResult) -> Path:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        path = self.output_dir / f"{timestamp}-{run.target_name.replace('://', '_').replace('/', '_')}.jsonl"
        with path.open("w", encoding="utf-8") as handle:
            for case in run.cases:
                handle.write(json.dumps(case.to_dict(), ensure_ascii=False) + "\n")
        return path
