

def test_heuristics_returns_reason_codes_for_depth_and_code():
    from src.conversation.complexity_heuristics import ComplexityHeuristics
    msg = "Please analyze this code: ```python\ndef run():\n    return 1\n```"
    result = ComplexityHeuristics.assess(msg, context=[])

    assert result["escalate"] is True
    assert "DEPTH_KEYWORD" in result["reason_codes"]
    assert "CODE_BLOCK" in result["reason_codes"]


def test_heuristics_ignores_simple_greeting():
    from src.conversation.complexity_heuristics import ComplexityHeuristics
    result = ComplexityHeuristics.assess("hello", context=[])

    assert result["escalate"] is False
    assert result["reason_codes"] == []
