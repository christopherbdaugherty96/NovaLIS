# Notification Scheduling Boundary Spec
Date: 2026-03-09
Commit: 6932b42
Status: Draft candidate (pending ratification)
Scope: Boundaries for reminders and scheduled notifications.

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

## Audit Requirements
- Create/update/delete schedule events are logged.
- Delivery attempts and outcomes are logged.
- User override actions are logged.

## Non-Authorization Note
This boundary spec does not grant background autonomy and does not change current runtime phase state.
Phase-5 admission gate credit remains pending formal ratification.
