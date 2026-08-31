# Delivery Roadmap

| Milestone | Owner | Exit Criteria |
| --- | --- | --- |
| Control plane | Platform | Health, readiness, metrics, request IDs, local E2E pass |
| Media runtime | Experience | Avatar replay, fusion, bounded audio, adapter tests pass |
| Safe actions | Automation | Confirmation, audit, isolation, stale-state, stop tests pass |
| Production adapters | Integrations | PostgreSQL, Redis, model, Home Assistant, MQTT contract suites pass |
| Release | Operations | CI, backup restore, rollback, threat review, deployment validation pass |

Metrics tracked from the first environment are request latency, service readiness, task attempts/success/dead letters, blocked sensitive actions, consent changes, and retention deletions.