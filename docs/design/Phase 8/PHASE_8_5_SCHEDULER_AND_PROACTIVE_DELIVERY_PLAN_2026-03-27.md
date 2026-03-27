# Phase 8.5 Scheduler And Proactive Delivery Plan
Updated: 2026-03-27
Status: Design-only next step
Purpose: Define the narrow, auditable path from the current manual OpenClaw home-agent foundation to scheduled delivery without overstating autonomy

## Why Phase 8.5 Exists
The current runtime already has:
- manual home-agent templates
- a delivery inbox for surface-first review
- strict manual preflight for current envelopes

What it still does not have:
- proactive scheduling
- timed delivery
- a governance carve-out for any background trigger loop

Phase 8.5 is the step that adds scheduled triggering without pretending the full canonical Phase-8 execution model is already complete.

## Scope
Phase 8.5 should add only:
- a narrow scheduler for named briefing templates
- operator-visible schedule status
- proactive delivery rules tied to delivery mode
- rate limiting and quiet-hours interaction for scheduled runs
- explicit stop/pause controls for scheduled templates

Phase 8.5 should not add:
- broad autonomous task execution
- hidden recurring connectors
- always-on monitoring
- silent retries that bypass operator visibility

## Design Shape
Scheduler location:
- `nova_backend/src/openclaw/agent_scheduler.py`

Allowed initial scheduled templates:
- `morning_brief`
- `evening_digest`

Deferred templates:
- `inbox_check`
- any connector-backed review work

## Delivery Model
Use the already-live delivery model as the policy base:
- `widget`
- `chat`
- `hybrid`

Scheduled behavior should read this way:
- `widget`
  - result enters delivery inbox only
- `chat`
  - Nova posts the result into chat and records the run
- `hybrid`
  - Nova posts into chat and keeps a visible delivery item for later review

## Governance Requirements
Before scheduler code lands, all of the following must exist:
1. explicit scheduler module path
2. explicit runtime flag for scheduled delivery
3. explicit test carve-out for the scheduler path only
4. rate limit enforcement for scheduled runs
5. operator-visible last run / next run / paused state
6. ledger events for run triggered, run completed, run suppressed, run paused

## Operator Surface Requirements
The Agent page should gain:
- schedule enabled/paused status per template
- next planned run label
- last scheduled run outcome
- suppression reason when quiet hours or rate limit block a run

The Home page should remain lighter:
- delivery inbox
- next scheduled named brief if enabled

## Suggested Runtime Flags
- `home_agent_enabled`
  - already live
- `home_agent_scheduler_enabled`
  - Phase 8.5
- `home_agent_proactive_chat_enabled`
  - optional Phase 8.5 or later, depending on whether delivery mode alone is enough

## Required Tests
Add before shipping:
- scheduler only runs allowlisted templates
- quiet hours suppress delivery correctly
- rate limit suppresses repeated scheduled runs
- paused template does not fire
- scheduler never runs when `home_agent_enabled` is false
- delivery mode controls proactive chat vs. inbox behavior

## Recommended Order
1. add scheduler design packet
2. add scheduler runtime flag
3. add scheduler module behind explicit startup wiring
4. add operator-visible schedule state
5. add suppression + rate-limit tests
6. then allow morning/evening schedule activation

## Shipping Rule
Phase 8.5 is complete only when scheduled delivery is:
- visible
- pausable
- rate-limited
- ledgered
- truthful in runtime docs
