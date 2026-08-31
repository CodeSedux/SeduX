"""Dependency-free HTTP gateway for local development and smoke tests."""

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit

from shared.contracts import SERVICE_NAMES, ServiceStatus, health_payload


class GatewayHandler(BaseHTTPRequestHandler):
    server_version = "SeduXGateway/0.1.0"

    def _write_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/health":
            self._write_json(health_payload("gateway"))
            return
        if path == "/services":
            services = [
                ServiceStatus(name, "ok" if name == "gateway" else "planned").to_dict()
                for name in SERVICE_NAMES
            ]
            self._write_json({"services": services})
            return
        self._write_json({"error": "not_found"}, HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: object) -> None:
        return


def create_server(host: str = "127.0.0.1", port: int = 8080) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), GatewayHandler)


def main() -> None:
    server = create_server()
    print("SeduX gateway listening on http://127.0.0.1:8080", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()