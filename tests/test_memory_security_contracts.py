import unittest

from shared.governance import AuditEvent, ConsentRecord, RetentionPolicy
from shared.memory import MemoryEntry, MemoryOperation, MemoryScope
from shared.security import AccessScope, redact_sensitive_text


class MemorySecurityGovernanceContractsTests(unittest.TestCase):
    def test_memory_entry_tracks_scope_and_operation(self) -> None:
        entry = MemoryEntry(
            user_id="user-123",
            scope=MemoryScope.USER,
            operation=MemoryOperation.CREATE,
            key="favorite_color",
            value="blue",
            summary="Prefers blue interactions.",
        )
        self.assertEqual(entry.scope, MemoryScope.USER)
        self.assertEqual(entry.operation, MemoryOperation.CREATE)
        self.assertEqual(entry.key, "favorite_color")

    def test_redaction_preserves_non_sensitive_content(self) -> None:
        text = "Token abc123 should be hidden and email user@example.com kept masked."
        redacted = redact_sensitive_text(text)
        self.assertIn("[REDACTED]", redacted)
        self.assertIn("[EMAIL]", redacted)
        self.assertNotIn("abc123", redacted)

    def test_consent_record_and_audit_event_are_valid(self) -> None:
        consent = ConsentRecord(
            user_id="user-123",
            purpose="voice_analysis",
            granted=True,
            scopes=[AccessScope.VOICE, AccessScope.MEMORY],
        )
        event = AuditEvent(
            actor="system",
            action="memory_export",
            entity="memory:user-123",
            details={"requested_by": "user-123"},
        )
        self.assertTrue(consent.granted)
        self.assertIn(AccessScope.VOICE, consent.scopes)
        self.assertEqual(event.action, "memory_export")

    def test_retention_policy_requires_positive_ttl(self) -> None:
        policy = RetentionPolicy(purpose="voice", ttl_days=30)
        self.assertEqual(policy.ttl_days, 30)
        self.assertEqual(policy.purpose, "voice")

    def test_retention_policy_rejects_non_positive_ttl(self) -> None:
        with self.assertRaises(ValueError):
            RetentionPolicy(purpose="voice", ttl_days=0)
        with self.assertRaises(ValueError):
            RetentionPolicy(purpose="voice", ttl_days=-1)

    def test_memory_store_enforces_user_isolation_and_expiration_cleanup(self) -> None:
        from datetime import UTC, datetime, timedelta

        from shared.memory_runtime import MemoryStore

        store = MemoryStore()
        created = store.create(MemoryEntry(
            user_id="user-1",
            scope=MemoryScope.USER,
            operation=MemoryOperation.CREATE,
            key="favorite_color",
            value="blue",
            summary="Prefers calmer colors.",
        ))

        self.assertEqual(created.value, "blue")
        self.assertEqual(store.recall("user-1", "favorite_color").value, "blue")
        self.assertEqual(store.export("user-2"), [])

        updated = store.correct("user-1", "favorite_color", "green")
        self.assertEqual(updated.value, "green")

        expired = MemoryEntry(
            user_id="user-1",
            scope=MemoryScope.USER,
            operation=MemoryOperation.CREATE,
            key="old_fact",
            value="stale",
            expires_at=(datetime.now(UTC) - timedelta(days=1)).isoformat(),
        )
        store._entries[("user-1", "old_fact")] = expired
        self.assertEqual(store.purge_expired(datetime.now(UTC)), 1)

        store.delete("user-1", "favorite_color")
        with self.assertRaises(KeyError):
            store.get("user-1", "favorite_color")


if __name__ == "__main__":
    unittest.main()
