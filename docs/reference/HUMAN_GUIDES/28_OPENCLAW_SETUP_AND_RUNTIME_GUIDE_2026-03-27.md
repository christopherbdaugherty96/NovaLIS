# OpenClaw Setup and Runtime Guide
Updated: 2026-03-27
Status: Plain-language OpenClaw guide

## Purpose
This guide explains how OpenClaw is set up inside Nova today.

It is intentionally practical.
It answers:
- what OpenClaw is in the current repo
- where the code lives
- what settings and environment values matter
- what works end to end today
- what is still deferred

## The Simple Mental Model
OpenClaw has two different surfaces inside Nova.

1. Remote bridge
- this is the token-gated HTTP bridge
- it is read, review, and reasoning only
- it is not broad execution authority

2. Home-agent foundation
- this is the local Agent page and runtime
- it handles manual briefing-style runs and the narrow scheduler
- Nova still owns the voice and presentation

That means the user should think about it this way:
- Nova is the face
- OpenClaw is the worker layer inside Nova
- the user still talks to Nova

## Where It Lives In Code
### Remote bridge
- `nova_backend/src/api/bridge_api.py`

Live endpoints:
- `GET /api/openclaw/bridge/status`
- `POST /api/openclaw/bridge/message`

### Local home-agent foundation
- `nova_backend/src/api/openclaw_agent_api.py`
- `nova_backend/src/openclaw/task_envelope.py`
- `nova_backend/src/openclaw/agent_runtime_store.py`
- `nova_backend/src/openclaw/agent_runner.py`
- `nova_backend/src/openclaw/strict_preflight.py`
- `nova_backend/src/openclaw/agent_scheduler.py`

Live endpoints:
- `GET /api/openclaw/agent/status`
- `POST /api/openclaw/agent/templates/{template_id}/delivery`
- `POST /api/openclaw/agent/templates/{template_id}/schedule`
- `POST /api/openclaw/agent/templates/{template_id}/run`
- `POST /api/openclaw/agent/delivery/{delivery_id}/dismiss`

## What The Agent Page Actually Uses
The Agent page is built around three live templates:
- `morning_brief`
- `evening_digest`
- `inbox_check`

Current truth:
- `morning_brief` is runnable now
- `evening_digest` is runnable now
- `inbox_check` is visible but not connected yet

The Agent page also now shows setup/readiness for:
- local summarizer status
- weather provider status
- calendar source status
- remote bridge status
- scheduler status

## Settings That Matter
Runtime permissions live in `nova_backend/src/settings/runtime_settings_store.py`.

The key permissions are:
- `remote_bridge_enabled`
- `home_agent_enabled`
- `home_agent_scheduler_enabled`

What they mean:
- `remote_bridge_enabled`
  - allows the remote bridge to accept token-authenticated requests
- `home_agent_enabled`
  - allows the local home-agent templates to run
- `home_agent_scheduler_enabled`
  - allows the narrow scheduled briefing lane to run at its planned times

## Environment Values That Matter
### Optional remote bridge token
Use one of:
- `NOVA_OPENCLAW_BRIDGE_TOKEN`
- `NOVA_BRIDGE_TOKEN`

If neither is set:
- the remote bridge stays disabled
- the local Agent page still works

### Optional weather provider key
- `WEATHER_API_KEY`

If it is missing:
- the home-agent foundation still works
- weather becomes limited instead of full live weather

### Optional calendar file
- `NOVA_CALENDAR_ICS_PATH`

If it is missing:
- the home-agent foundation still works
- calendar snapshots stay optional and disconnected

### Local model route
OpenClaw prefers Nova's local model route for final summarization.

If the local model is unavailable:
- manual briefing runs can still fall back to deterministic summaries
- the setup/readiness panel will show that the summarizer is in fallback mode

## What Runs End to End Today
A normal manual run looks like this:
1. user opens the Agent page
2. Nova loads `GET /api/openclaw/agent/status`
3. the user runs `morning_brief` or `evening_digest`
4. `agent_runner.py` builds a small envelope from the template
5. `strict_preflight.py` checks the envelope against the current strict foundation rules
6. the runner gathers weather, calendar, news, and schedule context
7. one local summary pass may happen at the end
8. `agent_personality_bridge.py` rewrites the result into Nova's voice
9. the run is recorded in the runtime store
10. the result appears in chat, surface delivery, or both depending on the template's delivery mode

A scheduled run looks similar, except:
- `agent_scheduler.py` claims the due template window
- the run is triggered as `scheduler`
- the outcome is recorded back into the template's schedule state

## How The Remote Bridge Is Bounded
The bridge is deliberately narrower than the local Agent page.

Current bridge behavior:
- token required
- stateless
- read, review, and reasoning only
- remote-safe capability filtering is active
- local-context and local-effect requests stay blocked

That means the bridge should allow things like:
- `daily brief`
- `news`
- `calendar`
- web research and second-opinion style requests

And it should block things like:
- memory changes
- schedule changes
- policy or settings changes
- local device control
- screen or local-context dependent requests

## What Is Still Not Live
Important truth:
- this is not full OpenClaw autonomous execution
- this is not broad governed envelope execution
- this is not connector-backed inbox work yet
- this is not home automation yet

Still deferred:
- richer connectors
- full canonical Phase-8 execution path
- broader operator controls for later action-level work

## Best Honest Summary
OpenClaw inside Nova is already real, but it is intentionally narrow.

Today it is:
- a governed remote bridge for remote-safe read/reasoning requests
- a local home-agent foundation for briefings, delivery, and a narrow scheduler

It is not yet:
- a broad autonomous worker with full execution authority
