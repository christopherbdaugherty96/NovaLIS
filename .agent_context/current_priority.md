# Current Priority

Current priority:

```text
Everyday UX Friction + Live Daily Workflow Testing
```

Status:

```text
active — priority lock set 2026-05-10
```

Priority lock: `docs/status/ACTIVE_PRIORITY_LOCK_2026-05-10_EVERYDAY_UX_FRICTION.md`

Test plan: `docs/PROOFS/Everyday-UX/LIVE_DAILY_WORKFLOW_TEST_PLAN_2026-05-10.md`

The question driving this workstream:

```text
Can a normal person use Nova every day without confusion?
```

Cap 16 `governed_web_search` is certified and locked (2026-05-10, P1–P5, 60 tests). This
workstream was selected from a clean base after Cap 16 locked (no open PRs at selection time).

---

## Planned branch sequence

```text
PR 1 (active): docs/everyday-ux-friction-priority-lock — priority lock + test plan (docs-only)
PR 2:          proof/everyday-ux-live-workflow-baseline — live baseline evidence
PR 3:          docs/nova-conversation-response-contract — response shape contract
PR 4:          fix/everyday-ux-friction-slice-1 — first small implementation slice
```

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
