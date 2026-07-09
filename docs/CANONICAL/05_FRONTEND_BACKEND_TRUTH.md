# 05 — Frontend / Backend Truth (how the code is laid out)

**Status: current.** Structural orientation, maintained by hand. The authoritative navigation
source is `REPO_MAP.md`; this file only summarizes it.

## Source of record

- [`../../REPO_MAP.md`](../../REPO_MAP.md) — engineer navigation map for code and docs.

## Backend (`nova_backend/`)

Fastest useful read order (from `REPO_MAP.md`):

1. `src/brain_server.py` — app assembly, middleware, lifespan, singleton wiring.
2. `src/websocket/session_handler.py` — live session loop, command routing, governor invocation.
3. `src/governor/` — authority spine (see [03_GOVERNANCE_TRUTH.md](03_GOVERNANCE_TRUTH.md)).
4. `src/executors/` — one worker per capability ID.
5. `src/conversation/` — routing, DeepSeek bridge, general-chat runtime, safety filter.
6. `src/working_context/` — session continuity, assistive noticing.
7. `src/memory/` — governed memory store and recall.
8. `src/personality/` — two-layer voice system.
9. `src/openclaw/` — Phase 8 home-agent runner, scheduler, preflight.

## Frontend (runtime-served)

- Canonical served UI is the **modular static bundle** at `nova_backend/static/`:
  `index.html`, `dashboard-config.js`, `dashboard.js`, `dashboard-workspace.js`,
  `dashboard-control-center.js`, `dashboard-chat-news.js`, plus `style.phase1.css`,
  `dashboard-surfaces.css`, `orb.js`.
- Do **not** review it as if `dashboard.js` alone were the whole UI.

## The frontend mirror caveat (important)

- `Nova-Frontend-Dashboard/` is a **historical mirror copy**, useful for comparison only.
- `nova_backend/static/` is the runtime-served canonical frontend.
- If `scripts/check_frontend_mirror_sync.py` reports drift, **trust `nova_backend/static/`.**

## Tests

- `nova_backend/tests/` — runtime, governance, phase, and regression tests.
- Dashboard-focused tests should use `nova_backend/tests/_dashboard_bundle.py`.
