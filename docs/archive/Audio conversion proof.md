Audio conversion proof

```
[STT] Audio conversion successful
...
[STT] Vosk model loaded successfully
[STT] Transcription completed: 'hello' (5 chars)
```

STT is now:

* ✅ Receiving audio bytes
* ✅ Resolving correct ffmpeg path
* ✅ Converting WebM → WAV
* ✅ Loading Vosk model
* ✅ Producing transcript
* ✅ Returning text to UI
* ✅ Remaining fail-closed on error
* ✅ Remaining offline-only
* ✅ Not touching Governor authority surface

---

# 🔒 SAVE & LOCK — STT Windows Subprocess Stabilization

## Document ID

`NOVA-PHASE4-STT-WINDOWS-STABILIZATION-v1.0`

## Status

LOCKED — Runtime Stable

## Change Summary

Replaced async `create_subprocess_exec` usage with:

* `subprocess.run(...)`
* Wrapped inside `asyncio.to_thread(...)`

### Rationale

On Windows:

* `asyncio.create_subprocess_exec` requires ProactorEventLoop
* Uvicorn reload spawns processes that revert to SelectorEventLoop
* This causes `NotImplementedError` during subprocess creation

Switching to:

```python
result = await asyncio.to_thread(subprocess.run, ...)
```

removes:

* Event loop dependency
* Uvicorn loop configuration sensitivity
* Windows async incompatibility
* Subprocess transport instability

---

## Authority Impact

None.

| Layer              | Status    |
| ------------------ | --------- |
| Governor           | Unchanged |
| Execution Boundary | Unchanged |
| Capability Surface | Unchanged |
| Network Authority  | Unchanged |
| Ledger             | Unchanged |

STT remains:

* Input-only
* Non-executing
* Local-only
* Phase-4 safe

---

## Stability Impact

Improved.

Removes entire class of:

* Windows async loop failures
* Uvicorn reload loop conflicts
* Proactor policy dependencies
* Subprocess transport errors

This is architecturally cleaner for your environment.

---

## System State After Lock

| Component             | Status        |
| --------------------- | ------------- |
| STT Pipeline          | Stable        |
| ffmpeg Resolution     | Deterministic |
| WAV Conversion        | Working       |
| Vosk Model            | Working       |
| Transcription         | Verified      |
| Windows Compatibility | Stable        |

---
successfully: 

1. Identified failure layer
2. Verified path correctness
3. Captured exception type
4. Identified OS loop limitation
5. Removed architectural fragility
6. Confirmed functional transcription

That is disciplined engineering.

---


