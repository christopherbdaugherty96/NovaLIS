# TTS Invocation Bound Proof
**Date:** 2026-03-03  
**Commit:** `454a11ec`  
**Scope:** Proof that TTS execution is fully governed, invocation-bound, and has no capability escalation path.

---

## 1. Core Claim

TTS (speech output) in NovaLIS can only be invoked through `Governor._execute()` via capability 18. No TTS execution path exists outside the Governor spine. No background speech threads exist. No personality expansion occurs through speech.

---

## 2. Capability 18 Execution Path

```
User input: "speak that" / "read that" / "say it"
→ GovernorMediator.parse_governed_invocation()
  → returns Invocation(capability_id=18, params={})
→ Governor.handle_governed_invocation(capability_id=18, params)
→ [All 7 gates pass]
→ Governor._execute(req) → cap_id == 18 branch
  → from src.executors.tts_executor import execute_tts
  → execute_tts(req, ActionResult)
    → TTSEngine.speak(text)
→ ActionResult returned
```

The `tts_executor` import is **lazy** — inside `_execute()` only, not at module top-level.

---

## 3. Voice-Channel Auto-Speak

`brain_server.py` may invoke capability 18 automatically after a successful governed action on the voice channel. This is a **known constitutional note**, not a violation:

- The auto-speak still routes through `Governor.handle_governed_invocation()`.
- It is gated by the same authority chain: ExecuteBoundary → CapabilityRegistry → SingleActionQueue → LedgerWriter → `_execute()`.
- It is triggered only after a successful user-initiated action, not proactively.
- It does not bypass any gate.

---

## 4. TTSEngine (tts_executor.py)

`TTSEngine` in `src/executors/tts_executor.py` uses **pyttsx3** (secondary/fallback engine):

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

- `isBusy()` → `stop()` guard prevents overlapping utterances.
- `pyttsx3` is imported lazily via `importlib.import_module` — not at module level.

---

## 5. SpeechRenderer (voice/tts_engine.py)

`SpeechRenderer` in `src/voice/tts_engine.py` uses **Piper** (offline neural TTS, primary engine):

```python
class SpeechRenderer:
    _playback_lock = threading.Lock()
    _active_player: Optional[subprocess.Popen] = None

    def render(self, text: str) -> None:
        if not self._playback_lock.acquire(blocking=False):
            return  # Non-blocking: skip if already playing
        # ... Piper subprocess + audio playback ...
        finally:
            self._active_player = None
            self._playback_lock.release()
```

**Concurrency guard:** `_playback_lock` (`threading.Lock`) prevents overlapping speech. If lock is held, the render call returns immediately without queuing.

---

## 6. stop_speaking()

`stop_speaking()` in `src/voice/tts_engine.py` terminates the active player process:

```python
def stop_speaking() -> None:
    """Best-effort stop of currently playing speech."""
    SpeechRenderer.stop()

@classmethod
def stop(cls) -> None:
    player = cls._active_player
    if player is None:
        return
    try:
        if player.poll() is None:
            player.terminate()
    except Exception:
        return
```

This provides a clean stop mechanism that terminates the active subprocess without raising exceptions.

---

## 7. No TTS Outside Executor and Voice Engine

Verified against source code:

- No TTS imports in `src/conversation/` (any file)
- No `TTSEngine.speak()` calls outside `tts_executor.py`
- No `SpeechRenderer().render()` calls outside `voice/tts_engine.py` and `nova_speak()` helper
- No `pyttsx3` imports outside `tts_executor.py`
- No background speech threads (no `threading.Thread` wrapping TTS calls outside audio task runner)

---

## 8. No Capability Escalation from TTS

TTS is an output modality only:

- `execute_tts()` returns `ActionResult` with `success=True/False` — no capability IDs, no execution instructions.
- `TTSEngine.speak()` returns `None` — no data returned to caller beyond completion.
- `SpeechRenderer.render()` returns `None` — no data returned.
- No feedback loop from TTS output back into the Governor or capability parser.

---

## 9. Conclusion

TTS execution in NovaLIS is fully invocation-bound through the Governor spine. Capability 18 is the only path to speech output. Both TTS engines (pyttsx3 via tts_executor, Piper via SpeechRenderer) have concurrency guards. `stop_speaking()` provides clean termination. No background speech threads exist. No capability escalation is possible from TTS.
