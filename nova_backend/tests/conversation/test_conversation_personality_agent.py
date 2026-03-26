from src.personality.conversation_personality_agent import ConversationPersonalityAgent


def test_conversation_personality_agent_softens_known_cancel_message():
    agent = ConversationPersonalityAgent()

    out = agent.present("Cancelled website open request.")

    assert out == "Okay. I canceled the website open request."


def test_conversation_personality_agent_softens_brief_runtime_status():
    agent = ConversationPersonalityAgent()

    out = agent.present("Muted.")

    assert out == "Okay. Muted."


def test_conversation_personality_agent_rewrites_fallback_more_naturally():
    agent = ConversationPersonalityAgent()

    out = agent.present(
        "I might have misunderstood that. Try one of these: what can you do, what time is it, today's news, or open documents."
    )

    lowered = out.lower()
    assert "didn't quite catch that" in lowered
    assert "what can you do" in lowered
