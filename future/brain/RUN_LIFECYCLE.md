# Run Lifecycle

Defines the full lifecycle for future governed Brain-planned runs.

This is planning only. It does not enable runtime execution.

---

## Core Principle

> A run must have a visible beginning, bounded middle, and explicit end.

No governed run should continue indefinitely, silently expand scope, or remain active after completion.

---

## Lifecycle States

```text
INTAKE
CONTEXT_ASSEMBLY
PLAN_DRAFTED
TRUST_REVIEW
PENDING_APPROVAL
APPROVED
RUNNING
PAUSED
RETRYING
COMPLETED
FAILED
CANCELLED
BLOCKED
REVOKED
EXPIRED
```

---

## Standard Flow

```text
User / signal
→ intake
→ context assembly
→ plan drafted
→ trust review
→ approval if required
→ governed execution
→ receipt
→ optional memory / learning proposal
→ close run
```

---

## State Rules

### INTAKE

Capture the request or signal.

Must determine:

- user goal
- domain
- risk hints
- whether context is needed

### CONTEXT_ASSEMBLY

Gather only relevant context.

Must exclude:

- unrelated memory
- stale data without warning
- credentials
- hidden authority grants

### PLAN_DRAFTED

Create a plan or envelope.

Must include:

- intended action
- allowed actions
- blocked actions
- stop conditions
- expected receipt

### TRUST_REVIEW

Show the user what NovaLIS believes it will do.

Must include risk, authority, and approval requirements.

### PENDING_APPROVAL

Waiting for user approval.

No medium/high-risk execution occurs here.

### APPROVED

Approval exists, but execution has not started yet.

Before entering RUNNING, the system must re-check scope and policy.

### RUNNING

Execution is active.

Must be:

- bounded
- logged
- interruptible
- monitored

### PAUSED

Execution is suspended because:

- user input needed
- uncertainty detected
- approval needed
- surface mismatch occurred

### RETRYING

Retry is allowed only when:

- retry count is under limit
- scope is unchanged
- risk did not escalate
- prior failure is understood

### COMPLETED

Goal reached.

Permission ends.

### FAILED

Run failed safely.

Must produce a failure receipt.

### CANCELLED

User stopped the run.

Permission ends.

### BLOCKED

Policy blocked the run or action.

Must explain why.

### REVOKED

User revoked permission.

Execution stops immediately.

### EXPIRED

Approval or run window expired.

A new approval is required.

---

## Terminal States

These states end permission:

```text
COMPLETED
FAILED
CANCELLED
BLOCKED
REVOKED
EXPIRED
```

A terminal run cannot resume. A new run/envelope is required.

---

## Retry Rules

Retries must be limited.

A retry may occur only if:

- same approved goal
- same approved surface
- same risk level
- no blocked action occurred
- retry limit not exceeded

Retries must not occur if:

- account action is requested
- credential prompt appears
- purchase prompt appears
- publish/send action appears
- scope changed
- uncertainty persists

---

## Receipts

Every non-trivial run must end with a receipt:

- run id
- starting request/signal
- plan/envelope
- approvals
- steps attempted
- blocked actions
- final state
- stop reason
- memory/learning recommendation

---

## First Implementation Target

Implement lifecycle as dry-run state transitions first.

No desktop/browser execution should depend on lifecycle logic until tests verify terminal states, approval gates, retries, and receipts.
