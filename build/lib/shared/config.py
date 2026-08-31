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


DEFAULT_SETTINGS = EnvironmentSettings()


def get_settings() -> EnvironmentSettings:
    return EnvironmentSettings()
