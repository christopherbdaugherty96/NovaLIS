# Capability 18 — Governed TTS Authority Proof
**Date:** 2026-03-02
**Commit:** `6574a355f2db7fb00d7e0fb9451f60f9f16eac21`
**Scope:** Complete proof for the governed text-to-speech capability.

---

## 1. Execution Path

```
User: "speak that"
  → GovernorMediator.parse_governed_invocation() → Invocation(18, {})
  → Governor.handle_governed_invocation(18, {})
    → [5 gates pass — same sequence as cap 16/17]
    → ActionRequest(capability_id=18, params={})
    → Governor._execute(req)
      → execute_tts(req, ActionResult)
        → SpeechFormatter().format_for_tts(text)
        → TTSEngine.speak(speak_text)
      → ActionResult(success=True, message="")
      → Ledger.log_event("ACTION_COMPLETED", ...)
```

---

## 2. Executor Implementation

**File:** `nova_backend/src/executors/tts_executor.py`

### TTSEngine:

```python
class TTSEngine:
    _engine = None

    @classmethod
    def speak(cls, text: str) -> None:
        if cls._engine is None:
            pyttsx3 = importlib.import_module("pyttsx3")
            cls._engine = pyttsx3.init()
        if cls._engine.isBusy():
            cls._engine.stop()
        cls._engine.say(text)
        cls._engine.runAndWait()
```

- **Lazy-loaded** via `importlib.import_module("pyttsx3")` — no import at module level
- **Concurrency guard** — stops active speech before starting new output
- **Offline** — `pyttsx3` uses OS-native speech synthesis, no network calls

### execute_tts:

| Input | Result |
|---|---|
| Empty/whitespace text | `ActionResult.failure("I don't have anything to speak.")` |
| Empty after formatting | `ActionResult.failure("I don't have anything to speak.")` |
| Valid text | `TTSEngine.speak(speak_text)` → `ActionResult(success=True, message="")` |
| Exception in speak | `ActionResult.failure("Speech failed.")` |

---

## 3. Non-Autonomy Guarantee

TTS triggers **only** when:
- Capability 18 is explicitly invoked via `"speak that"`, `"read that"`, `"say it"`
- Or auto-triggered after a successful governed action on voice channel (brain_server rendering path, which uses `nova_speak()` — a separate, non-governed rendering path)

TTS does **NOT**:
- Trigger in background
- Trigger on idle state
- Trigger from escalation reasoning
- Trigger from thought storage
- Trigger from internal planning

---

## 4. Import Discipline

- `TTSEngine.speak()` is called **only** in `tts_executor.py`
- `brain_server.py` does **not** contain `handle_governed_invocation(18`, `execute_tts(`, or `TTSEngine.speak(`
- Governor routing is confirmed: `elif req.capability_id == 18` exists in `governor.py`

---

## 5. Message Integrity

`execute_tts` returns `message=""` on success. This prevents:
- Overwriting `last_response` state with TTS confirmation text
- Replay corruption in the conversation layer

---

## 6. Test Verification

| Test | File | What It Proves |
|---|---|---|
| `test_execute_tts_fails_on_empty_text` | `tests/executors/test_tts_executor.py` | Empty text → `success=False` |
| `test_execute_tts_success_with_mocked_engine` | `tests/executors/test_tts_executor.py` | Valid text → `success=True`, engine called |
| `test_parse_speak_that_invocation` | `tests/test_governor_mediator_tts.py` | `"speak that"` → `Invocation(18, {})` |
| `test_tts_engine_speak_only_called_in_tts_executor` | `tests/adversarial/test_tts_spine_integrity.py` | No `TTSEngine.speak(` outside executor |
| `test_brain_server_does_not_invoke_capability_18_directly` | `tests/adversarial/test_tts_spine_integrity.py` | Brain server sealed from TTS authority |
| `test_governor_routes_capability_18_to_tts_executor` | `tests/adversarial/test_tts_spine_integrity.py` | Governor has `elif req.capability_id == 18` |
| `test_brain_server_does_not_auto_invoke_capability_18` | `tests/governance/test_tts_invocation_bound.py` | No auto-invocation in brain_server |
| `test_no_tts_execution_outside_governor_surface` | `tests/governance/test_tts_invocation_bound.py` | TTS authority sealed to governor |

---

## 7. Conclusion

Capability 18 is fully governed: registry-enabled, mediator-parsed, Governor-gated, ledger-tracked, offline, concurrency-guarded, non-autonomous, and verified by 8 dedicated tests covering unit, parser, adversarial, and governance layers.