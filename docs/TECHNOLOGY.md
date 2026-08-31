# Technology and Compatibility

| Component | Supported Version | License / Data Note |
| --- | --- | --- |
| Python | 3.12 | PSF; local runtime |
| FastAPI | 0.141.1 | MIT; no hosted data transfer |
| Uvicorn | 0.52.0 | BSD-3-Clause |
| PostgreSQL | 16.10 | PostgreSQL License; durable user data |
| Redis | 7.4.5 | Redis source terms; ephemeral data only |
| NVIDIA CUDA image | 12.8.1 | NVIDIA terms; optional GPU profile |

CPU mode requires 2 cores and 2 GB RAM for the control plane. GPU/model adapters must document model license, source URL, immutable revision, dataset provenance, telemetry, and provider retention before activation. Upgrade pull requests run compile, unit, local E2E, frontend syntax, migration review, and container health checks.