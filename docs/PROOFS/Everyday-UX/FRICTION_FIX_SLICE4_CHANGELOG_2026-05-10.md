# Everyday UX Friction — Fix Slice 4 Changelog

Branch: `fix/everyday-ux-friction-slice-1`  
Date: 2026-05-10

---

## What changed and why

### 1. Brightness patterns expanded (`governor_mediator.py`)

**Before:**
- Up: `brightness up`, `turn the brightness up`, `make the screen brighter`
- Down: `brightness down`, `turn the brightness down`, `make the screen dimmer`
- Nominal forms: `increase brightness`, `dim brightness`

**After (up):** Added `make screen brighter`, `screen brighter`, `brighter`.  
**After (down):** Added `screen brightness down`, `dim the screen`, `screen dimmer`,
`screen brightness down`.  
Also extended `increase/raise` and `decrease/lower/dim` forms to accept `screen brightness`
as well as bare `brightness`.

Why: "dim the screen" and "make screen brighter" are the most natural spoken phrases.
The existing patterns required "the screen" with "the" and didn't cover the bare `screen`
or `dim the screen` forms.

---

### 2. Memory recall — "about me" / "recall / show me" forms (`governor_mediator.py`)

**Before:** `MEMORY_RECALL_FRIENDLY_RE` covered only:
- "what do you remember"
- "show what you remember"
- "what's in my memory"

**After:** Expanded to also match:
- "what do you remember about me"
- "show me what you know about me"
- "show me what you remember about me"
- "recall my notes" / "recall my memories" / "recall memory"
- "show me my notes" / "show me my memories"
- "what have you saved" / "what have you stored"

**Routed to:** Cap 61 (memory), `action: list`.

Why: "what do you remember about me" is the most natural way to ask what Nova has stored.
All these forms were falling through to the LLM.

---

### 3. Story tracker — "track the X story" form (`governor_mediator.py`)

**Before:** `TRACK_STORY_RE` matched only `"track story X"` (topic before "story").  
**After:** Extended to also match `"track the X story"` (topic sandwiched: `track [the] <topic> story`).
Match extraction updated to use `topic1 or topic2` from two named groups.

Why: "track the ai regulation story" is the natural English word order. The existing pattern
required "track story ai regulation" which is grammatically inverted.

---

### 4. `SYSTEM_RE` — disk space / storage variants (`governor_mediator.py`)

**Added:** `check disk space`, `how much storage`, `disk space`, `storage space`,
`free space`, `storage usage` to the `SYSTEM_RE` alternation group.

**Routed to:** Cap 32 (system_check).

Why: Disk/storage questions are a natural subset of system status. "check disk space" and
"how much storage" are common desktop queries. They fell through to the LLM without
returning useful system data.

---

## Routing verification (all 24 phrases correct after slice 4)

| Phrase | Capability |
|---|---|
| dim the screen | Cap 21 |
| screen brightness down | Cap 21 |
| make screen brighter | Cap 21 |
| brighter | Cap 21 |
| screen brighter | Cap 21 |
| what do you remember about me | Cap 61 |
| show me what you know about me | Cap 61 |
| recall my notes | Cap 61 |
| what have you saved | Cap 61 |
| track the ai regulation story | Cap 52 |
| track the ukraine war story | Cap 52 |
| check disk space | Cap 32 |
| how much storage | Cap 32 |
| disk space | Cap 32 |
| free space | Cap 32 |
| increase brightness | Cap 21 ✓ regression |
| dim brightness | Cap 21 ✓ regression |
| track story ai regulation | Cap 52 ✓ regression |
| follow the ukraine war updates | Cap 52 ✓ regression |
| what do you remember | Cap 61 ✓ regression |
| louder | Cap 19 ✓ regression |
| is nova running | Cap 32 ✓ regression |
| go to downloads | Cap 22 ✓ regression |

---

## What this slice does NOT change

- No capability permissions, boundary changes, or new capability registrations.
- No changes to Cap 64 (email) executor logic.
- No OpenClaw expansion, no external writes, no new capabilities.
