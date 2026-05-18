# Approval Gate Certification Matrix — 2026-05-18

Status:

```text
planning / verification scaffold only
not a certification document
```

Purpose:

```text
Define the exact proof requirements before any approval-gate certification or lock-closeout claim.
```

This document:

- does not certify the approval gate
- does not change runtime behavior
- does not modify capability locks
- does not expand authority
- does not authorize autonomous execution

---

# Certification Discipline

```text
focused coverage != full certification
active != certified != locked
```

Current verified truth:

```text
PR #171 merged focused regression coverage for tested Cap 22 / Cap 64 paths.
PR #172 merged behavioral live-session coverage for tested Cap 22 / Cap 64 paths.
PR #175 documented broader workflow verification.
PR #176 fixed workflow regressions found by that pass.
Full approval-gate certification remains pending.
```

---

# Required Certification Matrix

| Capability | Confirmation Required | Pending State Tested | Approve Path Tested | Deny Path Tested | Cancel/Unrelated Input Tested | Ledger Sequence Tested | Live WS Session Tested | Runtime Verified | Certification Status |
|---|---|---|---|---|---|---|---|---|---|
| Cap 22 | yes | yes | yes | yes | yes | partial | yes | partial | pending |
| Cap 64 | yes | yes | yes | yes | yes | partial | yes | partial | pending |
| Other confirmation-bound capabilities | unknown/incomplete audit | pending | pending | pending | pending | pending | pending | pending | pending |

---

# Required Proof Before Certification Claim

## 1. Capability inventory complete

Required:

```text
Enumerate every confirmation-bound capability and every execution entry path.
```

---

## 2. Behavioral proof complete

Required:

```text
pending path blocks executor dispatch
approve path resumes through governed execution
no/cancel path does not execute
unrelated input does not execute
```

---

## 3. Ledger proof complete

Required:

```text
ACTION_ATTEMPTED
ACTION_COMPLETED
ACTION_DENIED
pending-state events
```

must appear only in expected governed sequences.

---

## 4. Live-session proof complete

Required:

```text
WebSocket/session approval flows verified
frontend state transitions verified
```

---

## 5. Regression protection complete

Required:

```text
must-fail tests for bypass attempts
executor dispatch forbidden during pending state
```

---

## 6. Scope boundaries preserved

Certification work must not include:

```text
OpenClaw expansion
browser/computer-use expansion
external writes
Shopify writes
email sending
autonomous workflows
```

---

# Current Safe Interpretation

```text
Approval-gate focused coverage exists for tested Cap 22 / Cap 64 paths.
Broader/full-suite approval-gate certification is still pending.
```

No document should currently say:

```text
approval gate fully certified
all confirmation paths proven
approval-gate closeout complete
```

until this matrix is fully resolved and independently verified.
