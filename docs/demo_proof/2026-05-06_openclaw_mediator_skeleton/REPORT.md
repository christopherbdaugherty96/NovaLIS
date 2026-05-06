# OpenClawMediator Skeleton Report - 2026-05-06

Status: draft / review required

## Purpose

This package proves the first OpenClawMediator skeleton under the active priority lock.

The skeleton creates one explicit policy boundary between a Nova/task envelope and future OpenClaw work. It is intentionally non-executing.

## What Was Added

- `nova_backend/src/openclaw/openclaw_mediator.py`
- `nova_backend/tests/openclaw/test_openclaw_mediator.py`

The module defines:

- `OpenClawDelegationEnvelope`
- `OpenClawMediatorDecision`
- `OpenClawMediatorReceipt`
- `OpenClawMediator`

## Runtime Boundary

The mediator skeleton:

- accepts a caller-provided delegation envelope
- requires read-only intent
- requires explicit allowed input scope
- blocks browser/computer-use
- blocks filesystem writes
- blocks external writes
- blocks email/calendar/Shopify/account actions
- blocks direct Cap 63 shortcut use
- returns a decision object
- returns a receipt/non-action statement

The mediator skeleton does not:

- execute OpenClaw
- call Cap 63
- call Governor
- call capabilities
- write files
- open browsers
- make network calls
- add runtime routes
- expand workflow automation

## Evidence

Focused pytest:

```text
18 passed
```

Raw evidence:

- `raw/focused_pytest_results.txt`
- `raw/openclaw_mediator_decision_payload.json`

The JSON evidence includes:

- a scoped read-only local/sample preview case with `decision: "preview_allowed"`
- a blocked browser/account/direct-Cap-63 case with `decision: "blocked"`
- `execution_performed: false`
- `authorization_granted: false`
- `openclaw_called: false`
- `governor_called: false`
- `capabilities_called: false`
- `filesystem_touched: false`
- `browser_opened: false`
- `network_called: false`

## Review Notes

This is a skeleton boundary, not a live delegation integration.

The next proof must still show a first read-only OpenClaw workflow through a reviewed mediator path before any broader reliance is claimed.
