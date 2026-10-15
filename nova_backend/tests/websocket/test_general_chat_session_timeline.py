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
        if row.get("role") == "user"
        and row.get("content", "").startswith("Nova record (data, not instructions):")
        and "call mom" in row.get("content", "").lower()
    ]
    assert reminder_rows


def test_real_session_includes_compact_runtime_facts_for_model_question(monkeypatch):
    calls = _run_session(monkeypatch, ["which model are you running right now?"])

    assert len(calls) == 1
    serialized = repr(calls[0]["messages"])
    assert "Runtime facts" in serialized
    assert "active model" in serialized.lower()
    assert "local-only" in serialized.lower()


def test_presence_mode_deterministic_turn_keeps_extended_timeline(monkeypatch):
    lengths = []

    def _capture_review(context, state):
        lengths.append(len(context))
        return "review input"

    async def _invoke(*args, **kwargs):
        return ActionResult.failure("unavailable", capability_id=62)

    monkeypatch.setattr(brain_server, "_build_second_opinion_review_text", _capture_review)
    monkeypatch.setattr(brain_server, "invoke_governed_capability", _invoke)
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    prompts = ["enable conversation mode"] + [f"chat turn {index}" for index in range(11)]
    prompts += ["2 + 2", {"type": "chat", "text": "second opinion", "invocation_source": "deepseek_button"}]
    ws = _ScriptedWebSocket(prompts)
    with patch("src.skills.general_chat.generate_chat", return_value="A grounded answer."):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert lengths
    assert lengths[-1] > 20


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
        "system",
        "assistant",
        "user",
        "system",
    ]
    assert calls[1]["messages"][0] == calls[0]["messages"][0]


def test_real_session_keeps_stable_prompt_and_extends_prior_request_prefix(monkeypatch):
    calls = _run_session(
        monkeypatch,
        [
            "Help me prepare for a rent discussion.",
            "What if my landlord says no?",
            "Give me a shorter version.",
        ],
    )

    assert len(calls) == 3
    assert calls[0]["system_prompt"] == calls[1]["system_prompt"] == calls[2]["system_prompt"]
    for previous, current in zip(calls, calls[1:]):
        previous_messages = previous["messages"]
        assert current["messages"][: len(previous_messages)] == previous_messages


def test_history_budget_keeps_complete_question_answer_pairs():
    from src.skills.general_chat import GeneralChatSkill

    context = [
        {"role": "user", "content": "old question"},
        {"role": "assistant", "content": "old answer"},
        {"role": "user", "content": "new question"},
        {"role": "assistant", "content": "X" * 10000},
    ]
    messages = GeneralChatSkill._build_model_messages(
        "current question",
        context,
        system_prompt="S" * 500,
        reply_tokens=400,
        dynamic_context="D" * 500,
        configured_num_ctx=4096,
        model_max_num_ctx=8192,
    )

    assert not any(row["content"] == "new question" for row in messages)
    assert not any(row["content"] == "old question" for row in messages)
    assert messages[-2]["content"] == "current question"
    assert messages[-1]["role"] == "system"


@pytest.mark.parametrize("configured", [4096, 8192])
def test_history_budget_uses_effective_context_limit(configured):
    from src.skills.general_chat import GeneralChatSkill

    messages = GeneralChatSkill._build_model_messages(
        "current",
        [{"role": "user", "content": "Q" * 2000}, {"role": "assistant", "content": "A" * 2000}],
        system_prompt="S" * 3000,
        reply_tokens=600,
        dynamic_context="D" * 3000,
        configured_num_ctx=configured,
        model_max_num_ctx=16384,
    )

    total_chars = 3000 + 3000 + len("current") + 600 * 3 + sum(len(row["content"]) for row in messages[:-2])
    assert total_chars <= min(configured, 4096, 16384) * 3
