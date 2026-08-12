# Nova Capability Inventory

**Canonical truth source.** Future verification UPDATES this file — do not create scattered
verification docs. Every "Live Verified" row is backed by observed evidence, not code reading.

Last broad capability verification: **2026-07-11** against fresh `main` (see QA Rule #1 below).
Latest targeted fresh-main acceptance: **2026-08-12** at
`c44b6d0cd72f0f91a6ec517427ad3fe2076beb30`. The targeted run did not reverify every capability or
complete every 36-section stress variant. This update distinguishes Nova's implemented local
reminder schedules from unimplemented background delivery, Google Tasks, and Google Reminders. It
adds no capability, connector, or authority.

---

## 2026-08-12 Current Update

```text
PR #334 merged Semantic Substrate Slice 1 as provider-neutral contracts/tests only.
PR #335 Google Workspace Foundation remains DRAFT / UNMERGED and adds no current-main capability.

Fresh-main real-user acceptance:
  docs/observation/FRESH_MAIN_REAL_USER_ACCEPTANCE_2026-08-12.md

Live-proven current reminder truth:
  Nova local reminder schedules exist.
  A deterministic handoff persisted a real SCH record.
  `show schedules` / `reminders` displayed it after a full backend-process restart.
  Background reminder delivery and automatic firing do not exist.
  Google Tasks and Google Reminders do not exist.

The same run reconfirmed approval/replay/bypass boundaries and real Cap 19 effects, while exposing
P1 conversation-truth defects and several P2 routing/source defects. Therefore implemented
capability and truthful capability narration are not yet consistent across all wording.
```

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
#312. Email/Google Tasks/Google Reminders/Traffic remain NOT IMPLEMENTED. Nova local reminder
schedules are now implemented but have no background delivery. Nothing here authorizes
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
PERSONAL        █████░░░░░  50%   calendar + local schedules; Gmail/Google Tasks/traffic absent
AUTOMATION      ██░░░░░░░░  20%   read-only only, by design
```

## Morning needs covered (measured against Chris's real routine): **~50%, with partial reminder coverage**

| Morning check | Status |
|---|---|
| Weather | 🟡 configured-location path works; explicit-location routing defect observed 2026-08-12 |
| News | 🟡 real sourced surface works; `give me today's news` parameter defect observed 2026-08-12 |
| Calendar | 🟡 local `.ics` today path works; `tomorrow` scope defect observed 2026-08-12 |
| Local reminder schedules | 🟡 persistent SCH records + retrieval work; cancellation routing defect and no background delivery |
| Google Tasks / Google Reminders | ❌ not built |
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

- **Configured-location weather** — returns real weather; arbitrary-location routing is currently
  not dependable.
- **News surface** — can return real headlines from live feeds; the exact `give me today's news`
  route is currently not dependable.
- **Today's local Calendar view** — reads the configured `.ics`; `tomorrow` scope wording is
  currently not dependable.
- **Local reminder schedules** — saves and retrieves persistent SCH records through the supported
  deterministic handoff; cancellation by advertised command and background delivery are not
  dependable.
- **C1 / business best-move** — deterministic, honest, governed.
- **The awareness brief on open** — assembles the above with honest per-section degradation.

**Cannot yet rely on:** email, Google Tasks/Google Reminders, background reminder alerts, or
traffic (not built); schedule cancellation by advertised command (routing defect observed
2026-08-12); web search without a configured key; consistently truthful/fast conversational chat.

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

- **2026-08-12** — Fresh-main real-user acceptance at `c44b6d0...`: local reminder schedule
  persisted and survived backend restart; `show schedules` / `reminders` retrieved it; Cap 19
  produced measured Windows volume effects; approval/replay/bypass boundaries held. The run also
  found P1 conversation-truth defects and did not complete every variant in the 36-section catalog.
  See `docs/observation/FRESH_MAIN_REAL_USER_ACCEPTANCE_2026-08-12.md`.

- **2026-07-06** — Full live verification against fresh `main`. Weather/News/Calendar/routing
  all PASS live (news + calendar were false negatives on the prior stale instance). Gmail/
  Tasks/Reminders/Traffic confirmed NOT IMPLEMENTED. Read-only preserved; 27 caps unchanged.
