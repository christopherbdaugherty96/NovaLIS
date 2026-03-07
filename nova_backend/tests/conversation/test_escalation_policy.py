

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
