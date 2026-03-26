# Phase 5 Trust, Onboarding, Voice, Workspace, And Visualizer Runtime Slice
Date: 2026-03-26
Status: Implemented in the current repository state on `main`
Scope: Land the first unified Trust Center page, first-run onboarding, stronger end-to-end TTS runtime behavior, a broader Workspace page, and the first human-facing local-project structure map without widening authority

## What Landed
This runtime slice closes a product gap more than a raw capability gap.

Nova now has:
- a dedicated `Trust` page with recent governed actions, blocked conditions, runtime health, and live capability-group visibility
- a dedicated `Workspace` page that extends the Home-page Workspace Home surface into a broader board for project continuity
- a first-run guide that points a non-technical user toward Home, Workspace, Trust, and explicit memory behavior
- a first user-facing local-project structure map surface in the dashboard
- stronger voice auto-speak behavior for voice-origin turns, with renderer fallback at the runtime speech layer

Important boundary:
- none of this adds silent autonomy
- none of this bypasses the Governor path
- the new pages are visibility and usability improvements, not new authority surfaces

## Why This Matters
Before this slice, Nova already had trust, workspace, local-project, and voice pieces.

The problem was that they were not yet packaged in the way a normal user would understand them.

This slice matters because it turns:
- trust review into a dedicated page
- workspace continuity into a clearer project board
- local-project understanding into a visible structure map
- first-run product orientation into an explicit guided surface
- the TTS path into a stronger end-to-end runtime chain for voice-triggered responses

For a non-technical user, this is a real product improvement, not just an internal code improvement.

## Runtime Behavior
### 1. Trust Center Is Now A Real Page
Nova now supports:
- `trust center`
- `trust review`
- `trust status`

The Trust page can now show:
- current operating mode
- last external call
- data-egress summary
- failure state
- recent governed runtime actions
- blocked conditions
- runtime health chips
- live capability groups

### 2. Workspace Board Extends Continuity Into A Clearer Daily Surface
Nova now supports:
- `workspace board`
- `project board`
- `project workspace`

The Workspace page now combines:
- focus project state
- thread summary visibility
- recent reports and project memory
- structure-map visibility
- calmer next actions tied to existing governed commands

### 3. Local Project Visualizer Stage 1 Is Live
Nova now supports:
- `show structure map`
- `show repo map`
- `visualize this repo`
- `visualize this project`

The result is a read-only structure map that:
- shows major folders and code surfaces
- attaches plain-language meaning to important nodes
- stays grounded in local repo structure and high-signal files

### 4. First-Run Guidance Is Now A Product Surface
The dashboard now opens a first-run modal when needed and gives clear entry points to:
- Home
- Workspace
- Trust
- Morning brief

The guide also explains that Nova remains invocation-bound and that explicit memory is user-controlled.

### 5. Voice Auto-Speak Is Stronger End To End
Voice-origin turns now route through a shared runtime speech helper that:
- converts the answer into speakable text
- stores the last spoken text
- uses the normal Nova speech path
- falls back to the TTS executor engine when the preferred renderer cannot play

This improves the real product loop for:
- voice question in
- answer on screen
- answer spoken back

Caveat:
- hardware/device validation still matters for final real-world confidence
- this slice improves the runtime path and fallback behavior; it does not claim universal audio-device closure

## Files Touched
- `nova_backend/src/brain_server.py`
- `nova_backend/src/voice/tts_engine.py`
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/style.phase1.css`
- `Nova-Frontend-Dashboard/index.html`
- `Nova-Frontend-Dashboard/dashboard.js`
- `Nova-Frontend-Dashboard/style.phase1.css`
- `nova_backend/tests/rendering/test_tts_engine.py`
- `nova_backend/tests/phase45/test_dashboard_workspace_board_widget.py`
- `nova_backend/tests/phase45/test_dashboard_trust_center_widget.py`
- `nova_backend/tests/phase45/test_dashboard_onboarding_widget.py`
- `nova_backend/tests/phase45/test_brain_server_basic_conversation.py`

## Validation
Focused TTS/runtime bundle:
```powershell
python -m pytest tests\rendering\test_tts_engine.py tests\executors\test_tts_executor.py -vv
```

Result:
- `6 passed`

Focused new dashboard surface bundle:
```powershell
python -m pytest tests\phase45\test_dashboard_workspace_board_widget.py tests\phase45\test_dashboard_trust_center_widget.py tests\phase45\test_dashboard_onboarding_widget.py -vv
```

Result:
- `6 passed`

Focused conversation-path bundle:
```powershell
python -m pytest tests\phase45\test_brain_server_basic_conversation.py -k "trust_center or structure_map or workspace_board or voice_time or voice_general_chat" -vv
```

Result:
- `5 passed`

Broader regression bundle:
```powershell
python -m pytest tests\phase45\test_brain_server_basic_conversation.py tests\phase45\test_brain_server_trust_status.py tests\phase45\test_dashboard_workspace_board_widget.py tests\phase45\test_dashboard_trust_center_widget.py tests\phase45\test_dashboard_onboarding_widget.py tests\phase45\test_dashboard_workspace_home_widget.py tests\phase45\test_dashboard_trust_review_widget.py tests\phase45\test_dashboard_memory_widget.py tests\phase45\test_dashboard_phase7_chat_controls.py tests\phase45\test_dashboard_operator_health_widget.py tests\phase45\test_dashboard_capability_surface_widget.py tests\phase45\test_dashboard_header_and_news_refinement.py tests\phase45\test_dashboard_system_status_widget.py tests\phase45\test_dashboard_tone_widget.py tests\phase45\test_dashboard_brief_shortcuts.py tests\phase45\test_dashboard_search_widget_followups.py tests\conversation\test_response_style_router.py tests\conversation\test_response_formatter.py tests\conversation\test_session_router.py tests\conversation\test_conversation_router.py tests\conversation\test_general_chat_tone.py tests\conversation\test_personality_interface_agent.py tests\test_tierb_conversation.py tests\executors\test_news_intelligence_executor.py tests\executors\test_web_search_executor.py tests\executors\test_tts_executor.py tests\rendering\test_tts_engine.py tests\adversarial\test_tts_spine_integrity.py tests\test_governor_execution_timeout.py -vv
```

Result:
- `222 passed`

Repo-health checks:
```powershell
node --check nova_backend\static\dashboard.js
python scripts\check_frontend_mirror_sync.py
python scripts\check_runtime_doc_drift.py
```

Results:
- dashboard script syntax check passed
- frontend mirror sync check passed
- runtime documentation drift check passed

## Manual Simulation Notes
Websocket-style simulation confirmed these user flows:

1. `trust center`
- returned `trust_status`
- returned a Trust Center summary message with recent actions and blocked conditions

2. `workspace board`
- returned `workspace_home`
- returned `thread_map`
- returned `project_structure_map`
- returned a short Workspace Home summary message

3. `visualize this repo`
- returned `project_structure_map`
- returned a readable local project structure map message grounded in the current repo

4. voice `what time is it`
- produced spoken output text: `It's 10:15 AM.` via the runtime speech helper

## Trust Notes
This slice does not introduce:
- automatic background action
- autonomous task execution
- hidden memory creation
- silent provider expansion
- hidden page-triggered execution

It does improve:
- product legibility
- trust review clarity
- onboarding clarity
- workspace continuity visibility
- voice-loop reliability
- local-project explanation for non-technical users

## Best Follow-On
The next strongest product steps after this slice are:
1. deeper project/workspace system work
2. richer trust-center history and drill-down
3. onboarding stage 2 with permissions and setup guidance
4. stronger visualizer stage 2 structured graph output
5. final real-device TTS confidence pass
