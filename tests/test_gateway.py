import json
import threading
import unittest
from urllib.request import urlopen

from services.gateway.main import create_server


class GatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = create_server(port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def get_json(self, path: str) -> dict:
        with urlopen(self.base_url + path) as response:
            self.assertEqual(response.status, 200)
            return json.load(response)

    def test_health_is_machine_readable(self) -> None:
        payload = self.get_json("/health")
        self.assertEqual(payload["service"], "gateway")
        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["timestamp"])

    def test_health_accepts_query_parameters(self) -> None:
        payload = self.get_json("/health?detail=1")
        self.assertEqual(payload["service"], "gateway")
        self.assertEqual(payload["status"], "ok")

    def test_services_accepts_query_parameters(self) -> None:
        payload = self.get_json("/services?format=compact")
        self.assertEqual(len(payload["services"]), 8)

    def test_services_exposes_initial_tracks(self) -> None:
        payload = self.get_json("/services")
        names = {service["name"] for service in payload["services"]}
        self.assertEqual(
            names,
            {"gateway", "voice", "avatar", "llm", "emotion", "task", "home", "screen"},
        )
        gateway = next(service for service in payload["services"] if service["name"] == "gateway")
        self.assertEqual(gateway["status"], "ok")


if __name__ == "__main__":
    unittest.main()