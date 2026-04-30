# Governed Run State Machine

This document defines the state model and transitions for governed desktop/browser/OpenClaw runs.

---

## States

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
POLICY_DENIED
```

---

## State Transitions

```text
CREATED → PENDING_APPROVAL
CREATED → APPROVED (if no approval required)

PENDING_APPROVAL → APPROVED (user approves)
PENDING_APPROVAL → DENIED (user rejects)

APPROVED → RUNNING

RUNNING → PAUSED (uncertainty / approval needed)
RUNNING → COMPLETED (goal reached)
RUNNING → FAILED (execution error)
RUNNING → CANCELLED (user stop)
RUNNING → TIMEOUT (timeout reached)
RUNNING → SCOPE_VIOLATION (left allowed scope)
RUNNING → POLICY_DENIED (policy blocks)

PAUSED → RUNNING (approval or clarification)
PAUSED → CANCELLED (user stop)

COMPLETED → TERMINAL
FAILED → TERMINAL
CANCELLED → TERMINAL
DENIED → TERMINAL
TIMEOUT → TERMINAL
SCOPE_VIOLATION → TERMINAL
POLICY_DENIED → TERMINAL
```

---

## Rules

- Terminal states cannot transition back to RUNNING.
- Any continuation requires a new envelope.
- Completion revokes all permissions.
- Pause retains state but requires re-validation before resume.

---

## First Implementation

Implement state transitions without execution first.

Validate transitions via test cases before integrating OpenClaw execution.
