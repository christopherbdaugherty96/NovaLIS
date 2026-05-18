# Cap 22 Open File / Folder Operator Journey

Status: proof scaffold / evidence pending / not locked / not globally certified.

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
| Proof document status | scaffold / evidence pending |
| Repo commit SHA | pending capture at proof time |
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
pending
```

Remaining gap:

```text
Capture this path against the current main commit during the proof run.
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
pending
```

Remaining gap:

```text
Run the approved-path proof and record ledger/receipt/open evidence.
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
pending
```

Remaining gap:

```text
Capture denied and cancelled session paths against the current main commit.
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
pending
```

Remaining gap:

```text
Capture unrelated-input behavior and record the current session contract.
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
pending
```

Remaining gap:

```text
Determine whether an automated recovery test path exists. If not, capture a
manual transcript and mark the automated gap plainly.
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
pending
```

Remaining gap:

```text
Capture path-root boundary behavior against the current main commit.
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
pending
```

Remaining gap:

```text
Run the live checklist only when explicitly ready for Cap 22 evidence.
Do not run lock commands from this scaffold.
```

---

## Required Test Commands

Record exact commands and results here when the proof run happens.

```text
pending
```

Candidate focused areas:

```text
Cap 22 executor tests
Cap 22 routing tests
behavioral session approval-gate tests
approval-gate regression tests
governor / ledger tests relevant to Cap 22
path-root boundary tests
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
pending
```

Remaining gap:

```text
Capture ledger excerpts from the exact proof run.
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
pending
```

Remaining gap:

```text
Capture receipt evidence after an approved live open proof.
```

---

## Manual Steps Performed

```text
pending
```

Required manual note when live proof is run:

```text
The target opened locally and matched the expected folder or file.
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
pending
```

---

## Remaining Unverified Items

```text
repo commit SHA for proof run
focused test command output
approved governed invocation evidence
pending non-execution evidence
denied/cancelled non-execution evidence
unrelated-input non-execution evidence
disallowed-path refusal evidence
ledger excerpts
receipt / Trust Panel evidence
manual live open observation
recovery behavior evidence
```

---

## Certification Status

Current status:

```text
Evidence packet scaffold created.
Cap 22 remains not locked.
Cap 22 remains not globally certified.
Full approval-gate certification remains pending.
```

Safe wording after this scaffold lands:

```text
Cap 22 operator-journey proof scaffold added. Evidence capture remains pending.
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

When ready for evidence capture:

```text
1. Run focused Cap 22 / approval-gate tests.
2. Capture pending, approved, denied/cancelled, and unrelated-input behavior.
3. Capture disallowed-path refusal behavior.
4. Run the live open proof on a known safe target.
5. Capture ledger and receipt evidence.
6. Update this document with exact outputs and remaining gaps.
7. Only then decide whether Cap 22 signoff is supportable.
```

Final boundary:

```text
This proof scaffold is not a lock.
This proof scaffold is not certification.
The current authorized user remains the approver.
```
