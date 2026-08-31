import unittest
from datetime import datetime, timezone

from shared.storage import (
    POSTGRES_SCHEMA,
    PostgresTable,
    QueueEnvelope,
    RedisBackedRateLimiter,
    RedisKey,
    RedisNamespace,
    RedisQueue,
)


class StorageContractTests(unittest.TestCase):
    def test_postgres_schema_covers_core_persistence_tables(self) -> None:
        names = {definition.name for definition in POSTGRES_SCHEMA}
        self.assertEqual(
            names,
            {
                PostgresTable.USERS,
                PostgresTable.CONVERSATIONS,
                PostgresTable.MESSAGES,
                PostgresTable.TASKS,
                PostgresTable.MEMORY_ENTRIES,
                PostgresTable.AUDIT_EVENTS,
            },
        )
        self.assertIn("user_id", next(
            definition.columns
            for definition in POSTGRES_SCHEMA
            if definition.name is PostgresTable.MEMORY_ENTRIES
        ))

    def test_redis_key_has_stable_namespace(self) -> None:
        key = RedisKey(RedisNamespace.TASK_QUEUE, "daily-briefing")
        self.assertEqual(key.render(), "sedux:task-queue:daily-briefing")
        with self.assertRaises(ValueError):
            RedisKey(RedisNamespace.SESSION, "bad:key").render()

    def test_queue_envelope_is_serializable_and_validated(self) -> None:
        timestamp = datetime(2026, 8, 28, tzinfo=timezone.utc)
        envelope = QueueEnvelope(
            queue="task-execution",
            task_id="task-123",
            payload={"type": "briefing"},
            enqueued_at=timestamp,
        )
        self.assertEqual(envelope.to_dict()["enqueued_at"], timestamp.isoformat())
        self.assertEqual(envelope.to_dict()["payload"]["type"], "briefing")
        with self.assertRaises(ValueError):
            QueueEnvelope(queue="", task_id="task-123", payload={})
        with self.assertRaises(ValueError):
            QueueEnvelope(queue="task-execution", task_id="task-123", payload={}, attempt=0)

    def test_redis_queue_preserves_fifo_order(self) -> None:
        queue = RedisQueue("task-execution")
        queue.enqueue(QueueEnvelope(queue="task-execution", task_id="task-1", payload={"n": 1}))
        queue.enqueue(QueueEnvelope(queue="task-execution", task_id="task-2", payload={"n": 2}))

        items = queue.dequeue(10)
        self.assertEqual([item.task_id for item in items], ["task-1", "task-2"])
        self.assertEqual(queue.pending(), 0)

    def test_redis_rate_limiter_enforces_windowed_limits(self) -> None:
        limiter = RedisBackedRateLimiter(limit=2, window_seconds=10)

        first = limiter.allow("user-1")
        second = limiter.allow("user-1")
        third = limiter.allow("user-1")

        self.assertTrue(first.allowed)
        self.assertTrue(second.allowed)
        self.assertFalse(third.allowed)
        self.assertGreaterEqual(third.retry_after, 0.0)


if __name__ == "__main__":
    unittest.main()
