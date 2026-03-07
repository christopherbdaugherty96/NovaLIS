# REPO_MAP - Nova

Purpose: deterministic navigation map for engineers and AI reviewers.

## Runtime Truth (Read First)

For runtime behavior, capability status, and execution authority truth, use:

`docs/current_runtime/CURRENT_RUNTIME_STATE.md`

If any file conflicts with runtime behavior, `CURRENT_RUNTIME_STATE.md` is authoritative.

## Canonical Governance

- `docs/canonical/NOVA COMPLETE CONSTITUTIONAL BLUEPRINT v1.9.txt`

## Main Surfaces

- `nova_backend/src/`: runtime backend (governor, skills, executors, services)
- `nova_backend/tests/`: tests and governance invariants
- `nova_backend/static/`: runtime-served frontend
- `Nova-Frontend-Dashboard/`: mirror frontend copy (must match runtime static files)
- `docs/current_runtime/`: generated runtime governance docs
- `docs/canonical/`: canonical governance and phase artifacts

## Recommended Review Order

1. `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
2. `nova_backend/src/brain_server.py`
3. `nova_backend/src/governor/`
4. `nova_backend/src/skills/` and `nova_backend/src/executors/`
5. `nova_backend/tests/`

## Reviewer Guardrails

- No new authority surfaces without governance updates
- No background execution or autonomous behavior
- No direct network imports outside approved mediation surfaces
- Prefer minimal diffs and invariant-preserving changes
