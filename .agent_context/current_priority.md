# Current Priority

Current priority:

```text
UI simplification inventory
```

Status:

```text
inventory written / classify-only / no runtime changes
```

Trust Review Card MVP is merged and closeout-reviewed as display-only, non-authorizing, and follow-ups tracked. It renders existing request-understanding review-card state as a visible non-action receipt surface; it does not authorize, confirm, dispatch, mutate state, call capabilities, call GovernorMediator, call OpenClaw, add browser/computer-use, add external writes, or create autonomous workflows.

The Web/News/UI proof lock is qualified closed. Browser Use screenshot/click-path proof, high-frequency browser event replay, broader visual UI proof, deeper widget-specific fuzzing, and timeline-drift fixtures are carried forward as proof debt, not as approval for browser/computer-use expansion.

Browser Use visual capture recovery was attempted and remains blocked/setup-required because the Browser Use / Node REPL path fails before JavaScript execution with `failed to write kernel assets: The system cannot find the path specified`. This is proof-infrastructure debt, not Nova runtime authority.

Completed most recent branch:

```text
docs/ui-simplification-inventory
```

Prior completed branches:

```text
docs/proof-infrastructure-closeout-review
test/non-search-widget-fuzzing
test/dashboard-event-replay-harness
```

Next branch:

```text
ui/simplify-dashboard-core-navigation
```

Near-term focus:

1. UI simplification inventory is complete and product-direction corrected.
2. Target: Start + Chat + News + CRM + Settings. Home/Memory/Workspace/Trust/Policy/Agent fold out of
   top-level nav.
3. CRM is future-facing/read-only/setup-required — no write actions.
4. Next: implement in ui/simplify-dashboard-core-navigation.
5. After implementation: proof/live-manual-ui-verification — operator walks simplified UI and records results.
6. Preserve no-authority boundaries: no new capability, no OpenClaw expansion, no browser/computer-use
   capability, no external writes, no autonomous workflows, no direct Cap 63 shortcut.

Do not jump to Cap 64 P5, Shopify write work, OpenClaw browser automation, broad advanced features, scheduler/installer work, external-write workflows, richer receipt work, or browser/computer-use expansion.

This file is a working agent context note. Exact runtime truth still comes from code and generated runtime docs.
