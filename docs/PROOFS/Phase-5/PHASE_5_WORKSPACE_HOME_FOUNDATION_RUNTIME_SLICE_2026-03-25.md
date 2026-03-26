# Phase 5 Workspace Home Foundation Runtime Slice
Date: 2026-03-25
Status: Implemented in the current repository state on `main`
Scope: Add a calm Home-page workspace operating surface that brings project continuity, governed memory, recent reports, and next actions together without widening authority

## What Landed
This runtime slice turns the Home page into a more useful daily workspace surface.

Nova now has a governed Workspace Home card that can:
- summarize the active workspace state
- highlight the current focus project
- surface current blocker, next step, and latest decision
- show recent project memory and recent analysis docs
- reflect recent trust activity and blocked conditions
- offer calm next-action buttons tied to existing governed commands

Important boundary:
- this is a product-layer consolidation, not a new authority layer
- the Workspace Home surface does not execute anything on its own
- all action buttons still route through the existing chat + governor path

## Why This Matters
Before this slice, Nova had:
- thread continuity
- explicit governed memory
- analysis documents
- trust review

But these lived in separate surfaces.

Workspace Home is the first product layer that brings those pieces together in one calmer place for a non-technical user.

It is the bridge between:
- `Nova has continuity tools`
and
- `Nova feels like an ongoing workspace`

## Runtime Behavior
### 1. `workspace home` Is Now A Real Runtime Command
Nova now supports:
- `workspace home`
- `project home`
- `show workspace home`

Explicit invocation returns:
- a `workspace_home` widget payload
- a short chat summary when the request is not a silent widget refresh

### 2. Silent Home Hydration Keeps The UI Calm
The Home page now silently refreshes:
- `show threads`
- `workspace home`

This means the Home page can stay current without adding command noise into chat during ordinary page review.

### 3. Workspace Home Uses Existing Governed Sources
The new surface is built from existing governed/runtime sources:
- project thread summaries
- governed memory overview and thread-linked memory
- session analysis documents
- trust review activity and blocked conditions

This matters because the surface is:
- grounded
- inspectable
- aligned with existing runtime truth

### 4. Recommended Actions Stay Bounded
Workspace Home can suggest actions such as:
- continue the focus project
- open project status
- review thread memory
- list analysis docs
- open Memory Center

These are convenience paths into already governed flows, not silent execution shortcuts.

## Files Touched
- `nova_backend/src/brain_server.py`
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/style.phase1.css`
- `Nova-Frontend-Dashboard/index.html`
- `Nova-Frontend-Dashboard/dashboard.js`
- `Nova-Frontend-Dashboard/style.phase1.css`
- `nova_backend/tests/phase45/test_brain_server_basic_conversation.py`
- `nova_backend/tests/phase45/test_dashboard_workspace_home_widget.py`

## Validation
Focused workspace-home bundle:
```powershell
python -m pytest tests\phase45\test_dashboard_workspace_home_widget.py tests\phase45\test_brain_server_basic_conversation.py -k "workspace_home or silent_memory_overview_refresh or silent_memory_list_refresh or silent_memory_show_refresh" -q
```

Result:
- `7 passed`

Broader dashboard/home regression:
```powershell
python -m pytest tests\phase45\test_dashboard_workspace_home_widget.py tests\phase45\test_dashboard_memory_widget.py tests\phase45\test_dashboard_operator_health_widget.py tests\phase45\test_dashboard_trust_review_widget.py tests\phase45\test_dashboard_phase7_chat_controls.py tests\phase45\test_brain_server_basic_conversation.py tests\phase45\test_dashboard_auto_widget_dispatch.py tests\phase45\test_dashboard_no_auto_widget_dispatch.py -q
```

Result:
- `66 passed`

Conversation / tone / governor safety bundle:
```powershell
python -m pytest tests\conversation\test_response_style_router.py tests\conversation\test_response_formatter.py tests\conversation\test_session_router.py tests\conversation\test_conversation_router.py tests\test_governor_execution_timeout.py tests\test_tierb_conversation.py tests\phase45\test_brain_server_tone_commands.py tests\conversation\test_general_chat_tone.py tests\conversation\test_personality_interface_agent.py -q
```

Result:
- `102 passed`

Repo-health checks:
```powershell
node --check nova_backend\static\dashboard.js
python scripts\generate_runtime_docs.py
python scripts\check_runtime_doc_drift.py
python scripts\check_frontend_mirror_sync.py
```

Results:
- dashboard script syntax check passed
- runtime documentation drift check passed
- frontend mirror sync check passed

## Trust Notes
This runtime slice does not introduce:
- new execution authority
- background automation
- hidden project-state mutation
- implicit memory creation
- unlogged task flow

It improves:
- workspace legibility
- continuity visibility
- calm next-step guidance
- daily product usability for non-technical users

## Best Follow-On
The next clean implementation step after this slice is:
- `codex/trust-center-stage1-recent-actions`

Reason:
- Workspace Home now gives Nova a calmer operating surface
- the next highest-value user need is one clearer place to review actions, approvals, blocks, and why Nova did what it did
