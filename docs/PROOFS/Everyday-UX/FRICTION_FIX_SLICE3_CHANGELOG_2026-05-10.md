# Everyday UX Friction — Fix Slice 3 Changelog

Branch: `fix/everyday-ux-friction-slice-1`  
Date: 2026-05-10

---

## What changed and why

### 1. Standalone "nova" prefix stripping (`governor_mediator.py`)

**Before:** `_normalize_spoken_request()` stripped "hey nova" and "ok nova" prefixes but left
a bare "nova" at the start of a phrase untouched.  
**After:** Added `re.sub(r"^\s*nova\b[\s,.\-!?:;]*", "", ...)` after the existing prefix strip.

Why: "nova show me the news" is a natural spoken form — the user says their device name first.
Without this, "nova show me the news" didn't normalize to "show me the news" and fell through
to the LLM instead of routing to Cap 56.

---

### 2. `WEATHER_RE` — "check weather" / rain variants (`governor_mediator.py`)

**Before:** Pattern covered `weather`, `whats the weather`, `hows the weather` but not `check
weather`, `check the weather`, or the rain-intent phrasing added in slice 2.  
**After:** Added `check (?:the )?weather|check weather` at the head of the alternation group.

Why: "ok nova check weather" correctly normalized to "check weather" after slice 2 prefix
removal, but WEATHER_RE didn't match it so it fell through.

---

### 3. `SYSTEM_RE` — "is nova running" / "status check" variants (`governor_mediator.py`)

**Before:** Covered "how am I doing", "device status" etc. but not "is nova running",
"everything ok", or "status check".  
**After:** Added `is nova running`, `is everything (?:ok|okay|working|fine)`, `everything ok`,
`status check` to the alternation group.

Why: Common status phrases used verbally weren't routing to Cap 32 (system_check).

---

### 4. Volume inline patterns expanded (`governor_mediator.py`)

**Before:** Volume-up branch matched `volume up`, `turn the volume up`, `make it louder`,
`make the volume louder`. Volume-down branch matched `volume down`, `turn the volume down`,
`make it quieter`, `make the volume quieter`, `make it softer`.  
**After:**
- Volume-up regex adds: `louder`, `too quiet`, `it's too quiet`
- Volume-down regex adds: `quieter`, `lower the volume`, `lower volume`, `too loud`,
  `it's too loud`

Why: "louder" and "quieter" as bare words are the most natural spoken adjustment phrases
and were not matched. "too loud" / "too quiet" are the second most common — both fell
through to the LLM.

---

### 5. Media pause — "stop/pause the music/audio" (`governor_mediator.py`)

**Before:** Media control block matched `play`, `pause`, `resume` as single words via
`(play|pause|resume)` regex, but not "stop the music", "pause the music", "pause the song".  
**After:** Added a block immediately after the play/pause/resume match:
```python
if re.match(r"^\s*(?:stop|pause)\s+(?:the\s+)?(?:music|song|playback|audio)\s*$", t, ...):
    return _invocation_if_enabled(20, {"action": "pause"})
```

Why: "stop the music" and "pause the music" are natural speech forms that bypass the bare
`pause` match. Now routed to Cap 20.

---

### 6. `MEMORY_SAVE_LATER_RE` — "save this for later / write this down" (`governor_mediator.py`)

**Added:** New pattern:
```
r"^\s*(?:save\s+(?:this|that)\s+for\s+later|write\s+(?:this|that)\s+down|log\s+(?:this|that))\s*[:\-]\s*(?P<body>.+?)\s*$"
```
**Routed to:** Cap 61 (memory), `action: save`.

Why: "save this for later: pick up groceries" and "write this down: dentist May 20" are
common desktop assistant phrases. They weren't handled by any existing memory pattern.

---

### 7. `GO_TO_FOLDER_RE` — "go to downloads / documents" (`governor_mediator.py`)

**Added:** New pattern:
```
r"^\s*go\s+to\s+(?:my\s+)?(?P<folder>documents|downloads|desktop|pictures)(?:\s+folder)?\s*$"
```
**Routed to:** Cap 22 (folder open), combined into the four-pattern folder match chain.

Why: "go to downloads" is a direct, natural phrase. The existing patterns (`open downloads`,
`show me my downloads`, `navigate to downloads`) didn't cover the "go to" form.

---

### 8. P3 integration test budget bypass (`conftest.py`)

**Added:** `nova_backend/tests/certification/cap_16_governed_web_search/conftest.py`

An `autouse` fixture that patches `provider_usage_store.snapshot()` to return a "normal"
budget state during all Cap 16 certification tests.

Why: P3 integration tests exercise the full Governor spine including the budget gate.
The budget gate reads live runtime state from disk. During a long development session the
12,000-token daily budget exhausts, causing 8 P3 tests to fail with `budget_state: limit`
even though the routing and execution code is correct. The conftest makes the tests
deterministic regardless of session token usage. Budget enforcement itself is tested in
the Governor unit tests, not here.

---

## Routing verification (all 16 phrases correct after slice 3)

| Phrase | Capability |
|---|---|
| louder | Cap 19 |
| too loud | Cap 19 |
| quieter | Cap 19 |
| stop music | Cap 20 |
| pause the music | Cap 20 |
| save this for later: dentist may 20 | Cap 61 |
| write this down: pick up groceries | Cap 61 |
| nova show me the news | Cap 56 |
| ok nova check weather | Cap 55 |
| is nova running | Cap 32 |
| go to downloads | Cap 22 |
| go to youtube | Cap 17 |
| go to documents folder | Cap 22 |
| note: check car insurance | Cap 61 |
| i need to remember that my dentist is may 20 | Cap 61 |
| show me my documents | Cap 22 |

---

## What this slice does NOT change

- No capability permissions, boundary changes, or new capability registrations.
- No changes to Cap 64 (email) executor logic.
- No OpenClaw expansion, no external writes, no new capabilities.
- No response-shift contamination fix (chained WS sessions) — still deferred.
