

def test_formatter_normalizes_punctuation_and_spacing():
    from src.conversation.response_formatter import ResponseFormatter
    raw = "Well!!This  is   fine"

    out = ResponseFormatter.format(raw)

    assert "!" not in out
    assert "  " not in out
    assert "This" in out


def test_format_payload_builds_speakable_and_summary_for_structured_text():
    from src.conversation.response_formatter import ResponseFormatter

    payload = ResponseFormatter.format_payload("Item one.\n- Item two")

    assert payload["user_message"].startswith("Summary:")
    assert "speakable_text" in payload


def test_speakable_text_strips_urls_and_paths():
    from src.conversation.response_formatter import ResponseFormatter

    out = ResponseFormatter.to_speakable_text("Open https://example.com and /tmp/file.txt")

    assert "http" not in out.lower()
    assert "/tmp" not in out


def test_friendly_fallback_guides_user():
    from src.conversation.response_formatter import ResponseFormatter

    out = ResponseFormatter.friendly_fallback()
    assert "weather" in out.lower()
    assert "today's news" in out.lower()


def test_initiative_is_suppressed_for_rewrite_style_preferences():
    from src.conversation.response_formatter import ResponseFormatter

    out = ResponseFormatter.with_conversational_initiative(
        "Baseline answer.",
        mode="brainstorming",
        allow_clarification=False,
        allow_branch_suggestion=True,
        allow_depth_prompt=True,
        presentation_preference="simpler",
    )

    assert out == "Baseline answer."
