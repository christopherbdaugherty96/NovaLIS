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


def test_agent_runtime_store_updates_delivery_mode(tmp_path: Path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")

    updated = store.set_template_delivery_mode("morning_brief", "chat")

    morning = next(item for item in updated["templates"] if item["id"] == "morning_brief")
    assert morning["delivery_mode"] == "chat"


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
        }
    )

    snapshot = store.snapshot()
    assert snapshot["delivery_ready_count"] == 1
    delivery = snapshot["delivery_inbox"][0]
    assert delivery["template_id"] == "morning_brief"

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
