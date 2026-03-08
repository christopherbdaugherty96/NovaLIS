# Trust Telemetry Authoritative Proof
Date: 2026-03-08
Commit: 9f5aba0
Scope: Proof that dashboard trust state is backend-emitted runtime telemetry, not UI-only inference.

## 1. Backend Emission Path
Primary file: `nova_backend/src/brain_server.py`

Evidence:
- `send_trust_status(...)` emits websocket payload:
  - `{"type": "trust_status", "data": ...}`
- Trust state is updated at governed execution and skill completion points
- Telemetry is emitted after state transitions (normal/degraded, local-only/online)

This makes trust status an explicit runtime signal channel from backend state.

## 2. UI Consumption Contract
Primary file: `nova_backend/static/dashboard.js`

Expected contract:
- UI listens for websocket messages of type `trust_status`
- UI trust panel fields are populated from payload data
- UI does not need to infer trust state from assistant prose

## 3. Governance Impact
This closes the observability mismatch class where text heuristics could diverge from runtime truth.
Trust panel state is now sourced from backend telemetry events tied to governed execution flow.

## 4. Related Runtime Invariants
- Governor remains sole authority for execution
- Trust telemetry is informational only (non-authorizing)
- Ledger remains action audit system of record

## 5. Conclusion
Trust telemetry now uses explicit backend-to-UI eventing and is suitable for Phase-4 proof closure and Phase-4.2 admission readiness.
