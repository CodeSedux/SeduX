from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class EnvironmentSettings:
    app_name: str = "sedux"
    env: str = os.getenv("SEDUX_ENV", "development")
    log_level: str = os.getenv("SEDUX_LOG_LEVEL", "INFO")
    host: str = os.getenv("SEDUX_HOST", "127.0.0.1")
    port: int = int(os.getenv("SEDUX_PORT", "8080"))
    debug: bool = os.getenv("SEDUX_DEBUG", "false").lower() == "true"
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    postgres_url: str = os.getenv("DATABASE_URL", "postgresql://sedux:sedux@localhost:5432/sedux")

    def __post_init__(self) -> None:
        if not self.app_name or not str(self.app_name).strip():
            raise ValueError("app_name must be non-empty")
        if not self.env or not str(self.env).strip():
            raise ValueError("env must be non-empty")
        if not self.host or not str(self.host).strip():
            raise ValueError("host must be non-empty")
        if not isinstance(self.port, int) or self.port <= 0:
            raise ValueError("port must be a positive integer")
        if not self.redis_url or not str(self.redis_url).strip():
            raise ValueError("redis_url must be non-empty")
        if not self.postgres_url or not str(self.postgres_url).strip():
            raise ValueError("postgres_url must be non-empty")


DEFAULT_SETTINGS = EnvironmentSettings()


def get_settings() -> EnvironmentSettings:
    return EnvironmentSettings()
