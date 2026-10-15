import asyncio

import src.skills.general_chat as general_chat_module
from src.skills.general_chat import GeneralChatSkill


def test_balanced_casual_answer_is_not_cut():
    skill = GeneralChatSkill()
    text = "One. Two. Three. Four."
    assert skill._shape_response_for_tone(
        text, mode="casual", tone_profile="balanced", explicit_depth=False
    ) == text


def test_timeline_keeps_complete_recent_turns_and_types_results():
    context = [
        {"role": "user", "content": "I need to discuss a rent increase."},
        {"role": "assistant", "content": "Lead with the facts and comparable rents."},
        {"role": "user", "content": "remind me to call Friday at 3"},
        {"role": "nova_result", "content": "Reminder saved for Friday at 3 PM."},
    ]
    messages = GeneralChatSkill._build_model_messages("ok and what if he says no", context)
    assert messages == context + [{"role": "user", "content": "ok and what if he says no"}]


def test_timeline_drops_a_long_turn_whole_instead_of_truncating_it():
    old = "old complete turn"
    too_large = "x" * 25000
    messages = GeneralChatSkill._build_model_messages(
        "current", [{"role": "user", "content": old}, {"role": "assistant", "content": too_large}]
    )
    assert all(row["content"] != too_large for row in messages)
    assert all(not row["content"].startswith("x") for row in messages)
    assert all(row["content"] != old for row in messages)
    assert messages[-1] == {"role": "user", "content": "current"}


class _Memory:
    def render_context_block(self, max_chars=300):
        return "my sister's birthday is June 3"

    def search(self, query, limit=3):
        if "sister" in query.lower():
            return [{"key": "sister birthday", "value": "June 3", "source": "explicit"}]
        return []


class _NovaMemory:
    def get_relationship_context(self, max_chars=150):
        return ""


def test_unrelated_question_does_not_receive_user_memory():
    skill = GeneralChatSkill(user_memory=_Memory(), nova_memory=_NovaMemory())
    assert "sister" not in skill._build_memory_context(
        "how do I handle a difficult conversation with my boss?"
    ).lower()


def test_directly_relevant_question_can_receive_user_memory():
    skill = GeneralChatSkill(user_memory=_Memory(), nova_memory=_NovaMemory())
    assert "sister" in skill._build_memory_context("when is my sister's birthday?").lower()


def test_message_budget_reserves_system_and_reply_space_without_partial_turns():
    context = [{"role": "user", "content": "a" * 5000}, {"role": "assistant", "content": "b" * 5000}]
    messages = GeneralChatSkill._build_model_messages(
        "current", context, system_prompt="s" * 12000, reply_tokens=2000
    )
    assert messages == [{"role": "user", "content": "current"}]


def _messages_sent_to_model(monkeypatch, query, context):
    captured = {}

    def fake_generate_chat(*args, **kwargs):
        captured.update(kwargs)
        return "A complete answer."

    monkeypatch.setattr(general_chat_module, "generate_chat", fake_generate_chat)
    result = asyncio.run(GeneralChatSkill()._run_local_model(query, context=context))
    assert result is not None and result.success
    return captured["messages"]


def test_rent_followup_is_sent_as_real_complete_turns(monkeypatch):
    context = [
        {"role": "user", "content": "My landlord proposed a 12% rent increase."},
        {
            "role": "assistant",
            "content": "Ask for the basis, compare nearby rents, and propose a smaller increase.",
        },
    ]
    messages = _messages_sent_to_model(monkeypatch, "ok and what if he says no", context)
    assert messages[:2] == context
    assert messages[-2] == {"role": "user", "content": "Okay and what if he says no."}
    assert messages[-1]["role"] == "system"


def test_reminder_result_is_sent_as_a_nova_result_not_assistant_prose(monkeypatch):
    context = [
        {"role": "user", "content": "remind me to call mom at 3pm"},
        {"role": "nova_result", "content": "Reminder saved: call mom at 3 PM."},
    ]
    messages = _messages_sent_to_model(monkeypatch, "what time did I say?", context)
    assert messages[:2] == context
    assert messages[-2] == {"role": "user", "content": "What time did I say?"}
    assert messages[-1]["role"] == "system"


def test_topic_switch_and_return_keeps_typed_turn_order(monkeypatch):
    context = [
        {"role": "user", "content": "Help me prepare for a rent discussion."},
        {"role": "assistant", "content": "Start with comparable rents and your payment history."},
        {"role": "user", "content": "What is TCP?"},
        {"role": "assistant", "content": "TCP is a reliable transport protocol."},
    ]
    messages = _messages_sent_to_model(monkeypatch, "Back to rent: what if he says no?", context)
    assert messages[:4] == context
    assert messages[-2] == {"role": "user", "content": "Back to rent: what if he says no?"}
    assert messages[-1]["role"] == "system"
