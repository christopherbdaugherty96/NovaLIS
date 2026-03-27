# Phase 7 - OpenClaw Home Agent Foundation Runtime Slice
Updated: 2026-03-26
Status: Landed on `main`

## Purpose
Record the runtime slice that adds Nova-owned personality framing and the first live OpenClaw home-agent foundation without widening authority into Phase-8 execution.

## What This Slice Adds
- a calmer, more present Nova system prompt tuned for product use rather than purely builder-facing restraint
- explicit conversational and task-report communication profiles
- a Nova-owned task-result presentation path so worker-style outputs are spoken in Nova's voice
- a dedicated `home_agent_enabled` runtime permission in Settings
- a new OpenClaw home-agent foundation package under `nova_backend/src/openclaw/`
- a dedicated Agent page in the dashboard
- manual briefing-template runs with delivery-mode controls
- Trust and Settings visibility for the home-agent foundation

## Important Boundary
This slice does **not** enable:
- scheduled background execution
- autonomous envelope execution
- broad OpenClaw tool access
- Phase-8 external execution authority

The live runtime shape is:
- Nova remains the visible voice, trust layer, and control surface
- OpenClaw is represented as a manual operator-facing foundation only
- named briefings can surface in chat and the operator surface
- quiet review work remains planned and surface-first

## Runtime Files Added
- `nova_backend/src/openclaw/task_envelope.py`
- `nova_backend/src/openclaw/agent_personality_bridge.py`
- `nova_backend/src/openclaw/agent_runtime_store.py`
- `nova_backend/src/openclaw/agent_runner.py`
- `nova_backend/src/api/openclaw_agent_api.py`

## Runtime Files Updated
- `nova_backend/src/brain_server.py`
- `nova_backend/src/executors/os_diagnostics_executor.py`
- `nova_backend/src/nova_config.py`
- `nova_backend/src/personality/interface_agent.py`
- `nova_backend/src/personality/conversation_personality_agent.py`
- `nova_backend/src/settings/runtime_settings_store.py`
- `nova_backend/src/audit/runtime_auditor.py`

## Frontend Files Updated
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/style.phase1.css`

Mirrored frontend copies stayed aligned:
- `Nova-Frontend-Dashboard/index.html`
- `Nova-Frontend-Dashboard/dashboard.js`
- `Nova-Frontend-Dashboard/style.phase1.css`

## Live Operator Surface
The dashboard now includes:
- an `Agent` page in the primary navigation
- runtime summary cards for the home-agent foundation
- template cards with delivery-mode toggles:
  - surface only
  - chat only
  - chat + surface
- manual run controls for currently available briefing templates
- recent-run history with:
  - estimated token usage
  - delivery channels
  - Nova-presented output text

## Current Template Truth
Live manual templates:
- `morning_brief`
- `evening_digest`

Planned/not yet connected:
- `inbox_check`

Current delivery model:
- named briefings default to hybrid delivery
- quiet review defaults to surface-only delivery

## Token / Model Strategy In This Slice
The home-agent foundation is intentionally low-token:
- structured data is collected first from existing local/governed skills
- one local summary call is attempted at the end
- deterministic fallback text is used if the local model path is unavailable

That keeps the slice aligned with the intended Nova/OpenClaw model:
- tools gather
- Nova summarizes
- Nova presents

## Diagnostics / Runtime Truth Improvements
This slice also required a runtime-auditor correction:
- extracted router/module surfaces had made some live features disappear from generated runtime docs
- the runtime auditor now recognizes:
  - extracted bridge routes
  - extracted websocket session handling
  - the OpenClaw home-agent foundation
- generated runtime truth once again reflects the real modularized app

## Verification
Passed:
- OpenClaw home-agent API / runner / store / personality bundle: `13 passed`
- bridge + personality + dashboard regression bundle: `23 passed`
- runtime auditor + diagnostics bundle: `16 passed`
- `node --check nova_backend/static/dashboard.js`
- `python -m py_compile` on changed runtime modules
- `python scripts/check_runtime_doc_drift.py`
- `python scripts/check_frontend_mirror_sync.py`

## What This Means
Nova now has a real product-facing foundation for the long-term OpenClaw vision:
- users still talk to Nova
- Nova still owns the trust and presentation layer
- a manual home-agent/operator surface is now live
- broader automation is still gated behind future Phase-8 execution work
