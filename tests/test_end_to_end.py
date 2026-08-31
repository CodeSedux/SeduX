import json
import threading
import unittest
from urllib.request import Request, urlopen

from services.gateway.main import create_server


class LocalEndToEndTests(unittest.TestCase):
    def test_client_can_discover_control_plane_over_http(self) -> None:
        server = create_server(port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            request = Request(f"http://127.0.0.1:{server.server_port}/services", headers={"Accept": "application/json"})
            with urlopen(request, timeout=2) as response:
                payload = json.load(response)
            self.assertEqual(response.status, 200)
            self.assertEqual(len(payload["services"]), 8)
            self.assertEqual(payload["services"][0]["name"], "gateway")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()