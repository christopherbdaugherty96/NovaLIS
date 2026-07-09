# 01 — Project Truth (what Nova is intended to be)

**Status: current.** This is intent and product definition, not a claim about what runs today.
For what runs today see [02_RUNTIME_TRUTH.md](02_RUNTIME_TRUTH.md).

## Source of record

- [`../product/PRODUCT_DEFINITION.md`](../product/PRODUCT_DEFINITION.md) — canonical "why" and
  "what". Stable; changes rarely. Everything below summarizes it.

## The definition, in short

- **Mission:** Nova should answer the first important question you have each day before you
  have to ask it.
- **Purpose:** reduce uncertainty. If something does not reduce uncertainty, it is probably not
  a priority.
- **Identity:** an awareness engine that helps you know what matters, converse about it, and use
  tools only when awareness changes what should happen next — asking before it acts.
- **Objective function:** "help me make the next better decision" — deliberately different from
  an assistant's "answer my question" or an agent's "complete my task".

## Shape the user sees

```text
Awareness      (what changed / what matters?)
    ↓
Conversation   (what do you want to know?)
    ↓
Capabilities   (how do we accomplish it?)   ← hidden Decision Engine decides which tools matter
```

Governance (permissions, memory, ledger, registry, queue, audit) sits **below the line**: it
supports the experience, it does not define it. Its one visible exception is legibility —
receipts, "why am I recommending this", and the approval moment before any action.

## Core principles that constrain every feature

- **Intelligence is not authority.** Intelligence proposes, Nova governs, the user decides.
- **Trust classes:** Fact, Reasoning, Inference — never present inference as fact.
- **Evidence rule:** build only what observed behavior proves is missing.
- **Decision / app-elimination / decision-relevance filters** decide what belongs.

## Phase framing (product-level, not runtime)

- Phase 1 — Can Nova work? Complete.
- Phase 2 — Can Nova be trusted? Complete.
- Phase 3 — Can Nova become a habit? **Current.** The input now is observed daily use, not more
  building.

> Note: `PRODUCT_DEFINITION.md` uses product-level phase framing (1–3). The generated runtime
> doc uses an engineering phase matrix (3.5–9) for the execution spine. These are two different
> numbering schemes for two different things; they are not in conflict. See
> [02_RUNTIME_TRUTH.md](02_RUNTIME_TRUTH.md).
