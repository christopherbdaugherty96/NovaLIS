# Phase 6 Local Surface Hardening And Governance Truth Alignment
Date: 2026-03-28
Status: Runtime alignment refresh
Scope: Close the remaining Phase-6 trust/truth gaps in local request boundaries, durable store integrity, timeout behavior, and capability governance metadata.

## What Changed
- local-only HTTP surfaces now reject non-loopback `Host` / `Origin` values on:
  - memory export
  - runtime settings
  - workspace/operator APIs
  - local OpenClaw agent APIs
- the websocket session now rejects non-loopback `Host` / `Origin` values before accept
- JSON-backed persistent stores now use a shared per-path lock and atomic file replace, preventing in-process write loss across fresh store instances
- `ExecuteBoundary.run_with_timeout(...)` now returns promptly on timeout while keeping the boundary slot occupied until the worker drains
- capability governance truth is now corrected for:
  - `49 headline_summary` -> `read_only_network`
  - `50 intelligence_brief` -> `read_only_network`
  - `52 story_tracker_update` -> `persistent_change`
  - `58 screen_capture` -> `persistent_change`
- generated runtime governance docs now omit sealed legacy skill shims from the live skill surface map

## Why This Belongs To Phase 6
The canonical Phase-6 core promises:
- truthful capability classification
- trustworthy review surfaces
- fail-closed governance boundaries
- no hidden widening of authority

These fixes are not new product ambition. They are closure work on the governance/trust substrate that Phase 6 already declared necessary.

## Files Touched
- `nova_backend/src/brain_server.py`
- `nova_backend/src/websocket/session_handler.py`
- `nova_backend/src/governor/execute_boundary/execute_boundary.py`
- `nova_backend/src/governor/capability_topology.py`
- `nova_backend/src/config/registry.json`
- `nova_backend/src/audit/runtime_auditor.py`
- `nova_backend/src/memory/governed_memory_store.py`
- `nova_backend/src/tasks/notification_schedule_store.py`
- `nova_backend/src/policies/atomic_policy_store.py`
- `nova_backend/src/patterns/pattern_review_store.py`
- `nova_backend/src/settings/runtime_settings_store.py`
- `nova_backend/src/personality/tone_profile_store.py`
- `nova_backend/src/usage/provider_usage_store.py`
- `nova_backend/src/executors/news_intelligence_executor.py`
- `nova_backend/src/executors/story_tracker_executor.py`
- `nova_backend/src/executors/screen_capture_executor.py`

## Verification
Run from `nova_backend/`:

- `python -m pytest tests\\test_memory_api.py tests\\test_runtime_settings_api.py tests\\test_websocket_local_guard.py tests\\test_execute_boundary_timeout_behavior.py tests\\phase5\\test_notification_schedule_store.py tests\\phase6\\test_capability_topology.py tests\\executors\\test_story_tracker_executor.py tests\\phase45\\test_screen_capture_executor.py tests\\governance\\test_screen_capture_requires_invocation.py tests\\governance\\test_ledger_only_governor_logs_actions.py tests\\test_runtime_governance_docs.py -q`
- `python -m pytest tests\\phase7 -q tests\\test_openclaw_bridge_api.py tests\\executors\\test_news_intelligence_executor.py tests\\test_governor_execution_timeout.py -q`
- `python ..\\scripts\\generate_runtime_docs.py`
- `python ..\\scripts\\check_runtime_doc_drift.py`
- `python ..\\scripts\\check_frontend_mirror_sync.py`

## Verification Snapshot
- focused hardening bundle: `42 passed`
- surrounding phase7 / bridge / news / timeout bundle: `45 passed`
- runtime documentation drift check: passed
- frontend mirror parity check: passed

## Honest Result
Phase 6 remains a review-oriented delegated-policy and trust-alignment phase.

What changed here is that the runtime now matches that claim more honestly:
- local-only surfaces behave like local-only surfaces
- timeout failure is prompt instead of only eventually visible
- durable JSON stores are safer under concurrent in-process writes
- capability-law metadata now reflects real network reads and durable local writes
