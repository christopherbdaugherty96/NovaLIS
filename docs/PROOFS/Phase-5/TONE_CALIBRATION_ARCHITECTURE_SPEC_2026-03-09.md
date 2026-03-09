# Tone Calibration Architecture Spec
Date: 2026-03-09
Commit: 6932b42
Status: Draft candidate (pending approval)
Scope: Constitutional design constraints for tone adaptation; not yet gate-approved.

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

## Non-Authorization Note
This spec approves design constraints only.
No new execution capability is granted.
Phase-5 admission gate credit remains pending formal approval.
