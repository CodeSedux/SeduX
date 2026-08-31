# Contributor Guide for SeduX

This document defines how to contribute safely, keep the project aligned with its product boundaries, and use the repository’s approval and push workflow without violating trust or safety requirements.

## 1. Mission and Boundaries

SeduX is a CPU-safe reference system for voice, avatar, emotion, task, home, and device orchestration. The project is intended to provide a transparent, auditable foundation for experimentation and controlled orchestration, not a production-grade deployment platform with unrestricted device control.

Contributors must respect these core boundaries:

- Use CPU-safe reference logic only unless a clearly labeled optional profile is involved.
- Do not ship model weights, proprietary avatar assets, or credentials.
- Do not enable destructive or high-risk actions without explicit confirmation flows.
- Do not claim production reliability from synthetic fixtures or unverified benchmarks.
- Keep consent, security, and user-control requirements explicitly enforced in code and documentation.

## 2. Safety Rules

### 2.1 Consent and User Control

- Microphone, camera, screen, memory, and home access are disabled until explicit consent exists.
- Submit, lock, alarm, and other high-impact system actions require a fresh confirmation step.
- Any flow involving personal data, memory access, or device control must clearly state purpose and scope.
- Audit exports must redact credentials and sensitive identifiers.

### 2.2 Security Requirements

- Never commit secrets, private keys, tokens, cloud credentials, or local environment values.
- Validate authentication, consent, and escalation paths before merging changes.
- Keep user-visible operations bounded and traceable.
- Prefer explicit permission checks over broad or implicit access.

### 2.3 AI and Automation Safety

- Treat model outputs as untrusted unless validated by deterministic checks or the project’s required governance logic.
- Respect privacy boundaries for memory and conversation state.
- Do not introduce actions that can trigger purchases, lockouts, alarms, or message sending without confirmation.
- Avoid hidden or automatic payload execution on the user’s system.

### 2.4 Operational Safety

- Reproduce changes with tests and deterministic validation before merging.
- Do not modify deployment or rollback paths without updating docs and validation steps.
- Keep service readiness and health checks passing before release.
- For infrastructure changes, preserve backup/restore and rollback readiness.

## 3. Contribution Standards

### 3.1 Before You Start

- Read the project overview in [README.md](README.md).
- Review the product constraints in [docs/PRODUCT_SCOPE.md](docs/PRODUCT_SCOPE.md).
- Review the operational guidance in [docs/OPERATIONS.md](docs/OPERATIONS.md).
- Check the backlog and open work in [IMPLEMENTATION_TODO.md](IMPLEMENTATION_TODO.md).

### 3.2 Required Checks

Run the project validation suite before submitting changes:

```bash
python -m unittest discover -s tests -v
```

If your change affects runtime behavior, service health, or integration contracts, also validate the relevant service endpoints or flows described in the operational docs.

### 3.3 Code Quality Expectations

- Keep changes small, specific, and traceable.
- Prefer readable, testable logic over clever shortcuts.
- Add or update tests for behavior changes.
- Include documentation when adding new runtime behaviors, user permissions, or new product boundaries.
- Avoid broad refactors that mix unrelated changes into one commit.

### 3.4 Pull Request Expectations

Every contribution should include:

- A clear title and summary
- The reason for the change
- Safety or consent implications, if applicable
- Verification commands and results
- Linkage to any tracked issue or work item

If a change touches consent, memory, device control, or security paths, include a short risk review in the PR description.

## 4. Auto Approval Policy

Low-risk changes may qualify for auto-approval when all of the following are true:

- The change is limited to documentation, tests, or small non-invasive code fixes.
- There are no permission, consent, or security boundary changes.
- The project’s relevant test suite passes.
- No credentials, secrets, or deployment values are exposed.
- The change does not modify destructive or high-risk actions.
- The patch remains within the project’s declared product scope.

Auto approval is intended only for safe, narrow, low-risk updates. Any change involving:

- authentication or authorization
- memory or personal data handling
- screen/home/device action execution
- deployment configuration
- model integration
- external service credentials

must receive explicit review before merge.

### Auto-approval checklist

Before marking a change as auto-approved, verify:

```bash
python -m unittest discover -s tests -v
```

Then confirm:

- no secrets were added
- no consent logic was bypassed
- no dangerous runtime actions were introduced
- the change matches the project scope
- documentation was updated if needed

## 5. Branch and Push Workflow

Use a clean branch for each change.

```bash
git checkout -b feature/your-change
# make your edits
git add .
git commit -m "Describe your change"
git push origin HEAD
```

If the repository uses a fork-based contribution model, push to your fork and open a PR against the main project repository.

### Recommended repo workflow

1. Start from a clean branch.
2. Make a focused change.
3. Run project validation.
4. Confirm the change stays within safety boundaries.
5. Commit with a precise message.
6. Push to the correct remote.
7. Open or update a PR.

## 6. Merge and Release Guidance

- Merge only after relevant tests pass.
- Do not merge if safety checks or consent protections are weakened.
- Release notes should call out operational, security, and behavior changes.
- For risky changes, perform rollback and restore checks before merge.

## 7. Emergency and Safety Escalation

If a change introduces risk, suspected consent misuse, leakage of secrets, or dangerous automation behavior:

- stop the change immediately
- revert the unsafe patch
- document the issue and impact
- notify the maintainers or repo owners
- validate the system before reopening the work

## 8. Final Contributor Reminder

SeduX values transparent, bounded, and user-safe contribution. If a change does not clearly respect consent, security, and operational safety, it should not be merged.

Contribute in a way that is readable, testable, reversible, and aligned with the project’s mission.
