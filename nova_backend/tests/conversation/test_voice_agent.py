from src.voice.stt_pipeline import STTAckConfig
from src.voice.voice_agent import VoiceExperienceAgent


def test_voice_agent_uses_mode_aware_acknowledgement_for_default_voice_ack():
    agent = VoiceExperienceAgent()

    payload = agent.build_ack_payload(STTAckConfig(enabled=True, text="Got it."), mode="analysis")

    assert payload == {"type": "ack", "message": "Okay."}


def test_voice_agent_trims_visual_followup_sections_from_spoken_output():
    agent = VoiceExperienceAgent()

    out = agent.prepare_spoken_reply(
        "The safest starting point is the first option.\n\nTry next:\n- Compare it with the second path.",
        mode="analysis",
    )

    assert "Try next" not in out
    assert "Compare it with the second path" not in out
    assert "The safest starting point is the first option." in out


def test_voice_agent_speaks_summary_and_notes_screen_for_long_answers():
    agent = VoiceExperienceAgent()

    out = agent.prepare_spoken_reply(
        "Summary: Start with the smaller workspace shell. It is calmer, easier to test, and less likely to sprawl. "
        "After that, add the richer board view once the first flow feels stable. "
        "If you want, I can compare that with the denser version.",
        mode="analysis",
    )

    assert out.startswith("Start with the smaller workspace shell.")
    assert "full answer on screen" in out
