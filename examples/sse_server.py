from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class SSEHandler(BaseHTTPRequestHandler):
    server_version = "BreaklabSSE/1.0"

    def do_POST(self) -> None:
        if self.path != "/api/chat/stream":
            self.send_error(404)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        _ = self.rfile.read(content_length)

        payloads = [
            {"content": "Hello"},
            {"content": " world"},
        ]

        body = b""
        for item in payloads:
            event = json.dumps(item)
            body += f"event: chunk\ndata: {event}\n\n".encode()

        body += b"event: done\ndata: {\"done\": true, \"citations\": [\"doc-9\"]}\n\n"

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()
        self.close_connection = True

    def log_message(self, format: str, *args: object) -> None:
        return


def build_server(port: int = 8765) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), SSEHandler)


def main() -> None:
    port = int(os.environ.get("BREAKLAB_SSE_PORT", "8765"))
    server = build_server(port)
    print(f"SSE test server listening on http://127.0.0.1:{port}/api/chat/stream")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
