# Capability Verification Audit
Date: 2026-03-25
Status: Sequential audit run against current main
Scope: Active governed runtime capabilities from CURRENT_RUNTIME_STATE.md

## [16] governed_web_search
- Method: targeted tests
- Evidence command: `python -m pytest tests\executors\test_web_search_executor.py tests\phase45\test_dashboard_search_widget_followups.py -q`
- Result: PASS
- Summary line: 11 passed in 3.36s
- Audit note: Executor and search-followup widget coverage.

## [17] open_website
- Method: targeted tests
- Evidence command: `python -m pytest tests\executors\test_webpage_launch_executor.py tests\phase45\test_brain_server_website_preview.py -q`
- Result: PASS
- Summary line: 6 passed in 12.89s
- Audit note: Executor planning/open + preview widget path.

## [18] speak_text
- Method: targeted tests + code review note
- Evidence command: `python -m pytest tests\executors\test_tts_executor.py tests\test_governor_mediator_tts.py -q`
- Result: PASS
- Summary line: 5 passed in 2.43s
- Audit note: Executor and mediator parse path are covered, but real-device spoken output still has a known product regression note and needs live hardware validation.

## [19] volume_up_down
- Method: targeted tests
- Evidence command: `python -m pytest tests\executors\test_local_control_executors.py -k "volume_executor" -q`
- Result: PASS
- Summary line: 2 passed, 11 deselected in 0.09s
- Audit note: Executor path verified through mocked OS volume control.

## [20] media_play_pause
- Method: targeted tests
- Evidence command: `python -m pytest tests\executors\test_local_control_executors.py -k "media_executor" -q`
- Result: PASS
- Summary line: 2 passed, 11 deselected in 0.07s
- Audit note: Executor path verified through mocked OS media control.

## [21] brightness_control
- Method: targeted tests
- Evidence command: `python -m pytest tests\executors\test_local_control_executors.py -k "brightness_executor" -q`
- Result: PASS
- Summary line: 1 passed, 12 deselected in 0.07s
- Audit note: Executor path verified through mocked OS brightness control.

## [22] open_file_folder
- Method: targeted tests + conversation simulation
- Evidence command: `python -m pytest tests\executors\test_open_folder_executor.py tests\test_open_folder_executor.py tests\phase45\test_brain_server_basic_conversation.py -k "open_folder or open_explicit_repo_path_confirmation_executes_resolved_repo_path or open_this_repo_confirmation_executes_resolved_repo_path or open_folder_named_workspace_resolves_to_repo_confirmation" -q`
- Result: PASS
- Summary line: 8 passed, 45 deselected in 4.33s
- Audit note: Executor + confirmation-routed conversation flows.

## [31] response_verification
- Method: targeted tests
- Evidence command: `python -m pytest tests\executors\test_response_verification_executor.py tests\test_governor_execution_timeout.py tests\test_brain_server_session_cleanup.py -k "response_verification or verification" -q`
- Result: PASS
- Summary line: 9 passed, 10 deselected in 3.95s
- Audit note: Executor quality + timeout policy + chat surface coverage.

## [32] os_diagnostics
- Method: targeted tests + dashboard contract
- Evidence command: `python -m pytest tests\executors\test_local_control_executors.py tests\phase45\test_dashboard_operator_health_widget.py tests\phase45\test_dashboard_capability_surface_widget.py tests\phase45\test_dashboard_trust_review_widget.py tests\phase45\test_system_status_reporting_contract.py -k "os_diagnostics or operator_health or trust_review or capability_surface or system_status" -q`
- Result: PASS
- Summary line: 18 passed, 5 deselected in 15.31s
- Audit note: Diagnostics executor + operator/trust dashboard surfaces.

## [48] multi_source_reporting
- Method: targeted tests
- Evidence command: `python -m pytest tests\executors\test_multi_source_reporting_executor.py tests\phase45\test_dashboard_intelligence_brief_widget.py -q`
- Result: PASS
- Summary line: 9 passed in 13.99s
- Audit note: Structured reporting executor + dashboard rendering seam.

## [49] headline_summary
- Method: targeted tests
- Evidence command: `python -m pytest tests\executors\test_news_intelligence_executor.py -k "summary or story_page_summary" -q`
- Result: PASS
- Summary line: 12 passed, 8 deselected in 2.47s
- Audit note: Headline summary, comparison, source-page read, and story-page follow-up coverage.

## [50] intelligence_brief
- Method: targeted tests + evaluation
- Evidence command: `python -m pytest tests\executors\test_news_intelligence_executor.py tests\evaluation\test_intelligence_brief_quality.py tests\phase45\test_dashboard_intelligence_brief_widget.py -k "brief or intelligence_brief" -q`
- Result: PASS
- Summary line: 9 passed, 14 deselected in 2.57s
- Audit note: Brief executor, quality contract, and dashboard widget coverage.

## [51] topic_memory_map
- Method: targeted test + code review
- Evidence command: `python -m pytest tests\executors\test_news_intelligence_executor.py -k "topic_map" -q`
- Result: PASS
- Summary line: 1 passed, 19 deselected in 2.31s
- Audit note: Targeted topic-map state update test plus shared news executor path review.

## [52] story_tracker_update
- Method: targeted tests
- Evidence command: `python -m pytest tests\executors\test_story_tracker_executor.py -k "track_update_view_compare_stop or retention_and_relationship_graph" -q`
- Result: PASS
- Summary line: 2 passed, 1 deselected in 0.13s
- Audit note: Track, update, stop, retain, and link actions.

## [53] story_tracker_view
- Method: targeted tests
- Evidence command: `python -m pytest tests\executors\test_story_tracker_executor.py -k "track_update_view_compare_stop or compare_stories or retention_and_relationship_graph" -q`
- Result: PASS
- Summary line: 3 passed in 0.15s
- Audit note: Show, compare, and graph view actions.

## [54] analysis_document
- Method: targeted tests
- Evidence command: `python -m pytest tests\executors\test_analysis_document_executor.py tests\test_governor_execution_timeout.py -k "analysis_document or create_document or summarize_doc or explain_section" -q`
- Result: PASS
- Summary line: 8 passed, 8 deselected in 2.34s
- Audit note: Create, list, summarize, explain, and timeout policy coverage.

## [55] weather_snapshot
- Method: targeted tests
- Evidence command: `python -m pytest tests\executors\test_info_snapshot_executor.py -k "weather_snapshot" -q`
- Result: PASS
- Summary line: 2 passed, 2 deselected in 0.19s
- Audit note: Weather widget success and fallback behavior.

## [56] news_snapshot
- Method: targeted tests
- Evidence command: `python -m pytest tests\executors\test_info_snapshot_executor.py -k "news_snapshot" -q`
- Result: PASS
- Summary line: 1 passed, 3 deselected in 0.19s
- Audit note: Headline snapshot cache and widget path.

## [57] calendar_snapshot
- Method: targeted tests
- Evidence command: `python -m pytest tests\executors\test_info_snapshot_executor.py -k "calendar_snapshot" -q`
- Result: PASS
- Summary line: 1 passed, 3 deselected in 0.19s
- Audit note: Agenda snapshot path.

## [58] screen_capture
- Method: targeted tests
- Evidence command: `python -m pytest tests\phase45\test_screen_capture_executor.py tests\governance\test_screen_capture_requires_invocation.py tests\governance\test_screen_capture_ledger_events.py -k "screen_capture" -q`
- Result: PASS
- Summary line: 11 passed in 0.17s
- Audit note: Invocation gating, ledger coverage, and failure handling.

## [59] screen_analysis
- Method: targeted tests
- Evidence command: `python -m pytest tests\executors\test_screen_analysis_executor.py tests\phase45\test_dashboard_context_insight_widget.py tests\governance\test_screen_capture_ledger_events.py -k "screen_analysis" -q`
- Result: PASS
- Summary line: 3 passed, 5 deselected in 0.12s
- Audit note: Analysis payload shape and dashboard insight rendering.

## [60] explain_anything
- Method: targeted tests
- Evidence command: `python -m pytest tests\executors\test_explain_anything_executor.py tests\phase45\test_explain_anything_router.py tests\governance\test_screen_capture_requires_invocation.py tests\governance\test_screen_capture_ledger_events.py -k "explain_anything" -q`
- Result: PASS
- Summary line: 15 passed, 5 deselected in 0.18s
- Audit note: Router, explicit invocation rule, and executor behavior.

## [61] memory_governance
- Method: targeted tests + conversation simulation
- Evidence command: `python -m pytest tests\phase5\test_memory_governance_executor.py tests\phase45\test_dashboard_memory_widget.py tests\phase45\test_brain_server_basic_conversation.py -k "memory" -q`
- Result: PASS
- Summary line: 22 passed, 38 deselected in 10.56s
- Audit note: Executor, dashboard memory center, and conversation flows.

