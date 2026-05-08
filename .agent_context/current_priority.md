# Current Priority

Current priority:

```text
Dashboard event replay harness / proof infrastructure only
```

Status:

```text
selected after Browser Use visual capture recovery remained blocked/setup-required
```

Trust Review Card MVP is merged and closeout-reviewed as display-only, non-authorizing, and follow-ups tracked. It renders existing request-understanding review-card state as a visible non-action receipt surface; it does not authorize, confirm, dispatch, mutate state, call capabilities, call GovernorMediator, call OpenClaw, add browser/computer-use, add external writes, or create autonomous workflows.

The Web/News/UI proof lock is qualified closed. Browser Use screenshot/click-path proof, high-frequency browser event replay, broader visual UI proof, deeper widget-specific fuzzing, and timeline-drift fixtures are carried forward as proof debt, not as approval for browser/computer-use expansion.

Browser Use visual capture recovery was attempted and remains blocked/setup-required because the Browser Use / Node REPL path fails before JavaScript execution with `failed to write kernel assets: The system cannot find the path specified`. This is proof-infrastructure debt, not Nova runtime authority.

Next branch:

```text
test/dashboard-event-replay-harness
```

Near-term focus:

1. Build deterministic dashboard event replay tests for existing UI behavior.
2. Cover repeated clicks, double submits, stale confirmation, rapid WebSocket messages, and duplicate-action prevention.
3. Preserve Browser Use visual capture as blocked/setup-required until the Node REPL/runtime asset issue is repaired.
4. Preserve no-authority boundaries: no new capability, no OpenClaw expansion, no browser/computer-use capability, no external writes, no autonomous workflows, no direct Cap 63 shortcut.

Do not jump to Cap 64 P5, Shopify write work, OpenClaw browser automation, broad advanced features, scheduler/installer work, external-write workflows, widget fuzzing, richer receipt work, or browser/computer-use expansion until the event replay harness branch is reviewed and merged or explicitly superseded.

This file is a working agent context note. Exact runtime truth still comes from code and generated runtime docs.
