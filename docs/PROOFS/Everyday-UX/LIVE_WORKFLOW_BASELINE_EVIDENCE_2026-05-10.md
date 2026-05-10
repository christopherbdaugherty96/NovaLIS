# Live Workflow Baseline Evidence — 2026-05-10

Branch: `proof/everyday-ux-live-workflow-baseline`

Priority lock: `docs/status/ACTIVE_PRIORITY_LOCK_2026-05-10_EVERYDAY_UX_FRICTION.md`

Nova version: Phase 8, running at `127.0.0.1:8000`

Method: Live WebSocket sessions against running Nova (Brave API key active, Ollama local
LLM active). Each conversational scenario was isolated in its own WebSocket session to prevent
context bleed. UI observations from dashboard HTML at `/`.

---

## Meta-observation before scenarios

The test plan used formal, structured prompt phrasing ("search for latest AI news",
"what are you trying to get done"). Real users text casually — abbreviations, typos,
vague phrasing. An additional casual-prompt set was run to capture this gap.

```
friction: test plan prompts were too formal to represent real usage
proposed fix: revise test plan to include casual variants for every scenario
boundary impact: docs only
severity: low
```

---

## S1 — Start Screen (UI observation)

**Method:** Parsed dashboard HTML at `/`

**Expected behavior:** A clear start screen. Obvious first action. No system detail visible
to a new user.

**Actual UI state:**

Headings present across the full dashboard surface:

```
"Dashboard Snapshot"         — technical, not user-facing language
"What are we getting done?"  — friendly, clear
"Screen help (experimental)" — "experimental" label creates uncertainty
"Top News"                   — clear
"Welcome to Nova"            — clear
"Start Here"                 — clear
"Current Focus"              — clear
"What Nova Can Do Right Now" — clear
"Project Threads"            — slightly technical
"OpenClaw Home Agent"        — HIGH FRICTION: internal code name as a heading
"Project Board"              — acceptable
"Structure Map"              — technical, internal
"Trust Center"               — internal governance term
"Setup, Voice, Privacy, and Comfort" — reasonable
"Reviewable Rules"           — governance language
"Governed Memory"            — governance language leaking into user surface
"Memory Overview"            — acceptable
"Memory Center"              — acceptable
```

Total buttons in the dashboard HTML: **90+**

Chat input placeholder: `"What are you trying to get done?"` — clear and helpful.

**Friction observed:**

1. `"OpenClaw Home Agent"` is a user-visible heading. "OpenClaw" is an internal code
   name for the agent automation layer. A new user has no idea what this means.
2. `"Governed Memory"`, `"Trust Center"`, `"Reviewable Rules"`, `"Structure Map"` —
   all internal governance/architecture terms that appear as section headings. A normal
   user does not think in these categories.
3. 90+ buttons across the full dashboard is overwhelming. Most are in secondary sections
   but the sheer count signals system complexity rather than user focus.

| Field | Value |
|---|---|
| friction | Internal code names and governance terms visible as section headings |
| severity | **medium** — confusing, but dashboard panels may collapse by default |
| proposed fix | Rename visible headings: "OpenClaw Home Agent" → "Nova Agent"; "Governed Memory" → "Memory"; "Trust Center" → "Activity Log" or "What Nova Did"; "Reviewable Rules" → "My Rules" |
| boundary impact | UI/JS/HTML only — no runtime change |

---

## S2 — "what can you do" / "what can u do"

**Prompt:** `what can you do` and `what can u do`

**Expected behavior:** A concise, useful summary of what Nova can actually do. No
governance jargon.

**Actual response:**

```
Nova Capabilities Right Now
Here's what is actually live on this device right now:
- Local-first everyday help is ready: explain things, help with project work, save memory,
  open local folders, and check system status.
- Research and reporting: I can search the web, summarize headlines, build intelligence
  briefs, and create multi-source reports.
- Verification and review: I can verify an answer or run a governed second-opinion pass
  without turning that into action.
- Story tracking: I can follow [TRUNCATED]
```

**Widgets:** none

**Friction observed:**

1. Response is truncated — cuts off mid-sentence. User never sees the full list.
2. "Local-first" is a product architecture term, not plain English.
3. "governed second-opinion pass" is internal governance language. A user just wants to
   know Nova can double-check things.
4. No widget — this response would benefit from a structured capability card, not a
   text wall.

| Field | Value |
|---|---|
| friction | Governance language, truncation, no structure |
| severity | **medium** |
| proposed fix | Rewrite in plain English: "local-first" → "works on your device", "governed second-opinion pass" → "can double-check answers". Ensure response completes without truncation. |
| boundary impact | LLM synthesis / response wording only |

---

## S3 — "help me plan my day"

**Prompt:** `help me plan my day`

**Expected behavior:** A helpful, natural response. May ask a clarifying question.

**Actual response:**

```
Okay, I can help with that. What kind of tasks do you have on your plate today?
```

**Widgets:** none

**Friction observed:**

1. "Okay, I can help with that." is a filler phrase that adds no information. Real
   assistants don't start with it.
2. Otherwise the response is short and appropriate — it asks for clarification rather
   than pretending to have calendar access.

| Field | Value |
|---|---|
| friction | Filler opener phrase |
| severity | **low** |
| proposed fix | Drop the "Okay, I can help with that." opener. Start with the question: "What's on your plate today?" |
| boundary impact | Response wording only |

---

## S4 — "search for latest AI news" / "search ai"

**Prompt:** `search for latest AI news`

**Expected behavior:** Cap 16 routes, results appear, search widget emitted.

**Actual response:**

```
Okay. I'm on it. Bottom line: Across multiple sources on "latest AI news", the top reports
align on AI News & Artificial Intelligence | TechCrunch and AI News | Latest News...
Search answer for "latest AI news"
Sources:
1. AI News | Latest News... — https://www.artificialintelligence-news.com/
2. AI News & Artificial Intelligence | TechCrunch — https://techcrunch.com/...
3. Reuters AI News...
```

**Widgets:** none — **search widget NOT emitted**

**Friction observed:**

1. **No search widget in the chat view.** The search results appear only as formatted
   text. The widget system is in place (proven in P3/P4 certification) but it is not
   being emitted to the chat WebSocket in this live path.
2. "Okay. I'm on it." — same filler opener.
3. "Bottom line: Across multiple sources on..." — template wording feels mechanical.
4. `search ai` (abbreviated) also worked — routing handles abbreviations correctly.

| Field | Value |
|---|---|
| friction | Search widget not appearing in chat despite capability being live |
| severity | **high** — widget is the designed result surface; text-only results are harder to scan |
| proposed fix | Verify the search widget is being emitted on the WS `widget` message type in the live path; the certification tests confirmed this — may be a live runtime path difference |
| boundary impact | Runtime — requires investigation before fix |

---

## S5 — "show me the news" / "whats new" / "any news"

**Prompt:** `show me the news`, `whats new`, `any news`

**Expected behavior:** News widget or news summary.

**Actual responses:**

`show me the news`:
```
Okay. Let me check. I didn't quite get that — no worries. Try something like: "what's the
news", "check the weather", "draft an email", or just say "what can you do"...
```

`whats new`:
```
Nothing big, just running smoothly. How are things on your end?
```

`any news`:
```
Okay. Let me check. I didn't quite get that — no worries. Try something like: "what's the
news"...
```

**Friction observed:**

1. "show me the news" is a completely natural request. It should route to news. It does not.
2. "whats new" is treated as small talk — Nova responds as if the user asked "what's up".
3. The error message for `any news` says to try `"what's the news"` — but the user said
   nearly the same thing. Nova's suggested exact phrasing is fragile.
4. The fallback message offers "draft an email" as a suggestion — email isn't set up,
   so suggesting it as a quick-escape option will immediately hit another failure.

| Field | Value |
|---|---|
| friction | Natural news phrases fail to route; fallback suggestions include non-working options |
| severity | **high** — news is a featured capability, basic phrasing doesn't trigger it |
| proposed fix | Add routing coverage for: "show me the news", "whats new", "any news", "news", "headlines". Remove "draft an email" from fallback suggestions if email isn't configured. |
| boundary impact | Routing (GovernorMediator or SessionRouter) — runtime |

---

## S6 — "what's the weather"

**Prompt:** `what's the weather`

**Expected behavior:** Weather with current conditions. May ask for location.

**Actual response:**

```
From the last update at 12:34 AM: 63 degrees F and Clear in Ann Arbor.
Location: Ann Arbor
Forecast: Today: 60F/41F, Partially cloudy
Try next: weather forecast, today's news, or morning brief.
```

**Widgets:** none

**Friction observed:**

1. "From the last update at 12:34 AM" — this is from a cached response from the
   previous session. The timestamp surfaced without context.
2. No weather widget in the chat view (same pattern as search).
3. "Try next:" suggestions are helpful — this is the best-behaved response in the set.

| Field | Value |
|---|---|
| friction | Stale cache timestamp surfaces unexpectedly; no widget |
| severity | **low** |
| proposed fix | Either surface freshness state naturally ("based on data from 12:34 AM") or hide the raw timestamp |
| boundary impact | Response wording only |

---

## S7 — "help me" / "idk what to do"

**Prompt:** `help me`, `idk what to do`

**Expected behavior:** An orienting question. Not a crash. Not a capability brochure.

**Actual responses:**

`help me`:
```
Nova Capabilities Right Now
Here's what is actually live on this device right now: [same list as S2]
```

`idk what to do`:
```
[TIMEOUT after 90s]
```

**Friction observed:**

1. "help me" returns the full capability list — the same as "what can you do". This is
   the wrong response. When someone says "help me" they're signaling confusion or being
   stuck, not asking for a product brochure. The right response is a short orienting
   question.
2. "idk what to do" — LLM cannot handle casual text with abbreviated language, times out.

| Field | Value |
|---|---|
| friction | Vague help request gets capability brochure; abbreviated casual text times out |
| severity | **medium** for "help me"; **high** for "idk what to do" |
| proposed fix | "help me" → ask an orienting question: "Happy to help — what are you trying to do?" or route to clarification. Add "idk", "dunno", "not sure" as clarification triggers. |
| boundary impact | Routing and response wording |

---

## S8 — "open my email"

**Prompt:** `open my email`

**Expected behavior:** A clear, honest setup-required message. Something like "Email isn't
connected yet — here's how to set it up."

**Actual response:**

```
I want to confirm: did you mean a website or a local file for 'my email'?
Say 'open website my email' or 'open file my email'.
```

**Friction observed:**

1. Email is neither a website nor a local file. The clarification is wrong. Asking a user
   to say "open website my email" is absurd and will not help them.
2. This should route to a setup-required state for email, not to the open-URL/open-file
   clarification flow.
3. The exact phrasing asked for ("open website my email") is not something a real user
   would say.

| Field | Value |
|---|---|
| friction | Wrong routing — email request routes to URL/file clarification instead of an honest "not supported" message |
| severity | **high** — confusing and sends user in the wrong direction |
| proposed fix | Add "open my email", "check email", "email inbox" as recognized phrases that return an honest capability boundary response. Nova's email capability (Cap 64) is `mailto:` draft only — no inbox access exists, and there is no setup path that enables it. Response should say: "I can help draft an email, but I can't access your inbox. Want me to draft one?" — not "set it up in Settings." |
| boundary impact | Routing (SessionRouter or GovernorMediator) — runtime |

---

## S10 — Quick action buttons (UI observation)

**Method:** Dashboard HTML at `/`

**Buttons visible in the chat/start area:**

```
Send, Talk, Search, Get headlines, Quick brief, Refresh channels, Expand details
```

**Friction observed:**

1. "Talk" — unclear. Voice input? Does it work? No tooltip or label context.
2. "Refresh channels" — unclear what "channels" means to a normal user.
3. "Get headlines" and "Search" are good — clear labels.
4. "Quick brief" is acceptable but "brief" is slightly internal/jargon.

| Field | Value |
|---|---|
| friction | "Talk" and "Refresh channels" labels are unclear |
| severity | **low** |
| proposed fix | "Talk" → "Voice" or add a tooltip. "Refresh channels" → "Refresh news feeds". |
| boundary impact | UI/HTML label change only |

---

## S11 — "tell me more about that" (follow-up)

**Prompt:** `tell me more about that`

**Expected behavior:** A coherent follow-up response. Nova should maintain some session
context.

**Actual response:** TIMEOUT after 90 seconds.

**Friction observed:**

1. With no prior context in the session, "tell me more" causes the LLM to stall —
   apparently it's trying to interpret the reference and hanging.
2. A better behavior would be: "I'm not sure what you'd like more info on — could you
   be more specific?"

| Field | Value |
|---|---|
| friction | Context-free follow-up causes LLM timeout instead of clarification |
| severity | **high** — timeout is a hard failure |
| proposed fix | Add a fast-path for context-free follow-ups: if no prior context exists, return a short clarification request rather than running LLM inference |
| boundary impact | Session/routing logic — runtime |

---

## S12 — "what went wrong"

**Prompt:** `what went wrong`

**Expected behavior:** If something failed, explain it. If nothing is in context, ask what
the user is referring to.

**Actual response:**

```
Next? What's up with *next*?
```

**Friction observed:**

1. Completely incorrect response — Nova misread "went" and "wrong" as something else
   (possibly "next step" or "what's next"). The response is nonsensical.
2. Italicizing *next* adds emphasis to a word that wasn't in the prompt.

| Field | Value |
|---|---|
| friction | Router/LLM severely misinterprets the phrase; response is nonsensical |
| severity | **high** — nonsensical responses destroy trust |
| proposed fix | Add "what went wrong", "why did that fail", "what happened" as recognized clarification/explanation triggers rather than routing to LLM freeform |
| boundary impact | Routing — runtime |

---

## S13 — "what should I do today"

**Prompt:** `what should I do today`

**Expected behavior:** Nova asks what the user is working on, or pulls a daily brief if
configured. Not a web search.

**Actual response:**

```
Bottom line: Across multiple sources on "What should I do today", the top reports align
on r/productivity on Reddit: What should I do today and "What Should I Do Today?" 9 New
Things to Try...
Sources:
1. "What Should I Do Today?" 9 New Things to Try — https://www.goodlifeproject.com/...
2. r/productivity on Reddit: What should I do today...
```

**Friction observed:**

1. Nova treated "what should I do today" as a web search query and searched the web for
   it literally. Results are lifestyle articles about productivity, not personal assistant
   output.
2. This is a routing failure — a personal planning question was treated as a search.
3. The search result content includes HTML artifacts (`&#8220;`, `&lsquo;`) leaking
   into the plain text response.

| Field | Value |
|---|---|
| friction | Personal planning question triggers web search; HTML entities in response |
| severity | **high** — wrong capability entirely; result is useless |
| proposed fix | Add "what should I do today", "help me figure out my day", "what's my plan" as daily-help triggers. Strip HTML entities from search synthesis output. |
| boundary impact | Routing — runtime. HTML entity stripping — synthesis output |

---

## Casual language observations (additional set)

These prompts were added after user feedback that the formal test plan prompts don't
reflect how real users actually text.

| Prompt | Response | Friction | Severity |
|---|---|---|---|
| `whats new` | "Nothing big, just running smoothly." | Treated as small talk, should offer news | medium |
| `any news` | Failed routing → "Try something like: 'what's the news'" | Natural phrase fails, suggested alternative is nearly identical | high |
| `search ai` | Real Brave results — works | None | — |
| `idk what to do` | TIMEOUT | LLM hangs on informal language | high |
| `why did that fail` | TIMEOUT | LLM hangs | high |
| `what can u do` | Correct capability list | Works with abbreviation | — |

---

## Summary of all friction by severity

### High (fix before claiming UX is ready)

1. **Search widget missing from chat** — S4: results appear as text only, no widget
2. **Natural news phrases fail** — S5: "show me the news", "any news" don't route
3. **"open my email" wrong routing** — S8: routes to file/URL clarification, not setup-required
4. **Follow-up timeout** — S11: "tell me more about that" causes LLM to hang
5. **"what went wrong" nonsensical response** — S12: router misfires, response is incoherent
6. **"what should I do today" routes to web search** — S13: completely wrong capability
7. **Casual/abbreviated language causes timeouts** — "idk what to do", "why did that fail"
8. **"any news" fails despite being very close to "what's the news"** — routing is too rigid

### Medium (confusing but not blocking)

1. **Capability response uses governance language** — S2: "governed second-opinion pass", "local-first"
2. **Capability response truncated** — S2: cuts off mid-sentence
3. **"help me" returns capability brochure** — S7: wrong response for a vague request
4. **"whats new" treated as small talk** — misses the news intent
5. **Dashboard section headings use internal names** — S1: "OpenClaw Home Agent", "Governed Memory", "Trust Center"

### Low (minor, fix when convenient)

1. **Filler openers** — S3, S4: "Okay, I can help with that." / "Okay. I'm on it."
2. **Stale cache timestamp** — S6: "from the last update at 12:34 AM" lacks context
3. **Quick action label clarity** — S10: "Talk", "Refresh channels"
4. **90+ buttons in full dashboard** — overwhelming if all visible at once

---

## Prioritized fix list for next branch (fix/everyday-ux-friction-slice-1)

Fixes should be sequenced by: (1) highest severity, (2) smallest blast radius.

**Round 1 — wording only, no routing change:**

1. Strip HTML entities from search synthesis output
2. Remove "draft an email" from the fallback suggestion list (email not configured)
3. Remove filler openers ("Okay, I can help with that.", "Okay. I'm on it.")
4. Rewrite governance language in capability response ("local-first" → "works on your device", etc.)
5. Rename dashboard headings: "OpenClaw Home Agent" → "Nova Agent", "Governed Memory" → "Memory"

**Round 2 — routing additions (keep change small):**

6. Add "show me the news", "any news", "whats new" as news routing triggers
7. Add "open my email", "check email", "email inbox" as recognized phrases → honest capability-boundary response ("I can draft emails but can't access your inbox")
8. Add "what should I do today", "help me figure out my day" as daily-help triggers (not search)
9. Add "idk", "idk what to do" as clarification triggers

**Round 3 — investigate before fixing (require own branch):**

10. Search widget missing from live chat path — diagnose root cause (P4 cert confirmed it works in test)
11. Follow-up / context-free "tell me more" timeout — needs session state guard

---

## Boundary impact summary

None of the Round 1 or Round 2 fixes above add capabilities, expand OpenClaw, add
browser/computer-use, add external writes, or create autonomous workflows. They are
wording changes and routing additions only. Round 3 items require investigation
before any code change is made.

---

## Capability workflow test — live results against all 27 enabled caps

**Date:** 2026-05-10  
**Method:** Each capability tested in its own isolated WebSocket session via TestClient.
Additional chained-session test run to capture workflow-level issues.

### Result by capability

| Cap | Name | Prompt used | Result | Notes |
|---|---|---|---|---|
| 16 | governed_web_search | `search nvidia news` | ✅ works | Real Brave results, sources listed |
| 17 | open_website | `open google.com` | ✅ works | Asks confirmation before opening |
| 18 | speak_text | not tested | — | — |
| 19 | volume_up_down | not tested | — | — |
| 20 | media_play_pause | not tested | — | — |
| 21 | brightness_control | not tested | — | — |
| 22 | open_file_folder | not tested | — | — |
| 31 | response_verification | `verify this: the earth orbits the sun` | ✅ works | Confidence score, potential issues, structured report |
| 31 | response_verification | `second opinion: is python better than JS` | ❌ misroutes | LLM acknowledges but doesn't verify |
| 32 | os_diagnostics | `check my system status` | ❌ misroutes | Falls back to "I didn't quite get that" |
| 32 | os_diagnostics | `os check` | ⚠️ partial | Routes but asks vague clarifying question |
| 48 | multi_source_reporting | `build me a report on openai from multiple sources` | ⚠️ partial | Acknowledges ("I'm digging in") — no report delivered |
| 49 | headline_summary | `summarize the top headlines` | ⚠️ blocked | Returns "no headline context loaded" — requires prior news call (not discoverable) |
| 49 | headline_summary | `summarize all headlines` (after `headlines`) | ✅ works | Must be two-step: load news first |
| 50 | intelligence_brief | `intelligence brief on the global AI chip supply` | ❌ timeout | "The request took too long and was cancelled." — Ollama CPU budget exceeded |
| 51 | topic_memory_map | not tested | — | — |
| 52 | story_tracker_update | `story tracker: AI regulation` | ❌ misroutes | LLM responds conversationally, no tracker action |
| 53 | story_tracker_view | not tested | — | — |
| 54 | analysis_document | not tested | — | — |
| 55 | weather_snapshot | `what's the weather today` | ✅ works | Real weather, location, forecast, follow-up suggestions |
| 55 | weather_snapshot | `what is the weather forecast for the week` | ❌ misroutes | Routes to Brave web search instead of weather cap |
| 56 | news_snapshot | `headlines` | ✅ works | Loads 5 sources, theme, top story |
| 56 | news_snapshot | `show me the news` | ❌ misroutes | Fallback message (as noted in S5) |
| 57 | calendar_snapshot | not tested | — | — |
| 58 | screen_capture | not tested | — | — |
| 59 | screen_analysis | not tested | — | — |
| 60 | explain_anything | `explain what bitcoin is` | ✅ works | Clear plain-English explanation |
| 60 | explain_anything | `explain large language models simply` | ❌ misroutes | Fails when "explain" comes first without "what" |
| 61 | memory_governance | `save this: I need to call the vendor tomorrow` | ✅ works | Memory ID, tier, scope, try-next suggestions |
| 61 | memory_governance | `remember I am researching AI chips` | ⚠️ partial | Saves but response only says "Got it. Thinking about AI chips?" — no memory ID or confirmation |
| 61 | memory_governance | `recent memories` | ✅ works | Shows memory list with ID and content |
| 62 | external_reasoning_review | not tested | — | — |
| 63 | openclaw_execute | not tested | — | — |
| 64 | send_email_draft | `draft an email to my team: subject AI chip update, say we are researching options` | ⚠️ partial | Asks "What should the email draft be about?" despite full content in prompt. Then honestly states it cannot send. |
| 65 | shopify_intelligence_report | not tested | — | — |

### Workflow-level findings (chained session)

A chained 8-step session (weather → news → search → brief → syscheck → explain → remember → email)
revealed a **response-shift contamination** pattern:

- When one step returns empty or fails fast (e.g., syscheck returning nothing), the `chat_done`
  that ends that step is consumed by the next step's collection loop
- The next step then collects the stale response from the *previous* step
- Effect: responses shift by 1–2 steps downstream in a chained session

This is a session/WebSocket protocol issue. It does not affect isolated sessions.

```
friction: chained sessions produce shifted responses when a step returns empty or times out fast
severity: high — workflow use is broken when capabilities fail mid-chain
proposed fix: ensure every governed invocation emits at least one chat message before chat_done,
even on failure; this prevents empty-response shifts
boundary impact: WebSocket/session handler — runtime
```

### Summary: capability usability by category

**Works reliably with natural phrasing (7 caps):**
- Cap 16: web search (`search X`, `search for X`)
- Cap 17: open website (`open X.com`)
- Cap 31: verify (`verify this: X`)
- Cap 55: weather (`what's the weather`)
- Cap 56: news (`headlines`, `news`, `top news`)
- Cap 60: explain (`explain what X is`)
- Cap 61: memory save (`save this: X`) and view (`recent memories`)

**Works but phrasing-sensitive — easy to miss (4 caps):**
- Cap 31: verify — `verify this:` works, `second opinion:` does not
- Cap 49: headline summary — requires prior news load; no discovery path
- Cap 55: weather — `what's the weather` works; `weather forecast for the week` routes to search
- Cap 60: explain — `explain what X is` works; `explain X simply` does not
- Cap 61: memory — `save this:` gives full confirmation; `remember X` gives vague acknowledgment
- Cap 64: email draft — starts but asks redundant clarification when content already provided

**Fails or times out in live environment (3 caps):**
- Cap 32: os_diagnostics — common phrases don't route; partial route gives unhelpful response
- Cap 50: intelligence_brief — CPU budget exceeded consistently
- Cap 52: story_tracker — routing doesn't fire for natural phrasing

**Not verified (13 caps):**
speak_text, volume_up_down, media_play_pause, brightness_control, open_file_folder,
topic_memory_map, story_tracker_view, analysis_document, calendar_snapshot,
screen_capture, screen_analysis, external_reasoning_review, openclaw_execute,
shopify_intelligence_report

### Additional findings to add to fix list

**Round 2 additions:**

- Add `second opinion: X` as a routing alias for `verify this: X` (Cap 31)
- Add `system check`, `check my system`, `system status` as os_diagnostics triggers (Cap 32)
- Add `weather this week`, `forecast for the week` as weather triggers (Cap 55) — not search
- Add `story tracker:` as a story tracker trigger (Cap 52)
- Fix `explain X` routing to not require `what` — `explain X simply` should also route to Cap 60
- Fix `remember X` to emit a memory ID confirmation same as `save this: X`
- Fix email draft to not ask for content when content was already in the prompt

**Round 3 (investigate before fixing):**

- Chained-session response shift (empty step causes downstream response contamination)
- Cap 50 intelligence_brief CPU budget timeouts — Ollama too slow for this cap's synthesis load
- Cap 48 multi_source_reporting — starts but produces no output; may share the CPU issue
