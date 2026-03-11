# Phase-4.2 Authority Remediation Addendum
Date: 2026-03-11
Commit Base: e5a5cfa
Status: Complete
Scope: Closure hardening addendum for authority-bound runtime behavior discovered during final architecture audit.

## Remediation Objective
Resolve all active authority-leak risks identified in final Phase-4 / 4.2 / 4.5 audit so Phase-4.2 closure remains constitutionally valid.

## Findings Resolved

1. Runtime branch-level governed invocation bypasses in `brain_server.py`.
- Resolution:
  - Added mediated command execution helper:
    - `invoke_governed_text_command(...)`
    - `invoke_governed_capability(...)`
  - Weather/news/calendar/system/morning refresh flows now parse via `GovernorMediator` before capability execution.
- Files:
  - `nova_backend/src/brain_server.py`

2. Hidden multi-capability chain (`track_cluster` auto-invoking topic tracking capability).
- Resolution:
  - Removed auto invocation chain.
  - Replaced with explicit suggested follow-up command (`track story <topic>`), preserving user control.
- Files:
  - `nova_backend/src/brain_server.py`

3. Orchestrator direct executor touchpoint (`WebpageLaunchExecutor.plan_open(...)`).
- Resolution:
  - Extracted neutral planner utility to:
    - `nova_backend/src/utils/web_target_planner.py`
  - Runtime now calls `plan_web_open(...)` from utility module.
- Files:
  - `nova_backend/src/utils/web_target_planner.py`
  - `nova_backend/src/brain_server.py`
  - `nova_backend/src/executors/webpage_launch_executor.py`

4. UI implicit governed-action dispatch on websocket connect.
- Resolution:
  - Removed automatic `hydrateDashboardWidgets()` call from websocket `onopen`.
  - Widget refresh now requires explicit user interaction.
- Files:
  - `nova_backend/static/dashboard.js`
  - `Nova-Frontend-Dashboard/dashboard.js` (mirror sync)

5. Latent network bypass surfaces.
- Resolution A (staged model manager):
  - Removed direct requests/session usage from `llm_manager_vlock.py`.
  - Enforced model I/O through `ModelNetworkMediator`.
- Resolution B (legacy search tool):
  - Sealed `src/tools/web_search.py` as a non-network compatibility shim.
  - Eliminated direct network provider path from dormant legacy surface.

## Added Regression Guards
- `nova_backend/tests/adversarial/test_no_multi_capability_chain.py`
  - Prevents reintroduction of auto chain.
  - Prevents orchestrator reference to `WebpageLaunchExecutor`.
- `nova_backend/tests/phase45/test_dashboard_no_auto_widget_dispatch.py`
  - Asserts websocket open does not auto-send widget refresh commands.
- `nova_backend/tests/governance/test_legacy_bypass_surfaces_removed.py`
  - Asserts no direct requests path in staged LLM manager.
  - Asserts legacy web-search module remains sealed and non-network.

## Verification Results
- `python -m pytest -q` (from `nova_backend`) -> `282 passed`
- `python -m pytest -q tests/phase42` -> `17 passed`
- Targeted governance closure pack:
  - `python -m pytest -q tests/executors/test_multi_source_reporting_executor.py tests/rendering/test_intelligence_brief_renderer.py tests/phase42/test_intelligence_report_contract.py tests/phase42/test_phase42_dashboard_report_interaction.py tests/rendering/test_speech_formatter.py tests/governance/test_deepseek_non_authorizing.py tests/adversarial/test_no_multi_capability_chain.py tests/phase45/test_dashboard_no_auto_widget_dispatch.py tests/governance/test_legacy_bypass_surfaces_removed.py`
  - Result: `23 passed`
- `python scripts/generate_runtime_docs.py` -> completed
- `python scripts/check_runtime_doc_drift.py` -> passed
- `python scripts/check_frontend_mirror_sync.py` -> passed

## Constitutional Result
- Intelligence-authority separation preserved.
- Invocation-bound behavior restored for patched flows.
- No hidden autonomy path remains in remediated surfaces.
- Phase-4.2 closure remains valid after post-audit hardening.
