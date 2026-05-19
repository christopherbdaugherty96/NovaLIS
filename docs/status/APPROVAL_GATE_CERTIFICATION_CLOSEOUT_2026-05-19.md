# Approval Gate Certification Closeout — 2026-05-19

Status:

```text
certified for current registry-confirmation-bound scope only
```

---

## Certification Decision

Approval-gate certification is complete for the current
registry-confirmation-bound capability scope:

- **Cap 22** `open_file_folder`
- **Cap 64** `send_email_draft`

These are the only two capabilities in `registry.json` with
`requires_confirmation: true` as of commit `e117957` on main.

---

## Evidence Dimensions Checked

| Dimension | Cap 22 | Cap 64 |
|---|---|---|
| Pending state blocks execution | yes — PR #171 / #172 | yes — PR #171 / #172 |
| Approve path resumes governed execution | yes — PR #171 / #172 / #200 | yes — PR #171 / #172 / #195 |
| Deny/cancel/unrelated does not execute | yes — PR #172 / #200 | yes — PR #172 / #195 |
| Duplicate-yes does not double-execute | yes — PR #197 | yes — PR #197 |
| Ledger sequence correct | yes — PR #172 / #200 / #201 | yes — PR #172 / #195 / #196 |
| Live WebSocket proof | yes — PR #201 | yes — PR #196 / #198 |
| Receipt endpoint evidence | yes — PR #201 | yes — PR #196 / #198 |
| Recovery (disconnect clears pending) | yes — PR #203 | yes — PR #203 |
| Automated test suite | yes — PR #200 (23 tests) | yes — PR #195 (132 tests) |
| Path-root boundary enforcement | yes — PR #200 (5 tests) | n/a |

---

## Evidence Sources

```text
PRs: #171, #172, #195, #196, #197, #198, #200, #201, #203
Proof docs:
  docs/PROOFS/Operator-Journeys/CAP22_OPEN_FILE_FOLDER_OPERATOR_JOURNEY.md
  docs/PROOFS/Operator-Journeys/CAP64_EMAIL_DRAFT_OPERATOR_JOURNEY.md
Certification matrix:
  docs/capability_verification/APPROVAL_GATE_CERTIFICATION_MATRIX_2026-05-18.md
Recovery tests:
  nova_backend/tests/websocket/test_recovery_no_stale_approval.py
```

---

## What This Certifies

```text
The approval-gate behavior for the current registry-confirmation-bound
capabilities is certified against the completed evidence matrix.
```

Specifically:

- The `pending_governed_confirm` state blocks executor dispatch
  until the user explicitly confirms.
- Approved actions proceed through the governed ledger sequence
  (ACTION_ATTEMPTED, ACTION_COMPLETED).
- Denied, cancelled, and unrelated inputs do not execute.
- Duplicate confirmations do not cause double execution.
- Pending state does not survive WebSocket disconnect
  (session isolation is enforced).
- New sessions can create fresh pending actions after disconnect.
- Live proof confirms real WebSocket interaction matches
  automated test assertions.

---

## What This Does NOT Certify

```text
This certification is narrowly scoped. It does not certify:
```

- All Nova capabilities
- All future registry states
- All governance behavior
- All local actions
- All external effects
- Broad autonomy
- OpenClaw execution
- Browser/computer-use expansion
- Shopify writes
- Autonomous email sending
- Finance automation
- Social posting automation
- Hidden background work

If `registry.json` adds new `requires_confirmation: true`
capabilities in the future, those are NOT covered by this
closeout and require their own evidence chain.

---

## Capability Lock Status

```text
capability_locks.json intentionally NOT modified by this closeout.
```

The P1-P5 per-capability lock process is a separate certification
path from the approval-gate behavioral proof. Cap 22 and Cap 64
remain `locked: false` in `capability_locks.json`. Per-capability
lock decisions require their own reviewed priority lock.

Current lock truth:

```text
Cap 16 — locked (P1-P5 pass, locked_date 2026-05-10).
Cap 22 — not locked (P1-P4 pending in locks file, approval-gate certified).
Cap 64 — not locked (P1-P4 pass, P5 pending, approval-gate certified).
Cap 65 — not locked (P1-P4 pass, P5 pending).
```

---

## Registry Snapshot

Registry source at time of certification:

```text
nova_backend/src/config/registry.json on main at e117957
```

Confirmation-bound capabilities at this snapshot:

```text
Cap 22 — open_file_folder — requires_confirmation: true
Cap 64 — send_email_draft — requires_confirmation: true
```

No other active capability has `requires_confirmation: true`.

---

## Preserved Boundaries

```text
Intelligence is not authority.
```

This closeout does not authorize:

- Autonomous execution
- Hidden background work
- Browser/computer-use expansion
- External writes
- OpenClaw authority expansion
- Direct Cap 63 shortcut use
- Shopify writes
- Finance automation
- Social posting automation
