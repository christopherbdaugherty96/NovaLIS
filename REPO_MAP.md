# REPO_MAP - Nova

Purpose: clear navigation map for engineers, reviewers, and future collaborators.

## Start Here

If you are new to the project, use this recommended reading order to learn the authority model:

1. `docs/CANONICAL/00_INDEX.md` — how to read repo truth (defines the authority model)
2. `docs/status/DAILY_COMMAND_CENTER.md` — where the project is right now
3. `docs/capability_verification/CAPABILITY_INVENTORY.md` — what verifiably works
4. `docs/product/PRODUCT_DEFINITION.md` — identity, mission, phases
5. `docs/current_runtime/CURRENT_RUNTIME_STATE.md` — generated runtime truth
6. `docs/reference/HUMAN_GUIDES/README.md` — plain-language explanation
   (historical/explanatory; aligned to the May 2026 stage frame)

This is a reading order, not an authority ranking. For runtime-existence claims, generated
runtime docs win; CANONICAL explains how to resolve conflicts.

This sequence gives you:
- the truth-reading rules first
- the current state second
- the runtime truth third
- the human explanation as supporting reference

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

- `automations/`
  - tracked Codex automation definitions and memory snapshots that should stay reviewable in GitHub
  - active local runtime copies still live under `$CODEX_HOME/automations/`

## Backend Orientation

If you are reviewing the backend, this is the fastest useful order:

1. `nova_backend/src/brain_server.py` — app assembly, middleware, lifespan, singleton wiring
2. `nova_backend/src/websocket/session_handler.py` — live session loop, all command routing, governor invocation
3. `nova_backend/src/governor/` — authority spine: mediator, governor, registry, execute boundary, network mediator
4. `nova_backend/src/executors/` — capability workers (one per capability ID)
5. `nova_backend/src/conversation/` — routing, deepseek bridge, general chat runtime, safety filter
6. `nova_backend/src/working_context/` — session continuity, assistive noticing, operational remembrance
7. `nova_backend/src/memory/` — governed memory store and recall
8. `nova_backend/src/personality/` — two-layer voice system (see guide 30 for the distinction)
9. `nova_backend/src/openclaw/` — Phase 8 home-agent runner, scheduler, preflight, personality bridge

## Frontend Orientation

If you are reviewing the user experience surface, start here:

1. `nova_backend/static/index.html`
2. `nova_backend/static/dashboard-config.js`
3. `nova_backend/static/dashboard.js`
4. `nova_backend/static/dashboard-workspace.js`
5. `nova_backend/static/dashboard-control-center.js`
6. `nova_backend/static/dashboard-chat-news.js`
7. `nova_backend/static/style.phase1.css`
8. `nova_backend/static/dashboard-surfaces.css`
9. `nova_backend/static/orb.js`

Then compare with:

- `Nova-Frontend-Dashboard/`

Review note:
- the live frontend is now a modular static bundle
- do not review it as if `dashboard.js` alone were the whole UI
- dashboard-focused tests should use `nova_backend/tests/_dashboard_bundle.py`

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
