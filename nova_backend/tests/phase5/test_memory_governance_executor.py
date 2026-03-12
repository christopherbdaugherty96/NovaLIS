from __future__ import annotations

from pathlib import Path

from src.actions.action_request import ActionRequest
from src.executors.memory_governance_executor import MemoryGovernanceExecutor
from src.memory.governed_memory_store import GovernedMemoryStore


class _FakeLedger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, metadata: dict) -> None:
        self.events.append((event_type, metadata))


def test_memory_save_list_show_lock_defer_roundtrip(tmp_path: Path):
    ledger = _FakeLedger()
    store = GovernedMemoryStore(tmp_path / "memory_items.json")
    executor = MemoryGovernanceExecutor(ledger=ledger, store=store)

    save_result = executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "save",
                "title": "Deployment issue",
                "body": "Container import path still fails.",
                "scope": "project",
                "tags": ["deployment", "python"],
            },
        )
    )
    assert save_result.success is True
    item = dict(save_result.data or {}).get("memory_item") or {}
    item_id = str(item.get("id") or "")
    assert item_id.startswith("MEM-")

    list_result = executor.execute(
        ActionRequest(capability_id=61, params={"action": "list", "tier": "active"})
    )
    assert list_result.success is True
    listed = list(dict(list_result.data or {}).get("memory_items") or [])
    assert listed
    assert listed[0]["id"] == item_id

    show_result = executor.execute(
        ActionRequest(capability_id=61, params={"action": "show", "item_id": item_id})
    )
    assert show_result.success is True
    assert "Container import path" in show_result.message

    lock_result = executor.execute(
        ActionRequest(capability_id=61, params={"action": "lock", "item_id": item_id})
    )
    assert lock_result.success is True
    assert "locked" in lock_result.message.lower()

    defer_result = executor.execute(
        ActionRequest(capability_id=61, params={"action": "defer", "item_id": item_id})
    )
    assert defer_result.success is True
    assert "deferred" in defer_result.message.lower()

    event_types = [name for name, _ in ledger.events]
    assert "MEMORY_ITEM_SAVED" in event_types
    assert "MEMORY_ITEM_LISTED" in event_types
    assert "MEMORY_ITEM_VIEWED" in event_types
    assert "MEMORY_ITEM_LOCKED" in event_types
    assert "MEMORY_ITEM_DEFERRED" in event_types


def test_memory_unlock_and_delete_require_confirmation(tmp_path: Path):
    store = GovernedMemoryStore(tmp_path / "memory_items.json")
    executor = MemoryGovernanceExecutor(store=store)

    save_result = executor.execute(
        ActionRequest(
            capability_id=61,
            params={"action": "save", "title": "Temp", "body": "to remove"},
        )
    )
    item_id = str((save_result.data or {}).get("memory_item", {}).get("id") or "")

    lock_result = executor.execute(
        ActionRequest(capability_id=61, params={"action": "lock", "item_id": item_id})
    )
    assert lock_result.success is True

    unlock_without_confirm = executor.execute(
        ActionRequest(capability_id=61, params={"action": "unlock", "item_id": item_id})
    )
    assert unlock_without_confirm.success is False
    assert "requires explicit confirmation" in unlock_without_confirm.message.lower()

    unlock_with_confirm = executor.execute(
        ActionRequest(
            capability_id=61,
            params={"action": "unlock", "item_id": item_id, "confirmed": True},
        )
    )
    assert unlock_with_confirm.success is True

    delete_without_confirm = executor.execute(
        ActionRequest(capability_id=61, params={"action": "delete", "item_id": item_id})
    )
    assert delete_without_confirm.success is False
    assert "requires explicit confirmation" in delete_without_confirm.message.lower()

    delete_with_confirm = executor.execute(
        ActionRequest(
            capability_id=61,
            params={"action": "delete", "item_id": item_id, "confirmed": True},
        )
    )
    assert delete_with_confirm.success is True

    list_result = executor.execute(ActionRequest(capability_id=61, params={"action": "list"}))
    listed = list(dict(list_result.data or {}).get("memory_items") or [])
    assert all(entry.get("id") != item_id for entry in listed)


def test_memory_items_support_thread_link_and_filter(tmp_path: Path):
    store = GovernedMemoryStore(tmp_path / "memory_items.json")
    executor = MemoryGovernanceExecutor(store=store)

    save_result = executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "save",
                "title": "Thread snapshot",
                "body": "Deployment Issue continuity brief",
                "thread_name": "Deployment Issue",
                "thread_key": "deployment issue",
            },
        )
    )
    assert save_result.success is True
    memory_item = dict(save_result.data or {}).get("memory_item") or {}
    item_id = str(memory_item.get("id") or "")
    assert item_id.startswith("MEM-")
    links = dict(memory_item.get("links") or {})
    assert links.get("project_thread_name") == "Deployment Issue"
    assert links.get("project_thread_key") == "deployment issue"

    filtered = executor.execute(
        ActionRequest(
            capability_id=61,
            params={"action": "list", "thread_name": "Deployment Issue", "thread_key": "deployment issue"},
        )
    )
    assert filtered.success is True
    filtered_items = list(dict(filtered.data or {}).get("memory_items") or [])
    assert len(filtered_items) == 1
    assert filtered_items[0]["id"] == item_id

    show_result = executor.execute(
        ActionRequest(capability_id=61, params={"action": "show", "item_id": item_id})
    )
    assert show_result.success is True
    assert "Thread: Deployment Issue" in show_result.message


def test_thread_bridge_actions_require_orchestration_context(tmp_path: Path):
    store = GovernedMemoryStore(tmp_path / "memory_items.json")
    executor = MemoryGovernanceExecutor(store=store)

    snapshot_result = executor.execute(
        ActionRequest(capability_id=61, params={"action": "save_thread_snapshot", "thread_name": "Deployment Issue"})
    )
    assert snapshot_result.success is False
    assert "requires orchestration context" in snapshot_result.message.lower()

    decision_result = executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "save_thread_decision",
                "thread_name": "Deployment Issue",
                "decision": "Verify PYTHONPATH",
            },
        )
    )
    assert decision_result.success is False
    assert "requires orchestration context" in decision_result.message.lower()


def test_summarize_thread_counts_reports_linked_memory(tmp_path: Path):
    store = GovernedMemoryStore(tmp_path / "memory_items.json")
    executor = MemoryGovernanceExecutor(store=store)

    executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "save",
                "title": "Snapshot A",
                "body": "Deployment continuity",
                "thread_name": "Deployment Issue",
                "thread_key": "deployment issue",
            },
        )
    )
    executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "save",
                "title": "Decision A",
                "body": "Decision text",
                "thread_name": "Deployment Issue",
                "thread_key": "deployment issue",
            },
        )
    )
    executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "save",
                "title": "Research Snapshot",
                "body": "Governance notes",
                "thread_name": "AI Governance Research",
                "thread_key": "ai governance research",
            },
        )
    )

    counts = store.summarize_thread_counts()
    assert counts.get("deployment issue") == 2
    assert counts.get("ai governance research") == 1


def test_summarize_thread_insights_includes_latest_decision_and_timestamp(tmp_path: Path):
    store = GovernedMemoryStore(tmp_path / "memory_items.json")
    executor = MemoryGovernanceExecutor(store=store)

    executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "save",
                "title": "Decision: Deployment Issue",
                "body": "Project thread: Deployment Issue\n\nDecision\nVerify PYTHONPATH before rebuilding",
                "thread_name": "Deployment Issue",
                "thread_key": "deployment issue",
                "tags": ["decision"],
            },
        )
    )
    executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "save",
                "title": "Thread Snapshot: Deployment Issue",
                "body": "Continuity brief content",
                "thread_name": "Deployment Issue",
                "thread_key": "deployment issue",
            },
        )
    )

    insights = store.summarize_thread_insights()
    dep = dict(insights.get("deployment issue") or {})
    assert int(dep.get("memory_count") or 0) == 2
    assert str(dep.get("last_memory_updated_at") or "").strip()
    assert "Verify PYTHONPATH before rebuilding" in str(dep.get("latest_decision") or "")
