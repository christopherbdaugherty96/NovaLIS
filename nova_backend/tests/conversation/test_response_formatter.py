

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


def test_format_payload_keeps_plain_numbered_option_lists_unwrapped():
    from src.conversation.response_formatter import ResponseFormatter

    payload = ResponseFormatter.format_payload(
        "1. Minimal operator dashboard\n2. Research-first workspace\n3. Ambient command center"
    )

    assert payload["user_message"].startswith("1. Minimal operator dashboard")
    assert not payload["user_message"].startswith("Summary:")


def test_format_payload_keeps_explicit_bottom_line_when_present():
    from src.conversation.response_formatter import ResponseFormatter

    payload = ResponseFormatter.format_payload(
        "Bottom line: The review mostly agrees.\n\nAgreement Level: Medium\nMain gap: add one caveat."
    )

    assert payload["user_message"].startswith("Bottom line: The review mostly agrees.")


def test_format_payload_uses_first_top_headline_as_summary_anchor():
    from src.conversation.response_formatter import ResponseFormatter

    payload = ResponseFormatter.format_payload(
        "Top Headlines\n1. Markets rose after the inflation print cooled.\n\nSignals to Watch\n- Bond yields"
    )

    assert payload["user_message"].startswith("Summary: Markets rose after the inflation print cooled.")


def test_speakable_text_strips_urls_and_paths():
    from src.conversation.response_formatter import ResponseFormatter

    out = ResponseFormatter.to_speakable_text("Open https://example.com and /tmp/file.txt")

    assert "http" not in out.lower()
    assert "/tmp" not in out


def test_friendly_fallback_guides_user():
    from src.conversation.response_formatter import ResponseFormatter

    out = ResponseFormatter.friendly_fallback()
    assert "didn't quite" in out.lower()
    assert "what can you do" in out.lower()
    assert len(out) > 20


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


def test_formatter_applies_nova_style_contract_without_removing_light_warmth():
    from src.conversation.response_formatter import ResponseFormatter

    out = ResponseFormatter.format("Absolutely. Great question. I'd be happy to help with that.")

    lowered = out.lower()
    assert "absolutely" not in lowered
    assert "great question" in lowered
    assert "happy to help" in lowered
    assert out == "Great question. I'd be happy to help with that."


def test_formatter_preserves_spoken_sure_thing_acknowledgement():
    from src.conversation.response_formatter import ResponseFormatter

    out = ResponseFormatter.format("Sure thing. I can explain that more simply.")

    assert out == "Sure thing. I can explain that more simply."


def test_formatter_uses_nova_brainstorming_initiative_tail():
    from src.conversation.response_formatter import ResponseFormatter

    out = ResponseFormatter.with_conversational_initiative(
        "A clean starting point is a simpler dashboard shell.",
        mode="brainstorming",
        allow_branch_suggestion=True,
        allow_depth_prompt=True,
    )

    assert "A clean starting point is a simpler dashboard shell." in out
    assert "compare two or three directions or go deeper on one path" in out


def test_formatter_rewrites_brainstorming_intro_into_nova_wording():
    from src.conversation.response_formatter import ResponseFormatter

    out = ResponseFormatter.format("Here are a few ideas. One is calmer. One is denser.", mode="brainstorming")

    assert out.startswith("Here are a few grounded directions.")


def test_formatter_rewrites_analytical_i_think_intro_into_nova_wording():
    from src.conversation.response_formatter import ResponseFormatter

    out = ResponseFormatter.format("I think the first trade-off matters most.", mode="analytical")

    assert out == "The clearest read is that the first trade-off matters most."
