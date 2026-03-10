from typing import Any, Dict, Literal

PolicyDecision = Literal["ALLOW_ANALYSIS_ONLY", "DENY", "ASK_USER"]


class EscalationPolicy:
    EXPLICIT_DEPTH_HINTS = (
        "deep",
        "deeper",
        "deep dive",
        "in detail",
        "detailed",
        "thorough",
        "break this down",
        "explain fully",
        "full analysis",
        "compare",
        "trade-off",
        "tradeoff",
        "implication",
    )

    def __init__(self, config: dict | None = None):
        self.config = config or {
            "max_tokens_cap": 900,
            "max_escalations_per_session": 5,
            "cooldown_turns": 2,
            "ask_user_threshold": 3,
        }

    def conversational_flags(
        self,
        heuristic_result: Dict[str, Any],
        user_message: str,
        session_state: dict,
    ) -> Dict[str, bool]:
        text = (user_message or "").strip().lower()
        depth_score = float(heuristic_result.get("depth_opportunity_score", 0.0))
        ambiguity_score = float(heuristic_result.get("ambiguity_score", 0.0))
        exploratory = bool(heuristic_result.get("exploratory_intent", False))
        transactional = bool(heuristic_result.get("transactional_query", False))

        turn = int(session_state.get("turn_count", 0))
        last_clarification_turn = session_state.get("last_clarification_turn")
        clarification_on_cooldown = (last_clarification_turn is not None and turn == last_clarification_turn)

        direct_execution = any(cmd in text for cmd in ("search ", "open ", "speak that", "read that", "say it"))

        return {
            "allow_clarification": ambiguity_score >= 0.5 and not clarification_on_cooldown and not transactional,
            "allow_branch_suggestion": heuristic_result.get("expansion_candidate", False) and exploratory and not direct_execution,
            "allow_depth_prompt": depth_score >= 0.6 and exploratory and not transactional and not direct_execution,
        }

    def decide(
        self,
        heuristic_result: Dict[str, Any],
        user_message: str,
        session_state: dict,
    ) -> PolicyDecision:
        """Execution escalation decision only (non-conversational)."""
        text = (user_message or "").strip().lower()

        # Phase-4 runtime rule: deep analysis is invocation-bound.
        # No heuristic-only auto escalation.
        if not bool(session_state.get("deep_mode_armed", False)):
            return "DENY"

        explicit_depth_request = any(hint in text for hint in self.EXPLICIT_DEPTH_HINTS)
        depth_score = float(heuristic_result.get("depth_opportunity_score", 0.0))
        should_escalate = bool(heuristic_result.get("escalate")) or explicit_depth_request or depth_score >= 0.55

        if not should_escalate:
            return "DENY"

        if session_state.get("last_escalation_turn") is not None:
            turns_since = session_state.get("turn_count", 0) - session_state["last_escalation_turn"]
            if turns_since < self.config["cooldown_turns"]:
                return "DENY"

        escalation_count = session_state.get("escalation_count", 0)
        if escalation_count >= self.config["max_escalations_per_session"]:
            return "ASK_USER"

        if session_state.get("deep_mode_disabled"):
            return "DENY"

        if escalation_count >= self.config.get("ask_user_threshold", 3):
            return "ASK_USER"

        return "ALLOW_ANALYSIS_ONLY"

    @staticmethod
    def summarize_reason(heuristic_result: Dict[str, Any]) -> str:
        reasons = list(heuristic_result.get("reason_codes") or [])
        if not reasons:
            return "Deep mode was explicitly requested."

        readable = [str(code).replace("_", " ").lower() for code in reasons]
        if len(readable) == 1:
            return f"Triggered by {readable[0]}."
        if len(readable) == 2:
            return f"Triggered by {readable[0]} and {readable[1]}."
        return f"Triggered by {', '.join(readable[:-1])}, and {readable[-1]}."
