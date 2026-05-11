# Everyday UX Friction — Fix Slices 5, 6, 7 Changelog

Branch: `fix/everyday-ux-friction-slice-1`  
Date: 2026-05-10

---

## Slice 5 — News, weather, mute, note, screenshot gaps

### News variants
`NEWS_RE` extended: `news headlines`, `top stories [today]`, `show me today's news`,
`what's the top stories`.

### Weather variants
`WEATHER_RE` extended: `weather today/tonight/tomorrow`, `today's weather`,
`tonight's weather`, `whats the forecast`, `the forecast`, `forecast for today/tomorrow`.

### Mute variants
Mute inline regex extended: `volume off`, `silence`, `sound off`, `go silent`.

### Note memory save
`MEMORY_NOTE_RE` extended: `quick note: X`, `save note: X`, `add to notes: X`,
`add notes: X`, `jot this: X`.

### Screenshot — bare form
`SCREEN_CAPTURE_RE` extended: bare `screenshot`, `take a picture/photo/snap of the screen`,
`snap the screen`.

---

## Slice 6 — Volume set, folder, story update, verify ordering, battery, screen analysis

### Volume set — natural forms
`SET_VOLUME_RE` rewritten to match: `volume at 40`, `turn volume to 60`, `volume to 30`,
`set the volume to 75`, optional `%` / `percent` suffix.

### Folder — "take me to X"
`GO_TO_FOLDER_RE` extended: `take me to downloads`, `bring up desktop`.

### Story tracker — update natural forms
`UPDATE_STORY_RE` extended with 5 alternate topic capture groups:
- "update me on the X story"
- "whats new on X"
- "any updates on X"
- "news on X"
- "update story X" (existing)

### Verify — "is it true that X" ordering fix
Added early `VERIFY_RE` pre-check before `CLAIM_CHECK_RE` / Cap 16 heuristics so:
- "is it true that vaccines are dangerous" → Cap 31 (not Cap 16 health search)
- "check that claim: X" → Cap 31
- "is that true: X" → Cap 31

`VERIFY_RE` itself also expanded with these new anchor phrases.

### System — battery
`SYSTEM_RE` extended: `battery`, `battery status/level/life/charge`, `check battery`,
`how is my battery`, `battery percentage` → Cap 32.

### Screen analysis — natural forms
`SCREEN_ANALYSIS_RE` extended: `whats on my screen`, `what's on the screen`,
`what do I see on screen`, `help me read this screen`, `describe my screen`,
`look at my screen` → Cap 59.

---

## Slice 7 — Memory recall/search, news, weather, story unfollow, screen

### Memory recall — "what did i save"
`MEMORY_RECALL_FRIENDLY_RE` extended: `what did i/you save/store/note/jot`,
`what was saved/stored/noted`.

### Memory search — "find notes about X"
`MEMORY_SEARCH_RE` extended: `find my notes about/on X`, `look up my notes on/about X`.  
Added early pre-check before `SEARCH_RE` so "look up my notes on dentist" routes to
Cap 61 (not Cap 16 web search).

### News — more natural forms
`NEWS_RE` extended: `morning news`, `evening news`, `any news today`,
`what's happening in the world`.

### Weather — feel/clothing questions
`WEATHER_RE` extended:
- "is it cold/hot/warm/chilly/freezing [outside/today/tomorrow]"
- "will it be cold/hot/warm tomorrow"
- "should I bring a jacket/coat/umbrella/raincoat"
- "what's the temperature today/outside"

### Story tracker — unfollow
`STOP_TRACKING_RE` extended: `unfollow X`, `drop X [story]` → Cap 52 stop action.

### Screen analysis — more forms
`SCREEN_ANALYSIS_RE` extended: `scan the screen`, `read what is on screen`,
`what does the screen say`, `tell me what's on my screen` → Cap 59.

---

## Final coverage scan — 88 natural phrases, 0 unrouted

| Capability | Phrases routed |
|---|---|
| Cap 61 (memory) | 16 |
| Cap 56 (news) | 12 |
| Cap 55 (weather) | 10 |
| Cap 19 (volume) | 8 |
| Cap 32 (system) | 7 |
| Cap 52 (story tracker) | 7 |
| Cap 20 (media) | 4 |
| Cap 22 (folder) | 4 |
| Cap 31 (verify) | 4 |
| Cap 59 (screen analysis) | 4 |
| Cap 17 (website) | 3 |
| Cap 21 (brightness) | 3 |
| Cap 16 (web search) | 2 |
| Cap 58 (screenshot) | 2 |
| Cap 48 (intel brief) | 1 |
| Cap 62 (second opinion) | 1 |
| NONE (unrouted) | **0** |

---

## What these slices do NOT change

- No capability permissions, boundary changes, or new capability registrations.
- No changes to Cap 64 (email) executor logic.
- No OpenClaw expansion, no external writes, no new capabilities.
- Media next/skip not added — executor only supports play/pause/resume.
- Memory clear/forget-all not added — no safe confirm flow exists yet.
