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

> **Nova is an awareness engine that helps you know what matters, converse naturally about it,
> and use tools only when awareness changes what should happen next — asking before it acts.**

Not a chatbot, not a dashboard, not an agent. Intelligence proposes, Nova governs, you decide.
Personality may increase initiative, never authority.

**Objective function (the moat).** Assistants optimize *"answer my question."* Agents optimize
*"complete my task."* Nova optimizes *"help me make the next better decision."* That is a
different objective function, and it is what keeps Nova out of the crowded task-first lane.
Everything is subordinate to it: facts inform decisions, reasoning explains them, inference
suggests them (honestly, with uncertainty), capabilities execute them.

**User-facing shape (three visible layers):**

```text
Awareness      (what changed / what matters?)
    ↓
Conversation   (what do you want to know?)
    ↓
Capabilities   (how do we accomplish it?)   ← with a hidden Decision Engine deciding
                                              which tools matter, or that none do
```

**Governance is infrastructure, not product.** Governance, permissions, memory, ledger,
capability registry, policies, execution queue, and audit sit *below the line* — they support
the experience, they do not define it. A user should never think "I'm using the governance
layer" any more than they think "I'm using TCP/IP." The one exception that stays visible is
governance's **legibility** — receipts, "why am I recommending this," and the approval moment
before any action. Good infrastructure disappears; the trust it produces does not.

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

## Trust classes — epistemic honesty (core principle)

> **Nova never presents inference as fact. It distinguishes what it knows, what it can derive,
> and what it believes.**

This extends the honesty rule (never fabricate; "not connected" over invented data) into a
positive stance. Three trust classes, each shown differently:

1. **Fact** — objective, no confidence needed. *"Your attorney emailed at 8:13."*
2. **Reasoning** — a deterministic, inspectable combination of facts. *"Because traffic is
   delayed and rain is expected, I'd leave 15 minutes earlier."* (Its silent assumptions —
   your route, that the appointment is firm — must be surfaceable, not hidden.)
3. **Inference** — a learned model that is sometimes wrong. Must show confidence and invite
   correction. *"You usually review GitHub before email on Tuesdays. Confidence 61% — correct
   me if I'm wrong."* Inference lives **beside** awareness, not inside it, and inherits the
   strongest governance: advisory, inspectable, correctable, never silent.

Known live gap: today's weather line ("rain expected") presents a *forecast* as a *fact*. The
Fact class needs a seam — observed fact vs reported forecast vs Nova's own inference — a
Phase-4 refinement a morning will surface, not a build on spec.

## Governing filters (apply to every future feature)

- **Decision filter:** "Does this reduce the number of decisions Chris makes today? If yes it
  belongs; if no — even if impressive — it waits."
- **App-elimination metric:** "What's the next capability that eliminates another app from my
  morning?" (weather, news, calendar each eliminated one; Gmail would eliminate a fourth).
- **Decision-relevance filter:** "Does this change what Chris should decide or do?" Awareness
  that does not change a decision is noise (this is what stops Nova becoming a notification
  aggregator). "Know" counts only as *know in order to decide or do* — knowing for its own sake
  does not qualify.
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

**Awareness grows in three tiers** (the interface stays stable; only awareness deepens):

1. **Passive** — what Nova notices unasked (weather, calendar, email, news, GitHub, Shopify).
2. **Contextual** — facts combined *because of a question* ("should I leave?" fuses weather +
   traffic + calendar + location). This is context orchestration, not tool orchestration, and
   it is the single hardest thing in the vision — where personal-assistant efforts actually
   stall.
3. **Predictive** — learned patterns ("you forget expense reports after travel"). A different
   *risk class*, not a richer version: it is the gated learning layer, it can be confidently
   wrong, and it must be built last and shown as Inference (see Trust classes), never as fact.

Parallel truth: **Conversation is not a finished layer.** Live verification (2026-07-07) put it
at the weakest — multi-turn context ~61%, freeform LLM cancelled on CPU (#227). If awareness
outgrows conversation, richer awareness gets trapped behind friction expressing what you want.
Conversation remains active development, gated on evidence like everything else.
