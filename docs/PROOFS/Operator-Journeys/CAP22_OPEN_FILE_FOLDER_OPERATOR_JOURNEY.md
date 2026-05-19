# Cap 22 Open File / Folder Operator Journey

Status: automated + live proof captured / recovery pending / not locked / not globally certified.

Simulation source:

```text
docs/simulations/APPROVAL_GATE_WORKFLOW_SIMULATIONS.md
```

Live checklist source:

```text
docs/capability_verification/live_checklists/cap_22_open_file_folder.md
```

This document records the proof packet required for the Cap 22 open-file/folder
operator journey. It does not certify Cap 22, lock Cap 22, certify the full
approval gate, change runtime behavior, or expand authority.

Full approval-gate certification remains pending until broader/full-suite proof
supports it.

---

## Current Truth

```text
Capability: Cap 22 - open_file_folder
Runtime boundary: local open only inside Nova-approved path roots
Manual boundary: confirmation required before opening
Certification status: focused coverage exists / not locked
Approval-gate status: focused coverage merged / certification pending
Authority class: reversible_local
Risk level: confirm
```

Cap 22 must not be described as:

```text
arbitrary file mutation
external write
browser/computer-use expansion
file deletion
file modification
Cap 22 locked
Cap 22 globally certified
approval-gate certification complete
```

---

## Operator-Journey Contract

The Cap 22 journey must make this visible:

```text
What Nova understood (target path)
What Nova can do (open locally)
What requires approval (explicit confirmation)
What Nova will not do (mutate, delete, write externally)
What happens if the user says yes
What happens if the user says no / cancel
Where the evidence appears
```

Required preserved boundary:

```text
Nova identifies the target and recommends.
The current authorized user approves.
Execution stays bounded to local open through governed path roots.
Trust/receipt visibility is non-authorizing.
Memory and planning context do not grant permission.
```

---

## Proof Packet Metadata

| Field | Value |
| --- | --- |
| Simulation document version | `APPROVAL_GATE_WORKFLOW_SIMULATIONS.md` on main after PR #191 |
| Proof document status | automated + live proof captured / recovery pending |
| Repo commit SHA | `59f232e` (main after PR #197 merge) |
| Capability under test | Cap 22 `open_file_folder` |
| Authority classification | confirmation-required reversible local open |
| Runtime code changes | none in this proof doc |
| Generated runtime doc edits | none |
| Certification claim | none |

---

## Scenario A: Request Creates Pending State

User request:

```text
Open my Downloads folder.
```

Expected behavior:

```text
Nova identifies the request as Cap 22 / open file or folder.
Nova explains the target it understood.
Nova asks for explicit confirmation.
Nova creates pending confirmation state.
Nova does not open the folder while pending.
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
CAPTURED — 23 tests, 0 failures across 7 test files at commit 59f232e.

Behavioral session tests (11 passed):
  test_cap22_session_request_creates_pending_state_without_execution — PASSED
    asserts calls == [] (no executor dispatch)
    asserts ACTION_ATTEMPTED not in ledger events
    asserts ACTION_COMPLETED not in ledger events
    asserts "This action needs confirmation." in chat messages

Governance approval gate wiring tests (24 passed):
  test_pending_cap22_does_not_dispatch_or_log_action_attempted — PASSED
  test_session_handler_sets_pending_for_cap22 — PASSED

Brain server session cleanup test:
  test_open_file_folder_requires_confirmation_before_dispatch — PASSED
```

Remaining gap:

```text
No remaining automated gap for this scenario.
Live operator observation pending.
```

---

## Scenario B: Yes Resumes Through Governed Invocation

User input:

```text
yes
```

Expected behavior:

```text
Nova resumes the pending Cap 22 action only through governed invocation.
The governed invocation includes confirmed=True.
The local open action remains bounded to the requested target.
The approved path logs the expected governed ledger sequence.
The target opens locally through the system open handler.
```

Evidence to capture:

```text
behavioral session test output proving confirmed=True
Governor ledger sequence
manual observation or mocked open proof
Trust Panel receipt or receipt API evidence
```

Current evidence:

```text
CAPTURED — automated evidence at commit 59f232e.

Behavioral session tests:
  test_session_yes_resumes_pending_cap22_only_through_governed_invocation — PASSED
    asserts capability_id == 22
    asserts params["confirmed"] is True
    asserts session_id is set
    asserts exactly 1 invocation
    asserts ledger == ["ACTION_ATTEMPTED", "ACTION_COMPLETED"]
    asserts "Opened documents." in chat messages

  test_session_approved_cap22_uses_real_governor_ledger_sequence — PASSED
    asserts ACTION_ATTEMPTED count == 1
    asserts ACTION_COMPLETED count == 1
    uses real governor ledger (not mock)
    asserts "Opened folder:" or "Opened path:" in chat messages

Governance tests:
  test_governor_passes_cap22_with_confirmation — PASSED
  test_approved_cap22_runs_only_after_governor_attempt_ledger — PASSED
  test_session_handler_pending_confirm_sets_confirmed_true — PASSED
```

Remaining gap:

```text
No remaining automated gap for this scenario.
Live operator observation and receipt evidence pending.
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
Nova clears or blocks the pending Cap 22 action.
Nova does not open the target.
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
CAPTURED — automated evidence at commit 59f232e.

Behavioral session tests:
  test_session_no_clears_pending_without_execution — PASSED
    asserts calls == [] (no executor dispatch)
    asserts ACTION_ATTEMPTED not in ledger events
    asserts ACTION_COMPLETED not in ledger events
    asserts "Cancelled pending action." in chat messages

  test_session_cancel_clears_pending_without_execution — PASSED
    asserts calls == [] (no executor dispatch)
    asserts ACTION_ATTEMPTED not in ledger events
    asserts ACTION_COMPLETED not in ledger events
    asserts "Cancelled pending action." in chat messages

Governance tests:
  test_confirmation_resolver_accepts_no — PASSED
  test_session_handler_clears_pending_on_cancel — PASSED
```

Remaining gap:

```text
No remaining automated gap for this scenario.
```

---

## Scenario D: Unrelated Input Does Not Approve

User input:

```text
Tell me the latest news.
```

Expected behavior:

```text
Nova does not treat unrelated input as approval.
Nova does not execute the pending Cap 22 action.
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
CAPTURED — automated evidence at commit 59f232e.

Behavioral session tests:
  test_session_unrelated_input_cancels_pending_without_execution — PASSED
    asserts calls == [] (no executor dispatch)
    asserts ACTION_ATTEMPTED not in ledger events
    asserts ACTION_COMPLETED not in ledger events
    asserts "Cancelled the pending action before handling your new command."
      in chat messages

Governance tests:
  test_confirmation_resolver_rejects_ambiguous_input — PASSED
  test_session_handler_clears_pending_on_unrelated_input — PASSED

Current session contract: unrelated input cancels the pending action and
then processes the new input. The pending action is not silently kept.
```

Remaining gap:

```text
No remaining automated gap for this scenario.
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
Nova does not open the pending target during interruption or restore.
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
pending — no automated recovery test path exists for Cap 22.
```

Remaining gap:

```text
Recovery evidence remains pending. No automated recovery test path
exists in the current test suite. Same gap as Cap 64 recovery.
If needed, a manual recovery transcript can be captured during the
live proof session.
```

---

## Path Root Boundary Proof

This proof is specific to Cap 22 and has no Cap 64 parallel.

Expected behavior:

```text
Cap 22 only opens targets inside Nova-approved path roots.
A request targeting a path outside approved roots is refused before confirmation.
The executor does not attempt to open disallowed paths.
```

Evidence to capture:

```text
test output showing disallowed-path refusal
executor _is_allowed_path assertion
ledger or operator note
```

Current evidence:

```text
CAPTURED — automated evidence at commit 59f232e.

Path-root allowlist tests:
  test_is_allowed_path_accepts_home_subpath — PASSED
  test_is_allowed_path_rejects_parent_scope — PASSED
  test_is_allowed_path_accepts_workspace_root_outside_home — PASSED
  test_open_path_uses_workspace_root_allowlist — PASSED

Executor boundary tests:
  test_open_folder_rejects_non_preset — PASSED
  test_open_folder_accepts_explicit_path — PASSED
  test_open_folder_executor_opens_explicit_existing_path — PASSED
  test_open_folder_executor_fails_for_missing_explicit_path — PASSED
  test_open_folder_executor_opens_preset_folder — PASSED
```

Remaining gap:

```text
No remaining automated gap for path-root boundary proof.
```

---

## Live Open Proof

This proof is separate from automated behavioral session coverage.

Required live preconditions:

```text
Nova running at http://localhost:8000
Windows desktop with File Explorer available
chat tab open
target folder exists (e.g. Downloads, Documents)
```

Expected live behavior:

```text
Nova asks for confirmation before opening the target.
After yes, the local system open handler opens the target.
File Explorer (or default handler) shows the expected folder or file.
At least one matching receipt is visible through the Trust Panel or
http://localhost:8000/api/trust/receipts, if present on the current runtime.
```

Must not happen:

```text
no file mutation
no file deletion
no file creation
no external write
no arbitrary path access
no browser/computer-use expansion
```

Current live evidence:

```text
CAPTURED — live WebSocket proof at 2026-05-19T04:49 UTC on localhost:8000.

Live approval test:
  SENT: {"type":"chat","text":"open my documents folder"}
  RECV: "Open documents?\nThis action needs confirmation.\nReply 'yes'
        to proceed or 'no' to cancel."
  SENT: {"type":"chat","text":"yes"}
  RECV: chat_done (action executed)
  Receipt: ACTION_ATTEMPTED at 04:49:19 → ACTION_COMPLETED at 04:49:20
    capability_id: 22, success: true, authority_class: reversible_local,
    requires_confirmation: true, external_effect: false

Live denial test:
  SENT: {"type":"chat","text":"open my downloads folder"}
  RECV: "Open downloads?\nThis action needs confirmation.\nReply 'yes'
        to proceed or 'no' to cancel."
  SENT: {"type":"chat","text":"no"}
  RECV: chat_done (no action executed)
  Receipt check: no new Cap 22 receipt after 04:49:43 — denial confirmed
```

Remaining gap:

```text
No remaining live proof gap for approval and denial paths.
Recovery evidence remains pending.
```

---

## Required Test Commands

Commands run and results recorded at commit `59f232e`:

```text
python -m pytest tests/websocket/test_behavioral_session_approval_gate.py -v
  → 11 passed in 39.97s

python -m pytest tests/governance/test_approval_gate_wiring.py -v
  → 24 passed in 16.88s

python -m pytest tests/executors/test_open_folder_executor.py
    tests/test_open_folder_executor.py -v
  → 5 passed in 0.46s

python -m pytest tests/ -v -k "cap22 or cap_22 or open_file or
    open_folder or open_path or allowed_path"
  → 23 passed, 2557 deselected in 21.02s

python -m pytest tests/executors/test_local_action_executors.py
    tests/executors/test_system_control_executor.py
    tests/test_system_control_executor.py -v -k "open"
  → 4 passed, 9 deselected in 0.38s
```

Total unique Cap 22-related tests: 23, all passing.

Focused areas covered:

```text
Cap 22 executor tests — covered
Cap 22 routing tests — covered (brain server basic conversation)
behavioral session approval-gate tests — covered
approval-gate regression tests — covered
governor / ledger tests relevant to Cap 22 — covered
path-root boundary tests — covered
duplicate-yes non-double-execution — covered
```

Do not record:

```text
full-suite pass
approval-gate certification
Cap 22 locked
Cap 22 globally certified
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
bounded local open through approved path root
ACTION_COMPLETED or documented failure result after executor return
receipt evidence when open action succeeds
```

Captured ledger excerpt:

```text
Automated ledger verification at commit 59f232e:

Pending path (Scenario A):
  ACTION_ATTEMPTED not in ledger — ASSERTED
  ACTION_COMPLETED not in ledger — ASSERTED

Approved path (Scenario B):
  ledger == ["ACTION_ATTEMPTED", "ACTION_COMPLETED"] — ASSERTED
  (test_session_yes_resumes_pending_cap22_only_through_governed_invocation)

  Real governor ledger:
  ACTION_ATTEMPTED count == 1 — ASSERTED
  ACTION_COMPLETED count == 1 — ASSERTED
  (test_session_approved_cap22_uses_real_governor_ledger_sequence)

Denied / cancelled path (Scenario C):
  ACTION_ATTEMPTED not in ledger — ASSERTED
  ACTION_COMPLETED not in ledger — ASSERTED

Unrelated input path (Scenario D):
  ACTION_ATTEMPTED not in ledger — ASSERTED
  ACTION_COMPLETED not in ledger — ASSERTED

Duplicate-yes path:
  ACTION_ATTEMPTED count == 1 — ASSERTED
  ACTION_COMPLETED count == 1 — ASSERTED
  (test_session_duplicate_yes_does_not_double_execute_cap22)
```

Remaining gap:

```text
No remaining automated ledger gap.
Live receipt evidence captured (see Receipt / Trust Panel Evidence below).
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

Captured receipt excerpt:

```json
{
  "timestamp_utc": "2026-05-19T04:49:20.147722+00:00",
  "event_type": "ACTION_COMPLETED",
  "capability_id": 22,
  "request_id": "61454428-5819-4908-ba28-353b4e530ac5",
  "success": true,
  "status": "completed",
  "external_effect": false,
  "reversible": true,
  "authority_class": "reversible_local",
  "requires_confirmation": true
}
```

Denial receipt check:

```text
No new Cap 22 receipt generated after denial at 04:49:43 UTC.
Denial path correctly blocked execution and receipt creation.
```

Remaining gap:

```text
No remaining receipt gap for approval and denial paths.
```

---

## Manual Steps Performed

```text
1. Ran cap22_live_proof.py against localhost:8000 via WebSocket.
2. Nova identified "open my documents folder" as Cap 22.
3. Nova asked for confirmation before opening.
4. Sent "yes" — Documents folder opened locally.
5. Verified receipt at /api/trust/receipts showing ACTION_COMPLETED.
6. Ran cap22_live_denial.py — sent "no" to a Downloads open request.
7. Verified no new receipt was created for the denied action.
```

Manual observation:

```text
The target opened locally and matched the expected folder (Documents).
```

---

## Blocked-Path Evidence

The proof must show:

```text
pending action did not execute
denied action did not execute
cancelled action did not execute
unrelated input did not execute
disallowed path was refused before confirmation
ambiguous confirmation did not execute, if tested
duplicate yes did not double-execute, if tested
```

Captured blocked-path evidence:

```text
CAPTURED — automated evidence at commit 59f232e.

pending action did not execute — ASSERTED (Scenario A)
denied action did not execute — ASSERTED (Scenario C, "no" path)
cancelled action did not execute — ASSERTED (Scenario C, "cancel" path)
unrelated input did not execute — ASSERTED (Scenario D)
disallowed path was refused — ASSERTED
  (test_is_allowed_path_rejects_parent_scope,
   test_open_folder_rejects_non_preset)
duplicate yes did not double-execute — ASSERTED
  (test_session_duplicate_yes_does_not_double_execute_cap22)
```

---

## Remaining Unverified Items

```text
repo commit SHA for proof run — CAPTURED (59f232e)
focused test command output — CAPTURED (23 tests, 0 failures)
approved governed invocation evidence — CAPTURED (automated)
pending non-execution evidence — CAPTURED (automated)
denied/cancelled non-execution evidence — CAPTURED (automated)
unrelated-input non-execution evidence — CAPTURED (automated)
disallowed-path refusal evidence — CAPTURED (automated)
ledger excerpts — CAPTURED (automated assertions)
receipt / Trust Panel evidence — CAPTURED (live at 2026-05-19T04:49 UTC)
manual live open observation — CAPTURED (Documents folder opened)
recovery behavior evidence — PENDING (no automated path)
```

---

## Certification Status

Current status:

```text
Automated evidence captured: 23 tests, 0 failures across 7 test files.
Scenarios A-D: fully covered by automated evidence.
Path-root boundary: fully covered by automated evidence.
Duplicate-yes: covered.
Live proof: captured (approval + denial).
Receipt / Trust Panel evidence: captured (ACTION_COMPLETED receipt verified).
Recovery evidence: pending (no automated path).
Cap 22 remains not locked.
Cap 22 remains not globally certified.
Full approval-gate certification remains pending.
```

Safe wording after this evidence lands:

```text
Cap 22 automated + live proof captured (23 tests + live approval/denial
with receipt verification). Only recovery evidence remains pending.
```

Do not say:

```text
Cap 22 locked
Cap 22 certified
Cap 22 globally certified
approval gate complete
approval gate fully certified
all approval-gate paths proven
```

---

## Next Action

Automated and live evidence are captured. Remaining steps:

```text
1. Decide whether recovery evidence is needed for Cap 22 signoff
   or can remain a documented follow-up (same decision as Cap 64).
2. Only then decide whether Cap 22 signoff is supportable.
```

Final boundary:

```text
This proof scaffold is not a lock.
This proof scaffold is not certification.
The current authorized user remains the approver.
```
