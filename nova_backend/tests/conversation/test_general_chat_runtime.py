from __future__ import annotations

import asyncio

from src.base_skill import SkillResult
from src.conversation.general_chat_runtime import (
    resolve_pending_escalation_reply,
    run_general_chat_fallback,
)


class _FakeGeneralChatSkill:
    def __init__(self, result: SkillResult | None) -> None:
        self._result = result
        self.calls: list[dict] = []

    def can_handle(self, query: str) -> bool:
        return bool(query.strip())

    async def handle(self, query: str, context=None, session_state=None):
        self.calls.append(
            {
                "query": query,
                "context": list(context or []),
                "session_state": dict(session_state or {}),
            }
        )
        return self._result


def test_run_general_chat_fallback_injects_memory_context_and_chat_context():
    result = SkillResult(success=True, message="A helpful answer.", skill="general_chat")
    skill = _FakeGeneralChatSkill(result)
    project_threads = object()
    captured = {}
    session_state = {
        "session_id": "sess-1",
        "general_chat_context": [{"role": "assistant", "content": "Earlier reply."}],
    }
    session_context = [{"role": "user", "content": "Should not be used directly."}]

    def _select_relevant_memory_context(query: str, *, session_state, project_threads):
        captured["query"] = query
        captured["session_state"] = dict(session_state)
        captured["project_threads"] = project_threads
        return [{"memory_id": "MEM-1", "content": "Saved preference"}]

    outcome = asyncio.run(
        run_general_chat_fallback(
            "What should I focus on?",
            general_chat_skill=skill,
            session_state=session_state,
            session_context=session_context,
            project_threads=project_threads,
            select_relevant_memory_context=_select_relevant_memory_context,
        )
    )

    assert outcome is result
    assert captured["query"] == "What should I focus on?"
    assert captured["project_threads"] is project_threads
    assert session_state["last_memory_context"] == [{"memory_id": "MEM-1", "content": "Saved preference"}]
    assert skill.calls
    assert skill.calls[0]["context"] == [{"role": "assistant", "content": "Earlier reply."}]
    assert skill.calls[0]["session_state"]["relevant_memory_context"] == [
        {"memory_id": "MEM-1", "content": "Saved preference"}
    ]


def test_resolve_pending_escalation_confirm_updates_state_and_context():
    skill = _FakeGeneralChatSkill(
        SkillResult(
            success=True,
            message="Here is the deeper answer.",
            data={
                "conversation_context": {"topic": "gpu", "open_question": "Why do GPUs matter?"},
                "escalation": {"escalated": True, "thought_data": {"steps": ["inspect"]}},
            },
            skill="general_chat",
        )
    )
    session_state = {
        "pending_escalation": ("Why do GPUs matter?", [{"role": "user", "content": "Why?"}], {}),
        "deep_mode_armed": True,
        "turn_count": 4,
        "escalation_count": 0,
    }

    outcome = asyncio.run(
        resolve_pending_escalation_reply(
            "yes",
            session_state=session_state,
            general_chat_skill=skill,
        )
    )

    assert outcome.handled is True
    assert outcome.skill_result is not None
    assert outcome.skill_result.message == "Here is the deeper answer."
    assert outcome.context_entries == [
        {"role": "user", "content": "Why do GPUs matter?"},
        {"role": "assistant", "content": "Here is the deeper answer."},
    ]
    assert session_state["pending_escalation"] is None
    assert session_state["deep_mode_armed"] is False
    assert session_state["last_response"] == "Here is the deeper answer."
    assert session_state["conversation_context"] == {
        "topic": "gpu",
        "open_question": "Why do GPUs matter?",
    }
    assert session_state["escalation_count"] == 1
    assert session_state["last_escalation_turn"] == 4
    assert skill.calls[0]["session_state"]["turn_count"] == 999
    assert skill.calls[0]["session_state"]["deep_mode_armed"] is True


def test_resolve_pending_escalation_unavailable_uses_honest_message():
    skill = _FakeGeneralChatSkill(None)
    session_state = {
        "pending_escalation": ("Why do GPUs matter?", [{"role": "user", "content": "Why?"}], {}),
        "deep_mode_armed": True,
        "turn_count": 4,
        "escalation_count": 0,
    }

    outcome = asyncio.run(
        resolve_pending_escalation_reply(
            "yes",
            session_state=session_state,
            general_chat_skill=skill,
        )
    )

    assert outcome.handled is True
    assert outcome.skill_result is None
    assert outcome.message == "Deep analysis is unavailable right now, so I kept the brief version."
    assert session_state["pending_escalation"] is None
    assert session_state["deep_mode_armed"] is False
