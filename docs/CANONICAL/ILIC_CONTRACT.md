# Nova Internal Loopback Inference Channel (ILIC) Contract

## Status
- Constitutional component: **active**
- Plane: **Cognitive Plane**
- Scope: Local Ollama inference transport only

## Purpose
ILIC defines the only permitted transport path between Nova conversational cognition and local Ollama.
It exists to preserve conversational autonomy while preventing authority-surface expansion.

## Constitutional Boundary
ILIC is **not** a capability executor.
ILIC is **not** an external networking channel.
ILIC is **not** a substitute for Governor or NetworkMediator authority controls.

### Allowed
- Local loopback HTTP transport to Ollama for inference metadata and generation.
- Conversational reasoning support (digest checks, health checks, generation).

### Prohibited
- Non-loopback endpoints.
- Dynamic external host support.
- Redirect-following to alternate hosts.
- Proxy inheritance from environment.
- Capability/action execution through ILIC.

## Hard Constraints
1. **Scheme lock**: `http` only.
2. **Host lock**: `localhost` or `127.0.0.1` only.
3. **Port lock**: approved Ollama port only (`11434`).
4. **No path/query/fragment in base URL**.
5. **Loopback resolution enforcement**: hostname resolution must produce loopback addresses only.
6. **Proxy isolation**: `trust_env=False`, empty proxies map.
7. **Redirect denial**: all ILIC calls set `allow_redirects=False`.
8. **Timeout policy**:
   - metadata calls use strict connect/read timeout pair.
   - inference calls use strict connect/read timeout pair.
9. **Fail-closed startup validation**:
   - invalid ILIC endpoint blocks inference at manager initialization.
10. **Non-authorizing audit events only**:
   - `ILIC_REQUEST`, `ILIC_FAILURE`, `ILIC_VALIDATION_FAILED`.
   - no action capability ledger events for inference transport.

## Intelligence–Authority Split Mapping

### Cognitive Plane (ILIC)
Conversation Layer -> EscalationPolicy -> LLMManager (ILIC) -> Ollama (local loopback)

### Authority Plane (Governor)
Skills/Actions -> Governor -> NetworkMediator (capability-bound) -> External APIs

ILIC must never invoke authority-plane components.

## Residual Risk
- Local host compromise remains possible if the local model service is compromised.
- Prompt-level output risk remains a cognitive safety concern.
- Authority remains sealed as long as Governor and capability boundaries are unchanged.

## Governance Test Requirements
ILIC compliance requires CI tests for:
- loopback-only base URL validation
- non-loopback rejection
- DNS fail-closed behavior
- proxy isolation
- redirect denial presence
- import-surface restrictions for direct `requests`
- non-authorizing audit event usage
