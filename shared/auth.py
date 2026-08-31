from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
import hashlib
import hmac
import json
import os
from uuid import uuid4

from shared.security import AccessScope


class Role(StrEnum):
    USER = "user"
    OPERATOR = "operator"
    ADMIN = "admin"


@dataclass(frozen=True)
class AuthClaims:
    subject: str
    role: Role
    scopes: tuple[AccessScope, ...]
    expires_at: int
    token_id: str
    kind: str = "access"


class TokenService:
    def __init__(self, secret: str | None = None) -> None:
        self._secret = (secret or os.getenv("SEDUX_AUTH_SECRET", "")).encode()
        if len(self._secret) < 32:
            raise ValueError("SEDUX_AUTH_SECRET must contain at least 32 characters")
        self._revoked: set[str] = set()

    def issue(self, subject: str, role: Role, scopes: tuple[AccessScope, ...], ttl_seconds: int = 900, kind: str = "access") -> str:
        if not subject or ttl_seconds < 1:
            raise ValueError("subject and a positive TTL are required")
        payload = {
            "sub": subject,
            "role": role.value,
            "scopes": [scope.value for scope in scopes],
            "exp": int((datetime.now(UTC) + timedelta(seconds=ttl_seconds)).timestamp()),
            "jti": uuid4().hex,
            "kind": kind,
        }
        encoded = self._encode(json.dumps(payload, separators=(",", ":")).encode())
        signature = self._encode(hmac.new(self._secret, encoded.encode(), hashlib.sha256).digest())
        return f"{encoded}.{signature}"

    def verify(self, token: str, required_scope: AccessScope | None = None, kind: str = "access") -> AuthClaims:
        try:
            encoded, signature = token.split(".", 1)
            expected = self._encode(hmac.new(self._secret, encoded.encode(), hashlib.sha256).digest())
            if not hmac.compare_digest(signature, expected):
                raise PermissionError("invalid token signature")
            payload = json.loads(self._decode(encoded))
            claims = AuthClaims(
                payload["sub"], Role(payload["role"]), tuple(AccessScope(scope) for scope in payload["scopes"]),
                int(payload["exp"]), payload["jti"], payload["kind"],
            )
        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as error:
            raise PermissionError("invalid token") from error
        if claims.token_id in self._revoked or claims.expires_at <= int(datetime.now(UTC).timestamp()) or claims.kind != kind:
            raise PermissionError("token is expired, revoked, or has the wrong type")
        if required_scope is not None and required_scope not in claims.scopes:
            raise PermissionError("required scope is missing")
        return claims

    def rotate_refresh(self, refresh_token: str, ttl_seconds: int = 86400) -> str:
        claims = self.verify(refresh_token, kind="refresh")
        self._revoked.add(claims.token_id)
        return self.issue(claims.subject, claims.role, claims.scopes, ttl_seconds, "refresh")

    @staticmethod
    def _encode(value: bytes) -> str:
        return base64.urlsafe_b64encode(value).rstrip(b"=").decode()

    @staticmethod
    def _decode(value: str) -> bytes:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
