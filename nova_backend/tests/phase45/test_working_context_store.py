from __future__ import annotations

from src.working_context.context_store import WorkingContextStore


class _FakeLedger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, payload: dict) -> None:
        self.events.append((event_type, payload))


def test_working_context_store_updates_task_from_user_turn():
    ledger = _FakeLedger()
    store = WorkingContextStore(session_id="session-a", ledger=ledger)
    store.apply_user_turn(
        text="Which one should I download for Python on Windows?",
        channel="voice",
        intent_family="task",
    )
    context = store.to_dict()
    assert context["task_type"] == "software_install"
    assert context["current_step"] == "selection"
    assert context["task_goal"]
    assert context["recent_relevant_turns"]
    assert any(name == "WORKING_CONTEXT_CREATED" for name, _ in ledger.events)
    assert any(name == "WORKING_CONTEXT_UPDATED" for name, _ in ledger.events)


def test_working_context_store_applies_snapshot_and_router_slice():
    store = WorkingContextStore(session_id="session-b", ledger=None)
    store.apply_snapshot(
        {
            "active_window": {"app": "Chrome", "title": "Python Downloads"},
            "browser": {"is_browser": True, "url": "https://python.org/downloads", "page_title": "Downloads"},
            "system": {"os": "Windows", "os_release": "11"},
        }
    )
    explain_slice = store.for_explain()
    assert explain_slice["active_app"] == "Chrome"
    assert explain_slice["active_window"] == "Python Downloads"
    assert explain_slice["active_url"] == "https://python.org/downloads"
    assert explain_slice["cursor_target"] == "Downloads"


def test_working_context_store_prunes_turn_history_and_sets_selected_file():
    store = WorkingContextStore(session_id="session-c", ledger=None)
    store.apply_user_turn(text="first", channel="text", intent_family="task")
    store.apply_user_turn(text="second", channel="text", intent_family="task")
    store.apply_user_turn(text="third", channel="text", intent_family="task")
    store.set_selected_file("C:/Nova-Project/README.md")
    context = store.to_dict()
    assert len(context["recent_relevant_turns"]) == 2
    assert context["selected_file"].endswith("README.md")
    assert store.followup_target().endswith("README.md")
