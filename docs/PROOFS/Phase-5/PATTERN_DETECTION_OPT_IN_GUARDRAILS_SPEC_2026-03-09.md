# Pattern Detection Opt-In Guardrails Spec
Date: 2026-03-09
Commit: 6932b42
Status: Draft candidate (pending ratification)
Scope: Defines constraints for pattern detection in Phase-5 design.

## Core Rule
Pattern detection is opt-in only and cannot produce autonomous execution.

## Required Guardrails
1. Explicit user opt-in is required before pattern analysis.
2. Patterns are advisory only and routed to a review queue.
3. No auto-apply of detected patterns.
4. No implicit delegation from historical interaction traces.
5. No background cognition loop is permitted.
6. Any action from a pattern output still requires explicit user invocation and Governor mediation.

## Boundary Conditions
- Pattern outputs are informational proposals.
- Proposals are visible, reversible, and discardable.
- Proposals cannot reorder UI priorities automatically.

## Audit Requirements
- Pattern generation events are logged.
- Opt-in state transitions are logged.
- Approval and rejection decisions are logged.

## Non-Authorization Note
This spec does not unlock autonomous behavior and does not expand authority.
Phase-5 admission gate credit remains pending formal ratification.
