import asyncio
from pathlib import Path
from unittest.mock import patch

from src.skills.general_chat import GeneralChatSkill
from src.personality.tone_profile_store import ToneProfileStore


def test_general_chat_depth_hint_detection():
    assert GeneralChatSkill._user_requested_depth("go deeper on this topic") is True
    assert GeneralChatSkill._user_requested_depth("give me the long version") is True
    assert GeneralChatSkill._user_requested_depth("quick summary please") is False


def test_general_chat_concise_enforcer_limits_length_and_sentences():
    long_text = (
        "First sentence has useful context. "
        "Second sentence adds details. "
        "Third sentence should be dropped. "
        "Fourth sentence should also be dropped."
    )
    out = GeneralChatSkill._enforce_concise_response(long_text, max_sentences=2, max_chars=120)
    assert "First sentence" in out
    assert "Second sentence" in out
    assert "Third sentence" not in out
    assert len(out) <= 120


def test_general_chat_detailed_tone_changes_prompt_and_preserves_more_context(tmp_path: Path):
    store = ToneProfileStore(tmp_path / "tone_profile.json")
    store.set_global_profile("detailed")
    skill = GeneralChatSkill(tone_store=store)
    captured = {}

    def _fake_generate_chat(_prompt: str, **kwargs):
        captured.update(kwargs)
        return (
            "First sentence has useful context. "
            "Second sentence adds details. "
            "Third sentence keeps important nuance. "
            "Fourth sentence rounds it out."
        )

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        result = asyncio.run(skill._run_local_model("What is a GPU?"))

    assert result is not None
    assert result.success is True
    assert "Third sentence keeps important nuance." in result.message
    assert "butler-like courtesy" not in captured["system_prompt"]
    assert "Tone profile: Detailed." in captured["system_prompt"]
    assert captured["max_tokens"] > 90
    assert (result.data or {}).get("tone_profile") == "detailed"


def test_general_chat_concise_tone_tightens_casual_chat_budget(tmp_path: Path):
    store = ToneProfileStore(tmp_path / "tone_profile.json")
    store.set_global_profile("concise")
    skill = GeneralChatSkill(tone_store=store)
    captured = {}

    def _fake_generate_chat(_prompt: str, **kwargs):
        captured.update(kwargs)
        return (
            "First sentence has useful context. "
            "Second sentence adds details. "
            "Third sentence keeps important nuance."
        )

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        result = asyncio.run(skill._run_local_model("What is a GPU?"))

    assert result is not None
    assert result.success is True
    assert "Second sentence adds details." not in result.message
    assert captured["max_tokens"] <= 70
    assert "Tone profile: Concise." in captured["system_prompt"]
    assert (result.data or {}).get("tone_profile") == "concise"


def test_general_chat_uses_deterministic_local_greeting_without_model_call():
    skill = GeneralChatSkill()

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        result = asyncio.run(skill.handle("hello", context=[], session_state={}))

    assert result is not None
    assert result.success is True
    assert result.message == "Hello. What do you want to work on?"
    assert (result.data or {}).get("structured_data", {}).get("deterministic_social") is True


def test_general_chat_uses_deterministic_local_thanks_without_model_call():
    skill = GeneralChatSkill()

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        result = asyncio.run(skill.handle("thanks", context=[], session_state={}))

    assert result is not None
    assert result.success is True
    assert result.message == "You're welcome."


def test_general_chat_builds_bounded_conversational_prompt_with_session_context():
    skill = GeneralChatSkill()
    captured = {}

    def _fake_generate_chat(prompt: str, **kwargs):
        captured["prompt"] = prompt
        captured.update(kwargs)
        return "It matters because GPUs accelerate the parallel work used in graphics and machine learning."

    context = [
        {"role": "user", "content": "What is a GPU?"},
        {"role": "assistant", "content": "A GPU is a processor designed for highly parallel work, especially graphics and machine learning."},
        {"role": "user", "content": "I mostly care about why it matters for local AI."},
        {"role": "assistant", "content": "It matters because local AI inference benefits from fast parallel math and enough memory bandwidth."},
    ]
    session_state = {
        "active_topic": "local AI hardware",
        "project_thread_active": "Nova runtime polish",
        "session_id": "sess-1",
    }

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        result = asyncio.run(
            skill.handle("Why does that matter?", context=context, session_state=session_state)
        )

    assert result is not None
    assert result.success is True
    assert "Recent conversation" in captured["prompt"]
    assert "User: What is a GPU?" in captured["prompt"]
    assert "Nova: A GPU is a processor designed for highly parallel work" in captured["prompt"]
    assert "Current user message:\nWhy does that matter?" in captured["prompt"]
    assert "Active topic: local AI hardware" in captured["prompt"]
    assert "Active project thread: Nova runtime polish" in captured["prompt"]
    assert captured["session_id"] == "sess-1"


def test_general_chat_adds_natural_followup_prompt_for_exploratory_queries():
    skill = GeneralChatSkill()

    def _fake_generate_chat(_prompt: str, **kwargs):
        return "A good starting point is a simple dashboard with a few high-signal panels."

    session_state = {
        "turn_count": 0,
        "last_clarification_turn": None,
        "deep_mode_armed": False,
    }

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        result = asyncio.run(
            skill.handle(
                "Can we brainstorm options and compare trade-offs for Nova's dashboard layout?",
                context=[],
                session_state=session_state,
            )
        )

    assert result is not None
    assert result.success is True
    assert "simple dashboard with a few high-signal panels." in result.message
    assert "branch this into a few directions" in result.message


def test_general_chat_adds_reference_hint_for_ordinal_followup():
    skill = GeneralChatSkill()
    captured = {}

    def _fake_generate_chat(prompt: str, **kwargs):
        captured["prompt"] = prompt
        return "The first option is the best starting point because it is simpler to validate."

    context = [
        {"role": "user", "content": "Give me three dashboard ideas."},
        {
            "role": "assistant",
            "content": "Here are three ideas:\n1. Minimal operator dashboard\n2. Research-first workspace\n3. Ambient command center",
        },
    ]

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        result = asyncio.run(
            skill.handle(
                "Go with the first.",
                context=context,
                session_state={"session_id": "sess-ordinal"},
            )
        )

    assert result is not None
    assert result.success is True
    assert "Likely referenced prior option 1: Minimal operator dashboard" in captured["prompt"]
    assert "Current user message:\nGo with the first." in captured["prompt"]


def test_general_chat_rolls_older_context_into_summary():
    skill = GeneralChatSkill()
    session_state = {"active_topic": "Nova dashboard", "general_chat_summary": {}}
    context = [
        {"role": "user", "content": "I want to redesign Nova's dashboard for daily use."},
        {"role": "assistant", "content": "We can focus on clarity first."},
        {"role": "user", "content": "Give me three layout ideas."},
        {
            "role": "assistant",
            "content": "1. Minimal operator dashboard\n2. Research-first workspace\n3. Ambient command center",
        },
        {"role": "user", "content": "Which one would feel calm but still useful?"},
        {"role": "assistant", "content": "The minimal operator dashboard is the calmest."},
        {"role": "user", "content": "What should we prototype first?"},
        {"role": "assistant", "content": "Start with the minimal operator dashboard."},
        {"role": "user", "content": "Keep going."},
        {"role": "assistant", "content": "We should keep the first version narrow."},
        {"role": "user", "content": "What else matters?"},
        {"role": "assistant", "content": "Visual hierarchy and scannability."},
        {"role": "user", "content": "Continue."},
        {"role": "assistant", "content": "Then refine the trust surfaces."},
    ]

    retained = skill.roll_context_forward(context, session_state)

    assert len(retained) == skill._SUMMARY_RETAIN_CONTEXT_ENTRIES
    summary = session_state["general_chat_summary"]
    assert summary["topic"] == "Nova dashboard"
    assert "redesign nova's dashboard" in summary["user_goal"].lower()
    assert "what should we prototype first?" in summary["open_question"].lower()
    assert summary["relevant_options"][0] == "Minimal operator dashboard"


def test_general_chat_uses_summary_when_older_context_rolls_out():
    skill = GeneralChatSkill()
    captured = {}

    def _fake_generate_chat(prompt: str, **kwargs):
        captured["prompt"] = prompt
        return "Start with the minimal operator dashboard and refine it in small passes."

    context = [
        {"role": "user", "content": "I want to redesign Nova's dashboard for daily use."},
        {"role": "assistant", "content": "We can focus on clarity first."},
        {"role": "user", "content": "Give me three layout ideas."},
        {
            "role": "assistant",
            "content": "1. Minimal operator dashboard\n2. Research-first workspace\n3. Ambient command center",
        },
        {"role": "user", "content": "Which one would feel calm but still useful?"},
        {"role": "assistant", "content": "The minimal operator dashboard is the calmest."},
        {"role": "user", "content": "What should we prototype first?"},
        {"role": "assistant", "content": "Start with the minimal operator dashboard."},
        {"role": "user", "content": "Keep going."},
        {"role": "assistant", "content": "We should keep the first version narrow."},
    ]
    session_state = {
        "session_id": "sess-summary",
        "active_topic": "Nova dashboard",
        "general_chat_summary": {
            "topic": "Nova dashboard",
            "user_goal": "I want to redesign Nova's dashboard for daily use.",
            "open_question": "What should we prototype first?",
            "relevant_options": ["Minimal operator dashboard", "Research-first workspace"],
        },
    }

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        result = asyncio.run(
            skill.handle(
                "What should we build first now?",
                context=context,
                session_state=session_state,
            )
        )

    assert result is not None
    assert result.success is True
    assert "Earlier conversation summary" in captured["prompt"]
    assert "- Topic: Nova dashboard" in captured["prompt"]
    assert "- User goal: I want to redesign Nova's dashboard for daily use." in captured["prompt"]
    assert "Earlier options still relevant" in captured["prompt"]
