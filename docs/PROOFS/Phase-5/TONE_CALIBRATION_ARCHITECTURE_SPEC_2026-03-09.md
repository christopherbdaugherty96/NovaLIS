# Tone Calibration Architecture Spec
Date: 2026-03-09
Commit: 6932b42
Status: Historical draft input (superseded for the closed Phase-5 package)
Scope: Original tone-calibration design constraint input. Retained for traceability only.

## Historical Note
This document is not the current authority for the closed Phase-5 package.

Use instead:
- `PHASE_5_TONE_CALIBRATION_APPROVAL_ACT_2026-03-13.md`
- `PHASE_5_PROOF_PACKET_INDEX.md`

## Architectural Model
Hierarchical tone resolution:
1. Global base profile
2. Domain-level overrides
3. Fixed per-surface rendering adaptation
4. Explicit user overrides (highest priority)

## Allowed Mutation Class
- Tone calibration changes are formatting-only (`Class C`).
- No authority logic coupling is permitted.

## Required Constraints
1. No proactive adaptation announcements.
2. No persuasive framing.
3. User override and reset must be available.
4. Adaptation history must be inspectable.
5. Domain boundaries must be explicit and finite.
6. Surface adaptation defaults to fixed renderer rules, not hidden behavior learning.

## Governance and Audit Requirements
- Changes are logged in ledger or equivalent immutable audit stream.
- Each mutation is reversible.
- Kill switch semantics must disable adaptive mutation paths.

## Historical Decision
This document records the pre-approval design state only.
It does not satisfy the current Phase-5 authority chain by itself.
