# Model Network Mediation Proof
Date: 2026-03-08
Commit: 9f5aba0
Scope: Proof that local model network IO is mediated, constrained, and ledger-audited.

## 1. Mediator Boundary
Primary file: `nova_backend/src/llm/model_network_mediator.py`

Controls:
- Allowed schemes: `http`, `https`
- Host allowlist: localhost loopback/local addresses only
- IP classification rejects non-local/public endpoints
- DNS resolution check rejects resolved non-local addresses
- Request rate limiting (`RATE_LIMIT_PER_MINUTE`)
- Centralized request API (`request_json(...)`)
- Ledger events:
  - `MODEL_NETWORK_CALL`
  - `MODEL_NETWORK_CALL_FAILED`

## 2. Enforced Usage in LLM Path
- `nova_backend/src/llm/llm_manager.py` instantiates `ModelNetworkMediator`
- Model calls (`/api/show`, `/api/chat`, `/api/tags`) route through mediator
- `nova_backend/src/llm/llm_gateway.py` delegates to `llm_manager.generate(...)`

No direct arbitrary model HTTP calls are required in gateway flow.

## 3. Governance Alignment
This separates network authority surfaces cleanly:
- Governed external capability HTTP: `NetworkMediator`
- Local model transport HTTP: `ModelNetworkMediator`

Both are mediated and auditable; neither expands executor authority.

## 4. Test and Policy Evidence
- `tests/adversarial/test_no_direct_network_imports_outside_network_mediator.py`
- `tests/governance/test_no_direct_ollama_usage.py`
- `tests/test_ledger_event_allowlist.py` (model event types allowed and validated)

## 5. Conclusion
Local model IO is now explicitly mediated, bounded, and ledger-visible, satisfying Phase-4 network governance hardening needed before Phase-4.2 progression.
