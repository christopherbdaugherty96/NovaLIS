# 

## Nova Phase-4 — Governor Bypass Proof (Capability 16 Scope)

**Document ID:** `NOVA-GOV-BYPASS-PROOF-v1.0`  
**Status:** DRAFT — Pending Mechanical Verification  
**Scope:** Phase-4 staging (Option B), **Capability 16 only** (Governed Web Search)  
**Non-Authorizing:** This document does not grant authority. It records proof obligations and verification results.  
**Core Claim:** *No governed execution can occur without explicit, deterministic invocation through the Governor, and no outbound network can occur outside NetworkMediator.*

---

## 0) Definitions

- **Governor:** The sole authority gate for governed capabilities.
- **Governed capability:** Any action requiring elevated authority beyond read-only Phase-3 skills. In this proof, only **Capability 16** is considered.
- **Bypass:** Any execution or external network call that occurs without passing through required gates (invocation parsing → Governor → ExecuteBoundary → CapabilityRegistry → Executor → NetworkMediator), or any “silent online” behavior.
- **Phase-4 staging (Option B):** `GOVERNED_ACTIONS_ENABLED = True` is permitted, but capability scope is limited and must be proven safe.

---

## 1) The Claim (What This Proof Guarantees)

### 1.1 Execution cannot occur without explicit invocation
A governed action (Capability 16) will not run unless the user issues an explicit invocation that matches the deterministic invocation grammar.

### 1.2 No network can occur outside NetworkMediator
All outbound HTTP(S) requests are routed through `NetworkMediator` and are blocked if:
- capability is disabled
- domain/scheme is invalid
- destination is private/loopback
- rate limits are exceeded
- mediator refuses due to governance rules

### 1.3 No silent online boundary crossing
When Capability 16 runs, Nova emits an explicit boundary entry notice **before** any external request is made.

### 1.4 No fallback-to-execution
Inputs that do not match explicit invocation patterns cannot trigger governed execution through skill routing or chat paths.

---

## 2) Required Execution Path (Single Choke-Point)

For Capability 16, the only valid execution pipeline is:

User input
→ GovernorMediator.parse_governed_invocation(session_id, text)
→ returns Invocation OR ClarificationRequired OR None
→ Governor.handle_governed_invocation(capability_id=16, params)
→ ExecuteBoundary.allow_execution()
→ CapabilityRegistry.get(16) + enabled check
→ SingleActionQueue.try_begin(16)
→ WebSearchExecutor.execute(...)
→ NetworkMediator.request(capability_id=16, ...)
→ ActionResult returned to UI


### Proof obligation:
If execution occurs, it must be observable that this path was followed (ledger + code structure + tests).

---

## 3) Anti-Bypass Invariants (Tier-1 Enforcement)

### 3.1 Explicit Literal Invocation Only
- Governed execution triggers only on deterministic invocation patterns (e.g., `search for <query>`).
- No ranking, fuzzy matching, semantic inference, or “helpful” auto-execution.

**Verification method:** unit tests + manual adversarial inputs (Section 8).

### 3.2 ExecuteBoundary Is the Hard Gate
- If ExecuteBoundary denies, no governed capability may execute, regardless of invocation correctness.

**Verification method:** force boundary deny and confirm refusal for Capability 16.

### 3.3 CapabilityRegistry Required
- Capability must exist in the registry AND be enabled.
- If registry entry missing/disabled → refusal.

**Verification method:** disable capability 16 and confirm refusal.

### 3.4 SingleActionQueue Prevents Concurrency
- Concurrent execution attempts for the same capability are refused.

**Verification method:** rapid double invocation and confirm single execution.

### 3.5 NetworkMediator Is the Only Network Gate
- No direct `requests`, `httpx`, `urllib`, `aiohttp` usage outside mediator.
- Mediator enforces SSRF protections and governance rules.

**Verification method:** CI import audit + grep + tests.

---

## 4) Boundary Disclosure Guarantee (No Silent Online)

### 4.1 Required behavior
When a governed web search begins, Nova must emit:

> **“I’m checking online.”** *(or configured exact phrase)*

**before** the external request is made.

### 4.2 Evidence
- `brain_server` sends `boundary_notice` immediately upon receiving ActionResult with `boundary_notice`.
- `WebSearchExecutor` returns an ActionResult containing `boundary_notice` **prior** to network call.

**Verification method:** log timing and confirm notice is sent before mediator call.

---

## 5) No Execution via Skill Routing

### 5.1 Skill registry cannot trigger governed execution
- Phase-3 skills (weather/news/system/chat) must never call executors directly.
- Governed execution is accessible only via Governor invocation path.

**Verification method:** static analysis + test that skill routing cannot reach executor calls.

---

## 6) Ledger Evidence Requirements

For every governed execution attempt, the ledger must contain events that prove the path:

Minimum events for successful Capability 16 execution:

1. `GOVERNED_INVOCATION_RECEIVED` (or equivalent)
2. `EXECUTION_ALLOWED` (boundary passed)
3. `CAPABILITY_ALLOWED` (registry enabled)
4. `EXTERNAL_NETWORK_CALL` (mediator call)
5. `ACTION_COMPLETED` (final result)

Minimum events for refusal:

- `EXECUTION_DENIED` OR `CAPABILITY_DISABLED` OR `NETWORK_CALL_FAILED`

**Verification method:** run test suite and inspect ledger outputs.

---

## 7) Bypass Vectors Considered + Mitigations

### 7.1 Direct executor import and call
**Vector:** A skill imports `WebSearchExecutor` and calls it directly.  
**Mitigation:** executor not used by skills; CI import audit flags network libs; code review policy.

### 7.2 Hidden online access from Phase-3 skills
**Vector:** weather/news fetch using direct HTTP client.  
**Mitigation:** weather/news routed through NetworkMediator + CI audit.

### 7.3 Invocation ambiguity causing fallback execution
**Vector:** partial “search” text triggers execution without confirmation.  
**Mitigation:** deterministic invocation parsing; one-strike clarification; no fallback-to-execution.

### 7.4 UI-triggered auto-fetch
**Vector:** frontend loads and triggers search without user input.  
**Mitigation:** no auto-fetch allowed; governed invocations require explicit user action.

### 7.5 Domain/SSRF abuse
**Vector:** search hits internal IPs or file URLs.  
**Mitigation:** NetworkMediator blocks non-http(s), blocks private/loopback, validates host.

---

## 8) Adversarial Verification Checklist (Must Pass)

### 8.1 Invocation edge cases
- [ ] `search` → no execution; either no-op or one-strike clarification (per design)
- [ ] `search for` → one-strike clarification, no execution
- [ ] `search for   ` → one-strike clarification, no execution
- [ ] `search for cats` → boundary notice then results
- [ ] `Search for cats` → case-insensitive match works (if allowed)
- [ ] `look up cats` → refusal unless explicitly added to grammar

### 8.2 Capability gating
- [ ] Disable capability 16 in registry → refusal
- [ ] Remove capability 16 entry → refusal
- [ ] Boundary deny (`allow_execution=False`) → refusal

### 8.3 Network governance
- [ ] Attempt URL with `file://` → blocked
- [ ] Attempt URL to `127.0.0.1` or `192.168.x.x` → blocked
- [ ] Rate limit exceeded → blocked and logged

### 8.4 Concurrency
- [ ] Two rapid `search for ...` → only one executes, the other refused

### 8.5 No silent boundary
- [ ] Confirm boundary notice sent before network call

---

## 9) CI Enforcement Requirements

The following CI rules must exist and pass:

### 9.1 Import audit
Fail if any of these appear outside NetworkMediator module:
- `requests`
- `httpx`
- `aiohttp`
- `urllib`

### 9.2 Registry version lock (if used)
Fail if registry version mismatches expected runtime version.

### 9.3 No execution backdoors
Fail if any executor can be called without passing through Governor (static rule or test harness).

---

## 10) Evidence Log (To Fill During Verification)

- **Commit:** `<commit hash>`
- **Tag:** `<tag name>` (e.g., `phase-4-cap16-live`)
- **Runtime command:** `python -m uvicorn src.brain_server:app`
- **Verification date:** `<YYYY-MM-DD>`
- **Verification operator:** `<name>`

### Results
- Adversarial checklist: ✅/❌
- CI import audit: ✅/❌
- Ledger events verified: ✅/❌
- Boundary notice timing: ✅/❌

---

## 11) Conclusion

If (and only if) all items in Sections 8–10 pass, then:

> **Capability 16 is mechanically governed and bypass-resistant under Phase-4 staging.**

If any item fails, Phase-4 activation is **not** complete and execution must be treated as unsafe until corrected.

---