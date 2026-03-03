# 

## Nova Phase-4 — Governor Bypass Proof (All Capabilities)

**Document ID:** `NOVA-GOV-BYPASS-PROOF-v2.0`  
**Status:** VERIFIED — All executor branches covered  
**Scope:** Phase-4 runtime, **all 9 executor branches** (capabilities 16, 17, 18, 19, 20, 21, 22, 32, 48)  
**Non-Authorizing:** This document does not grant authority. It records proof obligations and verification results.  
**Core Claim:** *No governed execution can occur without explicit, deterministic invocation through the Governor, and no outbound network can occur outside NetworkMediator.*

---

## 0) Definitions

- **Governor:** The sole authority gate for governed capabilities.
- **Governed capability:** Any action requiring elevated authority beyond read-only Phase-3 skills.
- **Bypass:** Any execution or external network call that occurs without passing through required gates (invocation parsing → Governor → ExecuteBoundary → CapabilityRegistry → Executor → NetworkMediator), or any "silent online" behavior.
- **Phase-4 runtime:** `GOVERNED_ACTIONS_ENABLED = True` is permitted, with 7 capabilities currently enabled and 2 disabled.

---

## 1) The Claim (What This Proof Guarantees)

### 1.1 Execution cannot occur without explicit invocation
A governed action will not run unless the user issues an explicit invocation that matches the deterministic invocation grammar.

### 1.2 No network can occur outside NetworkMediator
All outbound HTTP(S) requests are routed through `NetworkMediator` and are blocked if:
- capability is disabled
- domain/scheme is invalid
- destination is private/loopback
- rate limits are exceeded
- mediator refuses due to governance rules

Capabilities 19, 20, 21, 22, 32 are local-only (no network calls). Capability 48 uses NetworkMediator when enabled.

### 1.3 No silent online boundary crossing
When a network capability runs, Nova emits an explicit boundary entry notice before any external request is made.

### 1.4 No fallback-to-execution
Inputs that do not match explicit invocation patterns cannot trigger governed execution through skill routing or chat paths.

---

## 2) Required Execution Path (Single Choke-Point)

For all governed capabilities, the only valid execution pipeline is:

```
User input
→ GovernorMediator.parse_governed_invocation(session_id, text)
→ returns Invocation OR ClarificationRequired OR None
→ Governor.handle_governed_invocation(capability_id, params)
→ ExecuteBoundary.allow_execution()
→ CapabilityRegistry.get(cap_id) + enabled check
→ SingleActionQueue.try_begin(cap_id)
→ LedgerWriter.log_event("ACTION_ATTEMPTED")
→ ActionRequest created (frozen=True, params=MappingProxyType)
→ Governor._execute(req) → routes to executor
→ ActionResult returned to UI
```

---

## 3) Executor Routing Table (All 9 Branches)

`Governor._execute()` in `governor.py` is the **only place** executors are instantiated. All imports are **lazy** (inside the method body), not top-level.

| `capability_id` | Import | Class/Function | Notes |
|---:|---|---|---|
| 16 | `from src.executors.web_search_executor import WebSearchExecutor` | `WebSearchExecutor(self.network, self._execute_boundary)` | Network via NetworkMediator |
| 17 | `from src.executors.webpage_launch_executor import WebpageLaunchExecutor` | `WebpageLaunchExecutor(self.ledger)` | Preset browser launch, no direct network |
| 18 | `from src.executors.tts_executor import execute_tts` | `execute_tts(req, ActionResult)` | Local pyttsx3 TTS |
| 19 | `from src.executors.volume_executor import VolumeExecutor` | `VolumeExecutor().execute(req)` | Local OS volume control |
| 20 | `from src.executors.media_executor import MediaExecutor` | `MediaExecutor().execute(req)` | Local OS media control |
| 21 | `from src.executors.brightness_executor import BrightnessExecutor` | `BrightnessExecutor().execute(req)` | Local OS brightness control |
| 22 | `from src.executors.open_folder_executor import OpenFolderExecutor` | `OpenFolderExecutor().execute(req)` | Local folder open (disabled in registry) |
| 32 | `from src.executors.os_diagnostics_executor import OSDiagnosticsExecutor` | `OSDiagnosticsExecutor().execute(req)` | Local read-only OS diagnostics |
| 48 | `from src.executors.multi_source_reporting_executor import MultiSourceReportingExecutor` | `MultiSourceReportingExecutor(self.network).execute(req)` | Network via NetworkMediator (disabled in registry) |

**Key invariants:**
- ALL executor imports are inside `Governor._execute()` — **no top-level imports** of executors anywhere.
- No other file in the codebase constructs `ActionRequest` objects.
- No other file calls executor `.execute()` methods.
- `SingleActionQueue` prevents concurrent execution.

---

## 4) Anti-Bypass Invariants (Tier-1 Enforcement)

### 4.1 Explicit Literal Invocation Only
- Governed execution triggers only on deterministic invocation patterns.
- No ranking, fuzzy matching, semantic inference, or "helpful" auto-execution.

### 4.2 ExecuteBoundary Is the Hard Gate
- If ExecuteBoundary denies, no governed capability may execute.

### 4.3 CapabilityRegistry Required
- Capability must exist in the registry AND be enabled.
- If registry entry missing/disabled → refusal.

### 4.4 SingleActionQueue Prevents Concurrency
- Concurrent execution attempts for the same capability are refused.

### 4.5 NetworkMediator Is the Only Network Gate
- No direct `requests`, `httpx`, `urllib`, `aiohttp` usage outside NetworkMediator.
- Mediator enforces SSRF protections and governance rules.
- Local-only executors (19, 20, 21, 22, 32) make no network calls.

### 4.6 Ledger Allowlist Enforcement
- `LedgerWriter.log_event()` rejects any event type not in `EVENT_TYPES` (defined in `src/ledger/event_types.py`).
- Unknown event types raise `LedgerWriteFailed`, blocking execution via fail-closed gate.
- **Previously listed as a gap — now RESOLVED.**

---

## 5) No Execution via Skill Routing

### 5.1 Skill registry cannot trigger governed execution
- Phase-3 skills (weather/news/system/chat) must never call executors directly.
- Governed execution is accessible only via Governor invocation path.

---

## 6) Ledger Evidence Requirements

For every governed execution attempt, the ledger must contain events that prove the path.

Minimum events for successful execution:
1. `ACTION_ATTEMPTED` (before ActionRequest creation — blocks if fails)
2. `ACTION_COMPLETED` (after executor returns — best-effort)

Additional events for capability 16:
- `SEARCH_QUERY` (non-blocking)
- `EXTERNAL_NETWORK_CALL` (from NetworkMediator)

Additional events for capability 17:
- `WEBPAGE_LAUNCH` (from executor, both success and failure)

---

## 7) Bypass Vectors Considered + Mitigations

### 7.1 Direct executor import and call
**Vector:** A module imports an executor and calls it directly.  
**Mitigation:** All executor imports are lazy, inside `Governor._execute()` only. CI import audit flags executor usage outside `governor.py`.

### 7.2 Hidden online access from conversation layer
**Vector:** `DeepSeekBridge` makes external HTTP calls.  
**Mitigation:** `DeepSeekBridge` uses local Ollama only — no NetworkMediator, no external API. No `requests`/`httpx` imports in conversation layer.

### 7.3 Invocation ambiguity causing fallback execution
**Vector:** partial command text triggers execution without confirmation.  
**Mitigation:** deterministic invocation parsing; one-strike clarification; no fallback-to-execution.

### 7.4 UI-triggered auto-fetch
**Vector:** frontend loads and triggers action without user input.  
**Mitigation:** no auto-fetch allowed; governed invocations require explicit user action.

### 7.5 Domain/SSRF abuse
**Vector:** network call hits internal IPs or file URLs.  
**Mitigation:** NetworkMediator blocks non-http(s), blocks private/loopback, validates host, performs DNS rebinding check via `socket.getaddrinfo`.

### 7.6 Unconstrained ledger event types
**Vector:** caller passes arbitrary event type string to ledger.  
**Mitigation:** `LedgerWriter.log_event()` enforces allowlist from `EVENT_TYPES` frozenset. Previously a gap — now resolved.

---

## 8) CI Enforcement Requirements

### 8.1 Import audit
Fail if any of these appear outside NetworkMediator module:
- `requests`
- `httpx`
- `aiohttp`
- `urllib`

### 8.2 No execution backdoors
Fail if any executor can be called without passing through Governor (static rule or test harness).

---

## 9) Conclusion

The Governor is the **unique, unconditional authority** for all governed execution across all 9 executor branches. No bypass path exists. All executors are lazy-imported exclusively inside `Governor._execute()`. No other file constructs `ActionRequest` objects or calls executor `.execute()` methods. Ledger allowlist enforcement is active. SingleActionQueue prevents concurrent execution. No direct network imports exist outside NetworkMediator.

