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


_MEM_ITEM = {
    "id": "MEM-1",
    "title": "Saved preference",
    "content": "Saved preference",
    "scope": "",
    "thread_name": "",
    "source": "explicit_user_save",
}


def _run_fallback(query: str = "What should I focus on?", memory_items=None):
    """Shared helper: runs run_general_chat_fallback and returns (outcome, skill, session_state)."""
    result = SkillResult(success=True, message="A helpful answer.", skill="general_chat")
    skill = _FakeGeneralChatSkill(result)
    session_state = {
        "session_id": "sess-1",
        "general_chat_context": [{"role": "assistant", "content": "Earlier reply."}],
    }
    items = memory_items if memory_items is not None else [dict(_MEM_ITEM)]

    def _select(q, *, session_state, project_threads):
        return items

    outcome = asyncio.run(
        run_general_chat_fallback(
            query,
            general_chat_skill=skill,
            session_state=session_state,
            session_context=[],
            project_threads=object(),
            select_relevant_memory_context=_select,
        )
    )
    return outcome, skill, session_state


def test_run_general_chat_fallback_injects_memory_context_and_chat_context():
    outcome, skill, session_state = _run_fallback()

    assert outcome is not None
    # Raw fetch result is preserved in last_memory_context unchanged
    assert session_state["last_memory_context"][0]["id"] == "MEM-1"
    assert skill.calls
    assert skill.calls[0]["context"] == [{"role": "assistant", "content": "Earlier reply."}]
    # packed_context is what reaches skill_state — content preserved, source_label applied
    packed = skill.calls[0]["session_state"]["relevant_memory_context"]
    assert len(packed) == 1
    assert packed[0]["content"] == "Saved preference"
    assert packed[0]["source"] == "confirmed_memory"  # explicit_user_save → confirmed_memory


def test_context_pack_wiring_stores_brain_trace_in_session_state():
    _, _, session_state = _run_fallback()
    trace = session_state.get("last_brain_trace")
    assert isinstance(trace, dict)
    assert "mode" in trace
    assert "trace_id" in trace
    assert trace["execution_performed"] is False
    assert trace["authorization_granted"] is False


def test_context_pack_wiring_drops_empty_content_items():
    # Items with no content should be dropped by the pack
    _, skill, _ = _run_fallback(memory_items=[{"id": "x", "title": "T", "content": ""}])
    packed = skill.calls[0]["session_state"]["relevant_memory_context"]
    assert packed == []


def test_context_pack_wiring_preserves_no_memory_as_empty():
    _, skill, _ = _run_fallback(memory_items=[])
    packed = skill.calls[0]["session_state"]["relevant_memory_context"]
    assert packed == []


def test_context_pack_wiring_brain_trace_mode_is_string():
    _, _, session_state = _run_fallback(query="let's brainstorm this")
    trace = session_state["last_brain_trace"]
    assert isinstance(trace["mode"], str)
    assert len(trace["mode"]) > 0


def test_context_pack_wiring_packed_context_includes_authority_label():
    _, skill, _ = _run_fallback()
    packed = skill.calls[0]["session_state"]["relevant_memory_context"]
    assert len(packed) == 1
    assert "authority_label" in packed[0]
    assert packed[0]["authority_label"] == "confirmed_project_memory"


def test_brain_trace_not_in_skill_state():
    # Trace must be stored on session_state only — not passed into skill_state,
    # which flows into prompt assembly.
    _, skill, session_state = _run_fallback()
    assert "last_brain_trace" in session_state
    assert "last_brain_trace" not in skill.calls[0]["session_state"]


def test_session_state_snapshot_taken_before_brain_trace_write():
    # skill_state is a snapshot of session_state taken BEFORE the trace is written.
    # If the snapshot were taken after, the trace would appear in the prompt path.
    _, skill, session_state = _run_fallback()
    # Trace present in session_state (written after snapshot)
    assert "last_brain_trace" in session_state
    # Absent from skill_state — proves snapshot was taken before the write
    assert "last_brain_trace" not in skill.calls[0]["session_state"]
    # Sanity: both point to different dicts
    assert skill.calls[0]["session_state"] is not session_state


def test_brain_trace_not_stored_when_query_empty():
    result = SkillResult(success=True, message="A.", skill="general_chat")
    skill = _FakeGeneralChatSkill(result)
    session_state: dict = {}

    outcome = asyncio.run(
        run_general_chat_fallback(
            "",
            general_chat_skill=skill,
            session_state=session_state,
            session_context=[],
            project_threads=object(),
            select_relevant_memory_context=lambda *a, **kw: [],
        )
    )
    assert outcome is None
    assert "last_brain_trace" not in session_state


def test_memory_items_without_source_become_candidate():
    item = {"id": "x", "title": "T", "content": "Some content"}  # no 'source'
    _, skill, _ = _run_fallback(memory_items=[item])
    packed = skill.calls[0]["session_state"]["relevant_memory_context"]
    assert len(packed) == 1
    assert packed[0]["source"] == "candidate_memory"
    assert packed[0]["authority_label"] == "candidate_memory"


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
