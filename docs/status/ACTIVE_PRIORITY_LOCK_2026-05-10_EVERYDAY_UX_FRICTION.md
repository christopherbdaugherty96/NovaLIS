# Active Priority Lock — 2026-05-10 Everyday UX Friction

Status: active

Date selected: 2026-05-10

This is human-maintained priority guidance, not generated runtime truth.

Generated runtime docs and actual code remain authoritative if they conflict with this lock.

---

## Active Workstream

```text
Everyday UX Friction + Live Daily Workflow Testing
```

---

## Why This Workstream

Nova now has strong coverage in governance, capability proof, and deterministic dashboard
safety contracts. Cap 16 is locked. The proof infrastructure is closeout-ready. The Trust
Review Card is merged as a non-authorizing display surface.

The main remaining bottleneck is not certification:

```text
Can a normal person use Nova every day without confusion?
```

This lock exists to answer that question before selecting the next capability expansion.

---

## Scope

### In scope

- UI friction: labels, buttons, layout, navigation, dead chips, confusing states
- Conversational response quality: wording, tone, clarity, governance noise
- Clarification flow: is the clarification question useful, prompt, and clear?
- Blocked/setup-required state explanations: are they honest, short, and helpful?
- Degraded state recovery: does Nova tell the user something useful when a capability fails?
- Live daily workflow testing: run Nova as a normal user and record what happens

### Out of scope

No:

- new capabilities
- OpenClaw expansion
- browser/computer-use
- external writes
- autonomous workflows
- Shopify writes
- email sending
- hidden memory behavior
- personality simulation
- chain-of-thought exposure
- direct Cap 63 shortcut

The goal is not to make Nova more human. The goal is:

```text
clearer, smoother, less confusing, still governed.
```

---

## Planned Branch Sequence

### PR 1 — priority lock and test plan (docs-only)

```text
docs/everyday-ux-friction-priority-lock
```

Adds:
- `docs/status/ACTIVE_PRIORITY_LOCK_2026-05-10_EVERYDAY_UX_FRICTION.md`
- `docs/PROOFS/Everyday-UX/README.md`
- `docs/PROOFS/Everyday-UX/LIVE_DAILY_WORKFLOW_TEST_PLAN_2026-05-10.md`
- Updated `.agent_context/current_priority.md`
- Updated `docs/status/CURRENT_WORK_STATUS.md`
- Updated `docs/todo/ACTIVE_TODO.md`

### PR 2 — live baseline evidence

```text
proof/everyday-ux-live-workflow-baseline
```

Records actual use: prompt, expected behavior, actual response, UI state, friction observed,
severity, proposed fix, boundary impact. No fixes in this branch.

### PR 3 — conversation response contract

```text
docs/nova-conversation-response-contract
```

Defines desired response shapes for: normal answer, search result, clarification, blocked
action, setup-required state, degraded state, no result, confirmation-required, daily task help.

### PR 4 — first implementation slice

```text
fix/everyday-ux-friction-slice-1
```

Small scope: clarification wording, blocked/setup-required wording, search response shape,
quick-action labels, dashboard helper text. Nothing more.

---

## Prior Workstream Close

Cap 16 `governed_web_search` is certified and locked (2026-05-10, all five phases, 60 tests).
No open PRs. This is a clean handoff point.

Recent merged chain:

```text
#128 — Trust Review Card MVP closeout
#129 — Browser Use visual capture blocker (blocked/setup-required classification)
#130 — dashboard event replay harness
#131 — non-search widget fuzzing
#132 — proof infrastructure closeout review
#133 — UI simplification inventory (docs-only, queued)
#134 — Cap 16 governed_web_search certification lock (LOCKED 2026-05-10)
```

---

## Preserved No-Authority Boundaries

Do not expand OpenClaw, add browser/computer-use, add external writes, or add autonomous
workflows based on this workstream.

UI simplification inventory is queued (`ui/simplify-dashboard-core-navigation`) but remains
inactive until a reviewed priority lock for that branch is established.

Cap 64 P5 remains paused. Do not jump to it from this workstream.
