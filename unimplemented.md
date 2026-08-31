# SeduX Unimplemented Steps

This document lists the remaining work for SeduX in a clean, step-by-step order so the team can build the project in logical phases without jumping ahead into high-risk functionality.

## Current Reality

The repository already contains a functioning foundation for:
- gateway health and readiness
- service registry and control-plane contracts
- runtime orchestration primitives
- task, memory, screen, home, emotion, and security domain contracts
- local test coverage for the implemented reference slice

The remaining work is primarily in production-grade infrastructure, integrations, security, deployment, and broad feature completion.

---

## Step 1: Stabilize the Core Platform

### Goal
Make the current control plane ready to support production-quality service growth.

### Tasks
- [ ] Add Redis connectivity for cache, rate limiting, and queues
- [ ] Implement structured logs with request correlation IDs
- [ ] Add metrics and observability endpoints for all core services
- [ ] Add service readiness and liveness probes
- [ ] Add timeout handling and graceful failure paths
- [ ] Add request tracing and consistent error responses
- [ ] Standardize API versioning across all public endpoints
- [ ] Add startup and shutdown lifecycle checks

### Definition of done
- All core services expose stable health and readiness states
- Gateway can handle failures without crashing
- Metrics expose request counts, latency, and state transitions
- The platform remains runnable in local and CI environments

---

## Step 2: Production-Ready Persistence and Security

### Goal
Establish durable data flow and safe access control before adding advanced assistant behavior.

### Tasks
- [ ] Add secure secret management and encryption-key handling
- [ ] Implement PostgreSQL-backed user, session, conversation, task, memory, and audit storage
- [ ] Add role-based access control and scoped permissions
- [ ] Add user isolation rules for memory, tasks, and conversations
- [ ] Add consent handling, retention, export, redaction, and deletion workflows
- [ ] Add authentication refresh rotation and token invalidation
- [ ] Add dependency review and API security review
- [ ] Add threat-model review for tool execution and device access

### Definition of done
- Users cannot access another user’s data
- Secrets are not stored in source files or plain config
- Audit logs exist for all sensitive actions
- Security and privacy controls are testable and documented

---

## Step 3: Build the Text Interaction Core

### Goal
Create the first end-to-end assistant workflow using text as the primary interface.

### Tasks
- [ ] Add conversation creation and retrieval APIs
- [ ] Add message persistence and conversation history
- [ ] Add context assembly rules for system prompts, memory, and tools
- [ ] Implement deterministic intent parsing for task and reminder flows
- [ ] Add LLM abstraction layer with a mock provider first
- [ ] Add tool invocation validation and schema checks
- [ ] Add confirmation flow for risky or irreversible actions
- [ ] Add conversation-level event streaming for text responses

### Definition of done
- A user can send a text request and receive a persisted response
- The assistant can safely formulate tasks and reminders
- Risky actions require confirmation
- Tool use is validated before execution

---

## Step 4: Task Service and Scheduler Completion

### Goal
Build the first truly useful autonomous feature set: task creation, scheduling, and execution.

### Tasks
- [ ] Complete one-time and recurring task models
- [ ] Add time zone handling and daylight-saving-safe scheduling
- [ ] Add idempotency keys for execution safety
- [ ] Add retry and dead-letter flows
- [ ] Add task conflict detection and history tracking
- [ ] Add cancellation, pause, and restart recovery
- [ ] Add scheduler polling or queue-based dispatch
- [ ] Add task lifecycle events and observability metrics

### Definition of done
- Tasks can be created, listed, cancelled, retried, and completed
- Recurring scheduling behaves correctly across time zones
- Restarting the system does not duplicate executed work
- Dead letters and failure history are visible

---

## Step 5: Memory and Personalization Layer

### Goal
Move from simple task execution to user-aware memory and personalization.

### Tasks
- [ ] Add explicit memory creation and recall APIs
- [ ] Add memory correction and explicit deletion flows
- [ ] Add sensitive-content filtering and exclusion rules
- [ ] Add user-scoped memory isolation checks
- [ ] Add export support for user memory records
- [ ] Add replaceable embedding and graph adapter interfaces
- [ ] Add memory retention and cleanup policies
- [ ] Add tests for user isolation and privacy boundaries

### Definition of done
- Memory can be created, recalled, corrected, and removed safely
- Sensitive data is excluded from general retrieval
- Different users do not access each other’s memory

---

## Step 6: Voice Pipeline Implementation

### Goal
Add voice as a transport layer rather than as the first core product requirement.

### Tasks
- [ ] Add optional local and cloud STT/TTS adapters behind a common interface
- [ ] Add deterministic CI-safe voice adapters and latency fixtures
- [ ] Add VAD, cancellation, and bounded-audio buffer handling
- [ ] Add audio event schemas for transcript, TTS, and viseme flow
- [ ] Add latency measurement for each adapter type
- [ ] Add backpressure handling for streaming audio
- [ ] Add tests for cancellation and buffer overflow behavior

### Definition of done
- Voice adapters can be swapped without breaking the system
- Latency and reliability can be measured in a reproducible way
- Audio streams remain bounded, cancellable, and safe under overload

---

## Step 7: Avatar and Visual Presence Layer

### Goal
Create a minimal avatar runtime that reflects the assistant state without depending on heavy visual complexity.

### Tasks
- [ ] Add a placeholder avatar scene and GLB asset contract
- [ ] Add idle, listening, thinking, speaking, and fallback states
- [ ] Add deterministic animation replay and event-driven state transitions
- [ ] Add viseme mapping and simple lip-sync behavior
- [ ] Add frame-time telemetry and low-performance fallback handling
- [ ] Add browser-side event handling for avatar updates

### Definition of done
- The avatar visibly reflects assistant state and events
- The system degrades gracefully under low performance
- The asset contract and state model are documented

---

## Step 8: Emotion Detection and Multimodal Signals

### Goal
Add emotion analysis in a privacy-aware and confidence-driven way.

### Tasks
- [ ] Add optional face, voice, and gaze signal fixtures
- [ ] Add consent-aware and retention-aware emotion data handling
- [ ] Add confidence-aware fusion logic across modalities
- [ ] Add missing-input handling for partial sensor data
- [ ] Add accuracy and retention validation fixtures
- [ ] Add user opt-out behavior for emotion collection

### Definition of done
- Emotion signals are modeled as uncertain observations, not absolute truths
- Missing or low-confidence inputs are ignored safely
- User consent and retention controls are enforced

---

## Step 9: Home Automation Integration

### Goal
Add smart-home capabilities behind strict permission and safety rules.

### Tasks
- [ ] Add Home Assistant adapter with permission checks
- [ ] Add MQTT adapter interface and safe command validation
- [ ] Add stale-state detection and unavailable-device handling
- [ ] Add duplicate-command prevention
- [ ] Add rollback and recovery logic for failed device actions
- [ ] Add tests for state drift, device unavailability, and command duplication
- [ ] Confirm sensitive actions like locks, alarms, and security controls require explicit approval

### Definition of done
- Device commands are validated before execution
- State drift and stale device data are handled safely
- Sensitive actions remain gated and auditable

---

## Step 10: Screen Automation Safety Layer

### Goal
Build screen automation as a permissioned, auditable, reversible system.

### Tasks
- [ ] Add read-only screen discovery and screenshot interfaces
- [ ] Add OCR and permission-based target validation
- [ ] Add dry-run action planning
- [ ] Add target verification before execution
- [ ] Add rate limits and emergency-stop behavior
- [ ] Add sandboxing and execution isolation
- [ ] Add confirmation gates for destructive or security-sensitive actions
- [ ] Add tests for confirmation, stop behavior, and safe execution boundaries

### Definition of done
- Screen actions cannot be executed without proper permission and confirmation
- Destructive operations are gated and reversible where possible
- The system can stop safely during unsafe conditions

---

## Step 11: Frontend and Browser Experience

### Goal
Create a usable interactive client for the control plane and assistant workflows.

### Tasks
- [ ] Scaffold an accessible React and TypeScript client
- [ ] Add the main chat and service status views
- [ ] Add task dashboard and settings views
- [ ] Add typed WebSocket connection handling and reconnection logic
- [ ] Add responsive UI testing and visual regression checks
- [ ] Add consent-driven model and device controls

### Definition of done
- The frontend is usable for basic interaction and service visibility
- Reconnection and failure states are handled gracefully
- User controls reflect consent and permissions

---

## Step 12: CI, Testing, and Quality Gates

### Goal
Convert the repository into a reliable engineering project with continuous validation.

### Tasks
- [ ] Add CI gates for formatting, linting, and type checking
- [ ] Add unit, integration, end-to-end, failure-injection, and load tests
- [ ] Add compatibility tests for upgrades and dependency changes
- [ ] Add test coverage for storage, security, scheduling, and automation
- [ ] Add hardware compatibility matrix and environment validation

### Definition of done
- The repo passes automated validation on every change
- Key workflows are covered by real integration tests
- The system is reproducible across standard development environments

---

## Step 13: Deployment, Backups, and Operations

### Goal
Prepare the project for safe rollout and recovery.

### Tasks
- [ ] Add backup procedures and restore validation
- [ ] Add observability dashboards and alert rules
- [ ] Add deployment health checks and rollback runbooks
- [ ] Add container and environment deployment validation
- [ ] Add load and resilience rehearsal procedures
- [ ] Add operational documentation for service restarts, recovery, and incident response

### Definition of done
- Services can be deployed with known rollback steps
- Backups and restore paths are documented and tested
- Operations teams have a working runbook for failures and recoveries

---

## Recommended Build Order

The best order for implementation is:

1. Core platform stabilization
2. Persistence and security
3. Text conversation and task orchestration
4. Memory and scheduling
5. Voice transport
6. Avatar presence
7. Emotion layer
8. Home automation
9. Screen automation
10. Frontend refinement
11. Release validation and operations

This ordering reduces risk and keeps the project progressing toward a working, auditable assistant rather than building disconnected features too early.

---

## Recommended First Milestone

The first strong milestone should be:

### Milestone: Safe text-first assistant

- conversation model works
- user-scoped task creation works
- memory isolation works
- confirmation flow works
- audit logging works
- restart-safe task state works

This milestone proves the real operating model of SeduX before adding camera, audio, avatar, home, or screen complexity.

---

## Final Recommendation

Do not build all features in parallel. Build in layers:
- foundation
- safe task automation
- memory and control
- voice and avatar
- smart-home and screen automation
- deployment readiness

This keeps SeduX realistic, testable, and safe.
