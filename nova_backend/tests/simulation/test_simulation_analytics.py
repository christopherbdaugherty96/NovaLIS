from __future__ import annotations

from .analytics import (
    aggregate_simulation_runs,
    export_analytics_html,
    export_analytics_json,
)
from .conversation_runner import build_run_record
from .conversation_simulator import ConversationTranscript, TranscriptTurn


def _sample_run_records():
    t1 = ConversationTranscript(
        turns=[
            TranscriptTurn(
                user_message="search for nuclear energy",
                nova_response="Search results",
                capability_triggered=16,
                capability_executor="web_search_executor",
                governor_decision="governed_invocation",
                execution_time_ms=100,
            ),
            TranscriptTurn(
                user_message="research nuclear energy",
                nova_response="Summary\n...\nKey Findings\n...\nSources\n- reuters.com\n- bbc.com\nConfidence\n0.8",
                capability_triggered=48,
                capability_executor="multi_source_reporting_executor",
                governor_decision="governed_invocation",
                execution_time_ms=240,
            ),
            TranscriptTurn(
                user_message="delete all files",
                nova_response="I can't do that right now.",
                governor_decision="no_route_fallback",
                execution_time_ms=12,
                errors=["I can't do that right now."],
            ),
        ]
    )
    t2 = ConversationTranscript(
        turns=[
            TranscriptTurn(
                user_message="system status",
                nova_response="System diagnostics ready.",
                capability_triggered=32,
                capability_executor="os_diagnostics_executor",
                governor_decision="governed_invocation",
                execution_time_ms=50,
            ),
            TranscriptTurn(
                user_message="research semiconductors",
                nova_response="Summary\n...\nKey Findings\n...\nSources\n- abcnews.go.com\n- foxnews.com\nConfidence\n0.7",
                capability_triggered=48,
                capability_executor="WRONG_EXECUTOR",
                governor_decision="governed_invocation",
                execution_time_ms=310,
                errors=["degraded"],
            ),
            TranscriptTurn(
                user_message="test unknown capability",
                nova_response="unknown",
                capability_triggered=999,
                capability_executor="unknown_exec",
                governor_decision="governed_invocation",
                execution_time_ms=5,
            ),
        ]
    )
    return [
        build_run_record(t1, scenario="scenario_a", profile="test", passed=True),
        build_run_record(t2, scenario="scenario_b", profile="test", passed=False),
    ]


def test_simulation_analytics_is_deterministic_and_complete(tmp_path):
    records = _sample_run_records()
    analytics = aggregate_simulation_runs(records)

    assert analytics["run_metadata"]["run_count"] == 2
    assert analytics["run_metadata"]["profiles"]["test"] == 2
    assert analytics["summary"]["total_turns"] == 6
    assert analytics["summary"]["run_count"] == 2
    assert analytics["summary"]["scenario_transcript_count"] == 2
    assert analytics["turn_latency"]["p95_turn_latency_ms"] >= analytics["turn_latency"]["p50_turn_latency_ms"]
    assert "3" in analytics["capability_chain_length"]
    assert analytics["capabilities"]["16"]["count"] == 1
    assert analytics["capabilities"]["48"]["count"] == 2
    assert analytics["executors"]["web_search_executor"]["count"] == 1
    assert analytics["executors"]["os_diagnostics_executor"]["count"] == 1
    assert analytics["integrity"]["capability_executor_mismatch_count"] >= 1
    assert analytics["integrity"]["unknown_capability_count"] >= 1
    assert analytics["integrity"]["structured_report_schema_total"] >= 1
    assert analytics["integrity"]["structured_report_schema_compliant"] >= 0
    assert 0.0 <= analytics["integrity"]["structured_report_schema_compliance_rate"] <= 1.0
    assert analytics["governor_decisions"]["governed_invocation"] >= 1
    assert analytics["scenarios"]["scenario_a"]["transcript_count"] == 1
    assert analytics["scenarios"]["scenario_b"]["transcript_count"] == 1
    assert analytics["top_failing_user_prompts"]

    json_path = export_analytics_json(analytics, tmp_path / "analytics.json")
    html_path = export_analytics_html(analytics, tmp_path / "analytics.html")
    assert json_path.exists()
    assert html_path.exists()
