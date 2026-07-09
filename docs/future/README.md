# Future Docs Guide

**Purpose:** Explain what future documents are for, how much authority they carry, and how they relate to Nova's live project state.

## Short Version

The `docs/future/` folder preserves direction.
It does not define current truth.

Use these sources in order of authority:
1. Running code
2. Generated runtime truth docs
3. Active TODO / current sprint docs
4. Future planning docs
5. Historical archives

## Ordering authority and how to read this folder

- The ordering authority for what comes next is
  `docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md` (lanes A–D + Horizon H1–H31). The older
  `ROADMAP.md` is **superseded for ordering** and kept only as reference.
- **A doc in this folder is reference until a lane in the July roadmap pulls it in.** Being
  filed here is not a promise, a release plan, or an active priority.
- To tell whether a given doc is active, parked, superseded, a fixture, or design history, use
  **`FUTURE_DOCS_MAP.md`** — it classifies the orphaned docs and names each one's intended home.

## Important Clarification (2026-05-03)

Some concepts described in this folder now have **implemented subsets**.

These include:
- Memory Loop (implemented, explicit, receipted)
- Context Pack (implemented and wired)
- Brain Mode / BrainTrace (implemented, non-authorizing)
- RoutineGraph v0 (implemented, non-authorizing)
- Plan My Week (implemented proposal + approval record)

Do not treat the future specifications as the current implementation.

The implemented system is a **partial realization** of these ideas, not full completion.

---

## Canonical Future Direction

- `NOVA_AURALIS_BIG_PICTURE_OPERATING_MODEL_2026-05-18.md` - future Nova/Auralis operating-model and measurement-spine direction.

- `ROADMAP.md` — historical phased expansion path; **superseded for ordering** by
  `NOVA_MASTER_ROADMAP_2026-07-05.md`.
- `NOVA_AGENT_STACK_RECOMMENDATIONS.md` — future governed agent-stack architecture direction.

## Brain, Memory, Learning, Routine, and Agent Stack Planning

These docs define future architecture direction. They are not live runtime capability claims:

- `BRAIN_HUMAN_GUIDE.md`
- `BRAIN_MEMORY_HUMAN_GUIDE.md`
- `NOVA_AGENT_STACK_RECOMMENDATIONS.md`
- `CONTEXT_PACK_SPEC.md`
- `LEARNING_LAYER_SPEC.md`
- `NOVA_SECOND_BRAIN_OBSIDIAN_RESEARCH_AND_IMPLEMENTATION_PLAN_2026-05-18.md`
- `ROUTINE_LAYER_SPEC.md`
- `DAILY_BRIEF_ROUTINE_SPEC.md`
- `GUARD_SYSTEM_SPEC.md`
- `TRACE_AND_OBSERVABILITY_SPEC.md`

---

## What Does Not Belong Here

Avoid treating this folder as:
- live feature proof
- implementation status
- current sprint authority
- release promises

---

## Why This Matters

Good future planning is useful.
Confusing future plans with current reality damages trust.

Nova should preserve ambition while staying honest about what exists now.
