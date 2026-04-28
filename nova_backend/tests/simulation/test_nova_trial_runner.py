from __future__ import annotations

import json

from .nova_trial_runner import render_trial_report, run_trial_scenarios
from .trial_evaluator import evaluate_trial, prioritize_gaps
from .conversation_simulator import ConversationTranscript, TranscriptTurn


def test_trial_evaluator_reports_capability_sequence_gap():
    scenario = {
        "name": "routing_gap",
        "script": ["search for python"],
        "expect": {"capability_sequence": [16]},
    }
    transcript = ConversationTranscript(
        turns=[
            TranscriptTurn(
                user_message="search for python",
                nova_response="I am not sure.",
                governor_decision="no_route_fallback",
            )
        ]
    )

    evaluation = evaluate_trial(scenario, transcript)
    gaps = prioritize_gaps([evaluation])

    assert evaluation["passed"] is False
    assert gaps[0]["category"] == "routing"
    assert gaps[0]["scenario"] == "routing_gap"


def test_trial_evaluator_ignores_malformed_fragment_rules():
    scenario = {
        "name": "malformed_rules",
        "script": ["hello nova"],
        "expect": {
            "required_response_fragments": [{"turn": "later", "contains": "hello"}],
            "forbidden_response_fragments": [{"turn": None, "contains": "goodbye"}],
        },
    }
    transcript = ConversationTranscript(
        turns=[
            TranscriptTurn(
                user_message="hello nova",
                nova_response="hello",
                governor_decision="chat",
            )
        ]
    )

    evaluation = evaluate_trial(scenario, transcript)

    assert evaluation["passed"] is True


def test_trial_evaluator_ignores_malformed_list_expectations():
    scenario = {
        "name": "malformed_expectations",
        "script": "hello nova",
        "expect": {
            "capability_sequence": 16,
            "governor_decisions": "chat",
            "required_response_fragments": {"turn": 1, "contains": "hello"},
        },
    }
    transcript = ConversationTranscript(
        turns=[
            TranscriptTurn(
                user_message="hello nova",
                nova_response="hello",
                governor_decision="chat",
            )
        ]
    )

    evaluation = evaluate_trial(scenario, transcript)

    assert evaluation["passed"] is False
    assert evaluation["gaps"][0]["category"] == "transcript"


def test_trial_evaluator_checks_policy_blocks_and_clarifications():
    scenario = {
        "name": "guardrails",
        "script": ["do unsafe thing", "open it"],
        "expect": {
            "no_policy_blocks": False,
            "policy_block_turns": [1],
            "clarification_turns": [2],
        },
    }
    transcript = ConversationTranscript(
        turns=[
            TranscriptTurn(
                user_message="do unsafe thing",
                nova_response="I can't help with that.",
                policy_blocked=True,
                governor_decision="policy_block",
            ),
            TranscriptTurn(
                user_message="open it",
                nova_response="What should I open?",
                clarification_triggered=True,
                governor_decision="clarification",
            ),
        ]
    )

    evaluation = evaluate_trial(scenario, transcript)

    assert evaluation["passed"] is True


def test_render_trial_report_includes_prioritized_gaps():
    report = render_trial_report(
        {
            "generated_at": "2026-04-21T00:00:00+00:00",
            "scenario_count": 1,
            "passed_count": 0,
            "failed_count": 1,
            "environment": {
                "usage_budget_state": "normal",
                "local_model_state": "available_or_fallback",
            },
            "evaluations": [
                {
                    "scenario": "routing_gap",
                    "passed": False,
                    "score": 0.7,
                    "gap_count": 1,
                    "capability_sequence": [],
                }
            ],
            "prioritized_gaps": [
                {
                    "severity": "high",
                    "scenario": "routing_gap",
                    "category": "routing",
                    "message": "Capability sequence did not match.",
                    "expected": [16],
                    "actual": [{"prompt": "open settings", "errors": ["Settings â†’ Usage"]}],
                }
            ],
            "analytics": {"summary": {"total_turns": 1, "error_rate": 0.0}},
            "run_log_dir": "logs",
            "analytics_path": "analytics.json",
        }
    )

    assert "# Nova Trial Report" in report
    assert "[HIGH] routing_gap / routing" in report
    assert "Environment: budget=normal" in report
    assert "## Gap Summary" in report
    assert "By severity: high=1" in report
    assert "By category: routing=1" in report
    assert "```json" in report
    assert '"prompt": "example"' not in report
    assert "Settings -> Usage" in report
    assert "Expected: \n```json\n[\n  16\n]\n```" in report

    unicode_report = render_trial_report(
        {
            "prioritized_gaps": [
                {
                    "severity": "low",
                    "scenario": "weather_gap",
                    "category": "response_quality",
                    "message": "Unicode cleanup check.",
                    "actual": ["72\u00b0F", "Settings \u2192 Usage"],
                }
            ],
        }
    )
    assert "72F" in unicode_report
    assert "Settings -> Usage" in unicode_report


def test_run_trial_scenarios_writes_logs_analytics_and_report(tmp_path):
    scenario_dir = tmp_path / "scenarios"
    scenario_dir.mkdir()
    (scenario_dir / "casual_checkin.json").write_text(
        json.dumps(
            {
                "name": "casual_checkin",
                "script": ["hello nova"],
                "expect": {},
            }
        ),
        encoding="utf-8",
    )

    summary = run_trial_scenarios(scenario_dir, tmp_path / "trial_out")

    assert summary["scenario_count"] == 1
    assert summary["passed_count"] == 1
    assert summary["failed_count"] == 0
    assert summary["prioritized_gaps"] == []
    assert (tmp_path / "trial_out" / "logs" / "casual_checkin.json").exists()
    assert (tmp_path / "trial_out" / "analytics.json").exists()
    report_path = tmp_path / "trial_out" / "latest_trial_report.md"
    assert report_path.exists()
    assert "PASS `casual_checkin`" in report_path.read_text(encoding="utf-8")


def test_run_trial_scenarios_handles_malformed_expect_and_duplicate_names(tmp_path):
    scenario_dir = tmp_path / "scenarios"
    scenario_dir.mkdir()
    payload = {
        "name": "duplicate",
        "script": ["hello nova"],
        "expect": "not a dict",
    }
    (scenario_dir / "first.json").write_text(json.dumps(payload), encoding="utf-8")
    (scenario_dir / "second.json").write_text(json.dumps(payload), encoding="utf-8")

    summary = run_trial_scenarios(scenario_dir, tmp_path / "trial_out")

    assert summary["scenario_count"] == 2
    assert (tmp_path / "trial_out" / "logs" / "duplicate.json").exists()
    assert (tmp_path / "trial_out" / "logs" / "duplicate_2.json").exists()


def test_trial_runner_script_supports_direct_execution_imports():
    import runpy
    from pathlib import Path

    script = str(Path(__file__).parent / "nova_trial_runner.py")
    namespace = runpy.run_path(
        script,
        run_name="nova_trial_runner_import_check",
    )

    assert callable(namespace["run_trial_scenarios"])
    assert namespace["default_output_dir"]().name == "reports"
