from src.skills.general_chat import GeneralChatSkill


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
