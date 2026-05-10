# Current Priority

Current priority:

```text
Awaiting reviewed priority lock — Cap 16 is complete and locked
```

Status:

```text
Cap 16 governed_web_search LOCKED 2026-05-10 (P1–P5 all pass, 60 tests)
No active workstream. A new reviewed priority lock is required before the next branch begins.
```

Cap 16 `governed_web_search` is fully certified and locked. All five phases passed:
P1 unit (16), P2 routing (17), P3 integration (19), P4 API (8), P5 live (FastAPI TestClient
with real BRAVE_API_KEY and real governor spine — basic search, natural phrasing, clarification
flow, and ledger events all verified). Lock applied 2026-05-10.

---

## Queued / planned (not active)

UI simplification inventory is complete and queued for a future implementation branch.
It does not become the active priority until a new reviewed priority lock authorizes the switch.

```text
Inventory branch: docs/ui-simplification-inventory (merged via PR #133)
Future implementation branch (queued): ui/simplify-dashboard-core-navigation
Target: Start + Chat / News / CRM / Settings
```

Do not begin ui/simplify-dashboard-core-navigation without a reviewed priority lock.

---

## Completed recent branches

```text
proof/cap-16-certification-lock       — Cap 16 governed_web_search LOCKED (P1–P5)
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
