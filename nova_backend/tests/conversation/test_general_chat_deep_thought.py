import asyncio

from src.skills.general_chat import GeneralChatSkill


def test_general_chat_deep_thought_payload_contains_explanation_fields():
    skill = GeneralChatSkill()
    skill.deepseek.analyze = lambda *_args, **_kwargs: (
        "Core answer: Data center demand is shifting toward inference-heavy workloads."
    )

    session_state = {
        "turn_count": 4,
        "escalation_count": 0,
        "last_escalation_turn": None,
        "deep_mode_armed": True,
        "deep_mode_disabled": False,
    }
    context = [{"role": "assistant", "content": "Earlier context"}] * 6

    result = asyncio.run(
        skill.handle(
            "Compare Nvidia and AMD and explain long-term implications for data centers.",
            context=context,
            session_state=session_state,
        )
    )

    assert result is not None
    assert result.success is True

    escalation = (result.data or {}).get("escalation", {})
    assert escalation.get("escalated") is True
    thought_data = escalation.get("thought_data") or {}
    assert thought_data.get("reason_summary")
    assert thought_data.get("mode") in {"analytical", "brainstorming", "implementation", "casual"}
    assert thought_data.get("suggested_tokens", 0) > 0
    assert thought_data.get("context_turns_used") == 6


def test_general_chat_ask_user_prompt_is_specific_for_deep_analysis():
    skill = GeneralChatSkill()
    session_state = {
        "turn_count": 6,
        "escalation_count": 3,
        "last_escalation_turn": None,
        "deep_mode_armed": True,
        "deep_mode_disabled": False,
    }
    context = [{"role": "assistant", "content": "Prior reply"}]

    result = asyncio.run(
        skill.handle(
            "Please analyze this architecture in detail.",
            context=context,
            session_state=session_state,
        )
    )

    assert result is not None
    assert result.success is True
    assert "deeper analysis" in result.message.lower()
    escalation = (result.data or {}).get("escalation", {})
    assert escalation.get("ask_user") is True


def test_general_chat_deep_thought_requests_deep_reason_profile():
    skill = GeneralChatSkill()
    captured = {}

    def _fake_analyze(*_args, **kwargs):
        captured.update(kwargs)
        return "Core answer: Demand is shifting toward inference-heavy workloads."

    skill.deepseek.analyze = _fake_analyze

    session_state = {
        "turn_count": 4,
        "escalation_count": 0,
        "last_escalation_turn": None,
        "deep_mode_armed": True,
        "deep_mode_disabled": False,
    }
    context = [{"role": "assistant", "content": "Earlier context"}] * 3

    result = asyncio.run(
        skill.handle(
            "Analyze the long-term implications of inference demand.",
            context=context,
            session_state=session_state,
        )
    )

    assert result is not None
    assert result.success is True
    assert captured.get("analysis_profile") == "deep_reason"
