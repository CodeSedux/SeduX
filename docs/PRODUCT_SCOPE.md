# Product Scope and Acceptance

## Supported Platforms

- Reference backend: CPython 3.12 on Linux x86_64 and arm64.
- Reference client: current Chrome, Edge, Firefox, and Safari with ES modules.
- CPU mode is mandatory. NVIDIA GPU and cloud model adapters are optional profiles.

## Non-Goals

- Shipping or redistributing model weights, proprietary avatar assets, or cloud credentials.
- Unattended destructive screen, lock, alarm, purchase, or message-send actions.
- Claiming production accuracy or availability from synthetic fixtures.

## Consent Boundaries

Microphone, camera, screen, memory, and home scopes are disabled until explicit purpose-specific consent exists. Submit, system, lock, and alarm actions require a fresh confirmation. Audit exports redact credentials.

## Reproducible Benchmarks

Run benchmarks on a named CPU/GPU, OS, Python version, adapter version, sample set hash, and warm-up count. Report p50/p95/p99 latency, throughput, errors, and sample count. STT WER and emotion accuracy must use versioned labeled fixtures; uptime and task success must use exported metrics over a declared interval. Aspirational targets in the build document are not acceptance evidence.