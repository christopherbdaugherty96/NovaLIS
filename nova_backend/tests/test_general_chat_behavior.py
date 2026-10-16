from src.skills.general_chat import GeneralChatSkill


def test_general_chat_has_local_memory_intelligence_fallback():
    text = GeneralChatSkill._local_conceptual_fallback(
        "What is the difference between memory and intelligence in an AI system?"
    )

    assert "Memory is stored context" in text
    assert "does not authorize actions" in text


def test_general_chat_does_not_ship_topic_specific_shopify_fallback():
    shopify = GeneralChatSkill._local_conceptual_fallback("Explain what Shopify is.")
    assert shopify == ""


def test_general_chat_has_local_governance_followup_fallbacks():
    safe_use = GeneralChatSkill._local_conceptual_fallback("How would Nova use it safely?")
    avoid = GeneralChatSkill._local_conceptual_fallback("What should it avoid doing?")

    assert "read-only" in safe_use
    assert "no silent writes" in avoid


def test_general_chat_geopolitical_refusal_helpers():
    assert GeneralChatSkill._is_geopolitical_query("tell me about the war") is True
    assert GeneralChatSkill._is_blanket_refusal("I'm sorry, I cannot assist with that topic") is True
    fallback = GeneralChatSkill._safe_geopolitical_fallback("tell me about the war")
    assert "neutral overview" in fallback.lower()
    assert "primary outlets" in fallback.lower()
