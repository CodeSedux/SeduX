from __future__ import annotations

from time import perf_counter
from typing import Any

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from shared.contracts import build_service_statuses, health_payload
from shared.orchestration import ServiceOrchestrator
from shared.operations import MetricsRegistry, StructuredLogger
from shared.protocol import API_VERSION, new_request_id


class ServiceListResponse(BaseModel):
    services: list[dict[str, Any]]


metrics_registry = MetricsRegistry()
logger = StructuredLogger("gateway")


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.ready = True
    yield
    application.state.ready = False


app = FastAPI(title="SeduX Gateway", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:4173",
        "http://localhost:4173",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Accept", "Authorization", "Content-Type", "X-Request-ID"],
    allow_credentials=True,
)
service_orchestrator = ServiceOrchestrator()


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or new_request_id()
    started_at = perf_counter()
    logger.emit(
        "request_received",
        "gateway request started",
        method=request.method,
        path=request.url.path,
        request_id=request_id,
    )
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.emit(
            "request_failed",
            "gateway request failed",
            method=request.method,
            path=request.url.path,
            request_id=request_id,
            error=str(exc),
        )
        raise
    finally:
        elapsed_ms = (perf_counter() - started_at) * 1000
        response_headers = getattr(locals().get("response"), "headers", None)
        if response_headers is not None:
            response_headers["X-Request-ID"] = request_id
            response_headers["X-API-Version"] = API_VERSION
            response_headers["Server-Timing"] = f"app;dur={elapsed_ms:.2f}"
        metrics_registry.increment("http_requests_total")
        metrics_registry.observe("http_request_duration_ms", elapsed_ms)
    return response


@app.get("/health")
def health() -> dict[str, Any]:
    return health_payload("gateway", ready=True)


@app.get("/health/live")
def health_live() -> dict[str, Any]:
    return health_payload("gateway", ready=True, detail="live")


@app.get("/health/ready")
def health_ready() -> dict[str, Any]:
    report = service_orchestrator.check_all().to_dict()
    return {
        "service": "gateway",
        "status": report["status"],
        "ready": report["ready"],
        "timestamp": report["checked_at"],
        "services": report["services"],
    }


@app.get("/services", response_model=ServiceListResponse)
def services() -> dict[str, Any]:
    return {"services": build_service_statuses()}


@app.get("/readiness")
def readiness() -> dict[str, Any]:
    return service_orchestrator.check_all().to_dict()


@app.get("/metrics")
def metrics() -> dict[str, object]:
    return metrics_registry.snapshot()
