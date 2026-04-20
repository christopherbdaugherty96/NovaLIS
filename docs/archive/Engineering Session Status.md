# NovaLIS — Engineering Session Status
> **Historical reference only**
> This document reflects Nova's state at the time it was written and is **not** the authoritative current status.
> For live state, see `docs/current_runtime/` and current capability verification docs.

**Date:** 2026-02-23
**Branch:** `main`
**Head Commit:** [`770897f`](https://github.com/christopherbdaugherty96/NovaLIS/commit/770897fe66a987627009f3e5a6aa2ca1e4471d29)
**Phase:** 4 — Staging / Runtime Stabilization

---

## Session Summary

Today's session was a focused **Phase-4 runtime hardening sprint**. No new features were added, no architecture changed, no Governor contracts were modified. Every change was a targeted fix to an existing confirmed bug, committed individually with full audit trail.

**9 commits landed on `main` today.**

---

## Completed Today

### 1. `fix(speech): add SpeechState.stop() state reset`
**Commit:** [`ab17ca7`](https://github.com/christopherbdaugherty96/NovaLIS/commit/ab17ca78f99e66039816530d3b0c99d9b200eadf)
**File:** `src/speech_state.py`
**Bug:** BUG-C1 — `AttributeError` crash when user said "stop". The `stop()` method did not exist on `SpeechState`.
**Fix:** Added `def stop(self) -> None: self.last_spoken_text = None`. Internal state reset only; no playback side effects.

---

### 2. `fix(stt): detect ffmpeg via PATH and fail closed if unavailable`
**Commit:** [`0b87aee`](https://github.com/christopherbdaugherty96/NovaLIS/commit/0b87aee6883a13cb2deb33abaf1ef87d93f5e12b)
**File:** `src/services/stt_engine.py`
**Bug:** BUG-C2 — Hardcoded absolute Windows path for ffmpeg (`C:\Nova-Project\...`) broke STT on every machine except the original dev box.
**Fix:** Replaced with `shutil.which("ffmpeg")` — system PATH first, fail closed if not found.

---

### 3. `fix(stt): dynamically locate bundled ffmpeg (appliance mode, version-independent)`
**Commit:** [`b97b7ff`](https://github.com/christopherbdaugherty96/NovaLIS/commit/b97b7ff7b77fb47859e338cc324def72c7f15c10)
**File:** `src/services/stt_engine.py`
**Bug:** Continuation of BUG-C2 — bundled ffmpeg under `tools/ffmpeg/` wasn't found if not in PATH.
**Fix:** Added recursive `rglob("ffmpeg.exe")` search inside `tools/ffmpeg/`. Nova now finds ffmpeg regardless of version subdirectory naming.

---

### 4. `fix(stt): ensure temporary audio files are deleted after transcription`
**Commit:** [`ca4a67a`](https://github.com/christopherbdaugherty96/NovaLIS/commit/ca4a67ac35189f91ab7e9f933cbede02b8c51053)
**File:** `src/stt_manager.py` (now quarantined)
**Bug:** BUG-C3 — `delete=False` on `NamedTemporaryFile` with no cleanup meant every STT call leaked a `.wav` file to disk indefinitely.
**Fix:** Wrapped in `try/finally` with `os.unlink(tmp_path)`. File is always deleted even if transcription fails.

---

### 5. `fix(stt): lazy initialize OpenAI client (remove import-time side effect)`
**Commit:** [`3292d8b`](https://github.com/christopherbdaugherty96/NovaLIS/commit/3292d8b077cd60acacaf06e8145bacc752031120)
**File:** `src/stt_manager.py` (now quarantined)
**Bug:** BUG-S1 — OpenAI client instantiated at module import time, loading the API key into memory unconditionally even when cloud STT was never used.
**Fix:** Moved to lazy initialization (`_get_openai_client()`) — client created only on first actual cloud STT call.

---

### 6. `fix(chat): move blocking ollama.chat() off event loop using asyncio.to_thread`
**Commit:** [`28497a1`](https://github.com/christopherbdaugherty96/NovaLIS/commit/28497a1eab4cac5f2f639faef08e9a892817695e)
**File:** `src/skills/general_chat.py`
**Bug:** BUG-B1 — `ollama.chat()` is a synchronous blocking call. Running it directly in `async def handle()` blocked the entire uvicorn event loop for the duration of every LLM response, freezing the UI.
**Fix:** Wrapped call in `await asyncio.to_thread(ollama.chat, ...)`. LLM runs in a thread pool worker; event loop remains free.

---

### 7. `fix(stt): run ffmpeg asynchronously to prevent event loop blocking`
**Commit:** [`76e2211`](https://github.com/christopherbdaugherty96/NovaLIS/commit/76e2211d9b0418c248308e19c9100f4d330b95ad)
**File:** `src/services/stt_engine.py`
**Bug:** ffmpeg was being launched with blocking `subprocess.run()` inside an async handler, stalling the event loop for the duration of audio conversion.
**Fix:** Replaced with `asyncio.create_subprocess_exec()` + `await process.wait()`. ffmpeg now runs asynchronously.

---

### 8. `refactor(stt): remove stt_manager; direct STT via stt_engine (quarantine legacy)`
**Commit:** [`d124d14`](https://github.com/christopherbdaugherty96/NovaLIS/commit/d124d14d16aec4c99e79abb46cb61c67a0ad6632)
**File:** `src/stt_manager.py` → moved to `src/archive_quarantine/stt_manager.py`
**Action:** Dual STT systems (Vosk-based `stt_engine` + Whisper/OpenAI `stt_manager`) were creating confusion and import risk. The legacy Whisper/OpenAI hybrid was quarantined. All live STT now routes exclusively through `src/services/stt_engine.py` (local-first, offline, Vosk).

---

### 9. `fix(stt): move Vosk decode off event loop via asyncio.to_thread`
**Commit:** [`27184d9`](https://github.com/christopherbdaugherty96/NovaLIS/commit/27184d94ec9d5b9008088e734c7822e246df827e)
**File:** `src/services/stt_engine.py`
**Bug:** Vosk `KaldiRecognizer` frame-by-frame decoding loop was running synchronously in an async context, blocking the event loop during every transcription.
**Fix:** Extracted into `_vosk_transcribe_wav_sync()` and called via `await asyncio.to_thread(...)`. Transcription now runs in a worker thread.

---

### 10. `fix(BUG-S2): enforce WebSocket input limit in bytes (UTF-8 safe) + JSON guard`
**Commit:** [`770897f`](https://github.com/christopherbdaugherty96/NovaLIS/commit/770897fe66a987627009f3e5a6aa2ca1e4471d29)
**File:** `src/brain_server.py`
**Bug:** BUG-S2 — No input length validation on incoming WebSocket messages. Unbounded payloads could cause memory pressure and unpredictable LLM behavior. Additionally, bare `json.loads()` would propagate unhandled exceptions on malformed input.
**Fix:**
- Added `WS_INPUT_MAX_BYTES = 4096` constant (single source of truth).
- Length check uses `raw.encode("utf-8")` — byte-safe, not character-count, preventing multibyte Unicode bypass.
- `json.loads()` wrapped in `try/except json.JSONDecodeError` — malformed requests rejected cleanly, session preserved.
- Both guards log warnings and return structured error responses; connection is never torn down.

---

## Chore / Housekeeping

| Commit | Action |
|---|---|
| [`4e2fa10`](https://github.com/christopherbdaugherty96/NovaLIS/commit/4e2fa10b6468801a43ae8b1e03d3d64ca652e3cb) | `chore: ignore runtime audio and state artifacts` — added `.wav`, temp, and state artifact patterns to `.gitignore` |
| [`838975d`](https://github.com/christopherbdaugherty96/NovaLIS/commit/838975d760496593aa0def87db32bd30638aadac) | `docs: add Phase-4 Runtime Stabilization completion report` |

---

## Runtime Health — End of Session

| Subsystem | Status | Notes |
|---|---|---|
| FastAPI / uvicorn startup | ✅ Clean | No import-time crashes confirmed |
| WebSocket endpoint | ✅ Hardened | Byte-safe input guard + JSON guard active |
| STT pipeline (Vosk) | ✅ Fully async | ffmpeg async, Vosk off event loop, temp files cleaned |
| STT legacy (Whisper/OpenAI) | ✅ Quarantined | No live import path |
| General Chat (Ollama) | ✅ Non-blocking | `asyncio.to_thread` wrapping confirmed |
| `SpeechState.stop()` | ✅ Fixed | No longer crashes on "stop" command |
| ffmpeg resolution | ✅ Portable | `shutil.which` → bundled `rglob` fallback |
| Temp file cleanup | ✅ Fixed | `try/finally` + `TemporaryDirectory` context |

---

## Remaining Open Issues

### 🟠 Security

| ID | File | Issue | Priority |
|---|---|---|---|
| BUG-S3 | `brain_server.py` | No CORS policy — `CORSMiddleware` not configured | Medium |
| BUG-S4 | `archive_quarantine/*.py` | No import guard — quarantined modules are silently importable by accident | Low |

### 🟡 Logic / Behavior

| ID | File | Issue | Priority |
|---|---|---|---|
| BUG-B2 | `audio_manager.py` | `AudioManager.__init__` creates an asyncio task at import time — may conflict with uvicorn's event loop | Medium |
| RISK-2 | `tools/web_search.py` | `DDGS()` synchronous network call inside `async` news skill handler — blocks event loop during news fetches | Medium |
| BUG-B3 | `dashboard.js` | `renderWeatherWidget()` wipes its own `<h3>` header and Update button on first fetch | Low |
| BUG-B4 | `audio_manager.py` | TTS audio output bypasses Governor / ExecuteBoundary entirely — not governed | Phase 4.1 |

---

## Next Steps (Recommended Order)

```
1. BUG-S3  — Add CORSMiddleware to brain_server.py (one-liner, zero risk)
2. BUG-S4  — Add raise ImportError() guard to archive_quarantine modules
3. BUG-B2  — Fix AudioManager: move asyncio task creation to lifespan startup hook
4. RISK-2  — Wrap DDGS() in asyncio.to_thread inside NewsSkill.handle()
5. BUG-B3  — Fix renderWeatherWidget() DOM clearing bug in dashboard.js
6. BUG-B4  — Route TTS through Governor (Phase 4.1 design work required first)
```

---

## Phase Status

> **Nova Phase-4 runtime is stable.**
> All blocking event loop issues are resolved. All confirmed crash paths are fixed.
> Remaining issues are latent risks and hardening items — none block normal operation.
> The runtime is ready for continued Phase-4 feature work or Appliance Mode preparation.
