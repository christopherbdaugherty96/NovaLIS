

def test_policy_allow_for_escalation_when_limits_not_hit():
    from src.conversation.escalation_policy import EscalationPolicy
    policy = EscalationPolicy()

    decision = policy.decide(
        {"escalate": True},
        "analyze this",
        {"turn_count": 3, "escalation_count": 0, "deep_mode_armed": True},
    )

    assert decision == "ALLOW_ANALYSIS_ONLY"


def test_policy_denies_during_cooldown():
    from src.conversation.escalation_policy import EscalationPolicy
    policy = EscalationPolicy({"max_tokens_cap": 900, "max_escalations_per_session": 5, "cooldown_turns": 3})

    decision = policy.decide(
        {"escalate": True},
        "analyze this",
        {"turn_count": 5, "escalation_count": 1, "last_escalation_turn": 4, "deep_mode_armed": True},
    )

    assert decision == "DENY"


def test_policy_asks_user_after_session_cap():
    from src.conversation.escalation_policy import EscalationPolicy
    policy = EscalationPolicy({"max_tokens_cap": 900, "max_escalations_per_session": 1, "cooldown_turns": 0})

    decision = policy.decide(
        {"escalate": True},
        "analyze this",
        {"turn_count": 5, "escalation_count": 1, "deep_mode_armed": True},
    )

    assert decision == "ASK_USER"


def test_policy_denies_when_deep_mode_not_armed():
    from src.conversation.escalation_policy import EscalationPolicy
    policy = EscalationPolicy()

    decision = policy.decide({"escalate": True}, "analyze this", {"turn_count": 3, "escalation_count": 0})

    assert decision == "DENY"


def test_policy_allows_explicit_depth_request_when_armed():
    from src.conversation.escalation_policy import EscalationPolicy

    policy = EscalationPolicy()
    decision = policy.decide(
        {"escalate": False, "depth_opportunity_score": 0.2},
        "Can you give me a deep dive on this?",
        {"turn_count": 2, "escalation_count": 0, "deep_mode_armed": True},
    )

    assert decision == "ALLOW_ANALYSIS_ONLY"


def test_policy_reason_summary_is_human_readable():
    from src.conversation.escalation_policy import EscalationPolicy

    summary = EscalationPolicy.summarize_reason(
        {"reason_codes": ["LONG_QUERY", "DEEP_CONTEXT", "MULTI_PART_QUERY"]}
    )

    assert "long query" in summary.lower()
    assert "deep context" in summary.lower()
