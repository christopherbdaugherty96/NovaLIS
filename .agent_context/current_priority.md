# Current Priority

Current priority:

```text
Cap 16 search reliability and conversation/search proof
```

Status:

```text
active / AGENTS.md governs this — do not override with UI simplification work
```

Cap 64 P5 remains paused until the Cap 16 proof path is stable. See AGENTS.md.

---

## Queued / planned (not active)

UI simplification inventory is complete and queued for a future implementation branch.
It does not become the active priority until Cap 16 search reliability proof is stable
and a reviewed priority lock authorizes the switch.

```text
Inventory branch: docs/ui-simplification-inventory (merged via PR #133)
Future implementation branch (queued): ui/simplify-dashboard-core-navigation
Target: Start + Chat / News / CRM / Settings
```

Do not begin ui/simplify-dashboard-core-navigation until the active Cap 16 priority
lock is closed and a new reviewed priority lock is established.

---

## Completed recent branches

```text
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
