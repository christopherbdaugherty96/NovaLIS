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
    assert "memory show" in save_result.message.lower()
    assert dict(save_result.data or {}).get("follow_up_prompts")

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


def test_memory_export_returns_non_deleted_items(tmp_path: Path):
    ledger = _FakeLedger()
    store = GovernedMemoryStore(tmp_path / "memory_items.json")
    executor = MemoryGovernanceExecutor(ledger=ledger, store=store)

    first = executor.execute(
        ActionRequest(
            capability_id=61,
            params={"action": "save", "title": "Keep", "body": "Retain this governed note."},
        )
    )
    second = executor.execute(
        ActionRequest(
            capability_id=61,
            params={"action": "save", "title": "Delete", "body": "Remove this governed note."},
        )
    )
    second_id = str((second.data or {}).get("memory_item", {}).get("id") or "")
    executor.execute(
        ActionRequest(
            capability_id=61,
            params={"action": "delete", "item_id": second_id, "confirmed": True},
        )
    )

    export_result = executor.execute(ActionRequest(capability_id=61, params={"action": "export"}))

    assert export_result.success is True
    payload = dict(export_result.data or {}).get("memory_export") or {}
    assert payload.get("export_version") == 1
    assert payload.get("item_count") == 1
    exported_items = list(payload.get("items") or [])
    assert len(exported_items) == 1
    assert exported_items[0]["title"] == "Keep"
    assert all(not bool(item.get("deleted")) for item in exported_items)
    assert "MEMORY_EXPORT_REQUESTED" in [name for name, _ in ledger.events]


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
    assert "Tags:" in show_result.message


def test_memory_save_persists_explicit_user_metadata(tmp_path: Path):
    store = GovernedMemoryStore(tmp_path / "memory_items.json")
    executor = MemoryGovernanceExecutor(store=store)

    save_result = executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "save",
                "body": "Client supplies alcohol; Pour Social does not sell alcohol.",
                "source": "explicit_user_save",
                "session_id": "session-123",
                "user_visible": True,
            },
        )
    )

    assert save_result.success is True
    item = dict(save_result.data or {}).get("memory_item") or {}
    assert item.get("source") == "explicit_user_save"
    assert item.get("session_id") == "session-123"
    assert item.get("user_visible") is True
    assert item.get("content_raw") == "Client supplies alcohol; Pour Social does not sell alcohol."
    assert str(item.get("content_display") or "").startswith("Client supplies alcohol")
    assert item.get("status") == "active"


def test_memory_supersede_preserves_visibility_links_and_sets_edit_metadata(tmp_path: Path):
    store = GovernedMemoryStore(tmp_path / "memory_items.json")
    executor = MemoryGovernanceExecutor(store=store)

    saved = executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "save",
                "title": "Pour Social alcohol policy",
                "body": "Client supplies alcohol; Pour Social does not sell alcohol.",
                "thread_name": "Pour Social",
                "thread_key": "pour social",
                "source": "explicit_user_save",
                "session_id": "session-1",
                "user_visible": True,
            },
        )
    )
    original = dict(saved.data or {}).get("memory_item") or {}
    original_id = str(original.get("id") or "")

    updated = executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "supersede",
                "item_id": original_id,
                "new_body": "Client supplies alcohol for private events only; Pour Social does not sell alcohol.",
                "confirmed": True,
                "source": "explicit_user_edit",
                "session_id": "session-2",
                "user_visible": True,
            },
        )
    )

    assert updated.success is True
    replacement = dict(updated.data or {}).get("memory_item") or {}
    assert replacement.get("source") == "explicit_user_edit"
    assert replacement.get("session_id") == "session-2"
    assert replacement.get("user_visible") is True
    assert replacement.get("status") == "locked"
    assert replacement.get("content_raw") == "Client supplies alcohol for private events only; Pour Social does not sell alcohol."
    assert dict(replacement.get("links") or {}).get("project_thread_name") == "Pour Social"
    assert original_id in list(dict(replacement.get("lock") or {}).get("supersedes") or [])


def test_memory_relevant_search_prefers_visible_matching_items(tmp_path: Path):
    store = GovernedMemoryStore(tmp_path / "memory_items.json")
    executor = MemoryGovernanceExecutor(store=store)

    executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "save",
                "title": "Pour Social alcohol policy",
                "body": "Client supplies alcohol; Pour Social does not sell alcohol.",
                "thread_name": "Pour Social",
                "thread_key": "pour social",
                "tags": ["events", "alcohol"],
            },
        )
    )
    executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "save",
                "title": "GPU note",
                "body": "Use enough VRAM for local inference.",
                "scope": "nova_core",
            },
        )
    )

    matches = store.find_relevant_items("What did we save about Pour Social alcohol?", thread_name="Pour Social", limit=3)
    assert matches
    assert matches[0]["title"] == "Pour Social alcohol policy"
    assert all(match.get("user_visible", True) for match in matches)


def test_memory_recent_and_search_commands_surface_recent_and_best_matches(tmp_path: Path):
    store = GovernedMemoryStore(tmp_path / "memory_items.json")
    executor = MemoryGovernanceExecutor(store=store)

    original = executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "save",
                "title": "Pour Social alcohol policy",
                "body": "Client supplies alcohol; Pour Social does not sell alcohol.",
                "thread_name": "Pour Social",
                "thread_key": "pour social",
                "tags": ["events", "alcohol"],
            },
        )
    )
    original_id = str((original.data or {}).get("memory_item", {}).get("id") or "")
    executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "supersede",
                "item_id": original_id,
                "new_body": "Client supplies alcohol for private events only; Pour Social does not sell alcohol.",
                "confirmed": True,
            },
        )
    )
    executor.execute(
        ActionRequest(
            capability_id=61,
            params={"action": "save", "title": "GPU note", "body": "Use enough VRAM for local inference."},
        )
    )

    recent = executor.execute(ActionRequest(capability_id=61, params={"action": "recent"}))
    assert recent.success is True
    assert "Recent Memory" in recent.message
    recent_items = list(dict(recent.data or {}).get("memory_items") or [])
    assert recent_items
    assert all(not dict(item.get("lock") or {}).get("superseded_by") for item in recent_items)

    search = executor.execute(
        ActionRequest(capability_id=61, params={"action": "search", "query": "Pour Social alcohol"})
    )
    assert search.success is True
    assert "Memory Search Matches" in search.message
    search_items = list(dict(search.data or {}).get("memory_items") or [])
    assert search_items
    assert "private events only" in str(search_items[0].get("body") or "")


def test_memory_show_includes_version_and_lineage(tmp_path: Path):
    store = GovernedMemoryStore(tmp_path / "memory_items.json")
    executor = MemoryGovernanceExecutor(store=store)

    saved = executor.execute(
        ActionRequest(
            capability_id=61,
            params={"action": "save", "title": "Policy", "body": "Old policy body."},
        )
    )
    original_id = str((saved.data or {}).get("memory_item", {}).get("id") or "")
    updated = executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "supersede",
                "item_id": original_id,
                "new_body": "New policy body.",
                "confirmed": True,
            },
        )
    )
    replacement_id = str((updated.data or {}).get("memory_item", {}).get("id") or "")

    show_result = executor.execute(
        ActionRequest(capability_id=61, params={"action": "show", "item_id": replacement_id})
    )

    assert show_result.success is True
    assert "Version:" in show_result.message
    assert "Lineage:" in show_result.message
    assert original_id in show_result.message


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


def test_memory_overview_reports_counts_recent_items_and_linked_threads(tmp_path: Path):
    store = GovernedMemoryStore(tmp_path / "memory_items.json")
    executor = MemoryGovernanceExecutor(store=store)

    executor.execute(
        ActionRequest(
            capability_id=61,
            params={
                "action": "save",
                "title": "Decision: Deployment Issue",
                "body": "Project thread: Deployment Issue\n\nDecision\nVerify PYTHONPATH before rebuild",
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
                "title": "Governance note",
                "body": "Preserve explicit revocation flows.",
                "scope": "nova_core",
            },
        )
    )

    result = executor.execute(ActionRequest(capability_id=61, params={"action": "overview"}))
    assert result.success is True
    assert "Governed Memory Overview" in result.message

    overview = dict(result.data or {}).get("memory_overview") or {}
    assert int(overview.get("total_count") or 0) == 2
    assert int(dict(overview.get("tier_counts") or {}).get("active") or 0) == 2
    linked_threads = list(overview.get("linked_threads") or [])
    assert linked_threads
    assert linked_threads[0]["thread_name"] == "Deployment Issue"
    recent_items = list(overview.get("recent_items") or [])
    assert recent_items
    assert dict(result.data or {}).get("follow_up_prompts")
