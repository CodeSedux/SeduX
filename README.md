# SeduX

Realtime AI assistant foundation for voice, avatar, emotion, task, home, and device workflows.

## Reference System

The repository contains an executable CPU-safe reference system for the SeduX control plane and its core domain runtimes. It includes service health and readiness, versioned events, request tracing, avatar state replay, emotion fusion, bounded voice processing, safe screen and home actions, task dead letters, isolated memory, authentication, consent workflows, metrics, and a multi-view browser client. External models and production integrations remain replaceable adapters.

Run the tests:

```bash
python -m unittest discover -s tests -v
```

Run the gateway:

```bash
uvicorn services.gateway.app:app --host 127.0.0.1 --port 8080
```

Run the frontend:

```bash
python -m http.server 4173 --directory frontend
```

Then inspect `http://127.0.0.1:8080/health`, `http://127.0.0.1:8080/readiness`, `http://127.0.0.1:8080/metrics`, or `http://127.0.0.1:4173`.

Container setup and rollback guidance is in [docs/OPERATIONS.md](docs/OPERATIONS.md). Product limits and benchmark rules are in [docs/PRODUCT_SCOPE.md](docs/PRODUCT_SCOPE.md).

The complete dependency-aware backlog is in [IMPLEMENTATION_TODO.md](IMPLEMENTATION_TODO.md). Unchecked items require external integration, broader validation, or production evidence and are intentionally not represented as complete.
