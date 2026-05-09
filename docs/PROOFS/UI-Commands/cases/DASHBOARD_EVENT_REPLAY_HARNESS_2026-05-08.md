# Dashboard Event Replay Harness Proof - 2026-05-08

Status: proof added / deterministic replay only

## Purpose

This proof adds deterministic dashboard event replay coverage after Browser Use screenshot/click-path capture remained blocked by runtime asset setup.

The goal is to prove existing dashboard interaction guards under event pressure without adding browser automation, browser/computer-use capability, new runtime authority, OpenClaw expansion, external writes, autonomous workflows, or direct Cap 63 shortcut use.

## Scope

Covered:

- repeated manual sends / double-submit pressure
- stale turn WebSocket events
- rapid `chat_done` events before assistant output
- widget events tied to the active manual turn
- duplicate assistant text in the same turn
- unsupported dashboard/WebSocket message fallback
- socket error / close cleanup
- source-contract anchoring against served and mirrored dashboard JavaScript

Not covered:

- physical browser click replay
- screenshot/click-path proof
- visual regression capture
- Browser Use/iab recovery
- autonomous browser actions
- new dashboard runtime behavior

## Method

Added a small Python replay harness in:

```text
nova_backend/tests/phase45/dashboard_event_replay_harness.py
```

The harness models the existing manual-turn dashboard contract from `dashboard-chat-news.js`:

- block overlapping manual sends while Nova is answering
- assign one active `turn_id`
- ignore stale turn events
- avoid clearing a manual turn on early `chat_done` without assistant output
- allow active-turn widget events to satisfy the manual turn
- dedupe repeated assistant text within a turn
- render unsupported dashboard messages as a visible non-action state

The harness does not drive a browser, open tabs, call Nova runtime APIs, call capabilities, call GovernorMediator, call OpenClaw, write files during replay, or perform network actions.

## Verification

Focused verification:

```text
python -m pytest nova_backend/tests/phase45/test_dashboard_event_replay_harness.py nova_backend/tests/phase45/test_dashboard_auto_widget_dispatch.py -q
22 passed
```

JavaScript syntax checks:

```text
node --check nova_backend/static/dashboard-chat-news.js
node --check Nova-Frontend-Dashboard/dashboard-chat-news.js
passed
```

Raw evidence:

- `../evidence/2026-05-08/raw/dashboard_event_replay_harness_results.json`
- `../evidence/2026-05-08/raw/dashboard_event_replay_pytest_results.txt`

## Findings

Pass:

- a second manual send while Nova is answering does not enqueue a second payload
- stale `chat` and `chat_done` events with the wrong `turn_id` are ignored
- an early `chat_done` without assistant output does not fake completion
- an active-turn widget response can complete a manual turn
- duplicate assistant text in the same manual turn is deduped
- unsupported dashboard messages are visible and explicitly non-executing
- socket error/close cleanup clears pending manual-turn state without sending extra payloads

Still blocked:

- Browser Use screenshot/click-path proof remains blocked/setup-required at the Node REPL kernel asset setup layer.
- High-frequency physical click replay remains unavailable until visual/browser proof infrastructure is repaired.

## Boundary

This proof does not add runtime behavior. It does not approve browser/computer-use expansion, OpenClaw expansion, external writes, autonomous workflows, new capabilities, direct Cap 63 shortcut use, scheduler work, installer work, or connector expansion.

