# Nova Capability Inventory

**Canonical truth source.** Future verification UPDATES this file — do not create scattered
verification docs. Every "Live Verified" row is backed by observed evidence, not code reading.

Last verified: **2026-07-06** against fresh `main` (see QA Rule #1 below).

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
| **Weather** (Visual Crossing) | ✅ | ✅ | ✅ | High |
| **News** (22 RSS feeds) | ✅ | ✅ | ✅¹ | High |
| **Calendar** (local .ics) | ✅ | ✅ | ✅ | High |
| Arithmetic / deterministic commands | ✅ | ✅ | ✅ | Low |
| Web search / research | ✅ | ❌² | 🟡 | Medium |
| General chat (Ollama gemma2:2b) | ✅ | 🟡³ | 🟡 | Medium |
| **Gmail / email / last-3-emails** | ❌ | — | — | Very High |
| **Google Tasks** | ❌ | — | — | High |
| **Google Reminders** | ❌ | — | — | High |
| **Traffic** | ❌ | — | — | High |
| Package tracking | ❌ | — | — | Low |

¹ News works; 2 of 22 feeds are dead (Reuters HTTP 401 — killed public RSS). Live feeds
(BBC/NPR/TechCrunch) return real headlines; dead feeds silently drop. Recommend pruning dead
feeds + adding per-feed health logging. Not a blocker.
² Web-search code routes correctly but no Brave API key is configured → cannot execute live.
³ General chat returns answers but is slow (>30s to first token on gemma2:2b).

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
