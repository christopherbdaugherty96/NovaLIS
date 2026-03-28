# Phase 8 Proof - System Map and Metered OpenAI Task-Report Slice
Updated: 2026-03-27
Status: Repo-grounded runtime proof

## What This Slice Added
This slice did two things:
- saved the current and future Nova system diagrams into a dedicated Phase-8 design document
- converted the local-first OpenAI policy from settings-only truth into a narrow live runtime fallback for OpenClaw task reports

## Repo-Grounded Runtime Truth
Live code paths:
- `nova_backend/src/providers/openai_responses_lane.py`
- `nova_backend/src/openclaw/agent_runner.py`
- `nova_backend/src/openclaw/agent_runtime_store.py`
- `nova_backend/src/api/openclaw_agent_api.py`
- `nova_backend/src/api/settings_api.py`
- `nova_backend/src/executors/os_diagnostics_executor.py`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/style.phase1.css`

Live design map:
- `docs/design/Phase 8/NOVA_SYSTEM_MAP_CURRENT_AND_FUTURE_2026-03-27.md`

## Runtime Behavior Confirmed
Current narrow behavior:
1. OpenClaw gathers data first
2. local summarizer is attempted first
3. OpenAI is only attempted when:
   - `metered_openai_enabled` is on
   - routing mode is `budgeted_fallback`
   - `OPENAI_API_KEY` is configured
   - daily metered budget is not at `limit`
4. if OpenAI is used, the run stores usage metadata
5. chat and delivery surfaces can show whether the run stayed local or used metered tokens
6. if both model paths fail, Nova returns a deterministic fallback summary

## Boundary Preserved
This slice does not make Nova cloud-first.

It preserves:
- local-first routing
- explicit metered permission
- budget state visibility
- Nova-owned presentation
- no broad new execution authority

## Still Deferred
- broad OpenAI routing outside the narrow OpenClaw task-report lane
- full canonical Phase-8 envelope execution
- live trading execution
- richer connector-backed home-agent work
