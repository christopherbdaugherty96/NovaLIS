# Morning 4 — Pre-Registered Probe Checklist

> "This observation phase is intended to falsify current hypotheses, not confirm them."

Rename to `MORNING_04_<date>.md` when run, and fill the RECORD lines in real time.

**Build under test:** current `main` at `ec380c39` (PR #302). Start a fresh server if possible.
**Status frame:** OBSERVATION-READY, NOT RELIANCE-READY. Externally verify any schedule/business
claim before trusting it.

## Why this morning exists

Morning 4 is the falsification test for the four fixes merged since Morning 3. If they worked, the
Morning 1–3 pains should be gone; if not, that's the next real gap. Pre-registered hypotheses:

- **H1 — Gotcha loop is dead.** No unsolicited "Gotcha. What should I continue from?" on open or
  after reconnect. (fix `71d1bbef`)
- **H2 — Natural brief phrasing routes.** `is it hot out?` → weather, `anything on my schedule?` →
  calendar, `what should I know today?` → news, without advisory fall-through. (fix `59b77844`)
- **H3 — Turns end cleanly.** No `Request not run` / "connection status" copy unless nothing
  actually ran; a slow advisory turn shows a *Thinking* indicator, not a failure. (fix `1eb3ba28`)
- **H4 (expected still-open) — Last-answer follow-up is NOT grounded.** `on what weekday?` after a
  search likely does not connect to the prior result. This is the candidate next slice (#4).

## Before opening — RECORD

- [ ] Port 8000 free / clean restart. Fresh or warm runtime: ____
- [ ] Launched via normal Nova path: ____
- [ ] Active model (expect `gemma2:2b`): ____
- [ ] Dashboard opened only for this session: ____
- [ ] Any runtime-doc churn / dirty worktree noted after start: ____

## Open brief — RECORD

- [ ] Weather section present: ____
- [ ] News section present: ____
- [ ] Calendar section present: ____
- [ ] Stale Auralis date (e.g. `July 9`) still shown without tense: ____
- [ ] Any unsolicited `Gotcha…` on open: ____

## Probe 1 — Gotcha loop (tests H1)

Wait 30–60s after opening; do not type. RECORD whether Nova repeats anything unprompted.
**Expected:** no repeated `Gotcha`, no composer lock. **RECORD:** ____

## Probe 2 — Natural weather (tests H2 + H3)

Prompt: `is it hot out?`
**Expected:** routes to weather; **no advisory turn at all** (H2). Record separately:

- [ ] Routed to weather (widget/content): ____
- [ ] `Request not run` / connection-status copy appeared? (must be NO — H3): ____
- [ ] Latency / did it need Stop: ____

Follow-up: `how should I stay cool?`
**Expected:** grounded weather advice OR a clear limitation — never a connection-status failure.
Note: if this one *does* reach the advisory model, a `Thinking…` indicator is now CORRECT; only a
failure/`Request not run` render counts against H3. **RECORD:** ____

## Probe 3 — Natural calendar (tests H2)

Prompt: `anything on my schedule?`
**Expected:** calendar answer from loaded `.ics`; if empty, "nothing scheduled"; no advisory
fall-through. **RECORD:** ____

Follow-up: `what about after that?`
**Expected:** honest answer/ask; does NOT invent events. **RECORD:** ____

## Probe 4 — News (tests H2)

Prompt: `what should I know today?`
**Expected:** news / loaded brief context; no generic "I didn't match that." **RECORD:** ____

Follow-up: `why does that matter?`
**Expected:** if a story is loaded, stays grounded; else asks which story. **RECORD:** ____

## Probe 5 — Last-answer follow-up (tests H4 — expected to fail)

Prompt: `look up when the next episode of House of the Dragon comes out`
Then: `on what weekday?`
**Expected:** may fail — that's the point. RECORD whether Nova connects the follow-up to the prior
search result, or loses the thread. This defines slice #4. **RECORD:** ____

## Probe 6 — Stop recovery

If any turn stalls, press Stop.
**Expected:** honest stopped/waiting message; composer clears; next prompt can be sent.
**RECORD:** ____

## Verdict fields

- Did Nova eliminate one uncertainty before you opened another app? ____
- First unanswered question: ____
- Most trust-damaging behavior: ____
- One wish of the day (3+ repeats across mornings = roadmap candidate): ____
- Would you use this tomorrow without "testing mode"? ____

## Falsification summary (fill after)

- H1 Gotcha dead: confirmed / falsified — ____
- H2 phrasing routes: confirmed / falsified — ____
- H3 clean completion: confirmed / falsified — ____
- H4 follow-up grounding gap: confirmed open / unexpectedly works — ____
- Next slice indicated by this morning: ____
