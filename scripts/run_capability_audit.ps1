$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $projectRoot "nova_backend"
$reportPath = Join-Path $projectRoot "docs\PROOFS\CAPABILITY_VERIFICATION_AUDIT_2026-03-25.md"

$entries = @(
    @{
        Id = 16
        Name = "governed_web_search"
        Method = "targeted tests"
        Command = "python -m pytest tests\executors\test_web_search_executor.py tests\phase45\test_dashboard_search_widget_followups.py -q"
        Note = "Executor and search-followup widget coverage."
    },
    @{
        Id = 17
        Name = "open_website"
        Method = "targeted tests"
        Command = "python -m pytest tests\executors\test_webpage_launch_executor.py tests\phase45\test_brain_server_website_preview.py -q"
        Note = "Executor planning/open + preview widget path."
    },
    @{
        Id = 18
        Name = "speak_text"
        Method = "targeted tests + code review note"
        Command = "python -m pytest tests\executors\test_tts_executor.py tests\test_governor_mediator_tts.py -q"
        Note = "Executor and mediator parse path are covered, but real-device spoken output still has a known product regression note and needs live hardware validation."
    },
    @{
        Id = 19
        Name = "volume_up_down"
        Method = "targeted tests"
        Command = "python -m pytest tests\executors\test_local_control_executors.py -k ""volume_executor"" -q"
        Note = "Executor path verified through mocked OS volume control."
    },
    @{
        Id = 20
        Name = "media_play_pause"
        Method = "targeted tests"
        Command = "python -m pytest tests\executors\test_local_control_executors.py -k ""media_executor"" -q"
        Note = "Executor path verified through mocked OS media control."
    },
    @{
        Id = 21
        Name = "brightness_control"
        Method = "targeted tests"
        Command = "python -m pytest tests\executors\test_local_control_executors.py -k ""brightness_executor"" -q"
        Note = "Executor path verified through mocked OS brightness control."
    },
    @{
        Id = 22
        Name = "open_file_folder"
        Method = "targeted tests + conversation simulation"
        Command = "python -m pytest tests\executors\test_open_folder_executor.py tests\test_open_folder_executor.py tests\phase45\test_brain_server_basic_conversation.py -k ""open_folder or open_explicit_repo_path_confirmation_executes_resolved_repo_path or open_this_repo_confirmation_executes_resolved_repo_path or open_folder_named_workspace_resolves_to_repo_confirmation"" -q"
        Note = "Executor + confirmation-routed conversation flows."
    },
    @{
        Id = 31
        Name = "response_verification"
        Method = "targeted tests"
        Command = "python -m pytest tests\executors\test_response_verification_executor.py tests\test_governor_execution_timeout.py tests\test_brain_server_session_cleanup.py -k ""response_verification or verification"" -q"
        Note = "Executor quality + timeout policy + chat surface coverage."
    },
    @{
        Id = 32
        Name = "os_diagnostics"
        Method = "targeted tests + dashboard contract"
        Command = "python -m pytest tests\executors\test_local_control_executors.py tests\phase45\test_dashboard_operator_health_widget.py tests\phase45\test_dashboard_capability_surface_widget.py tests\phase45\test_dashboard_trust_review_widget.py tests\phase45\test_system_status_reporting_contract.py -k ""os_diagnostics or operator_health or trust_review or capability_surface or system_status"" -q"
        Note = "Diagnostics executor + operator/trust dashboard surfaces."
    },
    @{
        Id = 48
        Name = "multi_source_reporting"
        Method = "targeted tests"
        Command = "python -m pytest tests\executors\test_multi_source_reporting_executor.py tests\phase45\test_dashboard_intelligence_brief_widget.py -q"
        Note = "Structured reporting executor + dashboard rendering seam."
    },
    @{
        Id = 49
        Name = "headline_summary"
        Method = "targeted tests"
        Command = "python -m pytest tests\executors\test_news_intelligence_executor.py -k ""summary or story_page_summary"" -q"
        Note = "Headline summary, comparison, source-page read, and story-page follow-up coverage."
    },
    @{
        Id = 50
        Name = "intelligence_brief"
        Method = "targeted tests + evaluation"
        Command = "python -m pytest tests\executors\test_news_intelligence_executor.py tests\evaluation\test_intelligence_brief_quality.py tests\phase45\test_dashboard_intelligence_brief_widget.py -k ""brief or intelligence_brief"" -q"
        Note = "Brief executor, quality contract, and dashboard widget coverage."
    },
    @{
        Id = 51
        Name = "topic_memory_map"
        Method = "targeted test + code review"
        Command = "python -m pytest tests\executors\test_news_intelligence_executor.py -k ""topic_map"" -q"
        Note = "Targeted topic-map state update test plus shared news executor path review."
    },
    @{
        Id = 52
        Name = "story_tracker_update"
        Method = "targeted tests"
        Command = "python -m pytest tests\executors\test_story_tracker_executor.py -k ""track_update_view_compare_stop or retention_and_relationship_graph"" -q"
        Note = "Track, update, stop, retain, and link actions."
    },
    @{
        Id = 53
        Name = "story_tracker_view"
        Method = "targeted tests"
        Command = "python -m pytest tests\executors\test_story_tracker_executor.py -k ""track_update_view_compare_stop or compare_stories or retention_and_relationship_graph"" -q"
        Note = "Show, compare, and graph view actions."
    },
    @{
        Id = 54
        Name = "analysis_document"
        Method = "targeted tests"
        Command = "python -m pytest tests\executors\test_analysis_document_executor.py tests\test_governor_execution_timeout.py -k ""analysis_document or create_document or summarize_doc or explain_section"" -q"
        Note = "Create, list, summarize, explain, and timeout policy coverage."
    },
    @{
        Id = 55
        Name = "weather_snapshot"
        Method = "targeted tests"
        Command = "python -m pytest tests\executors\test_info_snapshot_executor.py -k ""weather_snapshot"" -q"
        Note = "Weather widget success and fallback behavior."
    },
    @{
        Id = 56
        Name = "news_snapshot"
        Method = "targeted tests"
        Command = "python -m pytest tests\executors\test_info_snapshot_executor.py -k ""news_snapshot"" -q"
        Note = "Headline snapshot cache and widget path."
    },
    @{
        Id = 57
        Name = "calendar_snapshot"
        Method = "targeted tests"
        Command = "python -m pytest tests\executors\test_info_snapshot_executor.py -k ""calendar_snapshot"" -q"
        Note = "Agenda snapshot path."
    },
    @{
        Id = 58
        Name = "screen_capture"
        Method = "targeted tests"
        Command = "python -m pytest tests\phase45\test_screen_capture_executor.py tests\governance\test_screen_capture_requires_invocation.py tests\governance\test_screen_capture_ledger_events.py -k ""screen_capture"" -q"
        Note = "Invocation gating, ledger coverage, and failure handling."
    },
    @{
        Id = 59
        Name = "screen_analysis"
        Method = "targeted tests"
        Command = "python -m pytest tests\executors\test_screen_analysis_executor.py tests\phase45\test_dashboard_context_insight_widget.py tests\governance\test_screen_capture_ledger_events.py -k ""screen_analysis"" -q"
        Note = "Analysis payload shape and dashboard insight rendering."
    },
    @{
        Id = 60
        Name = "explain_anything"
        Method = "targeted tests"
        Command = "python -m pytest tests\executors\test_explain_anything_executor.py tests\phase45\test_explain_anything_router.py tests\governance\test_screen_capture_requires_invocation.py tests\governance\test_screen_capture_ledger_events.py -k ""explain_anything"" -q"
        Note = "Router, explicit invocation rule, and executor behavior."
    },
    @{
        Id = 61
        Name = "memory_governance"
        Method = "targeted tests + conversation simulation"
        Command = "python -m pytest tests\phase5\test_memory_governance_executor.py tests\phase45\test_dashboard_memory_widget.py tests\phase45\test_brain_server_basic_conversation.py -k ""memory"" -q"
        Note = "Executor, dashboard memory center, and conversation flows."
    }
)

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# Capability Verification Audit")
$lines.Add("Date: 2026-03-25")
$lines.Add("Status: Sequential audit run against current main")
$lines.Add("Scope: Active governed runtime capabilities from CURRENT_RUNTIME_STATE.md")
$lines.Add("")

Push-Location $backendRoot
try {
    foreach ($entry in $entries) {
        Write-Host ("=== [{0}] {1} ===" -f $entry.Id, $entry.Name)
        $output = cmd.exe /c $entry.Command 2>&1
        $exitCode = $LASTEXITCODE
        $nonEmpty = @($output | Where-Object { $_ -and $_.ToString().Trim().Length -gt 0 })
        $tail = if ($nonEmpty.Count -gt 0) { $nonEmpty[-1].ToString().Trim() } else { "No output captured." }
        $status = if ($exitCode -eq 0) { "PASS" } else { "FAIL" }

        $lines.Add(("## [{0}] {1}" -f $entry.Id, $entry.Name))
        $lines.Add("- Method: $($entry.Method)")
        $lines.Add("- Evidence command: ``$($entry.Command)``")
        $lines.Add("- Result: $status")
        $lines.Add("- Summary line: $tail")
        $lines.Add("- Audit note: $($entry.Note)")
        $lines.Add("")

        if ($exitCode -ne 0) {
            $lines.Add("## Audit Halt")
            $lines.Add(("Stopped after capability [{0}] due to a failing verification command." -f $entry.Id))
            $lines.Add("")
            break
        }
    }
}
finally {
    Pop-Location
}

Set-Content -Path $reportPath -Value $lines -Encoding UTF8
Write-Host ("Wrote capability audit to {0}" -f $reportPath)
