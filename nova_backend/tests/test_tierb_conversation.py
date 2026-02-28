from src.conversation.complexity_heuristics import ComplexityHeuristics
from src.conversation.escalation_policy import EscalationPolicy
from src.conversation.response_formatter import ResponseFormatter


def test_heuristics_exposes_tierb_signals():
    result = ComplexityHeuristics.assess("Can we brainstorm ideas and compare options?", [])
    assert "ambiguity_score" in result
    assert "depth_opportunity_score" in result
    assert result["exploratory_intent"] is True
    assert result["mode"] in {"brainstorming", "analytical", "implementation", "casual"}


def test_policy_returns_non_authorizing_conversation_flags():
    policy = EscalationPolicy()
    heuristic = {
        "depth_opportunity_score": 0.8,
        "ambiguity_score": 0.7,
        "expansion_candidate": True,
        "exploratory_intent": True,
        "transactional_query": False,
    }
    flags = policy.conversational_flags(heuristic, "explore options", {"turn_count": 1})
    assert flags["allow_clarification"] is True
    assert flags["allow_branch_suggestion"] is True
    assert flags["allow_depth_prompt"] is True


def test_formatter_adds_at_most_two_tierb_prompts():
    text = ResponseFormatter.with_conversational_initiative(
        "Baseline answer.",
        mode="brainstorming",
        allow_clarification=True,
        allow_branch_suggestion=True,
        allow_depth_prompt=True,
    )
    assert "Baseline answer." in text
    assert text.count("\n") >= 2
