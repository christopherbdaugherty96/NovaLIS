# Nova Capability Inventory

**Canonical truth source.** Future verification UPDATES this file — do not create scattered
verification docs. Every "Live Verified" row is backed by observed evidence, not code reading.

Last verified: **2026-07-11** against fresh `main` (see QA Rule #1 below). Latest status update
**2026-07-23** (grounded routing shipped; capability set unchanged — no new capability, connector,
or authority). PR #312 is verified on fresh main (see the 2026-07-23 update below); a future
morning provides additional real-use/product-acceptance input, not a re-verification of #312.

---

## 2026-07-23 Current Update

```text
SEVEN-MORNING THRESHOLD COMPLETE (docs/observation/SEVEN_MORNING_SYNTHESIS_2026-07-22.md).
Grounded brief/category routing — the synthesis rank-1 defect — shipped via PR #312 (merged
2026-07-23) after PR #311 timeout containment:
  category prompts reach governed Cap 49;
  brief/story follow-ups bind to the rendered Cap 50 clusters / active surface;
  numeric story commands resolve against a stable active-surface map;
  one confidence value feeds response body and the Trust strip;
  deterministic, source-bounded fallback preserved.
No capability was added, expanded, or unlocked. The registry, capability count, and the four
certification locks (Cap 16/22/64/65) are unchanged.

Live-verification status: PR #312's grounded brief/category routing is verified on fresh `main`
(docs/status/GROUNDED_BRIEF_ROUTING_CLOSEOUT_2026-07-23.md: restarted from clean main; the
full category -> second-story -> "what matters most" follow-up workflow, [Fallback] marking, and
a healthy interface were confirmed). The rows below keep their "Live Verified 2026-07-11" date; a
future morning is additional real-use/product-acceptance input, not the missing verification of
#312. Email/Reminders/Traffic remain NOT IMPLEMENTED. Nothing here authorizes
Google Tasks, Gmail, Traffic, new connectors, external writes, or autonomous execution.
```

---

## 2026-07-11 Current Update

```text
PR #295 fixed false "not configured" labels for news/weather.
PR #297 fixed dashboard websocket input reliability.
PR #298 landed grounded follow-up conversation over brief items and passed post-merge smoke:
  news selected-story carry-forward;
  weather no-invention rain follow-up;
  calendar selected-event "after that";
  unrelated weather-themed prompt stayed on normal GeneralChat path with no grounded facts
  injected.

General chat remains yellow for CPU model latency/quality, not because brief grounding is absent.
DeepSeek/cloud conversation remains parked until observed use of the grounded path proves a
genuine model-quality gap.
```

---

## QA Rule #1 (permanent)

> Before any live verification, confirm the running process matches current `main`.
> If not, **restart before testing.**

On 2026-07-06 the running backend was 4 days stale (up since 07-02, pre-dating that day's
merges). It produced two false negatives — News and Calendar both looked broken but the code
was fine. Always verify against a current-`main` instance.

---

## Readiness by tier

```
CORE PLATFORM   ██████████  95%   governance, caps, runtime truth, memory, C1
INFORMATION     ████████░░  80%   weather + news + calendar verified live
BUSINESS        ███████░░░  75%   C1, Shopify awareness, promotion queue, best-move
PERSONAL        ████░░░░░░  40%   calendar yes; email/reminders/traffic absent
AUTOMATION      ██░░░░░░░░  20%   read-only only, by design
```

## Morning needs covered (measured against Chris's real routine): **~50%**

| Morning check | Status |
|---|---|
| Weather | ✅ verified live |
| News | ✅ verified live |
| Calendar | ✅ verified live (reads .ics; honest "nothing today") |
| Reminders | ❌ not built (Google Tasks/Reminders) |
| Email | ❌ not built (Gmail) |
| Traffic | ❌ not built |
| Business (when needed) | ✅ C1 |

---

## Capability Registry

| Capability | Exists | Live Verified | Production Ready | Daily Value |
|---|:--:|:--:|:--:|:--|
| Governance / read-only / capability-lock | ✅ | ✅ | ✅ | Foundational |
| Runtime truth / health | ✅ | ✅ | ✅ | Foundational |
| Governed memory (+ seed loading) | ✅ | ✅ | ✅ | High |
| C1 / Auralis Today | ✅ | ✅ | ✅ | Medium (today) |
| Awareness brief + dogfood routing (#268) | ✅ | ✅ | ✅ | High |
| **Weather** (Visual Crossing) | ✅ | ✅ | ✅⁴ | High |
| **News** (RSS feeds) | ✅ | ✅ | ✅¹ ⁵ | High |
| **Calendar** (local .ics) | ✅ | ✅ | ✅ | High |
| Arithmetic / deterministic commands | ✅ | ✅ | ✅ | Low |
| Web search / research | ✅ | ❌² | 🟡 | Medium |
| General chat (Ollama gemma2:2b) | ✅ | 🟡³ | 🟡 | Medium |
| **Gmail / email / last-3-emails** | ❌ | — | — | Very High |
| **Google Tasks** | ❌ | — | — | High |
| **Google Reminders** | ❌ | — | — | High |
| **Traffic** | ❌ | — | — | High |
| Package tracking | ❌ | — | — | Low |

¹ News works; the dead Reuters feed (HTTP 401 — killed public RSS) silently drops. Live feeds
(BBC/NPR/TechCrunch) return real headlines. Recommend per-feed health logging. Not a blocker.
² Web-search code routes correctly but no Brave API key is configured → cannot execute live.
³ General chat returns answers but is slow (>30s to first token on gemma2:2b).
⁴ Weather false "not configured" label FIXED (PR #295, 2026-07-11). Root cause was structural,
not config: the brief read a top-level `connected` flag but the weather widget nests it under
`data`, so a working forecast always rendered "not configured". The brief now unwraps the
envelope; a genuine missing key still reads truthfully; a failed/rate-limited fetch reads
"temporarily unavailable" (never "not configured / add API key").
⁵ News false "not configured / check Brave" label FIXED (PR #295, 2026-07-11). Root cause:
one news request fans out to ~26 governed network calls (cap 56); the ~70s dashboard refresh
re-spent them and exhausted the 50/min rate limit, so later fetches returned empty and were
mislabeled. A 180s result cache collapses repeated refreshes onto one fetch; empty results now
read "temporarily unavailable" and never blame Brave (Brave = web search, not the news source).

**Conversation grounding (PR #298, 2026-07-11):** grounded follow-ups over brief items are now
implemented. Fetch-shaped prompts still route to deterministic widgets; follow-ups over loaded
news/weather/calendar facts answer from structured sourced session state before the LLM path.
Post-merge smoke from fresh main passed for selected news story carry-forward, weather
no-invention, calendar selected-event "after that", and unrelated prompt isolation. Any
local-vs-cloud model-quality comparison should now use this grounded path as the test surface.

---

## What Chris can confidently rely on EVERY DAY today

Not "what exists" — what is dependable:

- **Weather** — real, fast, honest.
- **News** — real headlines from live feeds (BBC/NPR/TechCrunch anchor it).
- **Calendar** — reads your calendar and reports honestly (including "nothing today").
- **C1 / business best-move** — deterministic, honest, governed.
- **The awareness brief on open** — assembles the above with honest per-section degradation.

**Cannot yet rely on:** email, reminders, traffic (not built); web search (no key); fast
conversational chat (slow model).

---

## News architecture (verified)

```
22 RSS feeds -> parallel fetch (NetworkMediator, cap 56) -> dedup by URL
   -> score/rank -> display   |   all-empty -> "News unavailable" (honest, no fabrication)
```
Free RSS, no API key, no vendor lock-in, defusedxml-safe (XXE-hardened), graceful degradation.
Keep this design; do not swap to a paid NewsAPI without a specific need.

---

## Verification log

- **2026-07-06** — Full live verification against fresh `main`. Weather/News/Calendar/routing
  all PASS live (news + calendar were false negatives on the prior stale instance). Gmail/
  Tasks/Reminders/Traffic confirmed NOT IMPLEMENTED. Read-only preserved; 27 caps unchanged.
