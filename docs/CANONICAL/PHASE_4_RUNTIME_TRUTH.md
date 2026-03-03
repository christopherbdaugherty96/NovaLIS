# PHASE-4 RUNTIME TRUTH SNAPSHOT

**Last updated:** 2026-03-03  
**This document is the single, authoritative record of the current governed runtime state for NovaLIS.**

---

## ✅ ACTIVE — RUNTIME LIVE

**Execution Scope:** Limited strictly to explicitly enabled capabilities listed below.

- **Governor spine:** ACTIVE
- **ExecuteBoundary:** ACTIVE (fail-closed; deterministic)
- **NetworkMediator:** ACTIVE (all outbound HTTP mediated; DNS rebinding protection active)
- **Ledger:** ACTIVE (all governed actions logged pre- and post-execution; allowlist enforced)
- **STT (Speech-to-Text):** ACTIVE (local, offline-first pipeline)

### Live Governed Capabilities

| ID | Name | Status | Risk Level | Data Exfiltration | Notes |
|----|------|--------|------------|-------------------|-------|
| 16 | `governed_web_search` | enabled | low | true | Active; search via NetworkMediator |
| 17 | `open_website` | enabled | low | false | Active; preset browser launch |
| 18 | `speak_text` | enabled | low | false | Active; pyttsx3 local TTS engine present; mediator sends empty params — text must be injected by brain_server |
| 19 | `volume_up_down` | enabled | low | false | Wired (registry + mediator + governor + executor), but executor is RESPONSE STUB — returns success message without calling any OS audio API |
| 20 | `media_play_pause` | enabled | low | false | Wired (registry + mediator + governor + executor), but executor is RESPONSE STUB — returns success message without sending any keypress or OS command |
| 21 | `brightness_control` | enabled | low | false | Wired (registry + mediator + governor + executor), but executor is RESPONSE STUB — returns success message without calling any screen brightness API |
| 22 | `open_file_folder` | disabled | confirm | false | Declared; disabled |
| 32 | `os_diagnostics` | enabled | low | false | Wired; executor uses real shutil.disk_usage() for disk stats but hardcodes network_status — partial implementation |
| 48 | `multi_source_reporting` | disabled | low | true | Declared; disabled |

---

## ⚠️ Implementation Quality Notes

Not all "enabled" capabilities in the registry are equal. The following three-tier classification applies:

| Tier | Symbol | Meaning | Capabilities |
|------|--------|---------|-------------|
| **Fully Implemented** | ✅ | Pipeline wired AND executor performs a real external effect on the OS or network | 16, 17 |
| **Wired with Issues** | ⚠️ | Pipeline wired, executor has real code but with a known defect or partial implementation | 18 (empty params), 32 (partial data) |
| **Wired (Stub)** | 🔶 | Full pipeline wired and registry-enabled, but executor returns a success message without performing any real OS operation | 19, 20, 21 |
| **Disabled** | 🔒 | Registry `enabled: false`; pipeline may or may not exist | 22, 48 |

**Details:**
- **Cap 18 (speak_text):** The `pyttsx3` TTS engine is real and functional. However, `GovernorMediator` parses the trigger phrases (`speak that`, `read that`, `say it`) and emits `Invocation(capability_id=18, params={})` — an empty params dict. The executor reads `req.params.get("text", "")`, so if `brain_server.py` does not inject a `text` key into params before calling the Governor, TTS will always speak an empty string.
- **Cap 19 (volume_up_down):** `volume_executor.py` returns `ActionResult.ok(message=f"Volume {action}.")` but never calls any OS audio API (no `pycaw`, no `subprocess`, no `ctypes`). The full pipeline is wired but the executor performs no real OS operation.
- **Cap 20 (media_play_pause):** `media_executor.py` returns `ActionResult.ok(message="Playback started.")` etc. but never sends any keypress or OS command. Same stub pattern as cap 19.
- **Cap 21 (brightness_control):** `brightness_executor.py` returns `ActionResult.ok(message=f"Brightness {action}.")` but never calls any screen brightness API. Same stub pattern as caps 19 and 20.
- **Cap 32 (os_diagnostics):** `os_diagnostics_executor.py` uses `shutil.disk_usage("/")` for real disk stats (total/used/free GB), but `"network_status": "available"` is hardcoded — no actual network probe. CPU usage, RAM usage, process count, and OS version are absent.

---

## 🔒 Runtime Guards (Active)

### Execution Timeout Guard
`MAX_EXECUTION_TIME` is checked post-execution in `governor.py` (lines 183–192). If elapsed time exceeds the threshold, `EXECUTION_TIMEOUT` is logged to the ledger and `ActionResult.refusal` is returned.

### Memory Guard
`MAX_MEMORY_MB` is checked post-execution in `governor.py` (lines 194–207). If the RSS delta exceeds the threshold, `EXECUTION_MEMORY_EXCEEDED` is logged and `ActionResult.refusal` is returned.

### Ledger Allowlist Enforcement
`src/ledger/event_types.py` defines `EVENT_TYPES` as a `frozenset`. `writer.py` rejects any unknown event type with `raise LedgerWriteFailed(f"Unknown ledger event type: {event_type}")`. No unconstrained event type strings are accepted.

### DNS Rebinding Protection
`network_mediator.py` (lines 89–99) resolves hostnames via `socket.getaddrinfo` and blocks any address that is private, loopback, or link-local, raising `NetworkMediatorError`.

### Concurrency-Safe TTS
`SpeechRenderer` in `voice/tts_engine.py` uses `_playback_lock` (a `threading.Lock`) to prevent overlapping speech playback. `stop_speaking()` function terminates the active player process via `SpeechRenderer.stop()`.

---

## 🧠 Conversation & Cognitive Modules

Modules under `src/conversation/` (heuristics, escalation, thought store, Deep Thought bridge) are:

- **Non-authorizing** – they cannot construct `ActionRequest` or invoke capabilities directly.
- **Advisory only** – their output is treated as user‑facing text or internal hints, never as execution authority.
- **Execution‑isolated** – they operate strictly in the read‑only phase of the request lifecycle.
- **Local model only** – `DeepSeekBridge` uses local Ollama/phi3:mini. Full DeepSeek cloud API integration is design-only; no external network calls are made from the conversation layer.

---

## 🔒 Runtime Invariants

- Single authority spine: all actions execute only through `Governor.handle_governed_invocation()`.
- No autonomous or background execution loops.
- No persistent cognition memory across sessions (beyond ephemeral thought store).
- ExecuteBoundary and SingleActionQueue remain active for all governed calls.
- Ledger failure → execution denial (fail‑closed).
- Ledger event type allowlist enforced at write boundary.

---

## ❌ EXPLICITLY NOT PRESENT

- No autonomous actions
- No background cognition
- No proactive inference
- No persistent memory or cross-session identity state
- No Phase-5+ capabilities
- No non‑governor execution surface
- No external network calls from conversation layer

---

*All governance verification and phase compliance checks must begin by referencing this file.*