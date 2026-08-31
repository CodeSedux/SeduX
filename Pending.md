This conversation was generated with Duck.ai (https://duck.ai) using OpenAI's GPT-5.6 Luna Model. AI chats may display inaccurate or offensive information (see https://duckduckgo.com/duckai/privacy-terms for more info).

====================

User prompt 1 of 2 - 30/8/2026, 8:42:13 pm:
Analyseed Report of "GitHub.com/CodeSeduX/SeduX" Progress, Working Model and Next Steps

GPT-5.6 Luna:
<!-- **Analyzing search requests**

I need to interpret the user’s requests, which likely involves analyzing the current repository. I’ll perform a web search to gather information since that seems necessary here. Oh, and I noticed a possible typo: "Analyseed." I’ll be sure to search for the exact term instead, keeping it clear to avoid any confusion. My goal is to understand the context better so I can help the user effectively. -->
<!--  -->
<!-- **Preparing the report**

I need to formulate a report, and the first step is to inspect the README. I’ll make a to-do list and consider how the project tree is structured. It might also be helpful to look at the raw URLs involved. I believe reviewing the documentation in parallel will help me understand what’s necessary for the report. It's a practical approach to ensure everything’s covered! -->
<!--  -->
<!--  -->
# SeduX Progress, Working Model, and Next Steps

**Repository reviewed:** `CodeSedux/SeduX`  
**Assessment date:** August 30, 2026

## Executive assessment

SeduX is currently an **early architectural foundation**, not yet a functioning Jarvis-level assistant. The repository has a small executable control plane with a gateway, service registry, shared contracts, and tests. The broader capabilities—voice interaction, LLM reasoning, 3D avatar rendering, emotion recognition, screen automation, home control, task scheduling, and persistent memory—are primarily documented as planned architecture and backlog items.

The repository currently has:

- 5 commits
- 1 fork
- 0 stars
- A `main` branch
- Core directories for `services`, `shared`, and `tests`
- Build and planning documents
- A dependency-free gateway that can run without model weights, API keys, GPUs, databases, or external infrastructure <citation src="1"></citation>

The most accurate maturity classification is:

> **Phase 0 / Foundation prototype: executable control-plane slice, with the product architecture specified but most product functionality unimplemented.**

## What is working now

The current implementation appears intentionally limited but useful as a first vertical slice.

### Executable control plane

The repository currently provides:

- A shared service-status and health contract
- A standard-library-based gateway
- A service registry
- Health-check endpoints
- Contract tests
- A dependency-free local execution path

The documented commands are:

```bash
python -m unittest discover -s tests -v
python -m services.gateway.main
```

The gateway exposes:

```text
http://127.0.0.1:8080/health
http://127.0.0.1:8080/services
```

This is a sensible first milestone because it validates the basic service-discovery model without requiring expensive infrastructure or AI models. The repository explicitly states that the first slice is designed to run in a clean Python environment. <citation src="1"></citation>

### Architecture and planning

The project has a detailed build document covering:

- Backend services
- Frontend structure
- Voice processing
- LLM integration
- Avatar animation
- Emotion analysis
- Screen automation
- Scheduling
- Memory
- Home automation
- Security
- Deployment
- Performance targets

The documentation describes a seven-service backend model consisting of an API gateway, voice, avatar, LLM, emotion, task, home, and screen services. <citation src="2"></citation>

### Backlog quality

The implementation backlog is one of the stronger parts of the repository. It organizes the work into 15 tracks and states that a track should not be considered complete until its tests, security checks, and operational documentation pass. It also identifies dependencies between infrastructure, frontend, AI capabilities, automation, and governance. <citation src="1"></citation>

## What is not implemented yet

The gap between the stated vision and the current code is substantial.

### Voice pipeline

The design specifies:

- Wake-word detection
- Streaming STT
- VAD
- TTS
- Audio backpressure
- Cancellation
- Viseme events
- Local and cloud speech adapters

The proposed implementation includes Whisper, Deepgram, CosyVoice, and ElevenLabs options. However, these are currently architecture decisions and backlog items rather than demonstrated working services. <citation src="2"></citation>

### LLM and orchestration

The design calls for:

- Streaming chat
- Function calling
- Context management
- Tool execution
- Intent parsing
- Multi-step action plans
- Model-serving infrastructure

The document proposes models such as Qwen and Llama with vLLM or similar infrastructure, but no working LLM service is shown in the current build slice. The gateway currently reports planned services rather than executing end-to-end reasoning workflows. <citation src="2"></citation>

### 3D avatar

The planned avatar subsystem includes:

- Three.js or React Three Fiber
- GLB/GLTF assets
- ARKit blend shapes
- Lip synchronization
- Gestures
- Eye tracking
- Animation state transitions
- Performance fallbacks

The design defines avatar states such as `idle`, `listening`, `thinking`, `speaking`, `reacting`, `gesturing`, and `sleeping`. These are well specified conceptually, but the repository does not yet demonstrate a functioning frontend or avatar runtime. <citation src="2"></citation>

### Emotion engine

The proposed emotion system combines:

- Facial analysis
- Vocal emotion
- Text emotion
- Gaze estimation
- Confidence-weighted fusion
- Valence, arousal, and dominance scoring

The backlog appropriately places CPU-safe text emotion analysis before more complex multimodal processing. That sequencing is practical, but the emotion service itself remains future work. <citation src="1"></citation>

### Device and screen automation

The intended system would support:

- Screenshots
- OCR
- UI-element detection
- Mouse and keyboard actions
- Computer-use agents
- File operations
- Confirmation for destructive actions
- Audit trails
- Emergency stop
- Sandboxing

This is a high-risk area and should not be implemented as unrestricted agent access. The backlog correctly calls for capability-based permissions, dry-run mode, target verification, rate limits, and sandboxing before broad automation. <citation src="1"></citation>

### Databases and operational infrastructure

The build plan specifies PostgreSQL, Redis, queues, migrations, authentication, observability, Docker, and Kubernetes. None of these appear to be part of the current executable foundation. The repository therefore does not yet have a demonstrated persistence, authentication, multi-user, deployment, or production-operations layer. <citation src="1,2"></citation>

## Working model

The intended SeduX working model is a **multimodal, event-driven assistant** organized around a gateway and specialized services.

A typical interaction is envisioned as:

```text
User input
  → voice, text, camera, screen, or scheduled event
  → gateway
  → intent and context processing
  → memory and emotion retrieval
  → LLM reasoning
  → action plan
  → task, home, screen, or device service
  → voice, text, and avatar response
```

For example:

```text
Voice request
  → wake-word detection
  → streaming speech recognition
  → intent extraction
  → memory lookup
  → emotion analysis
  → LLM action plan
  → task scheduling or home-control action
  → TTS response
  → avatar animation and lip-sync
```

The design separates:

- **Input layer:** voice, visual, screen, and scheduler events
- **Orchestration layer:** routing and state management
- **Cognition layer:** LLM reasoning and planning
- **Emotion layer:** multimodal analysis
- **Memory layer:** short- and long-term context
- **Action layer:** device, screen, and home actions
- **Output layer:** text, audio, avatar, and device feedback <citation src="2"></citation>

This separation is appropriate, but the project should avoid building all services simultaneously. The current architecture is broad enough that uncontrolled parallel implementation could produce many disconnected prototypes without a usable product.

## Main strengths

### Good foundation-first decision

Starting with a dependency-free gateway is technically sound. It makes the architecture testable before introducing GPUs, model downloads, external APIs, databases, and complex deployment requirements.

### Clear separation of planned responsibilities

The service boundaries are understandable and map to distinct operational concerns:

- Voice
- LLM
- Avatar
- Emotion
- Tasks
- Home automation
- Screen automation

### Strong attention to safety in the backlog

The planned controls—confirmation flows, audit records, scopes, dry runs, emergency stop, rate limits, and sandboxing—are especially important for screen and device automation. <citation src="1"></citation>

### Useful performance targets

The build document defines measurable goals such as:

- Approximately 800 ms end-to-end interaction latency
- STT word-error-rate targets
- Task-completion targets
- Avatar frame-rate targets
- Service-specific latency budgets

These targets are useful as long as they are converted into reproducible benchmarks rather than treated as current results. <citation src="2"></citation>

## Main weaknesses and risks

### Vision is far ahead of implementation

The project description presents a complete AI companion, but the actual repository is still at the control-plane stage. This creates a risk of communicating planned capabilities as if they already exist.

The README should clearly label features as:

- Implemented
- Stubbed
- Designed
- Planned
- Experimental

### Scope is too broad for the current stage

SeduX combines at least eight difficult product areas:

- Real-time speech
- LLM agents
- 3D graphics
- Emotion inference
- Computer use
- Smart-home control
- Scheduling
- Long-term memory

Each could be a standalone project. The immediate goal should be a narrow, reliable vertical slice rather than infrastructure for every capability.

### Some performance targets are aggressive

The proposed sub-800 ms full-turnaround target is difficult when the pipeline includes speech recognition, LLM generation, TTS, networking, and avatar rendering. It should be decomposed into:

- Time to first transcript
- Time to first response token
- Time to first audio byte
- Time to completed response
- Time to completed action
- End-to-end p50 and p95 latency

### Emotion detection needs careful product boundaries

Emotion classifiers can be inaccurate across cultures, disabilities, lighting conditions, accents, and communication styles. SeduX should treat emotion as an uncertain signal—not as a fact about the user—and should support disabling each modality independently.

### Device automation has a large security surface

Screen control, file operations, smart locks, alarms, purchases, and communications require distinct permission levels. A general-purpose “full device access” capability should not exist as one unrestricted tool.

### The planned stack is not yet sufficiently consolidated

The build document lists many alternatives: local and cloud STT, local and cloud TTS, multiple LLMs, vector databases, graph databases, queue systems, and home-automation protocols. This is useful for exploration but too broad for an initial implementation.

A first release should select one primary path for each layer.

## Recommended next steps

### 1. Finish and formalize the foundation milestone

Before adding AI models, complete the control-plane milestone with:

- Versioned service-status schema
- Request IDs
- Structured error responses
- Readiness versus liveness checks
- Configuration loading
- Typed service metadata
- Gateway integration tests
- CI for tests, formatting, and type checking
- A small local end-to-end test

Suggested exit criterion:

> A clean machine can clone the repository, install the documented runtime, start the gateway, query health and service endpoints, and pass all tests with one command.

### 2. Build one narrow vertical slice

The best next product slice is:

```text
Text input
  → gateway
  → deterministic intent parser
  → one safe task action
  → streamed text response
  → audit event
```

For example:

> “Remind me tomorrow at 9 AM to review the project.”

This slice would validate the most important foundations:

- Request handling
- Intent extraction
- Task creation
- Persistence
- Response streaming
- Error handling
- User confirmation
- Auditability

It avoids the complexity of GPUs, cameras, avatar assets, and unrestricted computer control.

### 3. Add persistence before advanced intelligence

Implement PostgreSQL or another clearly selected storage layer for:

- Users
- Conversations
- Messages
- Tasks
- Memory entries
- Audit events

Do not introduce long-term memory until the project has explicit behavior for:

- Creating memories
- Correcting memories
- Deleting memories
- Exporting memories
- Isolating users
- Excluding sensitive information

The backlog already identifies these requirements. <citation src="1"></citation>

### 4. Implement the task service before device automation

Task scheduling is more bounded and testable than computer use. Implement:

- One-time tasks
- Recurring tasks
- Time zones
- Cancellation
- Idempotency
- Retries
- Execution history
- Notifications
- Restart recovery

This will produce a useful assistant even without voice or an avatar.

### 5. Add text chat before voice

A text-based assistant can validate:

- Conversation state
- Tool calling
- Memory boundaries
- Permission handling
- Action confirmation
- LLM orchestration
- Observability

Once the text workflow is reliable, voice becomes an additional input/output transport rather than the foundation of the entire product.

### 6. Introduce voice using test doubles first

Before integrating Whisper or cloud speech APIs, add:

- Fake STT adapter
- Fake TTS adapter
- Deterministic audio fixtures
- Streaming event schemas
- Cancellation tests
- Bounded-buffer tests
- Latency instrumentation

Then add one real STT provider and one TTS provider. Keep local and cloud implementations behind the same interfaces.

### 7. Implement a basic avatar only after event contracts stabilize

Start with:

- A placeholder GLB model
- `idle`, `listening`, `thinking`, and `speaking` states
- Simple viseme playback
- WebSocket event handling
- Low-performance fallback

Do not begin with photorealism, gaze tracking, full emotion fusion, and complex procedural animation. The avatar should first prove that it can reliably reflect assistant state.

### 8. Treat automation as a separate security project

For screen and device actions, implement the following order:

1. Read-only capability discovery
2. Screenshot capture
3. Dry-run action plans
4. User confirmation
5. One reversible action
6. Post-action verification
7. Audit logging
8. Sandboxed execution
9. Broader capability expansion

Destructive actions, messages, purchases, account changes, locks, alarms, and system settings should require explicit confirmation every time unless the user has deliberately configured a narrowly scoped exception.

### 9. Convert the backlog into milestones

The current backlog is comprehensive but still too document-oriented. Convert it into GitHub issues or milestones with:

- One capability per issue
- Dependencies
- Acceptance criteria
- Test requirements
- Security requirements
- Owner
- Definition of done
- Demo command or endpoint

A practical milestone sequence would be:

- **M0:** Gateway and contracts
- **M1:** Persistence and authentication
- **M2:** Text chat and task scheduling
- **M3:** Tool permissions and audit logs
- **M4:** Voice transport
- **M5:** Basic avatar
- **M6:** Home automation
- **M7:** Screen automation
- **M8:** Multimodal emotion and advanced memory

## Suggested repository improvements

The repository would benefit from the following changes:

- Rename or clarify the current milestone in the README
- Add a status matrix showing implemented versus planned features
- Add a quick-start section with expected output
- Add `CONTRIBUTING.md`
- Add a license
- Add CI workflows
- Add formatting and typing configuration
- Add an architecture diagram for the current system, separate from the future system
- Add API examples for `/health` and `/services`
- Add a changelog
- Add issue templates for features, bugs, and architecture decisions
- Remove or clearly mark unsupported performance claims
- Record exact supported Python versions and platform assumptions

## Overall conclusion

SeduX has a promising architectural direction and a sensible first implementation choice: a minimal, dependency-free control plane. Its strongest current asset is not the assistant functionality itself, but the structured plan for building that functionality.

The immediate priority should be to turn the architecture into a **small, demonstrable, end-to-end assistant workflow**. A text-based task assistant with persistence, permissions, audit logs, and reliable scheduling would provide substantially more validation than adding additional design documents or prematurely integrating every AI subsystem.

The next meaningful definition of progress should be:

> A user can submit a request, SeduX can interpret it, ask for confirmation when needed, execute one safe action, persist the result, return a response, and expose a complete audit trail—all locally and reproducibly.

That milestone would establish the working model on which voice, avatar, emotion, home automation, and screen control can be added safely.

--------------------

User prompt 2 of 2 - 30/8/2026, 9:15:46 pm:
Detailed Implemention Plan for Next Step cover all details of unimplementation

GPT-5.6 Luna:
<!--  -->
# SeduX Detailed Implementation Plan

This plan converts the current SeduX foundation into a working assistant incrementally. It covers the unimplemented areas identified in the repository: persistence, authentication, text interaction, LLM orchestration, tasks, memory, voice, avatar, emotion analysis, home automation, screen automation, security, observability, testing, and deployment.

The implementation should proceed in phases. Each phase must produce a runnable system before the next phase begins.

## Target architecture

```text
                    ┌─────────────────────┐
                    │  Web / CLI / Mobile  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │     API Gateway      │
                    │ auth, routing, SSE,  │
                    │ WebSocket, rate limit│
                    └──────┬─────┬─────────┘
                           │     │
             ┌─────────────┘     └─────────────┐
             ▼                                 ▼
      ┌──────────────┐                  ┌──────────────┐
      │ Conversation │                  │ Task Service │
      │ / LLM        │                  │ scheduler    │
      └──────┬───────┘                  └──────┬───────┘
             │                                 │
             ▼                                 ▼
      ┌──────────────┐                  ┌──────────────┐
      │ Memory       │                  │ Action       │
      │ Service      │                  │ Executor     │
      └──────┬───────┘                  └──────┬───────┘
             │                                 │
             ▼                    ┌────────────┴────────────┐
      ┌──────────────┐             ▼                         ▼
      │ Emotion      │      ┌──────────────┐          ┌──────────────┐
      │ Service      │      │ Home Control │          │ Screen Agent │
      └──────────────┘      └──────────────┘          └──────────────┘

      Voice Service ───────► Conversation Service
            │
            ├── STT
            └── TTS

      Avatar Client ◄────── event stream from Gateway
```

The gateway should remain the public entry point. Internal services should communicate through versioned contracts rather than directly sharing implementation details.

---

# Phase 0: Stabilize the current foundation

## Objectives

Before implementing new assistant functionality, make the existing gateway and service registry production-ready enough to support future services.

## Repository changes

Recommended structure:

```text
SeduX/
├── services/
│   ├── gateway/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── router.py
│   │   ├── middleware.py
│   │   └── health.py
│   ├── conversation/
│   ├── llm/
│   ├── memory/
│   ├── tasks/
│   ├── voice/
│   ├── emotion/
│   ├── avatar/
│   ├── home/
│   └── screen/
├── shared/
│   ├── contracts/
│   ├── errors/
│   ├── events/
│   ├── security/
│   ├── logging/
│   └── settings/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   └── fixtures/
├── migrations/
├── deployment/
│   ├── docker/
│   ├── compose/
│   └── kubernetes/
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── security/
│   └── operations/
└── pyproject.toml
```

## Required gateway improvements

Implement:

- Request IDs
- Structured JSON errors
- Configuration loading from environment variables
- Liveness endpoint
- Readiness endpoint
- Service timeout handling
- Service-unavailable handling
- Request logging
- API versioning
- CORS configuration
- Rate limiting
- Graceful shutdown

Suggested endpoints:

```text
GET    /health/live
GET    /health/ready
GET    /api/v1/services
POST   /api/v1/conversations
GET    /api/v1/conversations/{conversation_id}
POST   /api/v1/conversations/{conversation_id}/messages
GET    /api/v1/events
POST   /api/v1/tasks
GET    /api/v1/tasks
PATCH  /api/v1/tasks/{task_id}
DELETE /api/v1/tasks/{task_id}
```

## Shared response format

Every response should follow a consistent structure.

Success:

```json
{
  "request_id": "req_123",
  "data": {},
  "error": null
}
```

Failure:

```json
{
  "request_id": "req_123",
  "data": null,
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "The requested task does not exist.",
    "retryable": false
  }
}
```

## Definition of done

- Gateway starts on a clean machine.
- All existing tests pass.
- Every request receives a request ID.
- Failed service calls return structured errors.
- Readiness accurately reflects unavailable dependencies.
- No service exposes unversioned public endpoints.

---

# Phase 1: Configuration, persistence, and identity

## Objectives

Add durable storage and a minimum identity model before implementing conversations, tasks, or memory.

## Technology selection

Use one primary stack initially:

- PostgreSQL for durable relational data
- Redis only for temporary state, queues, locks, and rate limiting
- SQL migration tool
- One Python database access layer
- UUID identifiers
- UTC timestamps stored in the database
- User-local time zones stored separately

Do not add a vector database until ordinary persistence and memory lifecycle operations are working.

## Core database entities

### Users

```text
users
-----
id
external_subject
display_name
timezone
locale
status
created_at
updated_at
```

### Sessions

```text
sessions
--------
id
user_id
token_hash
expires_at
created_at
revoked_at
last_seen_at
```

### Conversations

```text
conversations
-------------
id
user_id
title
status
created_at
updated_at
archived_at
```

### Messages

```text
messages
--------
id
conversation_id
role
content
content_type
model_name
token_count
created_at
metadata_json
```

Allowed roles:

```text
user
assistant
system
tool
```

### Audit events

```text
audit_events
------------
id
user_id
request_id
actor
action
resource_type
resource_id
decision
parameters_hash
result_summary
created_at
```

Never store unrestricted screenshots, audio, API keys, or full sensitive tool arguments in the audit table.

## Authentication

Initially implement local authentication suitable for development:

- User creation through a protected administrative command
- Bearer tokens
- Hashed token storage
- Expiration
- Revocation
- Per-user authorization checks

Later support an external identity provider through an adapter:

```python
class IdentityProvider:
    def authenticate(self, credential: str) -> UserIdentity:
        ...
```

The rest of the application must depend on `UserIdentity`, not a specific authentication vendor.

## Configuration

Create typed configuration sections:

```text
SeduXConfig
├── server
├── database
├── redis
├── llm
├── voice
├── security
├── home
├── screen
├── observability
└── feature_flags
```

Example environment variables:

```text
SEDUX_ENV=development
SEDUX_HOST=127.0.0.1
SEDUX_PORT=8080
SEDUX_DATABASE_URL=postgresql://...
SEDUX_REDIS_URL=redis://...
SEDUX_LLM_PROVIDER=mock
SEDUX_LLM_MODEL=
SEDUX_ENABLE_SCREEN_CONTROL=false
SEDUX_ENABLE_HOME_CONTROL=false
```

Secrets must be loaded through environment variables or a secret manager. Never commit secrets to configuration files.

## Definition of done

- Database migrations run from an empty database.
- A user can authenticate.
- Conversations and messages survive process restarts.
- Users cannot read another user’s records.
- Audit records are generated for authenticated actions.
- The application runs with a mock database or test database in CI.

---

# Phase 2: Conversation service and text interface

## Objectives

Create the first complete user workflow:

```text
User text
  → conversation service
  → context assembly
  → deterministic/mock response
  → persisted assistant message
```

Do this before connecting a real LLM.

## Conversation API

Create a conversation:

```http
POST /api/v1/conversations
```

Request:

```json
{
  "title": "Project planning"
}
```

Send a message:

```http
POST /api/v1/conversations/{id}/messages
```

Request:

```json
{
  "content": "Remind me tomorrow at 9 AM to review the project.",
  "stream": true
}
```

Streaming event format:

```json
{
  "type": "message.started",
  "message_id": "msg_123"
}
```

```json
{
  "type": "message.delta",
  "message_id": "msg_123",
  "text": "I can create that reminder."
}
```

```json
{
  "type": "message.completed",
  "message_id": "msg_123"
}
```

Failure:

```json
{
  "type": "message.failed",
  "message_id": "msg_123",
  "code": "MODEL_TIMEOUT"
}
```

## Context assembly

Implement a context builder with explicit limits:

```text
system instructions
+ user preferences
+ recent conversation messages
+ relevant memories
+ available tools
+ current time and time zone
```

The context builder must enforce:

- Maximum message count
- Maximum character count
- Maximum token estimate
- Tool-specific context rules
- Sensitive-data filtering
- Conversation ownership

## Deterministic intent parser

Before integrating an LLM, implement simple intent detection for:

- Create reminder
- List reminders
- Cancel reminder
- Get current time
- General conversation

Example internal representation:

```json
{
  "intent": "task.create",
  "confidence": 0.96,
  "arguments": {
    "title": "review the project",
    "due_at": "2026-08-31T09:00:00",
    "timezone": "user"
  }
}
```

The parser should never execute an action directly. It only produces a proposed action for policy evaluation.

---

# Phase 3: LLM service and tool orchestration

## Objectives

Add model support without coupling the rest of SeduX to one model vendor.

## LLM adapter

Define a provider-neutral interface:

```python
class LLMProvider:
    def generate(
        self,
        messages: list[dict],
        tools: list[dict],
        options: GenerationOptions,
    ) -> LLMResponse:
        ...
```

Streaming interface:

```python
class StreamingLLMProvider(LLMProvider):
    def stream(self, request: LLMRequest):
        yield LLMEvent(...)
```

Implement providers in this order:

1. Mock provider
2. Local development provider
3. One hosted provider
4. Additional providers only when required

## Tool schema

Every tool must declare:

```json
{
  "name": "task.create",
  "description": "Create a reminder.",
  "risk_level": "low",
  "requires_confirmation": true,
  "parameters": {
    "type": "object",
    "properties": {
      "title": {"type": "string"},
      "due_at": {"type": "string"},
      "timezone": {"type": "string"}
    },
    "required": ["title", "due_at"]
  }
}
```

## Orchestration loop

```text
1. Receive user message.
2. Load conversation and user context.
3. Ask the LLM for text or a tool call.
4. Validate the tool name.
5. Validate arguments against the schema.
6. Evaluate permissions.
7. Request confirmation if required.
8. Execute the tool.
9. Record the audit event.
10. Return the tool result to the LLM.
11. Generate the final assistant response.
12. Persist all messages and events.
```

Set limits for:

- Maximum model turns
- Maximum tool calls per request
- Maximum execution time
- Maximum output tokens
- Maximum retry count

The orchestrator must stop on loops, repeated calls, invalid arguments, or policy violations.

## Confirmation state

Store pending confirmations:

```text
pending_confirmations
---------------------
id
user_id
conversation_id
tool_name
validated_arguments_json
risk_level
expires_at
status
created_at
```

The user must confirm the exact action, not an ambiguous general instruction.

Example:

```text
SeduX wants to create a reminder:
“Review the project”
Tomorrow at 09:00
Time zone: Europe/London

Confirm?
```

---

# Phase 4: Task service and scheduler

## Objectives

Implement a complete, reliable task system. This is the first useful assistant capability and should become the reference implementation for service design.

## Task schema

```text
tasks
-----
id
user_id
title
description
status
schedule_type
due_at
recurrence_rule
timezone
next_run_at
last_run_at
retry_count
created_at
updated_at
cancelled_at
```

Statuses:

```text
pending
running
completed
failed
cancelled
paused
```

## Supported schedules

Start with:

- One-time timestamp
- Daily recurrence
- Weekly recurrence
- Simple interval

Add full calendar recurrence rules later.

## Scheduler design

Use a durable polling scheduler first:

```text
1. Query tasks where next_run_at <= now.
2. Acquire a database lock.
3. Mark task as running.
4. Execute the task.
5. Record execution result.
6. Compute next_run_at.
7. Mark completed or failed.
```

Use an idempotency key:

```text
task_id + scheduled_execution_time
```

This prevents duplicate execution after process restarts.

## Task execution history

```text
task_executions
---------------
id
task_id
scheduled_for
started_at
completed_at
status
error_code
result_json
```

## Required behavior

- Correct time-zone conversion
- Restart recovery
- Duplicate-execution prevention
- Retry with backoff
- Cancellation
- Pause and resume
- Missed-task policy
- User notification
- Execution audit events

## Definition of done

A user can create, list, update, cancel, and complete a reminder. The task remains correct after restarting the service and changing the process schedule.

---

# Phase 5: Memory service

## Objectives

Add explicit, user-controlled memory rather than silently storing all conversations.

## Memory categories

```text
preference
profile
project
relationship
routine
instruction
fact
```

## Memory schema

```text
memories
--------
id
user_id
category
content
source
confidence
status
created_at
updated_at
expires_at
deleted_at
```

Statuses:

```text
active
superseded
deleted
pending_review
```

## Memory operations

Implement:

```text
memory.create
memory.list
memory.search
memory.update
memory.delete
memory.forget_all
```

The system should support natural commands such as:

- “Remember that I prefer concise answers.”
- “What do you remember about me?”
- “Forget my preference for concise answers.”
- “Forget everything about this project.”

## Memory extraction

Do not automatically save every fact. Begin with:

1. Explicit user instruction to remember
2. User-approved memory suggestions
3. No implicit sensitive-memory storage

Memory suggestions should be shown before persistence:

```text
I can remember that you prefer concise answers. Save this?
```

## Search strategy

Initial implementation:

- PostgreSQL full-text search
- Category filtering
- User ownership filtering
- Recency weighting

Later implementation:

- Embeddings
- Vector search
- Hybrid lexical and semantic ranking
- Memory deduplication

## Sensitive information policy

Do not automatically store:

- Passwords
- API keys
- Authentication tokens
- Financial account numbers
- Government identifiers
- Health information
- Private communications

---

# Phase 6: Voice service

## Objectives

Add voice as a transport around the existing text conversation workflow.

## Voice pipeline

```text
microphone
  → audio chunks
  → VAD
  → wake word
  → STT
  → conversation service
  → response text
  → TTS
  → audio chunks
  → client playback
```

## Audio event contracts

```json
{
  "type": "audio.input.started",
  "session_id": "voice_123"
}
```

```json
{
  "type": "transcript.partial",
  "text": "remind me tomorrow"
}
```

```json
{
  "type": "transcript.final",
  "text": "Remind me tomorrow at nine."
}
```

```json
{
  "type": "audio.output.chunk",
  "sequence": 12,
  "audio_format": "pcm_s16le",
  "data": "..."
}
```

## Adapters

Define:

```python
class SpeechToTextProvider:
    def transcribe_stream(self, audio_stream):
        ...
```

```python
class TextToSpeechProvider:
    def synthesize_stream(self, text_stream):
        ...
```

Implement:

- Fake provider for tests
- One local STT provider
- One local or hosted TTS provider

## Required voice behavior

- Partial transcripts
- Final transcript
- Silence detection
- User interruption
- Cancellation
- Backpressure
- Maximum recording duration
- Audio format validation
- Provider timeout
- Fallback error response

The voice service must not duplicate conversation logic. It should convert audio to text and text to audio.

---

# Phase 7: Avatar service and frontend

## Objectives

Add a minimal visual client that reflects assistant state.

## Initial avatar states

Implement only:

```text
idle
listening
thinking
speaking
error
```

Each state should map to an event:

```json
{
  "type": "avatar.state",
  "state": "thinking",
  "timestamp": "2026-08-30T12:00:00Z"
}
```

## Frontend responsibilities

The client should:

- Connect to the gateway
- Authenticate
- Display conversation text
- Render streaming response tokens
- Show confirmation prompts
- Display task status
- Subscribe to avatar events
- Handle reconnects
- Show service errors

## Avatar implementation order

1. Static placeholder
2. State machine
3. Basic idle animation
4. Speaking animation
5. Simple viseme playback
6. Gesture events
7. Emotion-driven animation
8. Performance fallback

Do not make the avatar responsible for business logic. It should render events generated elsewhere.

## Performance requirements

Measure:

- Frame rate
- Initial model-load time
- Memory usage
- WebSocket latency
- Time from response event to animation
- Behavior on low-end hardware

---

# Phase 8: Emotion service

## Objectives

Add emotion signals only after the basic conversation loop is stable.

## Initial implementation

Start with text-based signals:

```json
{
  "valence": -0.2,
  "arousal": 0.5,
  "dominance": 0.3,
  "labels": ["frustrated"],
  "confidence": 0.61,
  "source": "text",
  "timestamp": "2026-08-30T12:00:00Z"
}
```

The service should return uncertainty and source metadata.

## Fusion model

Later combine:

```text
text signal
+ vocal signal
+ facial signal
+ conversation context
```

Use confidence-weighted fusion:

\[
E = \frac{\sum_i w_i c_i E_i}{\sum_i w_i c_i}
\]

where:

- \(E_i\) is a modality’s estimate
- \(c_i\) is confidence
- \(w_i\) is the configured modality weight

If confidence is low, return “unknown” rather than forcing a label.

## Product behavior

Emotion should influence:

- Response tone
- Whether to ask a clarifying question
- Avatar animation
- Optional support suggestions

Emotion should not be treated as:

- A diagnosis
- Proof of intent
- A basis for punishment
- A basis for automated high-impact decisions

Provide per-modality disable controls.

---

# Phase 9: Home automation

## Objectives

Add safe integration with home devices using capabilities and explicit permissions.

## Adapter interface

```python
class HomeProvider:
    def list_devices(self, user_id: str):
        ...

    def get_state(self, device_id: str):
        ...

    def set_state(self, device_id: str, command: dict):
        ...
```

## Capability model

Each device should expose narrowly scoped capabilities:

```json
{
  "device_id": "light_living_room",
  "name": "Living room light",
  "capabilities": [
    "light.read",
    "light.set_brightness",
    "light.turn_on",
    "light.turn_off"
  ]
}
```

## Risk classes

```text
read-only: no confirmation
reversible low-risk action: configurable confirmation
security-sensitive action: always confirm
destructive or hazardous action: deny by default
```

High-risk examples include:

- Locks
- Alarms
- Cameras
- Garage doors
- Heating systems
- Purchases
- Safety devices

## Execution flow

```text
1. Discover device.
2. Validate ownership.
3. Validate capability.
4. Validate target state.
5. Show exact proposed action.
6. Obtain confirmation.
7. Execute.
8. Verify final state.
9. Record audit event.
```

---

# Phase 10: Screen automation

## Objectives

Add computer-use capabilities only after the permission and audit framework is complete.

## Initial restrictions

Start with read-only operations:

- Capture screenshot
- List visible applications
- Extract visible text
- Identify basic UI regions

Do not initially permit:

- Shell execution
- File deletion
- Sending messages
- Purchases
- Account changes
- Credential entry
- Unrestricted keyboard control

## Capability interface

```python
class ScreenCapability:
    name: str
    risk_level: str
    requires_confirmation: bool

    def validate(self, arguments):
        ...

    def dry_run(self, arguments):
        ...

    def execute(self, arguments):
        ...

    def verify(self, result):
        ...
```

## Safe execution flow

```text
observe
  → formulate plan
  → show plan
  → dry run
  → confirm
  → execute one step
  → verify
  → request confirmation for next risky step
```

## Emergency controls

Implement:

- Global stop endpoint
- Local keyboard stop shortcut
- Session cancellation
- Maximum action count
- Maximum execution time
- Focused-window verification
- Target-coordinate validation
- Action replay log
- Automatic shutdown on uncertainty

Screen automation should run in a sandbox or isolated worker process.

---

# Phase 11: Security and policy enforcement

## Central policy engine

Create one policy service used by every tool.

```python
class PolicyDecision:
    allowed: bool
    requires_confirmation: bool
    reason: str
    restrictions: dict
```

```python
class PolicyEngine:
    def evaluate(
        self,
        user,
        tool,
        arguments,
        context,
    ) -> PolicyDecision:
        ...
```

## Policy checks

Every action should be checked for:

- Authenticated user
- Resource ownership
- Tool availability
- Capability scope
- Risk level
- Confirmation state
- Rate limits
- Time restrictions
- Target validity
- Session validity
- Emergency-stop status

## Never trust model output

LLM-generated tool calls are untrusted input. Validate:

- Tool name
- JSON structure
- Argument types
- String length
- URL schemes
- File paths
- Device IDs
- Numeric ranges
- Allowed enum values

## Prompt-injection defense

Treat external content as data, not instructions. This includes:

- Web pages
- Emails
- Documents
- Screen text
- Calendar entries
- Smart-home device names

The system must not let external text override system policies or authorization rules.

## Audit requirements

Record:

- Who initiated the action
- Which conversation initiated it
- Tool name
- Risk level
- Confirmation status
- Sanitized argument summary
- Result
- Failure reason
- Timestamp
- Request ID

---

# Phase 12: Observability

## Logging

Use structured logs with:

```text
timestamp
level
service
request_id
user_id_hash
conversation_id
operation
duration_ms
status
error_code
```

Do not log:

- Passwords
- API keys
- Full audio
- Full screenshots
- Full private messages
- Unredacted tool arguments

## Metrics

Track:

- Request count
- Error count
- Request latency
- LLM latency
- Time to first token
- STT latency
- TTS latency
- Tool execution latency
- Task success rate
- Confirmation acceptance rate
- Queue depth
- Retry count
- WebSocket reconnect count
- Memory search latency

## Tracing

Use a trace ID across:

```text
gateway
→ conversation
→ LLM
→ tool
→ database
```

This is essential for diagnosing slow or duplicated actions.

---

# Phase 13: Testing strategy

## Unit tests

Test:

- Configuration validation
- Service registry
- Request routing
- Authentication
- Authorization
- Input schemas
- Intent parsing
- Context trimming
- Memory filtering
- Recurrence calculation
- Policy evaluation
- Tool argument validation
- Audio buffering
- Emotion fusion

## Contract tests

Every service should have tests for:

- Health response
- Service metadata
- Request schema
- Response schema
- Error schema
- Version compatibility

## Integration tests

Required workflows:

1. Create user.
2. Authenticate.
3. Create conversation.
4. Send text message.
5. Create reminder.
6. Confirm reminder.
7. Restart service.
8. Verify reminder still exists.
9. Execute reminder.
10. Verify audit record.

## Safety tests

Test that:

- A user cannot access another user’s task.
- An unconfirmed high-risk action is not executed.
- Invalid tool arguments are rejected.
- Replayed confirmation tokens fail.
- Expired confirmations fail.
- Duplicate scheduler execution is prevented.
- Emergency stop cancels automation.
- Prompt injection does not bypass policy.
- Sensitive fields are removed from logs.

## Load tests

Measure:

- Concurrent chat requests
- Streaming connections
- Task scheduler throughput
- Database connection limits
- LLM timeout behavior
- Voice-session concurrency
- WebSocket reconnect storms

---

# Phase 14: Deployment

## Local development

Provide a single command such as:

```bash
docker compose up
```

The local environment should include:

- Gateway
- PostgreSQL
- Redis
- Mock LLM
- Mock STT
- Mock TTS
- Web frontend
- Worker
- Observability dashboard, if available

## Staging

Use:

- Separate credentials
- Test model providers
- Restricted home devices
- Sandboxed screen automation
- Synthetic user data
- Automatic database migrations
- Backups
- Health checks
- Rollback procedure

## Production readiness

Before production:

- Secrets manager
- TLS
- Database backup and restore test
- Rate limiting
- Resource quotas
- Dependency pinning
- Vulnerability scanning
- Error alerting
- Incident response procedure
- Data deletion procedure
- Audit retention policy
- Disaster recovery test

---

# Recommended implementation order

The complete sequence should be:

```text
1. Gateway stabilization
2. Configuration system
3. Database migrations
4. Authentication and authorization
5. Conversation persistence
6. Text conversation API
7. Deterministic intent parser
8. Task service
9. Confirmation workflow
10. Audit logging
11. LLM adapter
12. Tool orchestration
13. Memory service
14. Text-to-speech and speech-to-text adapters
15. Real voice streaming
16. Basic frontend
17. Basic avatar state machine
18. Text emotion analysis
19. Home-control adapter
20. Screen read-only capabilities
21. Advanced avatar behavior
22. Multimodal emotion
23. Expanded automation
24. Production deployment
```

Do not reverse this order by starting with the avatar, full voice stack, or unrestricted computer-use agent. Those components depend on stable event contracts, authentication, persistence, policy enforcement, and observability.

# Immediate next milestone

The next implementation milestone should be:

## M1 — Persistent text assistant with safe task execution

It should support:

- User authentication
- Conversation creation
- Message persistence
- Text responses
- Reminder creation
- Reminder listing
- Reminder cancellation
- Confirmation for task creation
- Task persistence
- Scheduler execution
- Audit logging
- Structured errors
- Unit and integration tests
- Docker-based local startup

A successful demonstration would look like this:

```text
User: Remind me tomorrow at 9 AM to review the project.

SeduX: I can create this reminder:
       Review the project
       August 31, 2026 at 09:00
       Time zone: user time zone

       Confirm?

User: Confirm.

SeduX: Reminder created.

System: Task executes at the scheduled time.

SeduX: Reminder: review the project.
```

This milestone proves the core SeduX operating model: input, interpretation, policy, confirmation, execution, persistence, scheduling, and response. Voice, emotion, avatar, home control, and screen control can then be added as interchangeable layers over a functioning core.