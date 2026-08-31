import unittest

from shared.auth import Role, TokenService
from shared.governance import ConsentRecord
from shared.governance_runtime import GovernanceStore
from shared.operations import (
    MetricsRegistry,
    SlidingWindowRateLimiter,
    StructuredLogger,
    build_backup_command,
    build_restore_command,
    redis_readiness,
    validate_deployment_environment,
)
from shared.security import AccessScope


class SecurityOperationsTests(unittest.TestCase):
    def test_access_scope_and_refresh_rotation(self) -> None:
        tokens = TokenService("a-secure-development-secret-value-123")
        access = tokens.issue("user", Role.USER, (AccessScope.MEMORY,))
        self.assertEqual(tokens.verify(access, AccessScope.MEMORY).subject, "user")
        with self.assertRaises(PermissionError):
            tokens.verify(access, AccessScope.SCREEN)

        refresh = tokens.issue("user", Role.USER, (AccessScope.MEMORY,), kind="refresh")
        rotated = tokens.rotate_refresh(refresh)
        with self.assertRaises(PermissionError):
            tokens.verify(refresh, kind="refresh")
        self.assertEqual(tokens.verify(rotated, kind="refresh").subject, "user")

    def test_consent_export_deletion_and_redacted_audit(self) -> None:
        governance = GovernanceStore()
        governance.set_consent(ConsentRecord("user", "screen-control", True, [AccessScope.SCREEN]))
        governance.require("user", "screen-control", AccessScope.SCREEN)
        governance.record("user", "screen.read", "screen-control", {"value": "api_key=abc123"})
        exported = governance.export_user("user")
        self.assertIn("[REDACTED]", exported["audit"][-1]["details"]["value"])
        governance.delete_user("user")
        self.assertEqual(governance.export_user("user"), {"consents": [], "audit": []})

    def test_rate_limit_and_metrics(self) -> None:
        limiter = SlidingWindowRateLimiter(2, 10)
        self.assertTrue(limiter.allow("user", 1))
        self.assertTrue(limiter.allow("user", 2))
        self.assertFalse(limiter.allow("user", 3))
        self.assertTrue(limiter.allow("user", 12))
        metrics = MetricsRegistry()
        metrics.increment("requests")
        metrics.observe("latency_ms", 12.5)
        self.assertEqual(metrics.snapshot()["counters"]["requests"], 1)

    def test_structured_logging_and_redis_readiness(self) -> None:
        logger = StructuredLogger("gateway")
        event = logger.emit("startup", "gateway booted", build="0.1.0")
        self.assertEqual(event["service"], "gateway")
        self.assertEqual(event["message"], "gateway booted")
        self.assertIn("timestamp", event)
        self.assertIn("gateway", logger.snapshot()[-1]["service"])

        ready = redis_readiness(
            "redis",
            "redis://localhost:6379/0",
            timeout=0.1,
            ping=lambda url: True,
        )
        self.assertTrue(ready.ready)
        self.assertIn("redis://localhost:6379/0", ready.detail)

    def test_deployment_validation_and_backup_restore_helpers(self) -> None:
        valid = validate_deployment_environment(
            {
                "SEDUX_ENV": "production",
                "SEDUX_AUTH_SECRET": "a-very-long-and-strong-secret-value-12345",
                "DATABASE_URL": "postgresql://sedux:sedux@postgres:5432/sedux",
                "REDIS_URL": "redis://redis:6379/0",
            }
        )
        self.assertTrue(valid)

        invalid = validate_deployment_environment(
            {
                "SEDUX_ENV": "production",
                "SEDUX_AUTH_SECRET": "short",
            }
        )
        self.assertFalse(invalid)

        backup = build_backup_command("sedux", "/tmp/sedux-backup.dump")
        self.assertIn("pg_dump", backup)
        self.assertIn("--format=custom", backup)
        self.assertIn("sedux", backup)
        self.assertIn("/tmp/sedux-backup.dump", backup)

        restore = build_restore_command("/tmp/sedux-backup.dump", "sedux_restore")
        self.assertIn("pg_restore", restore)
        self.assertIn("sedux_restore", restore)


if __name__ == "__main__":
    unittest.main()