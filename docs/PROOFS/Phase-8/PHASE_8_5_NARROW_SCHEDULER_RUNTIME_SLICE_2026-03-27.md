# Phase 8.5 Narrow Scheduler Runtime Slice
Date: 2026-03-27
Status: Repo-grounded runtime proof

## Scope
This packet records the first live Phase 8.5 scheduler slice:
- narrow scheduled briefing execution only
- explicit runtime permission gate
- per-template schedule controls
- delivery inbox persistence
- no widening into broad autonomous execution

## What Landed
Runtime:
- `nova_backend/src/openclaw/agent_scheduler.py`
- `nova_backend/src/openclaw/agent_runtime_store.py`
- `nova_backend/src/openclaw/strict_preflight.py`
- `nova_backend/src/settings/runtime_settings_store.py`
- `nova_backend/src/api/openclaw_agent_api.py`
- `nova_backend/src/executors/os_diagnostics_executor.py`
- `nova_backend/src/audit/runtime_auditor.py`
- `nova_backend/src/brain_server.py`
- `nova_backend/src/ledger/event_types.py`

Frontend:
- `nova_backend/static/dashboard.js`

Governance test carve-out:
- `nova_backend/tests/governance/test_no_background_screen_monitoring.py`

## Runtime Truth
The shipped shape is:
- the scheduler lives in one dedicated allowlisted file
- scheduled execution requires both:
  - `home_agent_enabled`
  - `home_agent_scheduler_enabled`
- only schedule-ready templates are eligible
- current schedule-ready templates are:
  - `morning_brief`
  - `evening_digest`
- `inbox_check` remains visible but not schedule-ready

## Operator Surface
The Agent page now shows:
- scheduler status
- per-template schedule enable/pause control
- next-run label
- last scheduled outcome

The Home page continues to show:
- delivery inbox review

## Ledger Coverage
This slice adds:
- `OPENCLAW_AGENT_SCHEDULE_UPDATED`
- `OPENCLAW_AGENT_SCHEDULE_TRIGGERED`
- `OPENCLAW_AGENT_SCHEDULE_COMPLETED`
- `OPENCLAW_AGENT_SCHEDULE_FAILED`

## What This Does Not Claim
This slice does not claim:
- APScheduler or cron integration
- quiet-hours suppression
- rate-limit suppression
- broader envelope-governed external execution
- connector-backed scheduled work
- full canonical Phase-8 automation completion

## Test Coverage
Focused coverage for this slice includes:
- `nova_backend/tests/openclaw/test_agent_scheduler.py`
- `nova_backend/tests/openclaw/test_agent_runtime_store.py`
- `nova_backend/tests/test_openclaw_agent_api.py`
- `nova_backend/tests/test_runtime_settings_api.py`
- `nova_backend/tests/executors/test_os_diagnostics_openclaw_agent.py`
- `nova_backend/tests/test_runtime_auditor.py`
- `nova_backend/tests/governance/test_no_background_screen_monitoring.py`

Validated in this pass:
- focused scheduler/openclaw/runtime suite passed
- runtime docs regenerated after the runtime auditor change
- frontend mirror sync passed

## Bottom Line
Phase 8.5 is now live as a narrow, explicit, inspectable scheduler slice.

That improves daily usefulness without pretending Nova has already crossed into broad autonomous worker behavior.
