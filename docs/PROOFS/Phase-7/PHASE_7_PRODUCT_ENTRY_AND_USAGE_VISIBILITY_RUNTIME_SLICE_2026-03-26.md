# Phase 7 Product Entry And Usage Visibility Runtime Slice
Updated: 2026-03-26
Status: Verified runtime slice

## Purpose
This slice captures three linked product improvements:
- sharper product-entry messaging
- a real landing-preview surface
- honest provider-usage visibility for the governed reasoning lane

## What Landed
- first-run onboarding now highlights one clear magic moment: `explain this`
- the Introduction page now links to a separate landing-preview page
- `/landing` now serves a real product-facing messaging page
- governed reasoning usage now records estimated token awareness through the DeepSeek bridge
- Trust and Settings now surface estimated reasoning usage, budget state, and the current limit note without pretending to know exact billing

## Main Runtime Files
- `nova_backend/src/brain_server.py`
- `nova_backend/src/conversation/deepseek_bridge.py`
- `nova_backend/src/executors/os_diagnostics_executor.py`
- `nova_backend/src/usage/provider_usage_store.py`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/index.html`
- `nova_backend/static/landing.html`

## Main Design / Guide Files
- `docs/design/Phase 6/NOVA_PRODUCT_MESSAGING_HARDENING_AND_APPLICATION_PLAN_2026-03-26.md`
- `docs/design/Phase 7/PHASE_7_PROVIDER_USAGE_AND_BUDGET_VISIBILITY_PLAN_2026-03-26.md`
- `docs/design/Phase 8/PHASE_8_OPENCLAW_CANONICAL_GOVERNED_AUTOMATION_SPEC_2026-03-25.md`
- `docs/design/Phase 8/PHASE_8_OPENCLAW_GOVERNED_EXECUTION_PLAN.md`
- `docs/reference/HUMAN_GUIDES/14_FRONTEND_AND_UI_GUIDE.md`
- `docs/reference/HUMAN_GUIDES/03_WHAT_NOVA_CAN_DO.md`

## Verification
Passed:
- `python -m pytest tests\\conversation\\test_provider_usage_store.py tests\\conversation\\test_deepseek_usage_visibility.py tests\\conversation\\test_deepseek_bridge.py tests\\test_landing_page.py -vv`
- `python -m pytest tests\\phase45\\test_dashboard_onboarding_widget.py tests\\phase45\\test_dashboard_trust_center_widget.py tests\\test_runtime_settings_api.py -vv`
- `python -m pytest tests\\phase45\\test_brain_server_basic_conversation.py -k "bridge_status or connection_status or what_can_you_do_with_question_mark_stays_on_capability_path" -vv`
- `python -m py_compile` on changed backend files
- `node --check nova_backend/static/dashboard.js`

## Honest Boundaries
- provider usage is currently estimated for governed reasoning awareness, not exact billing truth
- exact provider cost parsing remains a later refinement
- the landing-preview page is a product surface, not a replacement for the main dashboard
