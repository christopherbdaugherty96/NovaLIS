

def test_formatter_normalizes_punctuation_and_spacing():
    from src.conversation.response_formatter import ResponseFormatter
    raw = "Well!!This  is   fine"

    out = ResponseFormatter.format(raw)

    assert "!" not in out
    assert "  " not in out
    assert "This" in out
