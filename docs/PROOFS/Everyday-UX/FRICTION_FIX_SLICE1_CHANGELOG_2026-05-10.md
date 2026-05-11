# Everyday UX Friction — Fix Slice 1 Changelog

Branch: `fix/everyday-ux-friction-slice-1`  
Date: 2026-05-10

---

## What changed and why

### 1. Filler opener removal (`conversation_router.py`)

**Before:** `MICRO_ACK` emitted "Okay. I'm on it.", "Okay. Let me think that through.", etc.  
**After:** All `MICRO_ACK` values are empty strings.

Why: Every analytical or action prompt opened with a filler phrase that added no information
and felt robotic. Users text naturally — the response should start with the answer.

---

### 2. Fallback text tightened (`response_formatter.py`)

**Before:** `friendly_fallback()` returned a longer message including "draft an email" as a
suggestion.  
**After:** Returns `"Not sure what you mean — try: "what's the news", "check the weather",
or "what can you do"."` — no email suggestion.

Why: "draft an email" was listed as a quick-action but email (Cap 64) is mailto-draft only
— no inbox, no setup path. Surfacing it in a fallback led to a follow-on failure for any
user who tried it.

---

### 3. HTML entity stripping (`response_formatter.py`, `web_search_executor.py`)

**Added:** `ResponseFormatter.strip_html_entities()` — unescape HTML entities and strip
stray unicode punctuation characters.

**Wired in:** `web_search_executor.py` now calls `strip_html_entities()` on:
- `researched_summary` before building report sections
- Source titles in `_format_visible_sources()`

Why: Brave search results return raw HTML entities (`&#8220;`, `&lsquo;`, etc.) in titles
and snippets. These were leaking into the user-visible synthesis output and into TTS.

---

### 4. Capability list rewrite (`brain_server.py`)

**Before:** "what can you do" response contained internal labels: "Local-first everyday
help is ready", "governed second-opinion pass", "local-first" references.  
**After:** Plain-English list with outcome-first framing (search, explain, memory, device
basics, story tracking, screen help).

Why: Internal nouns (governance, OpenClaw, local-first) are developer vocabulary, not user
vocabulary. The list now describes what a user can accomplish.

---

### 5. NEWS_RE, WEATHER_RE, SYSTEM_RE expanded (`governor_mediator.py`)

**News:** Added `whats (?:the )?news`, natural phrasing variants.  
**Weather:** Added `whats the weather`, `hows the weather`.  
**System:** Added `how is nova doing`, `device status`, `check my system`.

Why: Common abbreviations ("whats the news", "how's nova doing") weren't matching the
narrow keyword-only patterns and fell through to the LLM with no capability routed.

---

### 6. `second opinion: X` and `verify: X` colon syntax (`governor_mediator.py`)

**Before:** `SECOND_OPINION_RE` and `VERIFY_RE` required whitespace before the payload
text. `"second opinion: X"` failed to match because `:` is not whitespace.  
**After:** Changed `(?:\s+...)` to `(?:[\s:]+...)` to accept either whitespace or colon as separator.

Why: The natural way to type these is `"second opinion: <claim>"`. The colon variant was
silently falling through to the LLM without routing to Cap 62 / Cap 31.

---

### 7. Story tracker shorthand (`governor_mediator.py`)

**Added:** `STORY_TRACKER_SHORTHAND_RE` — matches `"story tracker: X"` and `"story tracker - X"`.  
**Routed to:** Cap 52 (story_tracker), `action: track`.

Why: "story tracker: AI regulation" is the intuitive shorthand for tracking a story, but
only "track story X" and "follow X" were caught by existing patterns.

---

### 8. Natural memory save (`governor_mediator.py`)

**Added:** `MEMORY_SAVE_NATURAL_RE` — matches `"remember that X"`.  
**Routed to:** Cap 61 (memory), `action: save`.

Why: "Remember this: X" was handled but "remember that X" was not. The "that" form is
common in natural speech: "remember that my dentist appointment is May 20".

---

### 9. Dashboard heading renames (`nova_backend/static/index.html`, `Nova-Frontend-Dashboard/index.html`)

| Before | After |
|---|---|
| OpenClaw Home Agent | Nova Agent |
| Trust Center | Activity Log |
| Governed Memory | Memory |

Why: Internal names leaked into user-facing headings. Users don't know what "OpenClaw" or
"Governed Memory" means. "Nova Agent", "Activity Log", and "Memory" are self-explanatory.

---

### 10. Test updates

- `test_router_detects_command_and_heavy_ack` — removed `assert out.micro_ack` (intentionally
  emptied as part of filler removal).
- `test_friendly_fallback_guides_user` — removed `"didn't quite"` assertion (text changed).

---

## What this slice does NOT change

- No capability permissions, boundary changes, or new capability registrations.
- No routing changes to Cap 64 (email) executor logic — redundant clarification is a
  separate Cap 64 executor issue, deferred to a follow-up slice.
- No changes to response-shift contamination in chained WS sessions (Round 3, requires
  investigation).
- No OpenClaw expansion, no external writes, no new capabilities.
