from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SERVER_SCRIPT = REPO_ROOT / "examples" / "sse_server.py"
CONFIG_PATH = REPO_ROOT / "config" / "example_sse_target.yaml"


def build_demo_config(port: str) -> Path:
    config_text = f"""target:
  name: local-sse-demo
  attestation: \"I own this system or have written permission to test it.\"
  type: http
  base_url: http://127.0.0.1:{port}
  path: /api/chat/stream
  method: POST
  stream: true
  response_mode: sse
  body_template: '{{\"question\": \"{{prompt}}\", \"history\": []}}'
  headers:
    Content-Type: application/json
  timeout: 10.0
  sse:
    text_field: content
    citations_field: citations
    status_field: done
options:
  k: 1
  judge_enabled: false
  layers:
    - injection
    - exfiltration
    - citation
"""
    temp_dir = REPO_ROOT / "artifacts"
    temp_dir.mkdir(exist_ok=True)
    path = temp_dir / "demo_sse_target.yaml"
    path.write_text(config_text, encoding="utf-8")
    return path


def main() -> int:
    env = os.environ.copy()
    port = "8765"
    env["BREAKLAB_SSE_PORT"] = port

    server = subprocess.Popen(
        [sys.executable, str(SERVER_SCRIPT)],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    config_path = build_demo_config(port)
    try:
        time.sleep(0.5)
        result = subprocess.run(
            [sys.executable, "-m", "breaklab.cli", "attack", "--config", str(config_path)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        return result.returncode
    finally:
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
