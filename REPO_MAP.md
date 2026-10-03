# REPO_MAP - Nova

Purpose: a navigation map for engineers, reviewers, and AI agents.

## Start here

1. `.agent_context/current_priority.md`: current work ordering (the top Alpha 0 block governs)
2. `AGENTS.md`: binding rules for agents working in this repository
3. `docs/CANONICAL/00_INDEX.md`: how to read repo truth and resolve conflicting documents
4. `docs/current_runtime/CURRENT_RUNTIME_STATE.md`: generated runtime truth
5. `docs/capability_verification/CAPABILITY_INVENTORY.md`: what has been verified, and how
6. `docs/product/PRODUCT_DEFINITION.md`: identity and permanent architecture

This is a reading order, not an authority ranking. Code is authoritative for behavior. Generated
runtime documents are authoritative only for what their generators measure. Older status
documents keep their history but may carry stale "current" wording.

## Runtime truth

Generated from code by `scripts/generate_runtime_docs.py`; do not edit by hand:

- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- `docs/current_runtime/GOVERNANCE_MATRIX.md`
- `docs/current_runtime/ROUTE_PROTECTION_COVERAGE.md`
- `docs/current_runtime/BYPASS_SURFACES.md`

## Documentation layers

- `docs/CANONICAL/`: truth-reading rules and canonical governance, runtime, and roadmap truth
- `docs/current_runtime/`: generated runtime truth
- `docs/status/`: work chronology (the Daily Command Center and dated status records)
- `docs/product/`: product definition, limitations, and user-facing explanations
- `docs/capability_verification/`: capability verification status and evidence index
- `docs/PROOFS/`, `docs/demo_proof/`: dated proof packages, evidence for the revisions they name
- `docs/future/`, `docs/design/`: strategy and design; non-authorizing
- `docs/reference/HUMAN_GUIDES/`: plain-language explanations (historical framing, May 2026)

## Main repository surfaces

- `nova_backend/src/`: backend runtime
- `nova_backend/tests/`: governance, adversarial, durability, WebSocket, and regression tests
- `nova_backend/static/`: the frontend Nova actually serves
- `Nova-Frontend-Dashboard/`: maintained mirror of the frontend. Tests require byte parity with
  `nova_backend/static/`; when they disagree, `nova_backend/static/` is what users see
- `installer/windows/`: Windows installer definition and bootstrap script
- `scripts/`: launchers, runtime-truth generation, and consistency checks
- `.agent_context/`: current priority and agent context; `handoffs/` holds Codex/Claude handoffs
- `automations/`: tracked Codex automation definitions

## Backend orientation

Fastest useful reading order:

1. `nova_backend/src/brain_server.py`: app assembly, middleware, startup, singletons
2. `nova_backend/src/websocket/session_handler.py`: live session loop and command routing
3. `nova_backend/src/governor/`: the authority spine
   - `governor_mediator.py`: parses and routes governed invocations
   - `governor.py`: approval consumption, dispatch, timeouts, outcome records
   - `approval_grants.py`: single-use, action-bound approval grants
   - `capability_registry.py`, `execute_boundary/`, `network_mediator.py`
4. `nova_backend/src/ledger/`: append-only ledger and event types
5. `nova_backend/src/executors/`: one worker per capability
6. `nova_backend/src/utils/local_request_guard.py`, `route_protection.py`: local-only boundary
7. `nova_backend/src/memory/`: governed memory
8. `nova_backend/src/durability/`: state layout, corruption-safe readers, snapshots, recovery
   control plane (not yet adopted by the ordinary runtime)
9. `nova_backend/src/conversation/`, `providers/`: routing, local and external reasoning
10. `nova_backend/src/openclaw/`: bounded home-agent runner and scheduler

## Frontend orientation

1. `nova_backend/static/index.html`
2. `nova_backend/static/dashboard-config.js`
3. `nova_backend/static/dashboard.js`
4. `nova_backend/static/dashboard-workspace.js`
5. `nova_backend/static/dashboard-control-center.js`
6. `nova_backend/static/dashboard-chat-news.js`
7. `nova_backend/static/style.phase1.css`, `dashboard-surfaces.css`
8. `nova_backend/static/orb.js`

The frontend is a modular static bundle; do not review `dashboard.js` as if it were the whole
UI. Dashboard tests use `nova_backend/tests/_dashboard_bundle.py`.

## Review guardrails

- no hidden autonomy; background work only through the OpenClaw scheduler, and only when
  explicitly enabled in Settings
- no direct execution from model reasoning; governed actions go through the Governor
- no silent persistence; durable memory requires an explicit save
- outbound requests go through mediation; known exceptions are listed in
  `docs/current_runtime/BYPASS_SURFACES.md`
- local-only interfaces stay local-only
- no drift between explanatory docs and runtime truth

## Short version

- read `.agent_context/current_priority.md` to know what is being worked on
- read the generated runtime docs to know what is live
- read `brain_server.py` and `src/governor/` to understand control flow
- read the tests to see which boundaries are enforced
