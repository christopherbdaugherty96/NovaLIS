# Runtime Truth

This page is the human-readable map of what Nova does today.

Canonical truth navigation lives at `docs/CANONICAL/00_INDEX.md`; the runtime-specific canonical map is `docs/CANONICAL/02_RUNTIME_TRUTH.md`.

For exact generated runtime state, use:

- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/GOVERNANCE_MATRIX.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`

Generated runtime docs and code beat roadmap language.

## Works Now

- FastAPI backend app imports and serves the local dashboard.
- `/ws` WebSocket path exists and accepts chat sessions.
- Local dashboard static UI is served from `nova_backend/static`.
- Capability registry loads active runtime capabilities from `nova_backend/src/config/registry.json`.
- Governor checks capability existence, enabled state, confirmation requirements, execution boundary, queue state, budget gates, and ledger writes before dispatch.
- Local HTTP boundary middleware blocks non-loopback/rebinding-style access.
- Trust receipt API routes exist at `/api/trust/receipts` and `/api/trust/receipts/summary`.
- Generated runtime docs are present under `docs/current_runtime`.

## Works With Setup

- Local LLM-backed responses require local model/runtime configuration.
- Weather, news, and search depend on provider/network configuration.
- Calendar snapshot behavior depends on local calendar data/configuration.
- Voice features depend on local speech tooling and model paths.
- Shopify intelligence is read-only and requires credentials/configuration.

## Partially Implemented

- Trust surfaces exist, but proof browsing and friendly receipt explanations still need product polish.
- OpenClaw runtime code exists, but broad browser/computer-use expansion is not certified.
- Brain/Task Understanding scaffolds exist, but the full Brain router is not live authority.
- Goal and workflow visibility surfaces exist, but broad execution envelopes remain deferred.
- Cost posture metadata exists; full runtime cost enforcement remains incomplete.

## Intentionally Blocked

- Shopify writes.
- Gmail/calendar writes.
- Email sending. Nova can open a local draft after confirmation; the human sends.
- Purchases, posting, account changes, external writes, and broad autonomous workflows.
- Treating memory, notes, receipts, or docs as permission.
- Browser/computer-use expansion without a separate reviewed governance lock.

## Not Built

- One-click mainstream installer.
- Full consumer onboarding.
- General autonomous agent swarm.
- Enterprise orchestration layer.
- Complete daily operating-system workflow automation.

## Stale Or Historical

Some docs are retained as design history, audit trail, or future planning. If a historical document conflicts with runtime code or generated runtime docs, treat it as historical.

Use this rule:

```text
runtime code + generated runtime docs + tests > roadmap docs
```
