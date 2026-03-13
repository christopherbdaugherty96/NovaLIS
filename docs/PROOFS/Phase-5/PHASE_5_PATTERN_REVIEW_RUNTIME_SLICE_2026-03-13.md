# Phase-5 Pattern Review Runtime Slice
Date: 2026-03-13
Status: Implemented runtime slice
Classification: Proof artifact

## Purpose
This slice begins the Phase-5 pattern-detection track in the safest allowed form:

- explicit opt-in only
- user-triggered review generation only
- advisory proposals routed to a review queue
- no automatic action execution
- discardable and inspectable proposal handling

It follows the guardrail spec that pattern detection must stay informational, reversible, and non-authorizing.

## What Landed
Implemented:
- persistent opt-in state for pattern review
- explicit commands:
  - `pattern opt in`
  - `pattern opt out`
  - `pattern status`
  - `review patterns`
  - `review patterns for <thread>`
  - `accept pattern <id>`
  - `dismiss pattern <id>`
- persistent advisory review queue
- quiet Home-page pattern-review widget
- recent pattern-decision history
- ledger-visible opt-in, generation, acceptance, and dismissal events

## Runtime Shape
This runtime slice adds:
- a review-queue store outside the authority path
- advisory proposal generation from:
  - project thread summaries
  - linked memory insights
- proposal types such as:
  - blocked thread without a next step
  - repeated blocker theme across threads
  - durable context without a recent saved decision

Important constraint:
- no pattern review runs until the user opts in
- no background cognition loop is introduced
- accepting a proposal does not execute anything
- acting on a proposal still requires explicit user commands

## Files Touched
Backend:
- `nova_backend/src/patterns/pattern_review_store.py`
- `nova_backend/src/brain_server.py`
- `nova_backend/src/ledger/event_types.py`
- `nova_backend/src/working_context/pattern_review_store.py` (non-persistent compatibility shim)

Frontend:
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/style.phase1.css`
- mirrored to `Nova-Frontend-Dashboard/`

Tests:
- `nova_backend/tests/phase5/test_pattern_review_store.py`
- `nova_backend/tests/phase5/test_pattern_review_contract.py`
- `nova_backend/tests/phase45/test_dashboard_pattern_review_widget.py`

## Safety / Governance Notes
Still preserved:
- explicit opt-in required before pattern generation
- proposals are advisory only
- no auto-apply of proposals
- no background generation loop
- no UI reordering or priority mutation from proposal output
- any action suggested by a proposal still requires explicit invocation

Acceptance is informational:
- `accept pattern <id>` records that the proposal was kept for review
- it does not trigger execution or persistence beyond the review queue itself

## User-Facing Result
Users can now:
- opt in to pattern review deliberately
- ask Nova to review ongoing work for repeated patterns
- inspect proposals in a quiet dashboard surface
- accept or dismiss proposals explicitly
- use proposal suggestions as starting points for explicit follow-up commands

This makes Nova more reflective about ongoing work without making it autonomous.

## Verification
Run date: 2026-03-13

Commands:
- `$env:PYTHONPATH='nova_backend'; python -m pytest -q nova_backend/tests/phase5`
- `$env:PYTHONPATH='nova_backend'; python -m pytest -q nova_backend/tests/phase45`
- `$env:PYTHONPATH='nova_backend'; python -m pytest -q nova_backend/tests`
- `python scripts/check_frontend_mirror_sync.py`
- `python scripts/check_runtime_doc_drift.py`

Results:
- `nova_backend/tests/phase5`: `41 passed`
- `nova_backend/tests/phase45`: `49 passed`
- full backend suite (`nova_backend/tests`): `395 passed`
- frontend mirror sync check: passed
- runtime documentation drift check: passed

## Phase-5 Meaning
This slice is the first implemented step in the pattern-detection track.

It moves Nova further toward:
- reflective continuity support
- explicit review of repeated work patterns
- more informed daily guidance

without introducing hidden initiative or authority drift.

