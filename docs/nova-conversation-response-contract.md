# Nova Conversation Response Contract

Branch: `docs/nova-conversation-response-contract`  
Date: 2026-05-10  
Source: `docs/PROOFS/Everyday-UX/LIVE_WORKFLOW_BASELINE_EVIDENCE_2026-05-10.md`

---

## Purpose

This document converts the live baseline friction findings into desired
response shapes before any code changes are written. Each entry is a
specific, testable contract: given this input, Nova should produce this
output, not that output.

The contracts cover two categories:
- **Routing contracts** — wrong capability or no capability selected
- **Response-shape contracts** — right capability selected but response text
  is wrong (governance language, truncation, brochure dump, etc.)

---

## Routing Contracts

### RC-1 — Email: "open my email"

| | Current | Contract |
|---|---|---|
| Input | `open my email` | `open my email` |
| Routed to | Cap 17 (website open) | Cap 64 (email), action: `setup_required` |
| Response | URL-or-file clarification | "Email in Nova is mailto-based — it can open a draft in your default mail app but doesn't have inbox access. Want me to open a draft?" |

**Also covers:** `check my email`, `my inbox`, `email inbox`, `read my emails`

**Why current is wrong:** Cap 64 exists and is enabled. "open my email" should
not resolve as a website. It should trigger the email capability, which
knows it has no inbox and returns the correct scoped message.

---

### RC-2 — Context-free follow-ups: "tell me more about that"

| | Current | Contract |
|---|---|---|
| Input (no prior context) | `tell me more about that` | `tell me more about that` |
| Response | LLM timeout | "What are you referring to? I don't have context from a previous message." |

**Also covers:** `go deeper on that`, `expand on that`, `explain that more`,
`more detail please`

**Why current is wrong:** With no prior session state, these timeout waiting
for context that doesn't exist. The router should detect context-free follow-up
and return an immediate clarification — no LLM call needed.

**Proposed routing:** `needs_clarification: true` with clarification prompt:
"What should I go deeper on?"

---

### RC-3 — Context-free error: "what went wrong"

| | Current | Contract |
|---|---|---|
| Input (no prior context) | `what went wrong` | `what went wrong` |
| Response | Nonsensical LLM output | "What situation are you asking about?" |

**Also covers:** `why didn't that work`, `what failed`, `what's the error`,
`why isn't this working`

**Why current is wrong:** Without context, these are unanswerable. The router
should treat bare error-diagnosis phrases as context-required clarifications.

---

### RC-4 — Daily intent: "what should I do today"

| | Current | Contract |
|---|---|---|
| Input | `what should i do today` | `what should i do today` |
| Routed to | Cap 16 (web search) | Clarification |
| Response | Web search results | "Are you asking about your calendar/tasks, or looking for a productivity suggestion?" |

**Also covers:** `what's my plan today`, `what do I need to do today`,
`what's on my plate today`

**Why current is wrong:** "what should I do today" is not a web search query.
It's either a calendar/task question (which Nova can't answer without those
integrations) or a prompt for daily structure (which needs clarification). Web
search is the wrong fallback.

**Proposed routing:** `needs_clarification: true` with clarification prompt:
"Are you checking your schedule, or looking for a productivity plan?"

---

### RC-5 — Informal confusion: "idk what to do"

| | Current | Contract |
|---|---|---|
| Input | `idk what to do` | `idk what to do` |
| Response | LLM timeout | "Sounds like you're stuck — what are you working on?" |

**Also covers:** `not sure what to do`, `i don't know where to start`,
`i'm lost`, `what do i even do`, `where do i begin`

**Why current is wrong:** Informal confusion phrases should be treated as
orientation requests — no LLM call, no search, just a warm clarification.

---

### RC-6 — Casual failure question: "why did that fail"

| | Current | Contract |
|---|---|---|
| Input (no prior context) | `why did that fail` | `why did that fail` |
| Response | LLM timeout | "What was the action or step that failed?" |

**Also covers:** `why did it stop`, `why is it broken`, `why isn't it working`,
`what's wrong with it`

---

### RC-7 — "help me"

| | Current | Contract |
|---|---|---|
| Input | `help me` | `help me` |
| Response | Full capability brochure | "What are you working on? I can search the web, check the news or weather, remember things, or help you think through a problem." |

**Why current is wrong:** A brochure response to "help me" is a classic UX
failure — the user said "help" because they don't know what to ask. A
capability list makes the confusion worse. The correct response is a short,
warm orienting question.

**Proposed routing:** Detected as bare help intent → direct response from
a short scripted handler, not the capability list.

---

## Response-Shape Contracts

### RS-1 — Capability response: no governance language

**Current:** "What can you do" returns phrases like "governed second-opinion
pass", "local-first everyday help is ready", "OpenClaw".

**Contract:** Plain-English, outcome-first descriptions only.

| Forbidden | Allowed |
|---|---|
| "governed second-opinion pass" | "check a claim or get a second read on something" |
| "local-first everyday help" | "works on your device without sending data out" |
| "OpenClaw" | never surfaces to users |
| "capability" (as a noun in response) | "thing I can do" or just describe it |

**Note:** Already fixed in brain_server.py as part of slice 1. This entry
documents the contract so regression is detectable.

---

### RS-2 — Capability response: no truncation mid-sentence

**Current:** "What can you do" response ends mid-sentence or mid-list.

**Contract:** All capability list responses must end at a complete sentence
or a complete list item. Never truncate mid-bullet.

**Test:** The last character of the response must be `.`, `!`, `?`, `)`,
or end with a complete word, not `—` or `,`.

---

### RS-3 — Response opening: no filler openers

**Contract:** All responses begin with content, never with:
- "Okay."
- "Sure!"
- "Absolutely."
- "Of course."
- "Great question."

**Note:** Already fixed in conversation_router.py (MICRO_ACK emptied)
as part of slice 1.

---

### RS-4 — Fallback response: concise, no dead-end suggestions

**Contract:** When intent is unclear, the fallback must be ≤ 2 sentences
and must not suggest a capability that isn't fully working.

Current: `"Not sure what you mean — try: "what's the news", "check the
weather", or "what can you do"."`

This is correct. Do not add "draft an email" until Cap 64 has inbox access.

---

## Open items NOT in this contract

These are noted but require investigation before a contract can be written:

| Item | Why deferred |
|---|---|
| Search widget not appearing in chat | Needs live WS session debug — widget confirmed in P4 cert, not in live chat |
| Capability response truncates mid-sentence | Root cause unknown — may be formatter, may be response length limit |
| "tell me more" with prior context | With context this should work — needs separate test |

---

## Verification approach

For each routing contract:
- Unit test in `test_conversation_router.py` or a new
  `test_governor_mediator_contracts.py`
- Assert correct `capability_id` or `needs_clarification: true`
- Assert clarification prompt contains expected orienting question

For each response-shape contract:
- Check `response_formatter.py` strips governance language
- Check capability list response text does not contain forbidden phrases
- Add assertion to existing formatter tests where applicable

---

## Implementation order (recommended)

1. **RC-7** (help me) — one-line router change, high impact
2. **RC-2, RC-3, RC-5, RC-6** (context-free follow-ups / confusion) — group
   as "ambient clarification" patterns in `governor_mediator.py`
3. **RC-4** ("what should I do today") — remove from search heuristics,
   add clarification
4. **RC-1** ("open my email") — route to Cap 64 setup_required path
5. **RS-2** (capability list truncation) — diagnose, then fix in brain_server
