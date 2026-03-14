# Notification Scheduling Boundary Spec
Date: 2026-03-09
Commit: 6932b42
Status: Historical draft input (superseded for the closed Phase-5 package)
Scope: Original scheduling-boundary input. Retained for traceability only.

## Historical Note
This document is not the current authority for the closed Phase-5 package.

Use instead:
- `PHASE_5_NOTIFICATION_SCHEDULING_RATIFICATION_ACT_2026-03-13.md`
- `PHASE_5_PROOF_PACKET_INDEX.md`

## Core Rule
Notification scheduling is user-directed, explicit, and revocable.

## Required Constraints
1. A schedule can be created only by explicit user request.
2. No inferred reminders from observed behavior.
3. No autonomous schedule creation or recurrence expansion.
4. Every scheduled notification must be inspectable and cancellable.
5. Notification delivery must not bypass governor policy checks.
6. Notification text must remain factual and non-persuasive.

## Safety Requirements
- Default state is no schedule.
- Failed delivery must not trigger autonomous retries that violate policy envelopes.
- Rate limits and quiet-window policies are explicit and user-configurable.
- Explicit scheduling does not grant background autonomy.

## Audit Requirements
- Create/update/delete schedule events are logged.
- Delivery attempts and outcomes are logged.
- User override actions are logged.

## Historical Decision
This document records the pre-ratification boundary input only.
It does not satisfy the current Phase-5 authority chain by itself.
