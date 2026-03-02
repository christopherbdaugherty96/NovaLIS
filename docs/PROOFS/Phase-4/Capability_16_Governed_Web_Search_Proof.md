# Capability 16 — Governed Web Search Proof
**Date:** 2026-03-02
**Commit:** `6574a355f2db7fb00d7e0fb9451f60f9f16eac21`
**Scope:** End-to-end proof for the governed web search capability.

---

## 1. Full Execution Path

```
User: "search for climate change"
  → GovernorMediator.parse_governed_invocation() → Invocation(16, {"query": "climate change"})
  → Governor.handle_governed_invocation(16, {"query": "climate change"})
    → Gate 1: CapabilityRegistry.get(16) → Capability(governed_web_search, active, enabled=True)
    → Gate 2: is_enabled(16) → True
    → Gate 3: ExecuteBoundary.allow_execution() → True
    → Gate 4: SingleActionQueue.has_pending() → False
    → Gate 5: Ledger.log_event("ACTION_ATTEMPTED", {capability_id: 16, ...})
    → ActionRequest(capability_id=16, params={"query": "climate change"}, request_id=UUID)
    → Governor._execute(req)
      → Ledger.log_event("SEARCH_QUERY", {"query": "climate change"})
      → WebSearchExecutor(network, execute_boundary).execute(req)
        → NetworkMediator.request(capability_id=16, method="GET", url="https://api.search.brave.com/res/v1/web/search", ...)
      → ActionResult.ok(message=..., data={"widget": {"type": "search", "data": {"results": [...]}}})
      → Ledger.log_event("ACTION_COMPLETED", {capability_id: 16, request_id: UUID, success: True})
  → ActionResult returned to caller
```

---

## 2. Executor Implementation

**File:** `nova_backend/src/executors/web_search_executor.py`

### Key properties:

| Property | Implementation |
|---|---|
| **API endpoint** | `https://api.search.brave.com/res/v1/web/search` |
| **Auth** | `BRAVE_API_KEY` environment variable → `X-Subscription-Token` header |
| **Missing key** | Returns `ActionResult(success=False, message="Search service is not configured.")` |
| **Network routing** | All HTTP through `self.network` (NetworkMediator) |
| **Result cap** | Max 5 results, titles capped at 100 chars, snippets at 200 chars |
| **Hard timeout** | `SEARCH_HARD_TIMEOUT_SECONDS = 7.0` — wall-clock limit for entire operation |
| **Retry** | 1 retry with 0.5s backoff on `NetworkMediatorError` |
| **HTTP error handling** | 401 (auth failed), 429 (rate limit), 202 (unavailable), other non-200 — all deterministic messages |

### Output structure:

```json
{
  "widget": {
    "type": "search",
    "data": {
      "results": [
        {"title": "...", "url": "...", "snippet": "..."},
        ...
      ]
    }
  }
}
```

---

## 3. Failure Mode Coverage

| Failure | Handling |
|---|---|
| Empty query | `ActionResult(success=False, message="No search query provided.")` |
| Missing API key | `ActionResult(success=False, message="Search service is not configured.")` |
| Hard timeout (>7s) | `ActionResult(success=False, message="... Search timed out...")` |
| Network error (both retries) | `ActionResult(success=False, message="... network issue.")` |
| HTTP 401 | `ActionResult(success=False, message="... authentication failed.")` |
| HTTP 429 | `ActionResult(success=False, message="... rate limit reached...")` |
| HTTP 202 | `ActionResult(success=False, message="... temporarily unavailable...")` |
| Other non-200 | `ActionResult(success=False, message="... unexpected response...")` |
| Empty results | `ActionResult.ok(message="... No reliable results were found.")` |

Every path returns an `ActionResult`. No exceptions escape.

---

## 4. Ledger Events

| Event | Stage |
|---|---|
| `ACTION_ATTEMPTED` | Before execution (Governor) |
| `SEARCH_QUERY` | Before HTTP call (Governor, non-blocking) |
| `EXTERNAL_NETWORK_CALL` | After successful HTTP (NetworkMediator) |
| `NETWORK_CALL_FAILED` | On HTTP failure (NetworkMediator) |
| `ACTION_COMPLETED` | After executor returns (Governor, best-effort) |

---

## 5. Conclusion

Capability 16 is fully governed: registry-enabled, mediator-parsed, Governor-gated, network-mediated, ledger-tracked, timeout-bounded, and deterministically failure-handled.