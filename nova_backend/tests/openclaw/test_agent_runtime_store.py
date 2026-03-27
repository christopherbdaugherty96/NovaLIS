from pathlib import Path

from src.openclaw.agent_runtime_store import OpenClawAgentRuntimeStore


def test_agent_runtime_store_bootstraps_templates(tmp_path: Path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")

    snapshot = store.snapshot()

    assert snapshot["status"] == "foundation"
    assert snapshot["template_count"] >= 3
    assert any(item["id"] == "morning_brief" for item in snapshot["templates"])


def test_agent_runtime_store_updates_delivery_mode(tmp_path: Path):
    store = OpenClawAgentRuntimeStore(tmp_path / "agent_runtime.json")

    updated = store.set_template_delivery_mode("morning_brief", "chat")

    morning = next(item for item in updated["templates"] if item["id"] == "morning_brief")
    assert morning["delivery_mode"] == "chat"

