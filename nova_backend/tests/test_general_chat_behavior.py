from src.skills.general_chat import GeneralChatSkill


def test_general_chat_geopolitical_refusal_helpers():
    assert GeneralChatSkill._is_geopolitical_query("tell me about the war") is True
    assert GeneralChatSkill._is_blanket_refusal("I'm sorry, I cannot assist with that topic") is True
    fallback = GeneralChatSkill._safe_geopolitical_fallback("tell me about the war")
    assert "neutral overview" in fallback.lower()
    assert "primary outlets" in fallback.lower()
