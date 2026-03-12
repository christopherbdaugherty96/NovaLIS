from src.personality.interface_agent import PersonalityInterfaceAgent


def test_personality_interface_agent_removes_system_tokens():
    agent = PersonalityInterfaceAgent()
    out = agent.present("You should run this now. <function_call name='x'/> capability_id: 18")

    lowered = out.lower()
    assert "<function_call" not in lowered
    assert "capability_id" not in lowered
    assert "you should" not in lowered


def test_personality_interface_agent_rewrites_authority_and_emotional_language():
    agent = PersonalityInterfaceAgent()
    out = agent.present("Trust me. I recommend that you restart it. Don't worry, I'm here for you!")

    lowered = out.lower()
    assert "trust me" not in lowered
    assert "i recommend" not in lowered
    assert "don't worry" not in lowered
    assert "i'm here for you" not in lowered
    assert "reasonable option" in lowered


def test_personality_interface_agent_preserves_structured_content():
    agent = PersonalityInterfaceAgent()
    out = agent.present("Summary\n\n- Item one\n- Item two")

    assert out.startswith("Summary")
    assert "- Item one" in out
    assert "- Item two" in out
