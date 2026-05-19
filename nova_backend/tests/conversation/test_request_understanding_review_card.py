import asyncio

import pytest

from src.base_skill import SkillResult
from src.brain.brain_mode import BrainMode
from src.conversation.general_chat_runtime import run_general_chat_fallback
from src.conversation.request_understanding import build_request_understanding
from src.conversation.request_understanding_review_card import (
    RequestUnderstandingReviewCard,
    build_request_understanding_review_card,
)
from src.conversation.task_understanding_preview import build_task_understanding_preview


class _FakeGeneralChatSkill:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def can_handle(self, query: str) -> bool:
        return bool(query.strip())

    async def handle(self, query: str, context=None, session_state=None, on_chunk=None):
        self.calls.append({"query": query, "session_state": dict(session_state or {})})
        return SkillResult(success=True, message="ok", skill="general_chat")


def _noop_memory(query, *, session_state, project_threads):
    return []


def _memory_context(query, *, session_state, project_threads):
    return [{"content": "User prefers planning-only review before implementation."}]


def _run_fallback(query: str, *, memory=_noop_memory, session_state=None) -> dict:
    skill = _FakeGeneralChatSkill()
    asyncio.run(
        run_general_chat_fallback(
            query,
            general_chat_skill=skill,
            session_state=dict(session_state or {}),
            session_context=[],
            project_threads=object(),
            select_relevant_memory_context=memory,
        )
    )
    return skill.calls[0]["session_state"]


def _run_fallback_result(query: str, *, memory=_noop_memory, session_state=None) -> SkillResult:
    skill = _FakeGeneralChatSkill()
    result = asyncio.run(
        run_general_chat_fallback(
            query,
            general_chat_skill=skill,
            session_state=dict(session_state or {}),
            session_context=[],
            project_threads=object(),
            select_relevant_memory_context=memory,
        )
    )
    assert result is not None
    return result


def test_task_like_summary_request_produces_review_card():
    state = _run_fallback(
        "summarize this task",
        session_state={"conversation_context": {"user_goal": "Prepare a bounded review card."}},
    )

    card = state["request_understanding_review_card"]

    assert card["request_text"] == "summarize this task"
    assert card["goal"] == "summarize this task"
    assert card["detected_mode"]
    assert card["authority_effect"] == "none"
    assert card["execution_performed"] is False
    assert card["authorization_granted"] is False
    assert card["private_reasoning_exposed"] is False
    assert card["history_status"] == "not_available"
    assert card["relevant_receipts"] == []
    assert card["relevant_action_history"] == []


def test_bounded_envelope_request_produces_review_card():
    state = _run_fallback("make a bounded task envelope", memory=_memory_context)

    card = state["request_understanding_review_card"]

    assert card["goal"] == "make a bounded task envelope"
    assert card["allowed_planning_actions"]
    assert "create a non-executing task envelope" in card["allowed_planning_actions"]
    assert any(item["source"] == "stable_memory" for item in card["context_used"])


def test_ambiguous_task_request_produces_clarification_review_card():
    state = _run_fallback("turn this script into a scene plan")

    card = state["request_understanding_review_card"]

    assert card["clarification_needed"] is True
    assert card["confidence"] == 0.42
    assert "Ask one focused clarification" in card["suggested_next_step"]


def test_casual_chat_produces_no_review_card():
    state = _run_fallback(
        "hey how are you",
        session_state={"request_understanding_review_card": {"run_id": "stale"}},
    )

    assert "request_understanding_review_card" not in state
    assert "planning_run_preview" not in state


def test_review_card_enforces_non_authorizing_invariants():
    kwargs = {
        "request_text": "summarize this task",
        "request_type": "general",
        "detected_mode": "planning",
        "goal": "summarize this task",
    }

    with pytest.raises(ValueError, match="non-authorizing"):
        RequestUnderstandingReviewCard(**kwargs, authority_effect="approved")
    with pytest.raises(ValueError, match="must not record execution"):
        RequestUnderstandingReviewCard(**kwargs, execution_performed=True)
    with pytest.raises(ValueError, match="must not grant authorization"):
        RequestUnderstandingReviewCard(**kwargs, authorization_granted=True)
    with pytest.raises(ValueError, match="must not expose private reasoning"):
        RequestUnderstandingReviewCard(**kwargs, private_reasoning_exposed=True)


def test_review_card_contains_blocked_execution_actions():
    state = _run_fallback("make a bounded task envelope")

    blocked = state["request_understanding_review_card"]["blocked_execution_actions"]

    assert "use OpenClaw" in blocked
    assert "open browser tabs" in blocked
    assert "send email" in blocked
    assert "authorize capabilities" in blocked


def test_general_chat_result_carries_review_card_for_display_only_payload():
    result = _run_fallback_result("make a bounded task envelope")

    card = result.data["request_understanding_review_card"]

    assert card["authority_effect"] == "none"
    assert card["execution_performed"] is False
    assert card["authorization_granted"] is False
    assert "use OpenClaw" in card["blocked_execution_actions"]


def test_builder_returns_none_without_task_preview():
    card = build_request_understanding_review_card(
        request_text="hey",
        request_understanding=build_request_understanding("hey"),
        task_understanding_preview=None,
        detected_mode=BrainMode.CASUAL,
    )

    assert card is None


def test_builder_uses_only_caller_provided_history():
    task_preview = build_task_understanding_preview("summarize this task")
    assert task_preview.plan is not None

    card = build_request_understanding_review_card(
        request_text="summarize this task",
        request_understanding=build_request_understanding("summarize this task"),
        task_understanding_preview=task_preview.plan,
        detected_mode=BrainMode.PLANNING,
        relevant_receipts=[{"event_type": "TEST_RECEIPT"}],
        relevant_action_history=[{"action": "reviewed"}],
        history_status="provided",
    )

    assert card is not None
    payload = card.to_dict()
    assert payload["relevant_receipts"] == [{"event_type": "TEST_RECEIPT"}]
    assert payload["relevant_action_history"] == [{"action": "reviewed"}]
    assert payload["history_status"] == "provided"


def test_review_card_does_not_create_execution_surface():
    state = _run_fallback("summarize this task")
    card = state["request_understanding_review_card"]

    assert "execute" not in card
    assert "run_capability" not in card
    assert "openclaw" not in card
    assert "_planning_run_manager" not in state
