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


def test_voice_agent_summarizes_structured_second_opinion_for_speech():
    agent = VoiceExperienceAgent()

    out = agent.prepare_spoken_reply(
        "Governed Second Opinion\n"
        "Bottom line: The review partly agrees with Nova's answer but found a meaningful caveat.\n"
        "Agreement Level: Medium (0.65)\n"
        "Review Confidence: High (0.90)\n"
        "Main gap: the answer needs a clearer caveat\n"
        "Best correction: explain the uncertainty in one sentence\n\n"
        "Full review:\nAccuracy: medium\nPotential Issues:\n- the answer needs a clearer caveat\n"
        "Suggested Corrections:\n- explain the uncertainty in one sentence\nConfidence: high",
        mode="analysis",
    )

    assert out.startswith("Second opinion ready.")
    assert "Bottom line: The review partly agrees with Nova's answer but found a meaningful caveat." in out
    assert "Agreement level Medium (0.65)." in out
    assert "Main gap: the answer needs a clearer caveat." in out
    assert "full review on screen" in out


def test_voice_agent_uses_bottom_line_for_structured_reports():
    agent = VoiceExperienceAgent()

    out = agent.prepare_spoken_reply(
        "INTELLIGENCE BRIEF\n"
        "Topic: AI regulation\n\n"
        "Bottom line: Regulatory pressure is rising faster than deployment teams expected.\n\n"
        "Summary\n"
        "-------\n"
        "Regulatory pressure is rising faster than deployment teams expected.",
        mode="analysis",
    )

    assert out.startswith("Report ready.")
    assert "Regulatory pressure is rising faster than deployment teams expected." in out
    assert "full answer on screen" in out
