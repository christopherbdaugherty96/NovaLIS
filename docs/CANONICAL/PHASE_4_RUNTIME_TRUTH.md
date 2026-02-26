# PHASE-4 RUNTIME TRUTH SNAPSHOT

**Last updated:** 2026-02-26  
**This document is the single, authoritative record of the current governed runtime state for NovaLIS.**

---

## ✅ ACTIVE — RUNTIME LIVE

**Execution Scope:** Limited strictly to explicitly enabled capabilities listed below.

- **Governor spine:** ACTIVE
- **ExecuteBoundary:** ACTIVE (fail-closed; deterministic)
- **NetworkMediator:** ACTIVE (all outbound HTTP mediated)
- **Ledger:** ACTIVE (all governed actions logged pre- and post-execution)
- **STT (Speech-to-Text):** ACTIVE (local, offline-first pipeline)

### Live Governed Capabilities

| ID | Name | Status | Risk Level | Data Exfiltration |
|----|------|--------|------------|-------------------|
| 16 | `governed_web_search` | enabled | low | true |
| 17 | `open_website` | enabled | low | false |
| 18 | `speak_text` | enabled | low | false |

All other capability IDs (19–22, 32, 48) are **disabled** and cannot be invoked at runtime.

---

## 🧠 Conversation & Cognitive Modules

Modules under `src/conversation/` (heuristics, escalation, thought store, future Deep Thought bridge) are:

- **Non-authorizing** – they cannot construct `ActionRequest` or invoke capabilities directly.
- **Advisory only** – their output is treated as user‑facing text or internal hints, never as execution authority.
- **Execution‑isolated** – they operate strictly in the read‑only phase of the request lifecycle.

---

## 🔒 Runtime Invariants

- Single authority spine: all actions execute only through `Governor.handle_governed_invocation()`.
- No autonomous or background execution loops.
- No persistent cognition memory across sessions (beyond ephemeral thought store).
- ExecuteBoundary and SingleActionQueue remain active for all governed calls.
- Ledger failure → execution denial (fail‑closed).

---

## ❌ EXPLICITLY NOT PRESENT

- No autonomous actions
- No background cognition
- No proactive inference
- No persistent memory or cross-session identity state
- No Phase-5+ capabilities
- No non‑governor execution surface

---

*All governance verification and phase compliance checks must begin by referencing this file.*