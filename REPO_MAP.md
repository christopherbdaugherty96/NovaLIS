# REPO_MAP - Nova

Purpose: clear navigation map for engineers, reviewers, and future collaborators.

## Start Here

If you are new to the project, use this order:

1. `docs/reference/HUMAN_GUIDES/README.md`
2. `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
3. `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
4. `docs/current_runtime/RUNTIME_FINGERPRINT.md`
5. `docs/canonical/CANONICAL_DOCUMENT_MAP.md`

This sequence gives you:
- the human explanation first
- the runtime truth second
- the deeper governance map after that

## Runtime Truth

For runtime behavior, authority boundaries, and live system status, use:

`docs/current_runtime/CURRENT_RUNTIME_STATE.md`

If any other file conflicts with live runtime behavior, `docs/current_runtime/CURRENT_RUNTIME_STATE.md` is authoritative.

Helpful companion files:
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- `docs/current_runtime/RUNTIME_TRUTH_ADDENDUM_2026-03-12.md`

## Documentation Layers

Nova's docs are intentionally separated by role:

- Human guides:
  - `docs/reference/HUMAN_GUIDES/`
  - plain-language explanation of the project

- Runtime truth:
  - `docs/current_runtime/`
  - generated and runtime-aligned operational truth

- Proof packets:
  - `docs/PROOFS/`
  - implementation and verification evidence

- Design docs:
  - `docs/design/`
  - design intent, planning, and future-phase thinking

- Canonical governance:
  - `docs/canonical/`
  - constitutional and governance source material

## Main Repository Surfaces

- `nova_backend/src/`
  - backend runtime, orchestration, governor path, executors, cognition, continuity, and memory systems

- `nova_backend/tests/`
  - runtime, governance, phase, and regression tests

- `nova_backend/static/`
  - runtime-served frontend assets

- `Nova-Frontend-Dashboard/`
  - historical mirror copy of the frontend
  - useful for comparison, but `nova_backend/static/` is the runtime-served canonical frontend
  - if `scripts/check_frontend_mirror_sync.py` reports drift, trust `nova_backend/static/`

- `docs/`
  - runtime truth, proofs, design docs, human guides, and governance material

## Backend Orientation

If you are reviewing the backend, this is the fastest useful order:

1. `nova_backend/src/brain_server.py`
2. `nova_backend/src/governor/`
3. `nova_backend/src/executors/`
4. `nova_backend/src/conversation/`
5. `nova_backend/src/working_context/`
6. `nova_backend/src/memory/`
7. `nova_backend/src/personality/`

## Frontend Orientation

If you are reviewing the user experience surface, start here:

1. `nova_backend/static/dashboard.js`
2. `nova_backend/static/orb.js`
3. `nova_backend/static/style.phase1.css`
4. `nova_backend/static/index.html`

Then compare with:

- `Nova-Frontend-Dashboard/`

## Review Guardrails

When reviewing changes, keep these constraints in mind:

- no hidden autonomy
- no background execution loops
- no silent persistence
- no direct execution from cognitive reasoning
- no direct network paths outside approved mediation
- no drift between explanatory docs and runtime truth

## Short Version

The simplest way to navigate Nova is:

- read the human guides to understand the project
- read the runtime truth docs to understand what is live
- read `brain_server.py` and `src/governor/` to understand control flow
- read tests to understand the enforced boundaries
