import unittest

from fastapi.testclient import TestClient

from services.gateway import app as gateway_app
from services.gateway.app import app
from shared.orchestration import ServiceOrchestrator


class FastAPIGatewayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_fastapi_health_endpoint(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["service"], "gateway")
        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["timestamp"])

    def test_fastapi_services_endpoint(self) -> None:
        response = self.client.get("/services")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("services", payload)
        names = {service["name"] for service in payload["services"]}
        self.assertEqual(
            names,
            {"gateway", "voice", "avatar", "llm", "emotion", "task", "home", "screen"},
        )

    def test_frontend_origin_can_read_service_registry(self) -> None:
        response = self.client.get(
            "/services",
            headers={"Origin": "http://127.0.0.1:4173"},
        )
        self.assertEqual(response.headers["access-control-allow-origin"], "http://127.0.0.1:4173")

    def test_response_includes_versioned_request_context(self) -> None:
        response = self.client.get("/health", headers={"X-Request-ID": "request-123"})

        self.assertEqual(response.headers["x-request-id"], "request-123")
        self.assertEqual(response.headers["x-api-version"], "v1")
        self.assertIn("app;dur=", response.headers["server-timing"])

    def test_metrics_count_gateway_requests(self) -> None:
        before = self.client.get("/metrics").json()["counters"].get("http_requests_total", 0)
        self.client.get("/health")
        after = self.client.get("/metrics").json()["counters"]["http_requests_total"]

        self.assertGreaterEqual(after, before + 2)

    def test_readiness_exposes_aggregate_orchestration_status(self) -> None:
        original = gateway_app.service_orchestrator
        gateway_app.service_orchestrator = ServiceOrchestrator(
            registry={"gateway": {"port": 8080}},
            probe=lambda name, metadata, timeout: None,
        )
        try:
            response = self.client.get("/readiness")
        finally:
            gateway_app.service_orchestrator = original

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")
        self.assertEqual(response.json()["services"][0]["state"], "running")


if __name__ == "__main__":
    unittest.main()
