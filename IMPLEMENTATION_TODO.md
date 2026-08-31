# SeduX Implementation Backlog

This backlog translates the build guide into 15 implementation tracks. A track is complete only when its tests, security checks, and operational documentation pass.

## Part 1: Vision, Scope, and Acceptance Criteria
- [x] Record product scope and target outcomes.
- [x] Define the first executable milestone: a health-checked control plane.
- [x] Replace aspirational metrics with reproducible benchmark definitions.
- [x] Document supported platforms, non-goals, and consent boundaries.

## Part 2: System Architecture
- [x] Add shared service status and health contracts.
- [x] Add a gateway health endpoint.
- [x] Add versioned REST and WebSocket schemas, request IDs, timeouts, retries, and tracing.
- [x] Validate the architecture with a local end-to-end test.

## Part 3: Backend Infrastructure
- [x] Create FastAPI entry points with typed settings and lifecycle hooks.
- [x] Add PostgreSQL migrations for users, conversations, messages, tasks, memory, and audit logs.
- [ ] Add Redis connectivity, rate limiting, queues, structured logs, metrics, and readiness probes.
- [x] Add CPU-only and GPU Docker Compose profiles.

## Part 4: Frontend and User Interface
- [ ] Scaffold an accessible React and TypeScript client.
- [x] Build chat, service status, task, home, screen, and settings views.
- [ ] Add typed WebSocket reconnection and responsive visual regression tests.
- [x] Keep model and device controls consent-driven.

## Part 5: 3D Avatar and Motion
- [ ] Add a placeholder avatar scene and documented GLB asset contract.
- [x] Implement avatar state transitions and deterministic animation replay.
- [x] Add blend-shape and viseme mapping.
- [x] Add frame-time telemetry and low-performance fallback validation.

## Part 6: Emotion Detection and Expression
- [x] Define modality result schemas and confidence semantics.
- [x] Implement CPU-safe text emotion analysis first.
- [x] Implement confidence-aware fusion with missing-input handling.
- [ ] Add optional face, voice, gaze, consent, retention, and accuracy fixtures.

## Part 7: Voice Pipeline
- [x] Define streaming audio, transcript, TTS, and viseme events.
- [x] Add CI-safe STT and TTS test doubles.
- [x] Implement VAD, backpressure, cancellation, and bounded buffers.
- [ ] Add optional local and cloud adapters with latency measurements.

## Part 8: Screen Automation and Device Access
- [x] Define capability-based actions and immutable audit events.
- [x] Implement read-only screenshot and OCR interfaces.
- [x] Require confirmation for submit, destructive, and system actions.
- [ ] Add dry-run, target verification, rate limits, emergency stop, and sandboxing.

## Part 9: Task Scheduling and Orchestration
- [x] Add typed task lifecycle and execution contracts.
- [x] Implement one-time and recurring schedules with timezone correctness.
- [x] Add idempotency, retries, dead letters, conflict detection, and history.
- [x] Test restarts, duplicate delivery, and daylight-saving changes.

## Part 10: Memory and Personality
- [x] Implement bounded short-term context.
- [x] Add explicit memory creation, retrieval, correction, export, and deletion.
- [x] Add replaceable embedding and graph adapters.
- [x] Test user isolation and sensitive-memory exclusion.

## Part 11: Home Automation
- [x] Define normalized device, capability, state, and scene schemas.
- [ ] Add Home Assistant and MQTT adapters with permission checks.
- [ ] Add stale-state, unavailable-device, duplicate-command, and rollback tests.
- [x] Confirm sensitive actions such as locks and alarms.

## Part 12: Security, Privacy, and Governance
- [x] Add authentication, refresh rotation, roles, and scopes.
- [ ] Add secure secret and encryption-key handling.
- [x] Add consent, retention, export, deletion, redaction, and audit workflows.
- [ ] Run dependency, container, API, and threat-model reviews.

## Part 13: Development Roadmap
- [x] Establish this dependency-aware 15-part backlog.
- [ ] Convert tracks into milestone issues with owners and exit criteria.
- [ ] Add CI gates for formatting, typing, tests, and security.
- [x] Track latency, reliability, task success, and privacy metrics from day one.

## Part 14: Technology Stack
- [x] Pin supported runtime, database, cache, and adapter versions.
- [x] Separate CPU dependencies from optional GPU and cloud dependencies.
- [x] Record licenses, model terms, data usage, and provenance.
- [ ] Add upgrade tests and a hardware compatibility matrix.

## Part 15: Implementation, Testing, and Operations
- [x] Add a dependency-free smoke-testable gateway foundation.
- [x] Add Dockerfiles, environment templates, setup commands, and migrations.
- [ ] Add unit, integration, end-to-end, load, and failure-injection tests.
- [ ] Add backups, observability, health checks, rollback runbooks, and deployment validation.

## Current Build Slice

The current reference slice is independent of model weights and cloud credentials. It provides tested control-plane and domain behavior with optional production adapters. Remaining unchecked work is primarily external integration, production security evidence, visual/load/failure testing, timezone scheduling, and deployment rehearsal.