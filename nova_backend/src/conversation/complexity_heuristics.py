import re
from typing import Any, Dict, List


class ComplexityHeuristics:
    """Deterministic heuristics for Stage-1 escalation decisions."""

    DEPTH_KEYWORDS = {
        "analyze",
        "analyse",
        "comparison",
        "compare",
        "contrast",
        "evaluate",
        "assessment",
        "pros and cons",
        "tradeoffs",
        "strategy",
        "plan",
        "scenario",
        "what if",
        "implications",
        "detailed",
        "in depth",
        "comprehensive",
        "explain thoroughly",
    }

    CODE_PATTERNS = [
        r"```",
        r"def .+\(.*\):",
        r"class .+:",
        r"import ",
        r"from .+ import",
        r"function ",
        r"return ",
        r"if __name__",
        r"<[a-z]+>",
        r"\bconst\b",
        r"\blet\b",
    ]

    SIMPLE_GREETINGS = {"hi", "hello", "hey", "good morning", "good afternoon"}

    @classmethod
    def assess(cls, user_message: str, context: List[Dict[str, str]]) -> Dict[str, Any]:
        text = (user_message or "").lower()
        word_count = len((user_message or "").split())

        reasons: List[str] = []

        if word_count > 30:
            reasons.append("LONG_QUERY")

        if any(keyword in text for keyword in cls.DEPTH_KEYWORDS):
            reasons.append("DEPTH_KEYWORD")

        if any(re.search(pattern, user_message or "") for pattern in cls.CODE_PATTERNS):
            reasons.append("CODE_BLOCK")

        if len(context or []) >= 6:
            reasons.append("DEEP_CONTEXT")

        if (user_message or "").strip().lower() in cls.SIMPLE_GREETINGS:
            reasons = []
            escalate = False
        else:
            escalate = len(reasons) > 0

        return {
            "escalate": escalate,
            "reason_codes": reasons,
            "confidence": 0.8 if escalate else 0.0,
            "suggested_max_tokens": 800 if escalate else 0,
        }
