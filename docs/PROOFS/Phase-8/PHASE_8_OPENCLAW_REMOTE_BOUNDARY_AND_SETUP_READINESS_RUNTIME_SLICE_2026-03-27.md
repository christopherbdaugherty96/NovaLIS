# Phase 8 Runtime Slice — Remote Boundary and Setup Readiness
Updated: 2026-03-27
Status: Repo-grounded runtime slice

## Purpose
This packet records the Phase-8 improvement slice that tightened the remote bridge boundary and added explicit setup/readiness reporting for the OpenClaw home-agent surface.

## What Changed
### Remote bridge
File:
- `nova_backend/src/api/bridge_api.py`

Changes:
- kept the existing prefix-based scope block
- added capability-aware remote-safe blocking on top of the prefix rules
- allowed only the current remote-safe capability set
- blocked local-context and local-effect capabilities even when they are read-only in a broader Nova sense
- added heuristic blocking for paraphrased state-changing bridge requests that do not cleanly match the existing mediator grammar

Runtime effect:
- the bridge remains read, review, and reasoning only
- the bridge is now closer to `remote-safe read/reasoning only` instead of relying mostly on prefix wording

### Agent status setup/readiness
File:
- `nova_backend/src/api/openclaw_agent_api.py`

Changes:
- `GET /api/openclaw/agent/status` now includes setup/readiness detail inside the agent snapshot
- setup/readiness covers:
  - local summarizer
  - weather provider
  - calendar source
  - remote bridge
  - scheduler
- the status payload now distinguishes:
  - what is required now
  - what is optional
  - what is paused
  - which templates are runnable or schedule-ready

Runtime effect:
- the Agent page can now explain why the current OpenClaw surface is ready, limited, optional, or paused instead of leaving the user to infer that from scattered cards

### Frontend agent surface
Files:
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard.js`

Changes:
- added a Setup and Readiness panel to the Agent page
- the panel renders the new readiness snapshot directly from the live status endpoint

Runtime effect:
- the user can see the real OpenClaw setup shape in product terms:
  - local summarizer ready or fallback
  - weather configured or optional
  - calendar connected or optional
  - remote bridge enabled, paused, or not configured
  - scheduler enabled or paused

## Tests Added Or Extended
Files:
- `nova_backend/tests/test_openclaw_bridge_api.py`
- `nova_backend/tests/test_openclaw_agent_api.py`

Coverage added:
- paraphrased memory-write bridge request is blocked
- local-context bridge request is blocked
- agent status returns readiness detail for the default limited setup state
- agent status returns connected setup inputs when weather, calendar, and bridge token are configured

## Focused Validation
Focused OpenClaw suite:
- `26 passed`

Covered in this pass:
- bridge API
- agent API
- runner
- runtime store
- scheduler

## Runtime Truth
This slice does not widen OpenClaw into full Phase-8 execution.

It improves the existing live surfaces by making them:
- safer remotely
- clearer locally
- easier to inspect end to end
