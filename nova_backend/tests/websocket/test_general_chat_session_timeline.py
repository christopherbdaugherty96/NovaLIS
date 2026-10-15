from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest
from src import brain_server
from src.actions.action_result import ActionResult
from src.conversation.session_router import GateResult
from tests.phase45._websocket_test_helpers import _ScriptedWebSocket

pytestmark = pytest.mark.slow


class _ReminderStore:
    def create_schedule(self, **kwargs):
        return {"id": "SCH-TEST-0001", "kind": kwargs["kind"], "recurrence": kwargs["recurrence"]}

    def summarize(self):
        return {
            "summary": "0 due | 1 upcoming",
            "active_count": 1,
            "due_count": 0,
            "upcoming_count": 1,
            "due_items": [],
            "upcoming_items": [],
            "policy_summary": "",
        }


def _run_session(monkeypatch, prompts, *, relevant_memory=None):
    captured = []

    def fake_generate_chat(*args, **kwargs):
        captured.append(dict(kwargs))
        return "A grounded answer."

    async def fake_invoke(*args, **kwargs):
        return ActionResult.ok(
            "Memory saved.",
            data={
                "memory_item": {
                    "id": "MEM-TEST-0001",
                    "title": "Sister birthday",
                    "content_raw": "my sister's birthday is June 3",
                }
            },
            capability_id=61,
        )

    monkeypatch.setattr(brain_server, "NotificationScheduleStore", _ReminderStore)
    monkeypatch.setattr(brain_server, "invoke_governed_capability", fake_invoke)
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        "src.memory.governed_memory_store.GovernedMemoryStore.list_items",
        lambda self, **kwargs: [],
    )
    monkeypatch.setattr(
        "src.memory.governed_memory_store.GovernedMemoryStore.find_relevant_items",
        lambda self, *args, **kwargs: list(relevant_memory or []),
    )
    ws = _ScriptedWebSocket(list(prompts))
    with patch("src.skills.general_chat.generate_chat", side_effect=fake_generate_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))
    return captured


def test_real_session_passes_saved_memory_to_the_followup_model_call(monkeypatch):
    calls = _run_session(
        monkeypatch,
        ["remember that my sister's birthday is June 3", "when is my sister's birthday?"],
        relevant_memory=[
            {
                "id": "MEM-TEST-0001",
                "title": "Sister birthday",
                "content_raw": "my sister's birthday is June 3",
                "source": "explicit_user_save",
            }
        ],
    )

    assert calls
    serialized = repr(calls[-1].get("messages"))
    assert "June 3" in serialized
    assert "confirmed" in serialized.lower()


def test_real_session_keeps_reminder_result_after_a_prior_chat_turn(monkeypatch):
    calls = _run_session(
        monkeypatch,
        ["explain TCP", "remind me to call mom at 3pm", "which reminder did I just make?"],
    )

    assert len(calls) == 2
    reminder_rows = [
        row
        for row in calls[-1].get("messages") or []
        if row.get("role") == "nova_result" and "call mom" in row.get("content", "").lower()
    ]
    assert reminder_rows


def test_real_session_routes_conversation_time_question_to_general_chat(monkeypatch):
    calls = _run_session(
        monkeypatch,
        ["remind me to call mom at 3pm", "what time did I say?"],
    )

    assert len(calls) == 1
    assert calls[-1]["messages"][-2]["content"].lower().startswith("what time did i say")


def test_real_session_places_per_turn_context_at_the_trailing_edge(monkeypatch):
    calls = _run_session(
        monkeypatch,
        ["Help me prepare for a rent discussion.", "What if my landlord says no?"],
    )

    assert len(calls) == 2
    assert [row["role"] for row in calls[0]["messages"]] == ["user", "system"]
    assert [row["role"] for row in calls[1]["messages"]] == [
        "user",
        "assistant",
        "user",
        "system",
    ]
    assert calls[1]["messages"][0] == calls[0]["messages"][0]
