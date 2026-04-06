from datetime import datetime
from pathlib import Path

from src.openclaw.agent_runtime_store import OpenClawAgentRuntimeStore


def test_agent_runtime_store_bootstraps_templates(tmp_path: Path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")

    snapshot = store.snapshot()

    assert snapshot["status"] == "foundation"
    assert snapshot["template_count"] >= 3
    assert snapshot["delivery_ready_count"] == 0
    assert snapshot["strict_foundation_label"] == "Manual preflight active"
    assert any(item["id"] == "morning_brief" for item in snapshot["templates"])
    assert any(item["id"] == "market_watch" for item in snapshot["templates"])
    morning = next(item for item in snapshot["templates"] if item["id"] == "morning_brief")
    assert morning["envelope_preview"]["max_network_calls"] == 11
    assert morning["envelope_preview"]["max_files_touched"] == 1
    assert morning["envelope_preview"]["read_only"] is True
    assert "weather.visualcrossing.com" in morning["envelope_preview"]["allowed_hostnames"]
    assert "Can only reach:" in morning["envelope_preview"]["scope_summary"]


def test_agent_runtime_store_updates_delivery_mode(tmp_path: Path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")

    updated = store.set_template_delivery_mode("morning_brief", "chat")

    morning = next(item for item in updated["templates"] if item["id"] == "morning_brief")
    assert morning["delivery_mode"] == "chat"


def test_agent_runtime_store_tracks_active_run(tmp_path: Path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")

    store.set_active_run(
        {
            "envelope_id": "ENV-RUN-1",
            "template_id": "morning_brief",
            "title": "Morning Brief",
            "triggered_by": "agent_page",
            "delivery_mode": "hybrid",
            "delivery_channels": {"widget": True, "chat": True},
            "started_at": "2026-04-03T11:00:00+00:00",
            "summary": "Collecting sources.",
            "scope_summary": "Tools: weather, calendar.",
            "budget_summary": "Can take up to 6 steps.",
            "budget_usage": {"summary": "Used so far: 2/6 steps."},
        }
    )

    snapshot = store.snapshot()

    assert snapshot["active_run"]["envelope_id"] == "ENV-RUN-1"
    assert snapshot["active_run"]["template_id"] == "morning_brief"
    assert snapshot["active_run"]["scope_summary"] == "Tools: weather, calendar."
    assert snapshot["active_run"]["budget_summary"] == "Can take up to 6 steps."
    assert snapshot["active_run"]["budget_usage"]["summary"] == "Used so far: 2/6 steps."
    assert snapshot["active_run_summary"] == "Morning Brief is running now from the Run now flow."

    updated = store.update_active_run(
        "ENV-RUN-1",
        {
            "status_label": "Summarizing",
            "summary": "Turning collected inputs into the final result.",
            "budget_usage": {"summary": "Used so far: 3/6 steps."},
        },
    )

    assert updated is not None
    snapshot = store.snapshot()
    assert snapshot["active_run"]["status_label"] == "Summarizing"
    assert snapshot["active_run"]["budget_usage"]["summary"] == "Used so far: 3/6 steps."
    assert snapshot["active_run_summary"] == "Morning Brief is summarizing from the Run now flow."

    store.clear_active_run("ENV-RUN-1")

    cleared = store.snapshot()
    assert cleared["active_run"] is None
    assert cleared["active_run_summary"] == "No home-agent runs are active right now."


def test_agent_runtime_store_records_surface_delivery_and_dismisses_it(tmp_path: Path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")

    store.record_run(
        {
            "envelope_id": "ENV-123",
            "template_id": "morning_brief",
            "title": "Morning Brief",
            "delivery_mode": "hybrid",
            "delivery_channels": {"widget": True, "chat": True},
            "presented_message": "Here's your morning.",
            "summary": "Here's your morning.",
            "usage_meta": {"route": "local_model", "summary": "Stayed local."},
        }
    )

    snapshot = store.snapshot()
    assert snapshot["delivery_ready_count"] == 1
    delivery = snapshot["delivery_inbox"][0]
    assert delivery["template_id"] == "morning_brief"
    assert delivery["usage_meta"]["route"] == "local_model"

    updated = store.dismiss_delivery(delivery["id"])
    assert updated["delivery_ready_count"] == 0


def test_agent_runtime_store_can_enable_template_schedule(tmp_path: Path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")

    snapshot = store.set_template_schedule_enabled("morning_brief", True)

    morning = next(item for item in snapshot["templates"] if item["id"] == "morning_brief")
    assert morning["schedule_enabled"] is True
    assert morning["schedule_status"] == "Scheduled"
    assert morning["next_run_label"].startswith("Next at ")


def test_agent_runtime_store_claims_due_schedule_only_once_per_window(tmp_path: Path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    store.set_template_schedule_enabled("morning_brief", True)
    now = datetime.now().astimezone().replace(hour=7, minute=5, second=0, microsecond=0)

    first_claim = store.claim_due_scheduled_templates(now=now)
    second_claim = store.claim_due_scheduled_templates(now=now)

    assert len(first_claim) == 1
    assert first_claim[0]["template_id"] == "morning_brief"
    assert second_claim == []


def test_agent_runtime_store_records_scheduled_run_outcome(tmp_path: Path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    store.set_template_schedule_enabled("morning_brief", True)

    snapshot = store.record_scheduled_run_outcome(
        "morning_brief",
        outcome="completed",
        note="Scheduled run completed.",
        now=datetime.now().astimezone(),
    )

    morning = next(item for item in snapshot["templates"] if item["id"] == "morning_brief")
    assert morning["last_scheduled_outcome"] == "completed"
    assert morning["last_scheduled_note"] == "Scheduled run completed."


def test_agent_runtime_store_skips_stale_same_day_schedule_windows(tmp_path: Path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")
    store.set_template_schedule_enabled("morning_brief", True)
    late_evening = datetime.now().astimezone().replace(hour=18, minute=0, second=0, microsecond=0)

    due = store.due_scheduled_templates(now=late_evening)
    snapshot = store.snapshot()

    assert due == []
    morning = next(item for item in snapshot["templates"] if item["id"] == "morning_brief")
    assert morning["schedule_enabled"] is True
    assert morning["schedule_status"] == "Scheduled"
    assert morning["next_run_at"]
