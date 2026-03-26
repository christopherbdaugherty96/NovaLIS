# Phase-5 Agent OS Stage-3 Product Surfaces Runtime Slice
Date: 2026-03-26
Status: Implemented on `main`
Scope: Deepen the non-technical-user product shell with Introduction and Settings pages, stronger Workspace and Trust drill-down, Structure Map stage 2 graph output, and clearer voice runtime confidence surfaces.

## Purpose
This slice turns several previously separate improvements into a calmer product layer for a normal user.

It specifically closes these gaps:
- deeper Workspace system work
- Trust Center stage 2 history and drill-down
- onboarding stage 2 setup and permissions guidance
- Structure Map stage 2 structured graph output
- user-visible voice runtime status and voice-check workflow

It does **not** claim that future phases are live.
Phase 7 remains partially live.
Phase 8+ remain designed, not runtime-authorized.

## Runtime Surfaces Added Or Deepened
1. Introduction page
- dedicated dashboard page
- plain-language explanation of what Nova is
- setup-mode overview
- first steps for non-technical users

2. Settings page
- explicit setup-mode selector:
  - Local Mode
  - Bring Your Own API Key
  - Managed Cloud Access
- local accessibility toggles
- voice status summary
- voice check launch path
- links back to Introduction, Home, and Trust

3. Workspace page stage 3
- selected-project drill-down stays on Workspace
- recent decisions feed
- stronger thread selection and switching without bouncing the user back into chat

4. Trust Center stage 2
- recent governed actions now support selection and detail drill-down
- blocked conditions now support selection and detail drill-down
- voice runtime section added
- settings handoff added

5. Structure Map stage 2
- structured graph summary
- graph nodes
- relationship list
- legend
- still read-only and explanatory

6. Voice confidence surface
- `voice status` returns runtime state and refreshes trust data
- `voice check` runs the governed TTS path and refreshes trust data
- speech runtime now records engine, status, error, and last attempt timestamp

## Code Surfaces Updated
Backend:
- `nova_backend/src/brain_server.py`
- `nova_backend/src/speech_state.py`
- `nova_backend/src/voice/tts_engine.py`
- `nova_backend/src/executors/tts_executor.py`

Frontend runtime:
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/style.phase1.css`

Frontend mirror:
- `Nova-Frontend-Dashboard/index.html`
- `Nova-Frontend-Dashboard/dashboard.js`
- `Nova-Frontend-Dashboard/style.phase1.css`

Validation:
- `nova_backend/tests/phase45/test_brain_server_basic_conversation.py`
- `nova_backend/tests/phase45/test_dashboard_onboarding_widget.py`
- `nova_backend/tests/phase45/test_dashboard_trust_center_widget.py`
- `nova_backend/tests/phase45/test_dashboard_workspace_board_widget.py`
- `nova_backend/tests/rendering/test_tts_engine.py`

## Verification Run For This Slice
Focused:
- `python -m pytest tests\phase45\test_dashboard_onboarding_widget.py tests\phase45\test_dashboard_workspace_board_widget.py tests\phase45\test_dashboard_trust_center_widget.py tests\rendering\test_tts_engine.py -q`
  - result: `10 passed`
- `python -m pytest tests\phase45\test_brain_server_basic_conversation.py -k "trust_center_command_returns_summary_and_status_widget or visualize_this_repo_returns_structure_map_and_widget or workspace_board_command_sends_workspace_thread_and_structure_widgets or workspace_board_prefers_selected_thread_detail_when_focus_exists or voice_status_command_returns_runtime_summary_and_trust_widget or voice_check_command_runs_tts_capability_and_reports_status" -q`
  - result: `6 passed`

Broader regression:
- `python -m pytest tests\phase45\test_dashboard_onboarding_widget.py tests\phase45\test_dashboard_workspace_board_widget.py tests\phase45\test_dashboard_trust_center_widget.py tests\phase45\test_dashboard_workspace_home_widget.py tests\phase45\test_dashboard_memory_widget.py tests\phase45\test_brain_server_basic_conversation.py tests\rendering\test_tts_engine.py tests\conversation\test_response_style_router.py tests\conversation\test_response_formatter.py tests\conversation\test_session_router.py tests\conversation\test_conversation_router.py tests\phase45\test_brain_server_tone_commands.py tests\conversation\test_general_chat_tone.py tests\conversation\test_personality_interface_agent.py tests\test_tierb_conversation.py -q`
  - result: `165 passed`

Repo-health checks:
- `node --check nova_backend/static/dashboard.js`
- `python scripts/check_frontend_mirror_sync.py`
- `python scripts/check_runtime_doc_drift.py`
  - all passed

## Product Meaning
After this slice, Nova is easier to enter, easier to configure honestly, easier to inspect, and easier to continue work in.

The most important product change is not a new capability ID.
It is that the dashboard is now closer to a real governed workspace for a non-technical person:
- Introduction explains the system
- Settings stores explicit product choices
- Workspace keeps project detail in one place
- Trust shows more of the why behind actions
- Voice has a visible confidence path instead of a silent hope-based path

## Remaining Honest Gaps After This Slice
1. Real-device audible confirmation is still the final voice caveat.
2. Provider connection and permission setup are still preference-first, not full connector management.
3. Workspace continuity can still deepen beyond the current stage-3 shell.
4. Phase 7 still needs richer structured intelligence routing and provider transparency.
5. Phase 8+ remain documented only.

## Conclusion
This slice completes the requested current product-surface work without loosening governance.
It improves:
- clarity
- inspectability
- continuity
- onboarding
- user confidence

while keeping Nova:
- invocation-bound
- governed
- visible
- phase-honest
