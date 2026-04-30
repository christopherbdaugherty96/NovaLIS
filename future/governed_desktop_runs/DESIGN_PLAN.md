# Governed Desktop Runs — Reality-Grounded Design Plan

This document grounds the governed desktop run proposal against the current NovaLIS architecture and defines a practical design path.

This is an implementation planning document, not runtime truth. Generated runtime documents remain authoritative for what NovaLIS can do today.

---

## Current Reality Check

As of the current generated runtime state:

- NovaLIS already has a governed execution spine.
- The authority path is: User → GovernorMediator → Governor → CapabilityRegistry → SingleActionQueue → LedgerWriter → ExecuteBoundary → Executor.
- `openclaw_execute` is already an active capability.
- OpenClaw home-agent foundations are active.
- Runtime invariants already state no broad autonomy, no hidden background execution except explicit scheduler carve-out, all actions through GovernorMediator, all outbound HTTP through NetworkMediator, and all execution logged.
- Full Phase-8 governed envelope execution is explicitly listed as not implemented yet.
- Trust Panel system is explicitly listed as not implemented yet.

Therefore, governed desktop runs should not be treated as a brand-new philosophy. They are the missing envelope-execution layer that would make NovaLIS' existing governance spine stronger for broader desktop/browser workflows.

---

## What Exists Today

### Existing Strengths

NovaLIS already has the right foundation:

1. GovernorMediator routing
2. CapabilityRegistry enablement control
3. ExecuteBoundary final permission gate
4. LedgerWriter audit logging
5. NetworkMediator outbound HTTP control
6. SingleActionQueue execution sequencing
7. Active OpenClaw execution surface
8. Generated runtime truth and drift discipline

These pieces mean the proposal should extend existing architecture, not bypass it.

### Existing Gap

The current gap is not "Nova needs governance."

The real gap is:

> NovaLIS needs a strict task envelope model for multi-step desktop/browser/OpenClaw runs.

The runtime already acknowledges this as deferred broader envelope-governed execution.

---

## Design Goal

Create a governed run layer that allows NovaLIS to operate across local apps, webpages, and OpenClaw workflows while preserving the core rule:

> NovaLIS may not act unless permission is given, may not leave the approved scope, and must stop when the task is done.

---

## Design Non-Goals

This work must not create:

- unrestricted computer access
- hidden background autonomy
- autonomous publishing
- autonomous purchasing
- autonomous credential handling
- direct OpenClaw bypass around GovernorMediator
- a second execution spine outside existing NovaLIS governance

---

## Proposed Architecture Addition

Add a new layer between intent approval and OpenClaw execution:

```text
User request
→ Conversation / intent parsing
→ GovernorMediator
→ CapabilityRegistry
→ Governed Run Envelope Builder
→ Envelope Policy Evaluator
→ Trust Review Card
→ User approval
→ SingleActionQueue
→ LedgerWriter start record
→ ExecuteBoundary
→ OpenClaw Governed Run Adapter
→ Scope Monitor
→ Step Ledger / Run Receipt
→ Stop condition
```

The new pieces are:

1. Governed Run Envelope Builder
2. Envelope Policy Evaluator
3. Trust Review Card rendering
4. OpenClaw Governed Run Adapter
5. Scope Monitor
6. Run Receipt / step ledger output
7. Pause / stop / revoke state model

---

## Proposed Files / Modules

Exact file paths should be adjusted to match the final implementation style, but the initial target could be:

```text
nova_backend/src/governor/governed_runs/
  __init__.py
  envelope.py
  policy.py
  states.py
  receipt.py
  scope_monitor.py

nova_backend/src/openclaw/governed_adapter.py

nova_backend/tests/governor/test_governed_run_envelope.py
nova_backend/tests/governor/test_governed_run_policy.py
nova_backend/tests/openclaw/test_openclaw_governed_adapter.py
```

UI/Trust Review files should be added only after confirming the dashboard structure at implementation time.

---

## Envelope Schema — First Build Target

Minimum viable envelope fields:

```json
{
  "run_id": "generated_id",
  "intent": "string",
  "goal": "string",
  "risk_level": "low|medium|high",
  "approved_steps": [],
  "allowed_surfaces": [],
  "allowed_actions": [],
  "blocked_actions": [],
  "required_approvals": [],
  "stop_conditions": [],
  "timeout_seconds": 300,
  "audit_level": "summary|step_receipt",
  "created_at": "timestamp"
}
```

Validation rules:

- `run_id`, `intent`, `goal`, `risk_level`, `allowed_actions`, `blocked_actions`, `stop_conditions`, and `timeout_seconds` are required.
- `risk_level` must be one of `low`, `medium`, `high`.
- `timeout_seconds` must be bounded.
- High-risk actions must require explicit approval.
- Empty allowed scope should fail closed.
- Unknown action types should fail closed.

---

## Policy Evaluator Responsibilities

The policy evaluator should answer five questions:

1. Is this envelope valid?
2. What is the risk tier?
3. Does this run require user approval before start?
4. Is the proposed next action inside scope?
5. Should the run continue, pause, or stop?

Initial policy outcomes:

```text
ALLOW
REQUIRE_APPROVAL
PAUSE
STOP
DENY
```

---

## State Machine

Initial run states:

```text
CREATED
PENDING_APPROVAL
APPROVED
RUNNING
PAUSED
COMPLETED
FAILED
CANCELLED
DENIED
TIMEOUT
SCOPE_VIOLATION
```

State rules:

- A run cannot enter RUNNING without approval when approval is required.
- A run cannot return to RUNNING after COMPLETED, CANCELLED, DENIED, or SCOPE_VIOLATION without a new envelope.
- Any scope violation stops or pauses the run depending on severity.
- Completion ends permission.

---

## Scope Monitor Responsibilities

The first scope monitor can be conservative and simple.

It should detect:

- URL/domain outside approved scope
- active app/window outside approved surface
- attempted blocked action
- attempted file access outside approved paths
- attempt to continue after stop condition
- risk escalation from read-only to write/upload/send/publish
- executor uncertainty

If the monitor is unsure, it should pause by default.

---

## OpenClaw Adapter Direction

The OpenClaw adapter should not receive vague prompts as its only constraint.

Instead, it should receive:

- the approved envelope
- current step
- allowed actions
- blocked actions
- stop condition
- timeout
- required receipt fields

OpenClaw may perform only actions represented by the envelope. If OpenClaw needs to do anything outside scope, the adapter must pause and request a new approval or new envelope.

---

## Trust Review Card

Before execution, the user should see:

- What Nova wants to do
- Why it wants to do it
- What surfaces it may use
- What actions are allowed
- What actions are blocked
- Risk level
- Timeout
- Stop condition
- Whether approval is required

This is essential because governance must be visible, not only internal.

---

## Ledger / Receipt Requirements

Every governed run should produce a receipt containing:

- run id
- user request
- envelope summary
- approval decision
- start time
- end time
- steps attempted
- policy decisions
- blocked actions
- final result
- stop reason

The receipt should be append-only and compatible with the existing ledger direction.

---

## First Safe Workflow

The first implemented workflow should be intentionally small:

```text
Open one approved URL, read visible page title or visible content summary, return the result, then stop.
```

Allowed:

- open approved URL
- read visible content
- summarize

Blocked:

- clicking unrelated links
- logging in
- downloading
- uploading
- entering credentials
- sending messages
- purchasing
- continuing after summary

This tests envelope creation, approval, execution, monitoring, receipt, and stop behavior without real risk.

---

## Test Plan Summary

Minimum tests before any real OpenClaw desktop/browser use:

1. Valid low-risk envelope passes validation.
2. Missing required fields fail closed.
3. Unknown risk tier fails closed.
4. Empty allowed actions fail closed.
5. Unknown action type fails closed.
6. High-risk action requires approval.
7. Scope violation pauses or stops.
8. User cancellation stops run.
9. Timeout stops run.
10. Completion revokes permission.
11. Executor uncertainty pauses run.
12. Attempted publish/send/purchase is blocked without fresh approval.
13. Run receipt is produced.

---

## Integration Order

1. Add envelope schema and tests.
2. Add policy evaluator and tests.
3. Add state model and tests.
4. Add receipt object and tests.
5. Add dry-run mode with no desktop execution.
6. Add Trust Review Card data payload.
7. Add dashboard rendering only after payload is stable.
8. Add OpenClaw governed adapter in dry-run mode.
9. Add first harmless browser task.
10. Regenerate runtime truth only after implementation is real.

---

## Relationship to YouTubeLIS

YouTubeLIS should remain parked until governed desktop runs exist.

YouTubeLIS should be a consumer of the governed run layer, not the reason to bypass it.

Possible later YouTubeLIS tasks:

- generate voiceover from approved script
- prepare visual reference list
- create upload metadata draft
- assemble local asset folders
- analyze channel performance exports

Publishing should remain final-human-approved.

---

## Honest Current Status

This plan is grounded in NovaLIS' current architecture, but it is not implemented yet.

The repo already has the core governance spine and OpenClaw surfaces. The missing piece is strict envelope-governed execution for broader desktop/browser runs.

The correct next move is schema + policy evaluator + tests, not immediate broad OpenClaw authority.
