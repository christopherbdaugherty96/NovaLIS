from src.openclaw.strict_preflight import evaluate_manual_envelope, strict_foundation_snapshot
from src.openclaw.task_envelope import TaskEnvelope


def test_strict_foundation_snapshot_reports_current_limits():
    snapshot = strict_foundation_snapshot()

    assert snapshot["status"] == "active"
    assert snapshot["label"] == "Manual preflight active"
    assert "weather" in snapshot["allowed_tools"]


def test_evaluate_manual_envelope_accepts_supported_brief():
    envelope = TaskEnvelope(
        id="ENV-OK",
        title="Morning Brief",
        template_id="morning_brief",
        tools_allowed=["weather", "calendar", "news", "schedules", "summarize"],
        allowed_hostnames=["weather.visualcrossing.com", "feeds.npr.org"],
        max_steps=6,
        max_duration_s=90,
        max_network_calls=8,
        max_files_touched=1,
        max_bytes_read=500000,
        max_bytes_written=0,
        triggered_by="agent_page",
    )

    decision = evaluate_manual_envelope(envelope)

    assert decision.allowed is True
    assert decision.violations == []


def test_evaluate_manual_envelope_rejects_unsupported_tool():
    envelope = TaskEnvelope(
        id="ENV-BLOCK",
        title="Inbox Check",
        template_id="inbox_check",
        tools_allowed=["email_read", "summarize"],
        allowed_hostnames=[],
        max_steps=4,
        max_duration_s=60,
        max_network_calls=0,
        max_files_touched=0,
        max_bytes_read=0,
        max_bytes_written=0,
        triggered_by="agent_page",
    )

    decision = evaluate_manual_envelope(envelope)

    assert decision.allowed is False
    assert any("unsupported_tools" in item for item in decision.violations)


def test_evaluate_manual_envelope_requires_hostnames_for_networked_tools():
    envelope = TaskEnvelope(
        id="ENV-HOSTS",
        title="Morning Brief",
        template_id="morning_brief",
        tools_allowed=["weather", "news", "summarize"],
        allowed_hostnames=[],
        max_steps=4,
        max_duration_s=60,
        max_network_calls=4,
        max_files_touched=0,
        max_bytes_read=1000,
        max_bytes_written=0,
        triggered_by="agent_page",
    )

    decision = evaluate_manual_envelope(envelope)

    assert decision.allowed is False
    assert "allowed_hostnames_missing" in decision.violations
