# Phase 7 Settings Runtime Permissions Slice
Date: 2026-03-26
Status: Implemented on `main`
Scope: Turn Settings from a visibility-only surface into a governed runtime control layer for setup mode, second-opinion access, and remote bridge access

## What This Slice Adds
This slice makes Settings materially real instead of informational only.

It adds:
- a persistent local runtime settings store
- backend APIs for reading and updating setup mode
- backend APIs for pausing or re-enabling governed second opinion
- backend APIs for pausing or re-enabling the remote bridge
- a recommended-defaults reset path
- Settings-page controls and settings-change history
- runtime enforcement so the same toggles affect diagnostics and actual allow/deny behavior

## What It Does Not Add
This slice does not add:
- in-app provider key entry
- connector OAuth or account linking
- remote bridge execution authority
- richer Phase-8 execution widening

Those still belong to later product or Phase-8 work.

## Product Meaning
Users can now make a few important setup choices in one place and trust that Nova will actually honor them.

The key user-facing improvement is:
- if governed second opinion is paused in Settings, Nova will say so and refuse to run it
- if the remote bridge is paused in Settings, remote ingress is blocked even if a bridge token exists
- setup mode now persists as product state instead of only living in browser storage

## Main Runtime Changes
Backend:
- `nova_backend/src/settings/runtime_settings_store.py`
- `nova_backend/src/brain_server.py`
- `nova_backend/src/executors/os_diagnostics_executor.py`
- `nova_backend/src/executors/external_reasoning_executor.py`
- `nova_backend/src/audit/runtime_auditor.py`

Frontend:
- `nova_backend/static/dashboard.js`
- `nova_backend/static/index.html`
- `nova_backend/static/style.phase1.css`
- `Nova-Frontend-Dashboard/dashboard.js`
- `Nova-Frontend-Dashboard/index.html`
- `Nova-Frontend-Dashboard/style.phase1.css`

Tests:
- `nova_backend/tests/test_runtime_settings_api.py`
- `nova_backend/tests/phase45/test_dashboard_onboarding_widget.py`
- `nova_backend/tests/phase45/test_dashboard_trust_center_widget.py`
- `nova_backend/tests/test_runtime_auditor.py`

## Verification
Focused verification passed:
- `python -m pytest nova_backend/tests/test_runtime_settings_api.py nova_backend/tests/phase45/test_dashboard_onboarding_widget.py nova_backend/tests/phase45/test_dashboard_trust_center_widget.py -vv`
- `python -m pytest nova_backend/tests/executors/test_web_search_executor.py nova_backend/tests/executors/test_news_intelligence_executor.py nova_backend/tests/test_openclaw_bridge_api.py nova_backend/tests/test_runtime_auditor.py -vv`
- `python -m pytest tests/phase45/test_brain_server_trust_status.py tests/phase45/test_dashboard_onboarding_widget.py tests/phase45/test_dashboard_trust_center_widget.py -vv` from `nova_backend/`

Additional checks:
- `python -m py_compile nova_backend/src/brain_server.py nova_backend/src/executors/os_diagnostics_executor.py nova_backend/src/executors/external_reasoning_executor.py nova_backend/src/settings/runtime_settings_store.py`
- `node --check nova_backend/static/dashboard.js`
- `python scripts/generate_runtime_docs.py`
- `python scripts/check_runtime_doc_drift.py`
- `python scripts/check_frontend_mirror_sync.py`

## Bottom Line
This slice closes the biggest remaining Settings truth gap.

Nova still does not pretend provider setup is fully connected in-app, but the Settings page now controls real runtime behavior instead of only explaining future intentions.
