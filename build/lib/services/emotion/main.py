"""Dependency-free emotion service stub for local smoke tests."""

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit

from shared.contracts import health_payload
from shared.emotion import analyze_text_emotion


class EmotionHandler(BaseHTTPRequestHandler):
    server_version = "SeduXEmotion/0.1.0"

    def _write_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if urlsplit(self.path).path == "/health":
            self._write_json(health_payload("emotion"))
            return
        self._write_json({"error": "not_found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if urlsplit(self.path).path not in {"/emotion/analyze", "/emotion/text"}:
            self._write_json({"error": "not_found"}, HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise TypeError("request body must be a JSON object")
            result = analyze_text_emotion(payload.get("text", ""))
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self._write_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        self._write_json(result.to_dict())

    def log_message(self, format: str, *args: object) -> None:
        return


def create_server(host: str = "127.0.0.1", port: int = 8004) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), EmotionHandler)


if __name__ == "__main__":
    server = create_server()
    print("SeduX emotion service listening on http://127.0.0.1:8004", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
