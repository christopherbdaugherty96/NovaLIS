# Nova Brief-Phrasing Intent Lane — Plan

Date: 2026-07-14

Status: **Implemented in the working tree on owner go (2026-07-14). Uncommitted, pending owner
review and a live browser smoke before merge.** Original status: planning artifact awaiting approval.

Implementation landed:
- `nova_backend/src/conversation/brief_intent_resolver.py` — pure resolver (31 unit tests).
- Guard block in `nova_backend/src/websocket/session_handler.py` (after arithmetic, before the
  exact-match capability branches) + import.
- `nova_backend/tests/conversation/test_brief_intent_resolver.py`.
- Verified: 972 passed across conversation + phase45 (941 prior + 31 new), no regressions. The
  resolver is unit-tested; the guard *wiring* is covered only by no-regression + parse check —
  a live drive of "is it hot out?" → weather is still pending.

Owner-agreed target: hybrid + disclosed, deterministic-first, scoped to weather / news / calendar.

This is a narrow, testable first slice of the broader
[`NOVA_CONVERSATION_COHERENCE_LAYER_PLAN.md`](NOVA_CONVERSATION_COHERENCE_LAYER_PLAN.md). That plan
targets meta-coherence (project-status / next-step / paused-work / memory-vs-docs). This lane
targets one thing only: **recognizing common morning phrasing for already-supported brief
capabilities, and asking a clarification when uncertain instead of silently falling through.**

This document is a plan, not runtime truth. Live status remains governed by `docs/current_runtime/`
and the code.

---

## 1. Why this lane (evidence, not conclusion)

Nova routes brief capabilities on the WebSocket hot path by **near-exact string match**, not by
meaning. From live code:

- Weather fires only when `lowered in {"weather", "weather update", "current weather"}` or matches
  `^weather in <place>$` — [session_handler.py:1290](../../nova_backend/src/websocket/session_handler.py).
- Calendar fires on an exact-string set (`"agenda for today"`, `"agenda for tomorrow"`, and the
  peers above it) — [session_handler.py:2455](../../nova_backend/src/websocket/session_handler.py).
- News fires on `is_headline_summary_request(...)` and `lowered in {"news","headlines","latest
  news","top news"}` — [session_handler.py:1199](../../nova_backend/src/websocket/session_handler.py)
  and [:1211](../../nova_backend/src/websocket/session_handler.py).

Any phrasing without the exact token misses every branch and falls through to the slow advisory
LLM path at [session_handler.py:4347](../../nova_backend/src/websocket/session_handler.py). That
fall-through is the same one whose display we corrected in the Morning 3 `status`-frame fix — the
render is now honest, but Nova still does not *understand* the phrasing.

Observed Morning 3 misses that this lane must fix (see
[`docs/observation/MORNING_03_2026-07-14.md`](../observation/MORNING_03_2026-07-14.md)):
`anyhting on my schedule?`, `theres heat alerts for outside, how should i stay cool?`.

**Conclusion:** the gap is an intent-normalization gap on the hot path, one layer above the
per-capability handlers. It is fixable deterministically without a model and without new authority.

---

## 2. Goal and non-goals

**Goal.** For weather, news, and calendar only: map common natural phrasings onto the *existing*
governed capability path; when confidence is medium, ask a scoped clarification; when confidence is
low, change nothing.

**Out of scope for this pass (hard boundaries):**

- Semantic / model / embedding classifier of any kind.
- Broadening general web search or general Q&A.
- Gmail / tasks / traffic or any not-yet-built capability.
- Any new execution authority, connector, or capability lock/signoff.
- Rewriting the conversation router or `session_handler.py` broadly.

This lane is Phase-3-aligned: it adds **no autonomy, no execution surface, and no model-inference
router of authority.** It only helps Nova recognize what the user is asking for among things it can
already do.

---

## 3. Design

### 3.1 Shape

Add one small, pure, deterministic module — proposed
`nova_backend/src/conversation/brief_intent_resolver.py` — and consult it from a **single new guard
block near the top of the existing hot-path cascade**, after the time/arithmetic checks and before
the exact-match capability branches (i.e., just before
[session_handler.py:1199](../../nova_backend/src/websocket/session_handler.py)).

The resolver does not mutate user text and does not call any capability itself. It returns a small
value object:

```
BriefIntent:
  capability: "weather" | "news" | "calendar" | None
  confidence: "high" | "medium" | "low"
  clarification: str | None        # populated only for medium
  matched_terms: list[str]         # for receipts / debugging
```

The guard block interprets that object and reuses paths that already exist — it invents no new
capability call:

- **high** → dispatch through the same `invoke_governed_text_command(governor, <canonical>, ...)`
  the existing branch uses (`"weather"`, `"news"`, or a calendar canonical such as
  `"agenda for today"`). Governed path unchanged; only the *trigger* is widened.
- **medium** → `send_chat_message(...)` with the clarification, then end the turn (`continue`). No
  capability fires. This is a normal chat frame, not a `status` frame.
- **low** / `None` → do nothing; the turn proceeds to the existing cascade exactly as today.

Carrying an explicit intent object (rather than rewriting `command_text`) is deliberate: text
rewriting would pollute logs/receipts and risk mis-hitting unrelated branches. The tag is isolated
and testable.

### 3.2 Confidence tiers (deterministic rules)

- **HIGH** — utterance contains a brief-domain signal term (from the v1 lexicon below), is
  question/status-shaped, contains **no authoring/command verb** (see 3.4), and is not clearly
  another domain. Example: `is it hot out?` → weather; `anything on my schedule?` → calendar.
- **MEDIUM** — an ambiguous preparation phrase that plausibly spans two or more brief domains, e.g.
  `do I need to prepare?`, `what should I do about today?`. → clarification:
  `"Do you mean your calendar, the weather, or the news?"`
- **LOW** — no brief-domain signal, or an authoring/command verb is present. Leave the existing
  advisory/general path untouched.

### 3.3 v1 lexicon (owner-supplied; the entire matcher for the first pass)

- **Weather:** `hot`, `cold`, `rain`, `jacket`, `stay cool`, `outside`, `heat alert`, `umbrella`
- **Calendar:** `anything on`, `what am I doing`, `plans`, `free`, `busy`, `schedule`, `after that`
- **News:** `anything happening`, `headlines`, `what should I know`, `what matters today`

These are the complete v1 surface. New terms are added only with a corresponding test. No wildcard
expansion, no stemming beyond simple lowercase/substring, no synonym generation.

### 3.4 The theft-guard (this lane's biggest risk)

The failure mode to prevent is a product/creation prompt being **stolen** by brief routing, e.g.
`build a weather page`, `design a news feed`, `make a calendar component`. Before any HIGH match,
the resolver returns LOW if the utterance contains an authoring/command intent — verbs such as
`build`, `make`, `create`, `design`, `implement`, `code`, `write`, `add`, `generate`, `draft`
paired with an artifact noun (`page`, `app`, `site`, `widget`, `component`, `feature`, `screen`,
`mockup`). This reuses the spirit of `ConversationRouter.COMMAND_PREFIXES`. The theft-guard is
tested as a first-class negative matrix, not an afterthought.

### 3.5 Interaction with existing paths

- **Grounded-brief follow-up.** When news context is already loaded, `what should I know today?`
  should prefer the existing grounded follow-up path
  ([`answer_grounded_brief_followup`, session_handler.py:4310](../../nova_backend/src/websocket/session_handler.py))
  over a fresh fetch. The resolver's news branch must defer to loaded-context grounding when present.
- **Schedule truth guard.** Calendar routing must continue to respect
  `schedule_commitment_guard` — the lane must never fabricate commitments; if no sourced calendar
  context exists, the guarded refusal still wins.
- **Status-frame fix.** Medium-confidence clarifications are ordinary chat messages. This lane must
  not emit `type:"status"` frames and must not reintroduce the Morning 3 misrender.

---

## 4. Test matrix (tests-first, before any wiring)

Proposed `nova_backend/tests/conversation/test_brief_intent_resolver.py` plus a hot-path
integration check.

**Positive (HIGH → capability):**

- `is it hot out?` → weather
- `do I need a jacket?` → weather
- `theres heat alerts for outside, how should i stay cool?` → weather (grounded follow-up)
- `anyhting on my schedule?` → calendar (typo-tolerant via existing InputNormalizer)
- `am I free after that?` → calendar
- `what's happening today?` / `anything happening?` → news
- `what should I know today?` with loaded news context → grounded brief/news follow-up

**Clarification (MEDIUM → ask, no capability fires):**

- `do I need to prepare?` → `"Do you mean your calendar, the weather, or the news?"`
- `what should I do about today?` → same clarification

**Negative / theft-guard (must NOT route to a brief capability):**

- `build a weather page` → LOW (product/creation, not weather)
- `design a news feed component` → LOW
- `make a calendar widget` → LOW
- `write a blog post about the heat wave` → LOW

**Regression (must stay green):**

- Existing exact triggers (`weather`, `news`, `agenda for today`, …) still route unchanged.
- Existing grounded-brief follow-up tests unchanged.
- No `type:"status"` frame emitted on any clarification turn.
- Negative-authority: resolver never calls a governor capability directly, never changes a lock,
  never issues an OpenClaw envelope. (Mirror the negative tests in the coherence-layer plan.)

---

## 5. Success bar (owner-defined)

A good first pass is **not** "Nova understands everything." It is:

- The three morning-brief domains feel less brittle for common phrasing.
- Nova states what it thinks you meant when confidence is not high.
- No new execution surface.
- No model-router dependency.
- Existing grounded-brief and conversation tests stay green.

---

## 6. What this explicitly does not do

No GovernorMediator / ExecuteBoundary / NetworkMediator changes. No new capability, connector, or
lock/signoff. No model or provider dependency. No autonomy or background job. No broad rewrite of
`session_handler.py` or the conversation router — one new module plus one guard block.

---

## 7. Open questions for owner (pre-code)

1. **Module vs. router method.** New `brief_intent_resolver.py` module (recommended, isolated and
   unit-testable) vs. folding the logic into `ConversationRouter`? Recommendation: separate module.
2. **Calendar canonical.** Route HIGH calendar matches to `"agenda for today"` specifically, or add
   a neutral calendar canonical? Recommendation: reuse `"agenda for today"` to avoid a new token.
3. **Clarification memory.** Should a MEDIUM clarification remember the pending domain so a one-word
   reply (`weather`) completes it, or treat the reply as a fresh turn? Recommendation: defer
   remembering to a later slice; keep v1 stateless.

---

## 8. Approval gate

Implementation starts only on explicit owner "go." Suggested sequence when approved:

1. Write `test_brief_intent_resolver.py` (positive / clarification / theft / negative-authority).
2. Add `brief_intent_resolver.py` (pure, deterministic, no I/O).
3. Add the single hot-path guard block; run targeted + grounded-brief + conversation suites green.
4. Stop for owner review before merge. Then measure against the next mornings before widening scope
   (search / general Q&A / model layer remain parked).
