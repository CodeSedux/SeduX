"""Dependency-free task service stub for local smoke tests."""

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlsplit

from shared.contracts import health_payload
from shared.task_runtime import TaskManager
from shared.tasks import TaskDefinition, TaskSchedule, TaskType

task_manager = TaskManager()


class TaskHandler(BaseHTTPRequestHandler):
    server_version = "SeduXTask/0.1.0"

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
            self._write_json(health_payload("task"))
            return
        if path in {"/tasks", "/tasks/list"}:
            user_id = parse_qs(urlsplit(self.path).query).get("user_id", [None])[0]
            self._write_json({"tasks": [task.to_dict() for task in task_manager.list(user_id)]})
            return
        self._write_json({"error": "not_found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/tasks/schedule":
            self._write_json({"error": "not_found"}, HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise TypeError("request body must be a JSON object")
            schedule = payload.get("schedule", {})
            if not isinstance(schedule, dict):
                raise TypeError("schedule must be a JSON object")
            task = TaskDefinition(
                task_id=payload["task_id"],
                user_id=payload["user_id"],
                name=payload["name"],
                type=TaskType(payload["type"]),
                schedule=TaskSchedule(**schedule),
                payload=payload.get("payload", {}),
                max_retries=payload.get("max_retries", 3),
            )
            created = task_manager.create(task)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            self._write_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        self._write_json(created.to_dict(), HTTPStatus.CREATED)

    def do_DELETE(self) -> None:
        path = urlsplit(self.path).path
        prefix = "/tasks/"
        if not path.startswith(prefix) or not path.removeprefix(prefix):
            self._write_json({"error": "not_found"}, HTTPStatus.NOT_FOUND)
            return
        try:
            cancelled = task_manager.cancel(path.removeprefix(prefix))
        except KeyError as error:
            self._write_json({"error": str(error)}, HTTPStatus.NOT_FOUND)
            return
        self._write_json(cancelled.to_dict())

    def log_message(self, format: str, *args: object) -> None:
        return


def create_server(host: str = "127.0.0.1", port: int = 8005) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), TaskHandler)


if __name__ == "__main__":
    server = create_server()
    print("SeduX task service listening on http://127.0.0.1:8005", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
