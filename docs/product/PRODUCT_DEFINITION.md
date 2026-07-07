# Nova Product Definition

Canonical product definition — the "why" and "what" behind the architecture. Stable; changes
rarely. For what Nova *can do today* see `docs/capability_verification/CAPABILITY_INVENTORY.md`;
for ordering see `docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md`.

## Mission

> **Nova should answer the first important question you have each day before you have to ask it.**

Measurable and human. It grows from weather / news / calendar / email / business / reminders
without being defined by any one of them.

## Purpose

**Reduce uncertainty.** Not "answer questions," not "summarize," not "automate everything."
If something does not reduce uncertainty, it probably isn't a priority.

The single success metric (Phase 3): *Did Nova eliminate ONE uncertainty before you reached
for another app?* — not "replace Gmail," not "answer everything." One.

## Identity

A **decision operating system**, not a chatbot or dashboard. Personal butler at the interface
layer; governed runtime at the execution layer. Intelligence proposes, Nova governs, you
decide. Personality may increase initiative, never authority.

Architecture shape: **Reality → Awareness → Decision → Conversation.** Chat is a tool, not the
center; awareness is the center.

## Operating loop

```text
Reality -> Awareness -> Decision -> Action (only with approval) -> Observation -> Learning
```

Observation and Learning close the loop — that is how Nova improves without guessing.

## The five layers

1. **Core Engine** (complete, production quality) — governance, capability system, read-only
   execution, governed memory, runtime truth, capability locking, deterministic
   recommendations, honest degradation.
2. **Awareness** (good, verified) — weather, news, calendar, business priority.
3. **Business** (strong) — C1 decision surface: many trusted inputs → one recommendation.
4. **Personal** (incomplete) — Gmail, Google Tasks/Reminders, Traffic are absent (not broken).
5. **Automation** (future, correctly postponed) — acts only with approval.

## The decision engine (reusable foundation)

C1 completed **Version 1 of the decision engine**: deterministic · governed · honest ·
testable · explainable. The engine is the same whether the input is Auralis, weather, email,
or calendar — only the inputs change. Future surfaces reuse this engine.

## Governing filters (apply to every future feature)

- **Decision filter:** "Does this reduce the number of decisions Chris makes today? If yes it
  belongs; if no — even if impressive — it waits."
- **App-elimination metric:** "What's the next capability that eliminates another app from my
  morning?" (weather, news, calendar each eliminated one; Gmail would eliminate a fourth).
- **Evidence rule:** implementation earns the right to collect evidence; evidence earns the
  right to stay. Build only what observed behavior proves is missing.

## Phases

- **Phase 1 — Can Nova work?** Complete.
- **Phase 2 — Can Nova be trusted?** Complete (governance, verification).
- **Phase 3 — Can Nova become a habit?** *Current.* Engineering alone will not solve it; the
  input is observed daily use, not more building.

## Future architecture (captured, not built)

The **Awareness Item** engine: normalize every connector/memory/reminder/news/business signal
into one object (title / source / priority / urgency / time-horizon / est-time / confidence /
suggested-action / reason / blocked-by / category); every surface (morning brief / watch /
car / pager) becomes a filter + ranking over Awareness Items; OS-style interrupt levels;
adaptive relevance learned from behavior. Build **only after** observed use proves the need —
it earns its place, it is not built on spec.
