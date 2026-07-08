# Live Verification Report — 2026-07-07

Pre-observation verification pass. Real live test of the running backend on current `main`.
No features built, no missing capabilities simulated, no mocked results. Every PASS was
observed live over the real `/ws` dashboard path.

## Environment

```text
Commit tested : 963f1d8 (main, clean working tree except 2 pre-existing runtime docs)
Branch        : main
Backend       : uvicorn src.brain_server:app on 127.0.0.1:8000, health /phase-status = 200
Model         : gemma2:2b (Ollama up; fallback phi3:mini)
Env           : WEATHER_API_KEY present; NOVA_CALENDAR_ICS_PATH present + .ics exists;
                Shopify/OpenClaw tokens loaded from nova_backend/.env
Launcher      : in-process env launcher (matches desktop-shortcut full-User-env launch)
QA Rule #1    : SATISFIED — killed the 4-day-stale process (started 07-06 19:01),
                restarted fresh on current main; verified fresh PID before testing.
```

## Result table

| # | Area | Verdict | Notes |
|---|------|---------|-------|
| 1 | Startup / health / WS | PASS | `/phase-status` 200; WS connects; on-connect greeting sent |
| 2 | Weather | PASS | Live "72–73°F Overcast, Ann Arbor; today 86/61" + weather widget |
| 3 | News | PASS | 5 live sources, real current headlines + news widget (~8–10s) |
| 4 | Calendar | PASS | Reads the .ics ("Nothing on your calendar today"); brief rose 4/8→5/8 |
| 5 | Awareness brief ("What's my brief?") | PASS | Renders "5 of 8 sections live"; weather+news widgets (~4–8s) |
| 6 | Arithmetic | PASS | "47+58"→"105", "deterministic, instant (bypasses LLM)" |
| 7 | Web search (Cap 16) | PASS | Real Reuters/TechCrunch/BBC results |
| 8 | "What can you do?" | PASS | Full capability list |
| 9 | Email | PASS (honest degrade) | "mailto-based… no inbox access. Want me to draft?" |
| 10 | Governance | PASS | 27 capabilities unchanged, no writes, tree clean, ledger appending |
| 11 | Model version lock | PASS (after owner confirm) | Fired on fresh start (stale fingerprint); cleared via "confirm model update" |
| 12 | Traffic | NOT IMPLEMENTED | "I didn't match that…" (no false claim) |
| 13 | Google Tasks | NOT IMPLEMENTED (misleading) | "my tasks today" → web-searches the phrase instead of degrading honestly |
| 14 | C1 "What's blocking Auralis?" | PARTIAL | No standalone intent; C1 is brief-embedded only |
| 15 | Conversation / LLM chat | PARTIAL / throughput-blocked | Routes to LLM post-unlock but responses time out on CPU (#227) |

## Model version lock (the headline finding)

On a fresh start the version-pin lock engaged: the stored trust-fingerprint (`9a34425a…`)
predated the current model/prompt/wrapper state, so inference was blocked and the on-connect
greeting showed "⚠️ Local model inference is currently locked pending confirmation."

- The lock is governance working as designed (it detects fingerprint drift and refuses to run
  the LLM until confirmed). It is NOT a crash.
- Deterministic surfaces (weather/news/calendar/brief/search/arithmetic/help) all worked
  **under** the lock — the lock gates LLM inference only.
- Owner authorized "confirm model update" in-session; it cleared the lock, rewrote the stored
  hash (`29bdc227…`), logged a MODEL_UPDATED ledger event (user_confirmed=True), and produced a
  clean greeting on the next connection. It will not re-trigger on restart unless the model,
  system prompt, wrapper, or model digest actually changes.

## Conversation layer (post-unlock)

Once unlocked, natural-language input routes to the LLM correctly (no more keyword misrouting),
but gemma2:2b on 8GB CPU-only hardware cannot return a freeform response inside the governor's
execution-timeout guard — responses come back "The request took too long and was cancelled" and
fall back to phi3:mini. This is the known throughput limitation (#227), confirmed live. It does
NOT affect the deterministic morning surfaces, which are the product's current core value.

Observed transient: the FIRST LLM-triggering request after unlock stalled the async event loop
(cold model load), briefly cancelling/slowing even deterministic requests (weather 10–14s, one
cancelled). The system settled and deterministic latency returned to normal (news ~10s, brief
~5s). Root: sync provider/model probe blocks the loop on cold start — same family as #227.

## Critical bugs

```text
None that block observation. The morning-critical deterministic surfaces work live.
```

## Non-critical issues (log only — do NOT fix during the Phase 3 freeze)

```text
1. Model-lock greeting: fires whenever the fingerprint drifts and shows a user-facing
   "inference locked" warning. Cleared for now. Consider (later, B-lane) softening the
   greeting and/or auto-confirming an unchanged-model restart.
2. "What are my tasks today?" mis-routes to web search (googles the phrase) instead of
   honest "tasks aren't integrated." Google Tasks is unbuilt; the fallthrough is misleading.
3. Keyword-collision routing: "summarize <X>" → news summary; "tell me about <X>" → web
   search. Capability keyword match precedes the LLM understanding layer.
4. Calendar "tomorrow" query echoes "today" copy; calendar connected but no near-term events
   (a "walk the dog" item added earlier may be a Task, not an Event).
5. Cold-start event-loop stall after any LLM activation (see above).
6. src/models/current_model_hash.txt is git-TRACKED but is machine-local trust state (the
   model-digest fingerprint differs per install). The owner-authorized unlock rewrote it, so
   it now sits modified-uncommitted. Open decision: gitignore it (treat as local state) vs keep
   it tracked (shared baseline). Left uncommitted pending that decision.
```

## Missing capabilities (stated plainly)

```text
Gmail inbox           — NOT IMPLEMENTED (mailto draft only, honestly disclosed)
Google Tasks / Reminders — NOT IMPLEMENTED (query mis-routes to web search)
Traffic / commute     — NOT IMPLEMENTED (honest no-match)
Package tracking      — NOT IMPLEMENTED
```

## Recommendation

```text
READY FOR OBSERVATION.

The morning value — the deterministic awareness brief (weather + news + calendar + project/
business state) — works live on current main. The LLM conversation weakness is a known,
non-blocking hardware/throughput limitation (#227) that does not touch the morning surfaces.

Caveat for the morning flow: if Nova is launched via the desktop shortcut with the full User
environment, calendar and weather work. The model-lock greeting is now cleared and will not
reappear on restart unless the model/prompt actually changes.
```

## How to reproduce

```text
1. Kill any process on :8000 (a stale process yields false negatives — QA Rule #1).
2. Launch with full env: .env (Ollama/Shopify/OpenClaw) + User-scope WEATHER_API_KEY and
   NOVA_CALENDAR_ICS_PATH. Confirm /phase-status = 200.
3. Over ws://127.0.0.1:8000/ws: DRAIN the on-connect greeting first, THEN send
   {"type":"chat","text":"<prompt>"}, then read until {"type":"chat_done"}.
   (Probing the greeting instead of the answer produces a false "everything is locked" reading.)
4. Prompts used: weather / headlines / calendar / "what's my brief" / "47+58" / web search /
   "check my email" / "what are my tasks today" / "how's my commute" / conversational prompts.
```
