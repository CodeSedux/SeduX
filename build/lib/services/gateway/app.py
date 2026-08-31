from __future__ import annotations

from time import perf_counter
from typing import Any

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from shared.contracts import build_service_statuses, health_payload
from shared.orchestration import ServiceOrchestrator
from shared.operations import MetricsRegistry
from shared.protocol import API_VERSION, new_request_id


class ServiceListResponse(BaseModel):
    services: list[dict[str, Any]]


metrics_registry = MetricsRegistry()


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.ready = True
    yield
    application.state.ready = False


app = FastAPI(title="SeduX Gateway", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:4173", "http://localhost:4173"],
    allow_methods=["GET"],
    allow_headers=["Accept"],
)
service_orchestrator = ServiceOrchestrator()


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or new_request_id()
    started_at = perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-API-Version"] = API_VERSION
    response.headers["Server-Timing"] = f'app;dur={(perf_counter() - started_at) * 1000:.2f}'
    metrics_registry.increment("http_requests_total")
    metrics_registry.observe("http_request_duration_ms", (perf_counter() - started_at) * 1000)
    return response


@app.get("/health")
def health() -> dict[str, Any]:
    return health_payload("gateway")


@app.get("/services", response_model=ServiceListResponse)
def services() -> dict[str, Any]:
    return {"services": build_service_statuses()}


@app.get("/readiness")
def readiness() -> dict[str, Any]:
    return service_orchestrator.check_all().to_dict()


@app.get("/metrics")
def metrics() -> dict[str, object]:
    return metrics_registry.snapshot()
