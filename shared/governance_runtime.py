from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta

from shared.governance import AuditEvent, ConsentRecord, RetentionPolicy
from shared.security import AccessScope, redact_sensitive_text


class GovernanceStore:
    def __init__(self) -> None:
        self.consents: dict[tuple[str, str], ConsentRecord] = {}
        self.audit: list[AuditEvent] = []

    def set_consent(self, record: ConsentRecord) -> ConsentRecord:
        timestamped = replace(record, created_at=record.created_at or datetime.now(UTC).isoformat())
        self.consents[(record.user_id, record.purpose)] = timestamped
        self.record(record.user_id, "consent.updated", record.purpose, {"granted": record.granted})
        return timestamped

    def require(self, user_id: str, purpose: str, scope: AccessScope) -> None:
        record = self.consents.get((user_id, purpose))
        if record is None or not record.granted or scope not in record.scopes:
            raise PermissionError("active consent is required")

    def record(self, actor: str, action: str, entity: str, details: dict[str, object]) -> AuditEvent:
        cleaned = {key: redact_sensitive_text(str(value)) for key, value in details.items()}
        event = AuditEvent(actor, action, entity, cleaned, datetime.now(UTC).isoformat())
        self.audit.append(event)
        return event

    def export_user(self, user_id: str) -> dict[str, object]:
        return {
            "consents": [item.to_dict() for (owner, _), item in self.consents.items() if owner == user_id],
            "audit": [item.to_dict() for item in self.audit if item.actor == user_id],
        }

    def delete_user(self, user_id: str) -> None:
        self.consents = {key: value for key, value in self.consents.items() if key[0] != user_id}
        self.audit = [event for event in self.audit if event.actor != user_id]

    def enforce_retention(self, policy: RetentionPolicy, now: datetime | None = None) -> int:
        cutoff = (now or datetime.now(UTC)) - timedelta(days=policy.ttl_days)
        kept: list[AuditEvent] = []
        removed = 0
        for event in self.audit:
            timestamp = datetime.fromisoformat(event.timestamp) if event.timestamp else datetime.now(UTC)
            if event.entity == policy.purpose and timestamp < cutoff:
                removed += 1
            else:
                kept.append(event)
        self.audit = kept
        return removed
