# Phase 8 Local-First OpenAI Routing and Visibility Runtime Slice
Date: 2026-03-27
Status: Repo-grounded runtime proof

## What landed
This runtime slice adds the first explicit OpenAI operating layer inside Nova's Phase-8 product direction without breaking the local-first default.

What is now true:
- OpenAI is represented as an optional metered lane
- local-first routing is represented directly in runtime settings
- a preferred OpenAI model can be recorded in runtime settings
- a daily metered token budget and warning threshold can be recorded in runtime settings
- provider usage tracking can now hold exact token counts and estimated cost when available
- diagnostics and connection-status surfaces now expose OpenAI readiness and budget posture
- the Agent setup surface now shows optional OpenAI-lane readiness
- Settings now show local-first AI routing and metered budget controls

## Files changed for this slice
Backend:
- `nova_backend/src/settings/runtime_settings_store.py`
- `nova_backend/src/usage/provider_usage_store.py`
- `nova_backend/src/api/settings_api.py`
- `nova_backend/src/executors/os_diagnostics_executor.py`
- `nova_backend/src/api/openclaw_agent_api.py`

Frontend:
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard.js`
- `Nova-Frontend-Dashboard/index.html`
- `Nova-Frontend-Dashboard/dashboard.js`

Tests:
- `nova_backend/tests/test_runtime_settings_api.py`
- `nova_backend/tests/conversation/test_provider_usage_store.py`
- `nova_backend/tests/test_openclaw_agent_api.py`
- `nova_backend/tests/executors/test_os_diagnostics_openclaw_agent.py`

Docs:
- `docs/design/Phase 8/OPENAI_AGENT_OPERATING_MODEL_2026-03-27.md`
- `docs/design/Phase 8/OPENAI_PROVIDER_ROUTING_AND_BUDGET_POLICY_2026-03-27.md`
- `docs/design/Phase 8/OPENAI_USAGE_VISIBILITY_SPEC_2026-03-27.md`
- `docs/design/Phase 8/TRADING_MODE_GUARDRAILS_2026-03-27.md`

## What this does not prove
This slice does not prove:
- that OpenAI is the default Nova runtime
- that OpenAI-backed execution authority is live
- that live trading is safe or authorized
- that invoice-accurate cost tracking exists

## Honest reading
This is a local-first governance and visibility slice, not a cloud-autonomy slice.
