"""Dependency-free avatar service stub for local smoke tests."""

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit

from shared.contracts import health_payload


class AvatarHandler(BaseHTTPRequestHandler):
    server_version = "SeduXAvatar/0.1.0"

    def _write_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if urlsplit(self.path).path == "/health":
            self._write_json(health_payload("avatar"))
            return
        self._write_json({"error": "not_found"}, HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: object) -> None:
        return


def create_server(host: str = "127.0.0.1", port: int = 8002) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), AvatarHandler)


if __name__ == "__main__":
    server = create_server()
    print("SeduX avatar service listening on http://127.0.0.1:8002", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
