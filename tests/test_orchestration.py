import unittest

from shared.orchestration import LifecycleState, ServiceOrchestrator


class OrchestrationTests(unittest.TestCase):
    def test_check_all_aggregates_cross_service_health(self) -> None:
        def probe(name, metadata, timeout):
            if name == "voice":
                raise TimeoutError("voice probe timed out")

        orchestrator = ServiceOrchestrator(
            registry={
                "gateway": {"port": 8080},
                "voice": {"port": 8001},
            },
            probe=probe,
        )

        report = orchestrator.check_all()

        self.assertEqual(report.status, "degraded")
        self.assertEqual(report.services[0].state, LifecycleState.RUNNING)
        self.assertEqual(report.services[0].status, "healthy")
        self.assertEqual(report.services[1].state, LifecycleState.FAILED)
        self.assertIn("timed out", report.services[1].error)

    def test_lifecycle_hooks_are_called_and_state_is_explicit(self) -> None:
        events = []
        orchestrator = ServiceOrchestrator(registry={})
        orchestrator.register(
            "task",
            {"port": 8005},
            start_hook=lambda name: events.append(f"start:{name}"),
            stop_hook=lambda name: events.append(f"stop:{name}"),
        )

        self.assertEqual(orchestrator.start("task"), LifecycleState.RUNNING)
        self.assertEqual(orchestrator.start("task"), LifecycleState.RUNNING)
        self.assertEqual(orchestrator.stop("task"), LifecycleState.STOPPED)
        self.assertEqual(events, ["start:task", "stop:task"])

    def test_startup_and_shutdown_hooks_support_aliases_and_timeouts(self) -> None:
        events = []

        def slow_startup(name: str, metadata: dict[str, object], timeout: float) -> None:
            events.append(f"startup:{name}:{timeout}")
            raise TimeoutError("startup timed out")

        orchestrator = ServiceOrchestrator(registry={})
        orchestrator.register(
            "worker",
            {"port": 8007},
            startup_hook=slow_startup,
            shutdown_hook=lambda name, metadata: events.append(f"shutdown:{name}"),
        )

        with self.assertRaises(TimeoutError):
            orchestrator.start("worker", timeout=0.01)
        self.assertEqual(orchestrator._services["worker"].state, LifecycleState.FAILED)

        orchestrator.register(
            "scheduler",
            {"port": 8008},
            startup_hook=lambda name, metadata: events.append(f"startup:{name}"),
            shutdown_hook=lambda name, metadata: events.append(f"shutdown:{name}"),
        )
        self.assertEqual(orchestrator.start("scheduler"), LifecycleState.RUNNING)
        self.assertEqual(orchestrator.stop("scheduler"), LifecycleState.STOPPED)
        self.assertIn("startup:scheduler", events)
        self.assertIn("shutdown:scheduler", events)

    def test_all_unhealthy_services_are_unavailable(self) -> None:
        orchestrator = ServiceOrchestrator(
            registry={"home": {"port": 8006}},
            probe=lambda name, metadata, timeout: (_ for _ in ()).throw(ConnectionError("offline")),
        )

        report = orchestrator.check_all()

        self.assertEqual(report.status, "unavailable")
        self.assertEqual(report.to_dict()["services"][0]["status"], "unhealthy")

    def test_unknown_service_is_rejected(self) -> None:
        orchestrator = ServiceOrchestrator(registry={})
        with self.assertRaises(KeyError):
            orchestrator.check("missing")

    def test_invalid_service_metadata_is_rejected_before_probe(self) -> None:
        orchestrator = ServiceOrchestrator(registry={})
        with self.assertRaises(ValueError):
            orchestrator.register("bad", {"port": 0})

    def test_readiness_report_exposes_ready_contract(self) -> None:
        orchestrator = ServiceOrchestrator(
            registry={"gateway": {"port": 8080}},
            probe=lambda name, metadata, timeout: None,
        )

        report = orchestrator.check_all()

        self.assertTrue(report.ready)
        self.assertTrue(report.to_dict()["ready"])
        self.assertEqual(report.status, "healthy")


if __name__ == "__main__":
    unittest.main()
