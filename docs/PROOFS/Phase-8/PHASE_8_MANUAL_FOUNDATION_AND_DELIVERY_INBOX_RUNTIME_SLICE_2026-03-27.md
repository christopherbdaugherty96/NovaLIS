# Phase 8 Manual Foundation And Delivery Inbox Runtime Slice
Updated: 2026-03-27
Status: Applied to runtime

## What This Slice Adds
- strict manual preflight for home-agent envelopes
- persistent delivery inbox for widget and hybrid runs
- dismiss flow for delivery items
- Home page delivery widget
- Agent page ready-for-review section
- diagnostics visibility for delivery counts and strict-foundation status

## Runtime Files
- `nova_backend/src/openclaw/strict_preflight.py`
- `nova_backend/src/openclaw/agent_runtime_store.py`
- `nova_backend/src/openclaw/agent_runner.py`
- `nova_backend/src/api/openclaw_agent_api.py`
- `nova_backend/src/executors/os_diagnostics_executor.py`
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/style.phase1.css`

## Tests
- `nova_backend/tests/openclaw/test_strict_preflight.py`
- `nova_backend/tests/openclaw/test_agent_runtime_store.py`
- `nova_backend/tests/openclaw/test_agent_runner.py`
- `nova_backend/tests/test_openclaw_agent_api.py`

## Truth Boundary
This slice does not add:
- scheduling
- broad autonomous execution
- connector-backed inbox work
- full canonical Phase-8 interception/minimization stack
