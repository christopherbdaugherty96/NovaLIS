# Everyday UX Friction — Slice 8 Changelog

**Branch:** `fix/everyday-ux-friction-slice-1`
**Date:** 2026-05-10
**Scope:** Second-pass scan — 23 unrouted phrases found across 6 categories; 20 fixed.

---

## What changed

### Governor routing (governor_mediator.py)

#### SEARCH_RE extended — `find me X`
- Added `find me`, `find me information about`, `find me details on` to
  SEARCH_RE alternation.
- `"find me a recipe for pasta"` → Cap 16 (was: unrouted)
- `"find me information about climate change"` → Cap 16 (was: unrouted)

#### WEATHER_RE — snow variants + `an umbrella`
- `(?:a\s+)?` → `(?:an?\s+)?` in the "should i bring/wear/take" line
  so `"an umbrella"` now matches (was: only `"a jacket"` etc. matched).
- Added `snow|hail|sleet|storm` to the rain alternation.
- Added optional `(?: today| tomorrow| this week)?` suffix to the
  bring/wear/take line.
- `"should i bring an umbrella"` → Cap 55 (was: unrouted)
- `"should i bring an umbrella today"` → Cap 55 (was: unrouted)
- `"will it snow tomorrow"` → Cap 55 (was: unrouted)
- `"is it going to snow"` → Cap 55 (was: unrouted)

#### NEWS_RE — bare catch-up phrases
- Added `catch me up` (bare, no "on the news" suffix), `what did i miss`,
  `anything new` / `anything new today` to NEWS_RE.
- `"catch me up"` → Cap 56 (was: unrouted)
- `"what did i miss"` → Cap 56 (was: unrouted)
- `"anything new today"` → Cap 56 (was: unrouted)

#### SEND_EMAIL_DRAFT_RE — `send` and `can you help me write`
- Extended verb alternation from `draft|compose|write|prepare` to also
  cover `send` and `can you help me write/draft/compose/send`.
- `"send an email"` → Cap 64 (was: unrouted)
- `"can you help me write an email"` → Cap 64 (was: unrouted)

#### MEMORY_RECALL_FRIENDLY_RE — `for me` suffix + `what have i saved`
- Added `(?:\s+for\s+me)?` to the `what have you saved` alternation.
- Added `what have i saved|stored` as an explicit alternate.
- `"what have you saved for me"` → Cap 61 (was: unrouted)
- `"what have i saved"` → Cap 61 (was: unrouted)

#### UPDATE_STORY_RE — `how is the X story doing/going`
- Added `topic6` named group: `how(?:'s| is) (?:the )?TOPIC story (?:doing|going|progressing)`.
- Updated topic extraction to include `topic6`.
- `"how is the AI story doing"` → Cap 52 (was: unrouted)
- `"how is the economy story going"` → Cap 52 (was: unrouted)

---

### Session layer (intent_patterns.py + session_handler.py)

#### TIME_QUERY_RE extended — date queries
- Added `what day is it`, `what's the date`, `what's today's date`,
  `what's today` to TIME_QUERY_RE.
- `"what day is it"` → session-layer time/date response (was: unrouted)

#### `_render_local_time_message()` updated
- Now includes day and date: `"It's 3:45 PM on Tuesday, May 10."` instead
  of just `"It's 3:45 PM."` — fixes the date-query case.

#### REMIND_ME_TIMELESS_RE (new pattern)
- Catches `"remind me to X"` and `"set a reminder"` without a time spec.
- Fires BEFORE REMIND_ME_RE (which requires `at TIME`).
- Response: "I need a time to set that reminder. Try: 'remind me at 3pm to
  call mom' or 'remind me daily at 9am to check email'."
- `"remind me to call mom"` → scripted clarification (was: LLM fallthrough)
- `"set a reminder"` → scripted clarification (was: LLM fallthrough)
- `"remind me at 3pm to call mom"` → still reaches REMIND_ME_RE ✓

---

## Scope note

Phrases intentionally left as LLM fallthrough (context-dependent or no
clear single-capability answer):
- `"yeah"`, `"no thanks"` — conversational, LLM handles fine
- `"translate this"`, `"save this"`, `"delete it"`, `"play it"` — no
  referent without prior context
- `"restart nova"`, `"shut down"` — out of scope for conversational
  routing; SYSTEM_RE handles the system-status angle
- `"never mind"` / `"forget it"` — already handled at line 42 of
  session_handler via `_classify_yn_response()` → "cancel"

---

## Tests

- 445 unit tests (conversation + websocket + governor): all pass
- 155 certification tests: all pass
