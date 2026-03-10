

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


def test_heuristics_detects_multi_part_analysis_and_larger_token_budget():
    from src.conversation.complexity_heuristics import ComplexityHeuristics

    result = ComplexityHeuristics.assess(
        "Compare Nvidia and AMD versus Intel and explain implications for data center spending.",
        context=[{"role": "assistant", "content": "Prior context"}] * 6,
    )

    assert result["escalate"] is True
    assert "MULTI_PART_QUERY" in result["reason_codes"]
    assert result["suggested_max_tokens"] >= 700
    assert result["complexity_score"] > 0.5
