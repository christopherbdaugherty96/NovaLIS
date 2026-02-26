from typing import Any, Dict, Literal

PolicyDecision = Literal["ALLOW", "DENY", "ASK_USER"]


class EscalationPolicy:
    def __init__(self, config: dict | None = None):
        self.config = config or {
            "max_tokens_cap": 900,
            "max_escalations_per_session": 5,
            "cooldown_turns": 2,
        }

    def decide(
        self,
        heuristic_result: Dict[str, Any],
        user_message: str,
        session_state: dict,
    ) -> PolicyDecision:
        del user_message

        if not heuristic_result.get("escalate"):
            return "DENY"

        if session_state.get("last_escalation_turn") is not None:
            turns_since = session_state.get("turn_count", 0) - session_state["last_escalation_turn"]
            if turns_since < self.config["cooldown_turns"]:
                return "DENY"

        if session_state.get("escalation_count", 0) >= self.config["max_escalations_per_session"]:
            return "ASK_USER"

        if session_state.get("deep_mode_disabled"):
            return "DENY"

        return "ALLOW"
