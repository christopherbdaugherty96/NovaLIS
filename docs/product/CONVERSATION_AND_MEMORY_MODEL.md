# Conversation and Memory Model

Last reviewed: 2026-04-28

This document explains how Nova uses conversation, context, memory, receipts, and runtime truth without turning any of them into execution authority.

## Short Version

- The current message is what the user just asked.
- Session context helps Nova understand follow-ups inside the current interaction.
- Mode and tone affect response style and routing behavior; they do not approve actions.
- Memory can support continuity; it is not permission to execute.
- Ledger entries and action receipts record governed actions; they are not personal memory.
- Runtime truth describes the current system surface generated from implementation.
- Stored plans and future docs do not run themselves.
- Real actions still require registered capabilities, governance checks, execution boundaries, confirmation where required, and receipt/ledger evidence.

Core rule: **intelligence is not authority.**

---

## Layer 1 — Current Message

The current message is the user's immediate request.

Nova may answer directly when the request is low-risk conversation, explanation, planning, summarization, or drafting that does not cross an execution boundary.

The current message alone does not authorize external effects.

---

## Layer 2 — Session Context

Session context helps Nova understand the current conversation.

Examples:
- follow-up references like "that one"
- recently discussed options
- active conversation mode
- recent user intent

Session context can improve interpretation, but it cannot bypass governance.

---

## Layer 3 — Mode and Tone

Mode and tone affect how Nova responds.

They may shape whether the assistant is casual, analytical, direct, explanatory, or work-focused.

They do not grant permission to execute actions.

---

## Layer 4 — Memory and Continuity

Memory is for continuity, not authority.

A memory layer may help Nova remember preferences, recurring context, topic state, or prior user-approved notes if implemented and enabled.

Memory must not:
- authorize actions
- bypass confirmation
- send email
- write to Shopify
- run background tasks by itself
- override capability boundaries
- silently turn a future plan into a live action

When memory behavior is unclear, trust the implementation and generated runtime truth over roadmap language.

---

## Layer 5 — Topic / Story / Thread Context

Some Nova surfaces track story, topic, or thread context for better continuity.

This is still reasoning support. It is not execution authority.

A tracked topic may help Nova summarize or explain what changed. It should not cause Nova to act unless a governed capability path explicitly handles the action.

---

## Layer 6 — Governed Action Boundary

When a request involves a real action, the request must route through Nova's governed action path.

The exact implementation can evolve, but the authority model should preserve this shape:

```text
User request
→ conversation / routing / intent handling
→ GovernorMediator
→ Governor / CapabilityRegistry
→ confirmation when required
→ ExecuteBoundary / executor
→ LedgerWriter
→ action receipt / trust receipt surface
```

If a capability is not registered or not allowed, it should not execute.

---

## Layer 7 — Ledger And Receipt Surfaces

The ledger records governed action events.

The Trust Receipts API and action receipt surfaces make those events easier to inspect.

Receipts are evidence of what happened; they are not memory instructions and they do not grant future permission.

Current receipt-related truth:
- `/api/trust/receipts` exposes recent receipt-worthy governed-action events.
- `/api/trust/receipts/summary` exposes a compact receipt summary.
- Dashboard Action Receipts should be treated as the visible UI surface when available; the API remains the direct proof source.
- The fuller Trust Review Card / Trust Panel experience remains future work.

---

## Layer 8 — Runtime Truth

Generated runtime truth docs describe the current runtime surface.

Use these for exact active capability and governance status:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/GOVERNANCE_MATRIX.md`

Human docs should link to generated truth instead of copying unstable exact counts everywhere.

---

## Layer 9 — Future Plans and Stored Documents

Future docs, TODO docs, design plans, and roadmap files are planning material.

They do not mean the feature exists today.
They do not authorize execution.
They do not create a background agent.

Current capability truth comes from implementation, tests, generated runtime docs, and capability verification records.

---

## Practical Examples

### Email Draft

Cap 64 can create a local mail client draft through `mailto:` after confirmation.
Nova does not use SMTP, access an inbox, or send email autonomously.
The human reviews and sends manually.

### Shopify Intelligence

Cap 65 is read-only Shopify reporting/intelligence.
It requires Shopify environment variables and credentials.
It must not be described as product editing, order editing, fulfillment, refunds, or customer messaging unless the implementation actually adds governed write capabilities later.

### Scheduler / Background Loop

Any scheduler or background-loop surface must remain gated, bounded, settings-controlled, and unable to bypass governance.
Background planning is not broad hidden autonomy.

---

## What Memory Cannot Do

Memory cannot:
- authorize actions
- bypass confirmation
- silently execute stored plans
- grant network access
- send email
- write to Shopify
- approve purchases
- perform account changes
- replace the ledger
- replace generated runtime truth

---

## Where To Inspect Each Layer

| Layer | Where to look |
|---|---|
| Product overview | `README.md`, `START_HERE.md` |
| First-use flow | `docs/product/FIRST_5_MINUTES.md`, `docs/product/TRY_THESE_COMMANDS.md` |
| Current user-facing status | `docs/product/WHAT_WORKS_TODAY.md`, `docs/product/KNOWN_LIMITATIONS.md` |
| Runtime truth | `docs/current_runtime/` |
| Capability proof | `docs/capability_verification/`, `docs/product/CAPABILITY_SIGNOFF_MATRIX.md` |
| Trust and receipts | `docs/product/TRUST_REVIEW_CARD_PLAN.md`, `docs/product/PROOF_CAPTURE_CHECKLIST.md` |
| Current tasks | `docs/todo/ACTIVE_TODO.md` |
| Future direction | `docs/future/` |

---

## Bottom Line

Conversation and memory help Nova understand.

Governance decides whether Nova may act.

Receipts prove what happened.

Runtime truth shows what exists.

Future docs describe direction, not current authority.
