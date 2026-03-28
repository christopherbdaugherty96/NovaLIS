# Phase 8.5 Scheduler And Proactive Delivery Plan
Updated: 2026-03-27
Status: Narrow scheduler plus policy suppression slice implemented; still the governing design reference for remaining widening decisions
Purpose: Define and now anchor the narrow, auditable path from the manual OpenClaw home-agent foundation to scheduled delivery without overstating autonomy

## Why Phase 8.5 Exists
The current runtime already has:
- manual home-agent templates
- a delivery inbox for surface-first review
- strict manual preflight for current envelopes

What it still does not have:
- richer proactive notification controls beyond the current chat/inbox model

Phase 8.5 is the step that adds scheduled triggering without pretending the full canonical Phase-8 execution model is already complete.

## Current Implementation Baseline
Live now in the repo:
- `nova_backend/src/openclaw/agent_scheduler.py`
- `home_agent_scheduler_enabled` runtime permission
- per-template schedule enable / pause controls on the Agent page
- next-run and last scheduled outcome visibility on the Agent page
- quiet-hours suppression tied to the shared notification policy layer
- hourly rate-limit suppression tied to the shared notification policy layer
- operator-visible suppression reasons on the Agent page
- scheduler-triggered ledger events and runtime truth detection
- scheduled runs recorded into the existing delivery inbox

Still intentionally deferred inside this lane:
- broader connector-backed scheduled work
- richer proactive notification controls beyond the current chat/inbox model

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
These are the requirements for the shipped narrow scheduler and for any further widening:
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
Current shipped coverage includes:
- scheduler never runs when `home_agent_scheduler_enabled` is false
- scheduler runs due allowlisted templates and records completion
- per-template schedule enable / disable state persists through the runtime store
- quiet hours suppress due scheduled runs and surface a held reason
- rate limit suppresses due scheduled runs and surface a held reason
- a previously suppressed slot runs once policy clears

Still needed before widening:
- scheduler only runs allowlisted templates
- paused template does not fire
- delivery mode controls proactive chat vs. inbox behavior

## Recommended Remaining Order
1. tighten proactive-chat delivery controls if chat-first scheduled delivery is widened further
2. add connector-backed schedule readiness only after the connector itself is stable
3. keep quiet-hours and rate-limit policy shared with the reminder layer unless there is a strong product reason to split it
4. then consider widening beyond morning/evening briefing templates

## Shipping Rule
Phase 8.5 is complete only when scheduled delivery is:
- visible
- pausable
- rate-limited
- ledgered
- truthful in runtime docs
