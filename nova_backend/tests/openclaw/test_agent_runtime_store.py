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
