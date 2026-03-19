from pathlib import Path

from src.personality.interface_agent import PersonalityInterfaceAgent
from src.personality.tone_profile_store import ToneProfileStore


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


def test_personality_interface_agent_applies_formal_profile(tmp_path: Path):
    store = ToneProfileStore(tmp_path / "tone_profile.json")
    store.set_global_profile("formal")
    agent = PersonalityInterfaceAgent(tone_store=store)

    out = agent.present("It's ready. Let's continue if you don't want to wait.")

    lowered = out.lower()
    assert "it's" not in lowered
    assert "let's" not in lowered
    assert "don't" not in lowered
    assert "it is ready" in lowered
    assert "let us continue" in lowered


def test_personality_interface_agent_applies_concise_profile_to_follow_ups(tmp_path: Path):
    store = ToneProfileStore(tmp_path / "tone_profile.json")
    store.set_global_profile("concise")
    agent = PersonalityInterfaceAgent(tone_store=store)

    out = agent.present(
        "Status ready.\n\nTry next:\n- option one\n- option two\n- option three\n- option four"
    )

    assert "- option one" in out
    assert "- option two" in out
    assert "- option three" not in out
    assert "Ask for more options" in out


def test_personality_interface_agent_applies_detailed_profile_to_dense_sections(tmp_path: Path):
    store = ToneProfileStore(tmp_path / "tone_profile.json")
    store.set_global_profile("detailed")
    agent = PersonalityInterfaceAgent(tone_store=store)

    out = agent.present(
        "Core answer: The short version is yes. Key drivers: latency, memory bandwidth. "
        "What to verify next: benchmark the target workload."
    )

    assert "Core answer: The short version is yes." in out
    assert "\n\nKey drivers:" in out
    assert "\n\nWhat to verify next:" in out
