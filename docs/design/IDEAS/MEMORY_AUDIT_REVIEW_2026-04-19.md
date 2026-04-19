# Memory Audit + First Fix Pass — Executive Review

**Date:** 2026-04-19
**Status:** Reference — use to guide next memory work

---

## Executive Truth

> Nova's storage layer is more mature than its retrieval/use layer.

That's a common and important maturity gap in AI systems. Saving data is easy; using it intelligently and safely is harder.

---

## What Was Found

### 1. Nova has multiple memory systems, not one

Four separate stores with distinct purposes:

- Governed Memory
- User Memory
- Nova Self-Memory
- Quick Corrections

That architectural separation is a good sign. It distinguishes:

- explicit durable facts
- user preferences
- relational/session context
- corrections feedback

Stronger than one giant memory blob.

---

### 2. Governed Memory is structurally strong, but underused in conversation

Explicit saved memories are written safely and richly structured, but were not automatically surfaced into chat context.

Users expect:

> If I told you to remember something important, it should help later.

If memory exists but doesn't influence interaction, it feels fake. That's a major UX gap.

---

### 3. User Memory is the most "alive" memory path

Lightweight user preferences and personal details are injected into prompts every turn. The least complex memory is currently the most operationally valuable.

Common in evolving systems.

---

### 4. Self-memory write path had dead potential

Self-memory had read structures but unwired write methods. The architecture anticipated richer continuity — the runtime behavior hadn't caught up.

- Bad architecture? No.
- Incomplete wiring? Yes.

---

## What Was Shipped

### `record_topic()` is now wired into conversation flow

After successful responses, Nova now extracts query topics and stores recurring themes.

Over time Nova builds actual topic patterns instead of an always-empty self-memory layer.

Right kind of first fix:
- Low risk
- Additive
- Measurable
- Doesn't destabilize core behavior

### Why this was the right first fix

Didn't attempt:
- Full semantic retrieval
- Autonomous memory summarization
- Complex relationship inference
- Giant memory rewrite

Instead: make one dead path alive. That's disciplined engineering.

### Documentation added

`docs/design/MEMORY_SYSTEM_REFERENCE.md` — complete verified reference covering all four stores, write/read paths, what's wired vs dead, atomic write pattern, scoring table, and known gaps.

---

## Remaining High-Value Next Steps (Priority Order)

### 1. Governed memory retrieval into conversation

Biggest user-facing win. Even simple top-N relevant retrieval would help. (Note: confirmed this IS already wired via `_select_relevant_memory_context()` in `brain_server.py` — but surfacing visibility to users remains an opportunity.)

### 2. Session summary hook

When sessions end, generate bounded summaries. Useful for continuity across sessions.

### 3. Quick corrections consumer

Corrections are stored but never used. Finish the loop or remove it.

Options:
- Inject recent uncorrected items as context hints at session start
- Surface in memory dashboard for user review
- Remove if not prioritized

### 4. Relationship insight capture

Careful and conservative only. Can get messy fast if overdone.

---

## Strategic Meaning for Nova

Nova is shifting from:

> memory as storage feature

toward:

> memory as behavioral infrastructure

That's a meaningful milestone.

---

## One Sentence Truth

**You discovered Nova's memory wasn't broken — it was partially dormant, and this pass successfully woke up one of the right parts without overengineering the rest.**
