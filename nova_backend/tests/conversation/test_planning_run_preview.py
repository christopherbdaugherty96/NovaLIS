import asyncio
import json

import pytest

from src.base_skill import SkillResult
from src.conversation.general_chat_runtime import run_general_chat_fallback
from src.conversation.planning_run_preview import (
    PlanningRunPreview,
    create_planning_run_preview,
    planning_run_manager,
)
from src.conversation.task_understanding_preview import build_task_understanding_preview


class _FakeGeneralChatSkill:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def can_handle(self, query: str) -> bool:
        return bool(query.strip())

    async def handle(self, query: str, context=None, session_state=None):
        self.calls.append({"query": query, "session_state": dict(session_state or {})})
        return SkillResult(success=True, message="ok", skill="general_chat")


def _noop_memory(query, *, session_state, project_threads):
    return []


def test_create_planning_run_preview_from_task_understanding_preview():
    task_preview = build_task_understanding_preview(
        "summarize this task",
        session_context={"task": "Prepare a planning-only run preview."},
    )
    assert task_preview.plan is not None

    session_state = {}
    run_preview = create_planning_run_preview(task_preview.plan, session_state=session_state)

    assert run_preview is not None
    assert run_preview.run_id
    assert run_preview.title == "summarize this task"
    assert run_preview.goal == "summarize this task"
    assert run_preview.status == "planning"
    assert run_preview.current_step
    assert run_preview.next_step
    assert run_preview.planning_only is True
    assert run_preview.authority_effect == "none"
    assert run_preview.execution_performed is False
    assert run_preview.authorization_granted is False
    assert session_state["planning_run_preview"]["run_id"] == run_preview.run_id
    assert session_state["last_interacted_run_id"] == run_preview.run_id


def test_create_planning_run_preview_none_plan_creates_nothing():
    session_state = {}

    assert create_planning_run_preview(None, session_state=session_state) is None
    assert "planning_run_preview" not in session_state
    assert "last_interacted_run_id" not in session_state


def test_planning_run_preview_rejects_non_planning_values():
    kwargs = {
        "run_id": "run_1",
        "title": "title",
        "goal": "goal",
        "status": "planning",
        "current_step": "understand request",
        "next_step": "build task envelope",
        "last_interacted_run_id": "run_1",
        "focused_run_id": "run_1",
    }

    with pytest.raises(ValueError, match="planning-only"):
        PlanningRunPreview(**kwargs, planning_only=False)
    with pytest.raises(ValueError, match="non-authorizing"):
        PlanningRunPreview(**kwargs, authority_effect="approved")
    with pytest.raises(ValueError, match="must not record executed"):
        PlanningRunPreview(**kwargs, execution_performed=True)
    with pytest.raises(ValueError, match="must not grant authorization"):
        PlanningRunPreview(**kwargs, authorization_granted=True)


def test_planning_run_preview_focus_updates_safely():
    session_state = {}
    first = build_task_understanding_preview("summarize this task", session_context={"task": "one"})
    second = build_task_understanding_preview("make a bounded task envelope")

    assert first.plan is not None
    assert second.plan is not None
    first_preview = create_planning_run_preview(first.plan, session_state=session_state)
    second_preview = create_planning_run_preview(second.plan, session_state=session_state)
    assert first_preview is not None
    assert second_preview is not None

    manager = planning_run_manager(session_state)
    focused = manager.update_focus(first_preview.run_id)

    assert focused is not None
    assert manager.last_interacted_run_id == first_preview.run_id
    assert focused.execution_performed is False
    assert focused.authorization_granted is False


def test_existing_focused_run_does_not_create_extra_hidden_run():
    session_state = {}
    first = build_task_understanding_preview("summarize this task", session_context={"task": "one"})
    second = build_task_understanding_preview("make a bounded task envelope")
    assert first.plan is not None
    assert second.plan is not None

    first_preview = create_planning_run_preview(first.plan, session_state=session_state)
    assert first_preview is not None
    manager = planning_run_manager(session_state)
    before_count = len(manager.list_runs())

    focused_preview = create_planning_run_preview(
        second.plan,
        session_state=session_state,
        focused_run_id=first_preview.run_id,
    )

    assert focused_preview is not None
    assert focused_preview.run_id == first_preview.run_id
    assert len(manager.list_runs()) == before_count


def test_general_chat_task_like_prompt_creates_planning_run_preview():
    skill = _FakeGeneralChatSkill()
    session_state = {"conversation_context": {"user_goal": "Plan the next safe Brain slice."}}

    asyncio.run(
        run_general_chat_fallback(
            "summarize this task",
            general_chat_skill=skill,
            session_state=session_state,
            session_context=[],
            project_threads=object(),
            select_relevant_memory_context=_noop_memory,
        )
    )

    passed_state = skill.calls[0]["session_state"]
    preview = passed_state["planning_run_preview"]

    assert preview["run_id"]
    assert preview["status"] == "planning"
    assert preview["current_step"]
    assert preview["next_step"]
    assert preview["last_interacted_run_id"] == preview["run_id"]
    assert preview["focused_run_id"] == preview["run_id"]
    assert preview["authority_effect"] == "none"
    assert preview["execution_performed"] is False
    assert preview["authorization_granted"] is False
    assert session_state["planning_run_preview"]["run_id"] == preview["run_id"]
    assert session_state["last_interacted_run_id"] == preview["run_id"]
    json.dumps(session_state["planning_run_preview"])
    assert "_planning_run_manager" not in preview
    assert "_planning_run_manager" not in passed_state


def test_general_chat_casual_prompt_does_not_create_run():
    skill = _FakeGeneralChatSkill()
    session_state = {}

    asyncio.run(
        run_general_chat_fallback(
            "hey how are you",
            general_chat_skill=skill,
            session_state=session_state,
            session_context=[],
            project_threads=object(),
            select_relevant_memory_context=_noop_memory,
        )
    )

    passed_state = skill.calls[0]["session_state"]

    assert "planning_run_preview" not in passed_state
    assert "planning_run_preview" not in session_state
    assert "last_interacted_run_id" not in session_state


def test_general_chat_casual_prompt_does_not_leak_prior_preview_to_skill_state():
    skill = _FakeGeneralChatSkill()
    session_state = {
        "planning_run_preview": {"run_id": "old_run"},
        "task_understanding_preview": object(),
        "task_understanding_prompt_block": "old task block",
        "task_understanding_envelope": object(),
    }

    asyncio.run(
        run_general_chat_fallback(
            "hey how are you",
            general_chat_skill=skill,
            session_state=session_state,
            session_context=[],
            project_threads=object(),
            select_relevant_memory_context=_noop_memory,
        )
    )

    passed_state = skill.calls[0]["session_state"]
    assert "planning_run_preview" not in passed_state
    assert passed_state["task_understanding_preview"] is None
    assert passed_state["task_understanding_prompt_block"] == ""
    assert "task_understanding_envelope" not in passed_state


def test_private_run_manager_does_not_leak_to_skill_state_on_later_turn():
    skill = _FakeGeneralChatSkill()
    session_state = {}
    task_preview = build_task_understanding_preview("make a bounded task envelope")
    assert task_preview.plan is not None
    create_planning_run_preview(task_preview.plan, session_state=session_state)
    assert "_planning_run_manager" in session_state

    asyncio.run(
        run_general_chat_fallback(
            "summarize this task",
            general_chat_skill=skill,
            session_state=session_state,
            session_context=[],
            project_threads=object(),
            select_relevant_memory_context=_noop_memory,
        )
    )

    passed_state = skill.calls[0]["session_state"]
    assert "_planning_run_manager" not in passed_state
    json.dumps(passed_state["planning_run_preview"])


def test_planning_run_preview_does_not_create_execution_surface():
    session_state = {}
    task_preview = build_task_understanding_preview("make a bounded task envelope")
    assert task_preview.plan is not None

    create_planning_run_preview(task_preview.plan, session_state=session_state)
    manager = planning_run_manager(session_state)

    assert not hasattr(manager, "execute")
    assert not hasattr(manager, "execute_run")
    assert not hasattr(manager, "run_capability")
