# Current Priority

Current priority:

```text
No active priority lock. Everyday UX Friction is closed.
```

Status:

```text
CLOSED — final merge PR #140 / closeout doc PR #144 / 2026-05-11
```

Closeout doc: `docs/PROOFS/Everyday-UX/EVERYDAY_UX_FRICTION_CLOSEOUT_2026-05-11.md`

Priority lock (archived): `docs/status/ACTIVE_PRIORITY_LOCK_2026-05-10_EVERYDAY_UX_FRICTION.md`

The question that drove this workstream:

```text
Can a normal person use Nova every day without confusion?
```

Answered: 7 friction points resolved, 12 phrases newly routed, RC-7 normalization-layer bug
fixed, full-pipeline test methodology added (98 assertions). See closeout doc.

Cap 16 `governed_web_search` remains certified and locked (2026-05-10, P1–P5, 60 tests).

---

## Deferred follow-ups (open GitHub issues — not active priority)

```text
#141 — Search widget not surfacing in live WebSocket sessions
#142 — RS-2 capability list truncation (context-length dependent)
#143 — "tell me more" with prior context — session-state-aware test needed
```

Each needs its own scoped investigation before it becomes an active priority.

---

## Next recommended (not active without its own reviewed lock)

```text
Interface Personality Layer MVP
— response shaping only; no tools, no execution, no memory writes
```

Do not begin without a reviewed priority lock for that specific branch.

---

## Queued / planned (not active without their own lock)

```text
ui/simplify-dashboard-core-navigation — queued UI implementation (needs own lock)
Cap 64 P5 — paused (needs own lock)
```

Do not begin either without a reviewed priority lock for that specific branch.

---

## Completed recent branches

```text
proof/cap-16-certification-lock       — Cap 16 governed_web_search LOCKED (P1–P5) — 2026-05-10
docs/ui-simplification-inventory      — docs-only / queued UI inventory
docs/proof-infrastructure-closeout-review
test/non-search-widget-fuzzing
test/dashboard-event-replay-harness
```

---

## Context carried forward

Trust Review Card MVP is merged and closeout-reviewed as display-only, non-authorizing,
and follow-ups tracked. It renders existing request-understanding review-card state as a
visible non-action receipt surface; it does not authorize, confirm, dispatch, mutate state,
call capabilities, call GovernorMediator, call OpenClaw, add browser/computer-use, add
external writes, or create autonomous workflows.

The Web/News/UI proof lock is qualified closed. Browser Use screenshot/click-path proof,
high-frequency browser event replay, broader visual UI proof, deeper widget-specific fuzzing,
and timeline-drift fixtures are carried forward as proof debt, not as approval for
browser/computer-use expansion.

Browser Use visual capture recovery was attempted and remains blocked/setup-required because
the Browser Use / Node REPL path fails before JavaScript execution with
`failed to write kernel assets: The system cannot find the path specified`.
This is proof-infrastructure debt, not Nova runtime authority.

---

## Preserved no-authority boundaries

Do not add capabilities, expand OpenClaw, add browser/computer-use, add external writes,
add autonomous workflows, or use direct Cap 63 shortcuts based on any queued UI work.

Do not jump to Cap 64 P5, Shopify write work, OpenClaw browser automation, broad advanced
features, scheduler/installer work, external-write workflows, richer receipt work, or
browser/computer-use expansion.

This file is a working agent context note. Exact runtime truth still comes from code and
generated runtime docs. AGENTS.md governs active priority.
