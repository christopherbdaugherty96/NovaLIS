# Cap 64 Email Draft Operator Journey

Status: proof scaffold / evidence pending / not Cap 64 P5 / not locked.

Simulation source:

```text
docs/simulations/APPROVAL_GATE_WORKFLOW_SIMULATIONS.md
```

Live checklist source:

```text
docs/capability_verification/live_checklists/cap_64_send_email_draft.md
```

This document records the proof packet required for the Cap 64 email-draft
operator journey. It does not certify Cap 64, complete P5, lock Cap 64, certify
the full approval gate, change runtime behavior, or expand authority.

Full approval-gate certification remains pending until broader/full-suite proof
supports it.

---

## Current Truth

```text
Capability: Cap 64 - send_email_draft
Runtime boundary: local mailto draft only
Manual boundary: the user reviews and sends manually
Certification status: P1-P4 passed historically / P5 pending / not locked
Approval-gate status: focused coverage merged / certification pending
```

Cap 64 must not be described as:

```text
SMTP email sending
Gmail sending
inbox access
autonomous email
customer-message automation
Cap 64 locked
approval-gate certification complete
```

---

## Operator-Journey Contract

The Cap 64 journey must make this visible:

```text
What Nova understood
What Nova can do
What requires approval
What Nova will not do
What happens if the user says yes
What happens if the user says no / cancel
Where the evidence appears
```

Required preserved boundary:

```text
Nova drafts and recommends.
The current authorized user approves.
Execution stays manual or governed inside approved bounded paths.
Trust/receipt visibility is non-authorizing.
Memory and planning context do not grant permission.
```

---

## Proof Packet Metadata

| Field | Value |
| --- | --- |
| Simulation document version | `APPROVAL_GATE_WORKFLOW_SIMULATIONS.md` on main after PR #191 |
| Proof document status | automated evidence captured / manual gaps pending |
| Repo commit SHA | `a1f8a4d` (main after PR #194) |
| Capability under test | Cap 64 `send_email_draft` |
| Authority classification | confirmation-required local draft handoff |
| Runtime code changes | none in this proof doc |
| Generated runtime doc edits | none |
| Certification claim | none |

---

## Scenario A: Request Creates Pending State

User request:

```text
Draft an email to test@example.com saying the meeting moved to 3 PM.
```

Expected behavior:

```text
Nova identifies the request as Cap 64 / email draft.
Nova explains that it can create a local draft only.
Nova explains that approval is required before opening the draft.
Nova creates pending confirmation state.
Nova does not open a mail client while pending.
Nova does not log ACTION_ATTEMPTED or ACTION_COMPLETED while pending.
```

Evidence to capture:

```text
behavioral session test output
executor non-dispatch assertion
ledger assertion showing no ACTION_ATTEMPTED / ACTION_COMPLETED while pending
operator transcript or proof note
```

Current evidence:

```text
PASS — test_pending_cap64_does_not_dispatch_or_log_action_attempted
PASS — test_cap64_session_request_creates_pending_state_without_execution
Commit: a1f8a4d
```

Remaining gap:

```text
None for this scenario. Automated evidence captured.
```

---

## Scenario B: Yes Resumes Through Governed Invocation

User input:

```text
yes
```

Expected behavior:

```text
Nova resumes the pending Cap 64 action only through governed invocation.
The governed invocation includes confirmed=True.
The request remains bounded to local mailto draft behavior.
The approved path logs the expected governed ledger sequence.
The user remains responsible for reviewing and sending manually.
```

Evidence to capture:

```text
behavioral session test output proving confirmed=True
Governor ledger sequence
manual observation that only a local draft was opened
Trust Panel receipt or receipt API evidence
```

Current evidence:

```text
PASS — test_governor_passes_cap64_with_confirmation
PASS — test_approved_cap64_runs_only_after_governor_attempt_ledger
PASS — test_session_yes_resumes_pending_cap64_only_through_governed_invocation
PASS — test_session_approved_cap64_uses_real_governor_ledger_sequence
Commit: a1f8a4d
```

Remaining gap:

```text
Manual observation of live mailto draft opening still pending.
Trust Panel receipt evidence pending — depends on runtime availability.
```

---

## Scenario C: No / Cancel Blocks Execution

User inputs:

```text
no
cancel
```

Expected behavior:

```text
Nova clears or blocks the pending Cap 64 action.
Nova does not open a mail client.
Nova does not dispatch the executor.
Nova does not log ACTION_ATTEMPTED or ACTION_COMPLETED for the denied action.
Nova explains that nothing was executed.
```

Evidence to capture:

```text
behavioral session test output
executor non-dispatch assertion
ledger assertion
operator transcript or proof note
```

Current evidence:

```text
PASS — test_session_no_clears_pending_without_execution
PASS — test_session_cancel_clears_pending_without_execution
Commit: a1f8a4d
```

Remaining gap:

```text
None for this scenario. Automated evidence captured.
```

---

## Scenario D: Unrelated Input Does Not Approve

User input:

```text
What's the weather?
```

Expected behavior:

```text
Nova does not treat unrelated input as approval.
Nova does not execute the pending Cap 64 action.
Nova either keeps the pending action safely unresolved or cancels/clears it
according to the current session contract.
Nova does not log ACTION_ATTEMPTED or ACTION_COMPLETED for the pending action.
```

Evidence to capture:

```text
behavioral session test output
ledger assertion
operator transcript or proof note
```

Current evidence:

```text
PASS — test_confirmation_resolver_rejects_ambiguous_input
PASS — test_session_unrelated_input_cancels_pending_without_execution
Commit: a1f8a4d
```

Remaining gap:

```text
None for this scenario. Automated evidence captured.
```

---

## Scenario E: Recovery After Interruption

Interruption cases:

```text
browser refresh
WebSocket disconnect
server restart
session restore where supported
```

Expected behavior:

```text
Nova does not execute the pending Cap 64 action during interruption or restore.
Nova explains the safe current state.
Nova requires fresh explicit approval before any governed execution can resume.
Nova does not reuse stale approval.
```

Evidence to capture:

```text
session/recovery test output where available
manual recovery transcript if no automated test path exists
ledger assertion showing no hidden execution
```

Current evidence:

```text
No automated recovery test exists as of a1f8a4d.
```

Remaining gap:

```text
No automated test simulates browser refresh, WebSocket disconnect, or server
restart during a pending Cap 64 confirmation. A manual transcript or future
automated recovery test is required to close this gap.
```

---

## Live Mailto Draft Proof

This proof is separate from automated behavioral session coverage.

Required live preconditions:

```text
Nova running at http://localhost:8000
mail client or mailto handler installed and configured
chat tab open
test recipient only
draft closed without sending
```

Expected live behavior:

```text
Nova asks for confirmation before opening the draft.
After yes, the local mail client or mailto handler opens a draft.
The draft contains the expected recipient and subject/body content.
The user closes the draft without sending.
At least one matching receipt is visible through the Trust Panel or
http://localhost:8000/api/trust/receipts.
```

Must not happen:

```text
no SMTP send
no Gmail API send
no inbox access
no autonomous send
no customer-message automation
no sent email
```

Current live evidence:

```text
Automated boundary evidence captured (no SMTP import, mailto-only external
call, draft-created-not-sent ledger event, review-not-sent user message).
Live manual mailto observation still pending.
```

Remaining gap:

```text
Run the live mailto checklist when explicitly ready for Cap 64 P5 evidence.
Confirm local draft opens and is closed without sending.
Do not run lock commands from this scaffold.
```

---

## Required Test Commands

Command:

```text
python -m pytest tests/governance/test_approval_gate_wiring.py \
  tests/websocket/test_behavioral_session_approval_gate.py \
  tests/executors/test_send_email_draft_executor.py \
  tests/certification/cap_64_send_email_draft/ \
  tests/test_send_email_draft_routing.py -v --tb=short
```

Result:

```text
132 passed, 0 failed, 28.79s
Commit: a1f8a4d (main after PR #194)
```

Test files covering Cap 64:

```text
tests/governance/test_approval_gate_wiring.py — 24 tests
tests/websocket/test_behavioral_session_approval_gate.py — 9 tests
tests/executors/test_send_email_draft_executor.py — 21 tests
tests/certification/cap_64_send_email_draft/test_p1_unit.py — 21 tests
tests/certification/cap_64_send_email_draft/test_p2_routing.py — 14 tests
tests/certification/cap_64_send_email_draft/test_p3_integration.py — 12 tests
tests/certification/cap_64_send_email_draft/test_p4_api.py — 6 tests
tests/test_send_email_draft_routing.py — 14 tests (duplicate of p2)
```

Do not record:

```text
full-suite pass
approval-gate certification
Cap 64 P5 complete
Cap 64 locked
```

unless those exact commands and proof steps actually completed.

---

## Ledger Evidence

Expected pending / denied / unrelated behavior:

```text
No ACTION_ATTEMPTED
No ACTION_COMPLETED
No executor dispatch
```

Expected approved behavior:

```text
governed invocation with confirmed=True
ACTION_ATTEMPTED before execution
bounded local draft handoff
ACTION_COMPLETED or documented failure result after executor return
receipt evidence when draft creation succeeds
```

Captured ledger evidence (automated assertions):

```text
Blocked paths (pending/denied/cancelled/unrelated):
  ACTION_ATTEMPTED not in ledger events — asserted in 5 tests
  ACTION_COMPLETED not in ledger events — asserted in 5 tests
  executor never called — asserted via mock side_effect=AssertionError

Approved path:
  ACTION_ATTEMPTED count == 1 — asserted
  EMAIL_DRAFT_CREATED in ledger events — asserted
  ACTION_COMPLETED count == 1 — asserted
  ledger event includes to and subject — asserted

Commit: a1f8a4d
```

Remaining gap:

```text
Live ledger excerpts from a running Nova instance are not captured here.
The automated assertions above prove the ledger contract at the code level.
```

---

## Receipt / Trust Panel Evidence

Expected evidence source:

```text
Trust Panel receipt surface, where implemented and available
http://localhost:8000/api/trust/receipts as direct proof source, if present on the current runtime
```

Expected receipt boundary:

```text
Receipt visibility is evidence only.
Trust Panel display does not authorize execution.
```

Captured receipt excerpt or screenshot reference:

```text
No automated receipt test exists as of a1f8a4d.
No test asserts receipt creation or Trust Panel API response.
```

Remaining gap:

```text
Receipt evidence depends on whether the current runtime exposes
http://localhost:8000/api/trust/receipts. Capture during live proof
only if endpoint is present. Do not assert receipt if endpoint is absent.
```

---

## Manual Steps Performed

```text
Live mailto draft observation: pending.
No manual steps have been performed yet.
```

Required manual note when live proof is run:

```text
The draft was opened locally and closed without sending.
```

---

## Blocked-Path Evidence

The proof must show:

```text
pending action did not execute
denied action did not execute
cancelled action did not execute
unrelated input did not execute
ambiguous confirmation did not execute, if tested
duplicate yes did not double-execute, if tested
```

Captured blocked-path evidence:

```text
pending action did not execute — PASS (test_pending_cap64_*)
denied action did not execute — PASS (test_session_no_clears_pending_*)
cancelled action did not execute — PASS (test_session_cancel_clears_pending_*)
unrelated input did not execute — PASS (test_session_unrelated_input_*)
ambiguous confirmation did not execute — PASS (test_confirmation_resolver_rejects_*)
duplicate yes did not double-execute — not tested
Commit: a1f8a4d
```

---

## Remaining Unverified Items

Verified:

```text
repo commit SHA for proof run — a1f8a4d
focused test command output — 132 passed, 0 failed
approved governed invocation evidence — captured
pending non-execution evidence — captured
denied/cancelled non-execution evidence — captured
unrelated-input non-execution evidence — captured
ledger excerpts (automated assertions) — captured
```

Still pending:

```text
receipt / Trust Panel evidence — no automated test, runtime-dependent
manual mailto draft observation — requires live Nova instance
recovery behavior evidence — no automated test exists
duplicate-yes non-double-execution — not tested
```

---

## Certification Status

Current status:

```text
Automated evidence captured for Cap 64 pending/approve/deny/cancel/unrelated/
ledger/mailto-boundary paths (132 tests, 0 failures, commit a1f8a4d).
Recovery, receipt/Trust Panel, and live mailto observation remain pending.
Cap 64 P5 remains pending.
Cap 64 remains not locked.
Full approval-gate certification remains pending.
```

Safe wording after this evidence update lands:

```text
Cap 64 automated evidence captured. Manual/live/recovery/receipt gaps remain.
Cap 64 P5 remains pending. Cap 64 remains not locked.
```

Do not say:

```text
Cap 64 P5 complete
Cap 64 locked
Cap 64 certified
approval gate complete
approval gate fully certified
all approval-gate paths proven
```

---

## Next Action

When ready for evidence capture:

```text
1. Run focused Cap 64 / approval-gate tests.
2. Capture pending, approved, denied/cancelled, and unrelated-input behavior.
3. Run the live mailto draft proof without sending email.
4. Capture ledger and receipt evidence.
5. Update this document with exact outputs and remaining gaps.
6. Only then decide whether Cap 64 P5 signoff is supportable.
```

Final boundary:

```text
This proof scaffold is not a lock.
This proof scaffold is not certification.
The current authorized user remains the approver.
```
