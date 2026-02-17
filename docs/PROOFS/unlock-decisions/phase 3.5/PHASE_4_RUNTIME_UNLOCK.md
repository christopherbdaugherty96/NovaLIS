PHASE_4_RUNTIME_UNLOCK.md

Nova Constitutional Runtime Authorization

Document Status

Artifact ID: NOVA-UNLOCK-PHASE-4-RUNTIME
Date: 2026-02-10
Scope: Phase-4 Runtime Authorization
Authority Change: Conditional
Phase Dependency: Phase-4 Design Approved
Phase-3.5 State: CLOSED, Frozen, Verified

1. Purpose

This document defines the conditions under which Phase-4 runtime authority may be enabled.

Phase-4 Runtime Unlock allows:

Controlled execution through the Governor

Explicit user-requested actions

External data retrieval on demand

This document does not authorize autonomy, background behavior, or learning.

2. Preconditions (Must Be True)

Phase-4 runtime may only be enabled if all conditions below are satisfied.

2.1 Phase-3.5 Containment Evidence

Required:

docs/PROOFS/governance-tests/reports/


Criteria:

Corpus executed against frozen system

Critical failures = 0

Verdict: CONTAINMENT_VERIFIED

If any critical failure exists → Unlock denied

2.2 Mechanical Execution Control

Execution must be:

Disabled by default

Enabled only through:

GOVERNED_ACTIONS_ENABLED = True


Requirements:

No direct executor access

All execution routed through Governor

No alternative code paths

Verification evidence required:

verification/runtime-scan-results.txt

2.3 Governor Enforcement Proof

Governor must enforce:

Required Controls
Control	Requirement
Intent gating	Explicit command phrase required
Confirmation	Required for destructive or persistent actions
Scope enforcement	Action limited to requested resource
Timeout	Execution bounded
Error envelope	Fail-safe response on error

Evidence required:

verification/governor-enforcement-proof.txt

2.4 Quarantine Integrity

Execution modules must remain:

Isolated behind Execution Boundary

Non-importable outside Governor

Not callable directly

Evidence required:

verification/quarantine-verification.txt

3. Phase-4 Execution Model

All runtime actions must follow:

User
→ Intent Detection
→ ActionRequest
→ Governor Validation
→ Confirmation (if required)
→ Execution Boundary
→ Result
→ Ledger


If any step is bypassed → Runtime must be disabled

4. Allowed Phase-4 Capabilities (Runtime)

Only the following categories are permitted.

4.1 External Information (On Request Only)

Allowed:

Weather (current / forecast)

News headlines

Time-sensitive factual queries

Constraints:

No background polling

No proactive updates

No monitoring

4.2 Local Resource Access

Allowed:

Open file (explicit path or selection)

Read document

Save document (confirmation required)

Not allowed:

Directory scanning without request

Automatic file selection

4.3 Application Launch

Allowed:

Open browser

Open specified application

Open webpage (explicit URL or search)

Not allowed:

Session persistence

Background control

Automation loops

5. Prohibited in Phase-4 Runtime

The following behaviors remain constitutionally forbidden:

Autonomy

Background execution

Monitoring or alerts

Scheduled actions

Learning or adaptation

Preference inference

Proactive suggestions that imply execution

Continuous conversation memory beyond session

Violation of any item requires:

Immediate rollback to Phase-3.5 state

6. Explicit Invocation Rule

Actions may occur only when:

User intent is explicit

Action verb present

Target specified

Examples:

Allowed:

“Open Chrome”

“Open this file”

“Show weather”

“Summarize headlines”

Not allowed:

“Maybe I should check the weather”

“It would be good to open that”

“You might want to…”

7. Confirmation Requirements

Confirmation required for:

File save / overwrite

File deletion

External write operations

System changes

Confirmation format:

Single-line neutral prompt.
No persuasive language.

8. Observability & Audit

Phase-4 runtime must generate:

8.1 Action Ledger

Each execution logs:

Timestamp

User command

Action type

Target

Result

Duration

Location:

logs/action_ledger.jsonl

8.2 Failure Reporting

If execution fails:

No retry loops

No alternative actions

Return neutral failure message

9. Runtime Activation Procedure

Phase-4 runtime is activated only by:

All evidence files present

All criteria verified

Reviewer approval recorded

Configuration change:

GOVERNED_ACTIONS_ENABLED = True


No other code changes permitted at activation time.

10. Evidence Bundle Structure
docs/PROOFS/unlock-decisions/<bundle>/
│
├── PHASE_4_RUNTIME_UNLOCK.md
├── baseline-evidence.json
├── main-evidence-record.md
└── verification/
    ├── runtime-scan-results.txt
    ├── quarantine-verification.txt
    └── governor-enforcement-proof.txt

11. Unlock Decision

* All evidence verified
* No critical failures
* Governor enforcement confirmed
* Quarantine intact

Decision

* Phase-4 Runtime UNLOCKED
☐ Phase-4 Runtime remains LOCKED

Date: ___2-11-26___
Reviewer:Chris AKA CBD

12. Safety Principle

Phase-3.5 proved:

System cannot act

Phase-4 Runtime must prove:

System can act — but only when explicitly commanded

13. Failure Conditions (Automatic Re-Lock)

Phase-4 must be disabled immediately if any of the following occur:

Execution outside Governor

Background behavior detected

Autonomous action observed

Ledger missing or incomplete

Confirmation bypass

Recovery action:

GOVERNED_ACTIONS_ENABLED = False
Return to Phase-3.5 mode

14. Operational Summary

Phase-4 Runtime introduces:

Capability increase
Authority increase

But preserves:

Zero autonomy
Zero initiative