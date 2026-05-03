# Current Stage Guide — Stages 3, 4, 5, and 6
Updated: 2026-05-02

## What This File Is
A plain-language explanation of what Stages 3, 4, and 5 mean in human terms.

For the authoritative implementation status, see:
- `docs/status/CURRENT_WORK_STATUS.md`
- `docs/status/WORKFLOW_STAGE_ROADMAP_2026-05-02.md`
- `docs/todo/ACTIVE_TODO.md`

---

## Stage 3 — Memory Loop

**What it means in plain language:**
Nova can now remember things you tell it to remember, and it will tell you when it is using
that memory. You can also update or remove memories, and Nova will never reuse something you
deleted.

**What is working now:**
- `remember [content]` — saves a new memory item and shows you a receipt
- `review memories` — lists saved items with IDs so you can see what Nova knows
- `update memory [id]: [new content]` — replaces an existing item with a newer version
- `forget [id]` — removes an item permanently; Nova will not use it again
- `why-used` — explains which memory context is active and why each item was selected

**What is NOT happening silently:**
- Nova does not save memory unless you explicitly ask it to
- Nova does not act on memory — memory provides context only, not authority
- Forgotten items are gone from all read paths immediately

**Proven by:** 62 tests and `docs/demo_proof/daily_operating_baseline/MEMORY_LOOP_PROOF.md`

---

## Stage 4 — Context Pack

**What it means in plain language:**
Before Nova answers a question that draws on your memory, search results, or project state,
it now assembles a clean, labeled bundle called a Context Pack. This bundle has hard size
limits, source labels on every item, and checks for stale or conflicting information — before
any of it reaches Nova's reasoning layer.

**What it means for you as a user:**
- You will not get answers that quietly mix authoritative runtime truth with old guesses
- Nova knows which items are confirmed memory vs. candidates vs. runtime facts
- Nova knows when two items conflict and will flag it rather than picking one silently
- The pack cannot execute or authorize anything — it is read-only input to reasoning

**What is NOT yet live:**
- The Context Pack is implemented and proven, but is not yet wired into live prompt assembly.
  That wiring is Stage 5 and 6 work. Nova's live answers do not yet fully use the Context Pack
  pipeline every turn — that integration is still in progress.

**Proven by:** 69 tests and `docs/demo_proof/daily_operating_baseline/CONTEXT_PACK_PROOF.md`

---

## Stage 5 — Brain Mode Contracts

**What it means in plain language:**
Nova now operates under explicit mode contracts when it reasons. Each mode has a defined set
of things it can do, things it cannot do, and whether it is allowed to make changes to the
codebase.

**The seven modes:**

| Mode | Purpose | May change code? |
|------|---------|-----------------|
| brainstorm | Explore ideas freely | No |
| repo_review | Review and explain existing code | No |
| implementation | Write or modify code | Yes |
| merge | Integrate branches and close PRs | Yes |
| planning | Plan work and structure decisions | No |
| action_review | Review proposed or past actions | No |
| casual | Conversational, low-stakes answers | No |

**The key rule:**
Only `implementation` and `merge` may mutate the repo. Every other mode is prohibited from
doing so. This is enforced in code, not just described as intended behavior.

**What is NOT yet live:**
- Brain mode classification runs in code but is not yet surfaced in the UI.
  You cannot yet see which mode Nova is operating in during a live conversation.
  That UI surface is Stage 6 work.

**Proven by:** 85 tests and `docs/demo_proof/daily_operating_baseline/BRAIN_MODE_PROOF.md`

---

## What The Three Stages Add Up To

Stages 3, 4, and 5 together mean:

1. Nova can remember explicit things you ask it to remember, without silent autosave or
   hidden reuse.
2. When Nova draws on that memory, it assembles a governed, labeled bundle first — with
   hard limits, source labels, and stale/conflict checks.
3. When Nova reasons, it operates under a mode contract that says exactly what it is and is
   not allowed to do in that mode.

The core infrastructure for memory, context, and mode discipline is implemented and tested.

Stage 6 has begun — the first wiring is already live.

---

## Stage 6 — Routine Surfaces (Active)

**What it means in plain language:**
Nova's memory, context, and mode foundations are now connected to the live prompt path.
Stage 6 is about building the first visible routines on top of that foundation — starting
with a governed Daily Brief and an everyday workflow demo.

**What is working now (Stage 6 start):**
- Context Pack is wired into `general_chat_runtime.py` — every general-chat turn now enforces
  budget limits, source labels, stale/conflict detection, and authority ranking before memory
  reaches the prompt
- Brain mode is classified on every turn and a BrainTrace is recorded in session state
- Memory items confirmed by the user (source: explicit_user_save) are preferred over
  auto-extracted candidates — every turn, not just in tests

**What is being built next:**
- Daily Brief RoutineGraph v0 — a governed, non-authorizing daily brief backed by receipts
- Everyday workflow demo: plan my week from tasks, notes, calendar context, and priorities,
  with an approval boundary and a receipt

**What is NOT yet live:**
- Brain mode is not yet surfaced per-turn in the UI (classified and traced internally)
- Routine execution with real approval gates (next Stage 6 work)
- Memory UX beyond the conversational loop (dedicated page, export)
