# Current Stage Guide — Stages 3, 4, 5, and 6
Updated: 2026-05-03

## What This File Is
A plain-language explanation of what Stages 3, 4, 5, and 6 mean in human terms.

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

**Proven by:** tests and `docs/demo_proof/daily_operating_baseline/MEMORY_LOOP_PROOF.md`

---

## Stage 4 — Context Pack

**What it means in plain language:**
Before Nova answers a question that draws on your memory, search results, or project state,
it now assembles a clean, labeled bundle called a Context Pack.

**What is live:**
- Context Pack is wired into `general_chat_runtime.py`
- Budget enforcement, source labels, stale/conflict detection, and authority ranking are active
- Context Pack cannot execute or authorize anything

---

## Stage 5 — Brain Mode Contracts

**What it means in plain language:**
Nova reasons under explicit mode contracts with strict boundaries.

**What is live:**
- Brain mode is classified every turn
- BrainTrace is recorded (non-authorizing, no chain-of-thought exposure)

**What is NOT yet live:**
- Brain mode is not visible per-turn in UI

---

## Stage 6 — Runtime Wiring and Routine Surfaces

**What it means in plain language:**
The system foundation is now wired. Stage 6 introduces routines built on top of it.

**What is working now:**
- Context Pack + Brain Mode are wired into runtime
- Daily Brief RoutineGraph v0 exists (non-authorizing)
- Plan My Week routine exists:
  - generates a structured plan
  - records approval decisions
  - produces receipts
  - does NOT execute real-world actions

**What is NOT happening:**
- No automation is triggered from routines
- Approval does not execute tasks

**What comes next (corrected):**
- Build a visible workflow layer (Daily Operator / business workflow demo)
- Surface Brain Mode, Context Pack, and Routine outputs in UI
- Introduce governed workflow workspace shell

---

## What These Stages Actually Mean

You now have:
- governed memory
- bounded context assembly
- structured reasoning modes
- non-authorizing routines

You do NOT yet have:
- automated workflows
- execution from plans
- visible workflow UI
- end-to-end product experience

---

## Reality Summary

Nova is now a governed reasoning + workflow substrate.

It is not yet a fully usable daily workflow product.
