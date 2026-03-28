from __future__ import annotations

from src.working_context.context_store import WorkingContextStore


class _FakeLedger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, metadata: dict) -> None:
        self.events.append((event_type, metadata))


def test_working_context_store_reset_clears_state_and_logs_event():
    ledger = _FakeLedger()
    store = WorkingContextStore(session_id="sess-reset", ledger=ledger)

    store.apply_user_turn(text="Continue Nova memory work", channel="text", intent_family="work")
    store.apply_patch(
        {
            "task_goal": "Finish operational remembrance visibility",
            "selected_file": "nova_backend/src/brain_server.py",
            "current_step": "adding reset flow",
        },
        source="unit_test",
    )

    before = store.to_dict()
    assert before["task_goal"] == "Finish operational remembrance visibility"
    assert before["selected_file"] == "nova_backend/src/brain_server.py"

    store.reset()

    after = store.to_dict()
    assert after["task_goal"] == ""
    assert after["selected_file"] == ""
    assert after["current_step"] == ""
    assert after["recent_relevant_turns"] == []

    event_types = [name for name, _ in ledger.events]
    assert "WORKING_CONTEXT_RESET" in event_types
