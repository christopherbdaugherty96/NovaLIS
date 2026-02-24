Below is a **canonical “Save & Lock” document** you can place in:

```
docs/CANONICAL/Phase-4_STT_Diagnostics_Lock.md
```

This captures only **confirmed facts**, no speculation, and preserves Phase-4 discipline.

---

# NOVA — Phase-4 STT Diagnostic State Lock

**Document ID:** NOVA-PHASE4-STT-DIAG-LOCK-v1.0
**Date:** 2026-02-23
**Status:** LOCKED — Runtime Diagnostic State
**Scope:** STT pipeline (local, offline-first)
**Authority Impact:** None
**Governor Impact:** None

---

## 1. Purpose

This document records the **confirmed runtime state** of the Speech-to-Text (STT) system after Phase-4 stabilization and recent troubleshooting.

This is a **diagnostic lock**, not a feature change.
It preserves verified facts before further modifications.

---

## 2. Current STT Architecture (Confirmed)

**Execution Path**

```
Browser audio (webm)
    ↓
/stt/transcribe endpoint
    ↓
stt_engine.transcribe_bytes()
    ↓
ffmpeg conversion → WAV
    ↓
Vosk local transcription
    ↓
text returned to UI
```

**Design Principles**

| Property                           | Status               |
| ---------------------------------- | -------------------- |
| Local-first                        | ✅                    |
| Offline operation                  | ✅                    |
| No cloud dependency                | ✅                    |
| Fail-closed behavior               | ✅                    |
| Governor bypassed (read-only path) | Expected / unchanged |

---

## 3. Confirmed Runtime Facts

### 3.1 FFmpeg Availability

Verified manually:

```
nova_backend\tools\ffmpeg\ffmpeg.exe -version
```

Result: **Success**

**Conclusion**

| Check                    | Status |
| ------------------------ | ------ |
| Binary present           | ✅      |
| Executable               | ✅      |
| Permissions OK           | ✅      |
| System PATH not required | ✅      |

FFmpeg path resolution is **working**.

---

### 3.2 Directory Structure Verified

Found binaries:

```
nova_backend/tools/ffmpeg/ffmpeg.exe
nova_backend/tools/ffmpeg/ffmpeg-8.0.1-essentials_build/.../bin/ffmpeg.exe
```

Resolution base:

```
Path(__file__).resolve().parents[2]
→ nova_backend/
```

Confirmed correct.

---

## 4. Observed Failure Behavior

Runtime logs:

```
[STT] Starting transcription
[STT] Converting audio to WAV format...
[STT] Audio conversion exception:
POST /stt/transcribe 200 OK
```

### Interpretation

| Layer         | Behavior                        |
| ------------- | ------------------------------- |
| Endpoint      | Returns 200                     |
| Exception     | Occurs during ffmpeg conversion |
| Error message | Not displayed                   |
| Result text   | Empty                           |
| Dashboard     | Shows nothing                   |

---

## 5. Root Cause Classification

This is **not**:

* ❌ Path failure
* ❌ Missing binary
* ❌ Permission issue
* ❌ Governor issue
* ❌ UI issue

This **is**:

> **Exception swallowed inside STT conversion block**

The actual ffmpeg error is currently hidden.

---

## 6. Locked Diagnostic Action (Phase-4 Safe)

### Approved Change Type

**Diagnostic visibility only**

Allowed modification:

Replace:

```python
except Exception:
    print("[STT] Audio conversion exception:")
```

With:

```python
except Exception as e:
    print("[STT] Audio conversion exception:", e)
```

### Constraints

* No logic changes
* No behavior changes
* No new logging framework
* No return changes
* No API changes

**Purpose:** Reveal actual failure cause.

---

## 7. Expected Failure Category (Not Yet Confirmed)

Most likely causes (pending diagnostic output):

* Unsupported webm codec
* Missing audio channel/rate conversion
* Invalid temp file path
* ffmpeg argument mismatch

**These are hypotheses only.**
No changes authorized until actual error is observed.

---

## 8. UI Behavior — Confirmed Correct

Because STT returns `""`:

| Layer     | Result            |
| --------- | ----------------- |
| API       | 200 OK            |
| UI        | No text displayed |
| Dashboard | Empty             |

This is correct fail-closed behavior.

---

## 9. Phase-4 Integrity Status

| Area                    | Status      |
| ----------------------- | ----------- |
| Governor Spine          | ✅ Unchanged |
| Execution Boundaries    | ✅ Unchanged |
| Capability Surface      | ✅ Unchanged |
| External Contracts      | ✅ Unchanged |
| Offline-first guarantee | ✅ Preserved |

No authority expansion occurred.

---

## 10. Next Authorized Step

1. Apply diagnostic print change
2. Restart Nova
3. Run STT once
4. Capture full error message
5. Create **targeted fix** based only on observed failure

No speculative fixes allowed.

---

## 11. Lock Statement

This document establishes the **current verified STT state** and freezes interpretation until the actual ffmpeg error is observed.

**Status: LOCKED**
Further changes must be based on runtime evidence.

---

## 12. System State Summary

Phase-4 Runtime Overall:

| Component          | Status                       |
| ------------------ | ---------------------------- |
| Web Search (Cap16) | Stable                       |
| WebSocket Guard    | Active                       |
| STT Architecture   | Correct                      |
| STT Conversion     | Failing (diagnostic pending) |
| UI                 | Correct                      |
| Governor           | Stable                       |

---
