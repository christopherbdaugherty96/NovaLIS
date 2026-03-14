# Pattern Detection Opt-In Guardrails Spec
Date: 2026-03-09
Commit: 6932b42
Status: Historical draft input (superseded for the closed Phase-5 package)
Scope: Original pattern-review guardrail input. Retained for traceability only.

## Historical Note
This document is not the current authority for the closed Phase-5 package.

Use instead:
- `PHASE_5_PATTERN_DETECTION_RATIFICATION_ACT_2026-03-13.md`
- `PHASE_5_PROOF_PACKET_INDEX.md`

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
- Pattern review does not unlock autonomous behavior.

## Audit Requirements
- Pattern generation events are logged.
- Opt-in state transitions are logged.
- Approval and rejection decisions are logged.

## Historical Decision
This document records the pre-ratification guardrail input only.
It does not satisfy the current Phase-5 authority chain by itself.
