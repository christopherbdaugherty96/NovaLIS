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
    AMBIGUITY_PATTERNS = {
        "this",
        "that",
        "it",
        "something",
        "stuff",
        "help me",
        "do it",
    }
    EXPLORATORY_CUES = {"ideas", "what if", "explore", "brainstorm", "options", "approach"}
    TRANSACTIONAL_CUES = {"thanks", "thank you", "ok", "okay", "done", "yes", "no", "cancel"}

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

        ambiguity_score = cls._ambiguity_score(text, word_count)
        depth_score = cls._depth_opportunity_score(text, word_count, reasons)
        exploratory = any(cue in text for cue in cls.EXPLORATORY_CUES)
        transactional = text.strip() in cls.TRANSACTIONAL_CUES

        return {
            "escalate": escalate,
            "reason_codes": reasons,
            "confidence": 0.8 if escalate else 0.0,
            "suggested_max_tokens": 800 if escalate else 0,
            "ambiguity_score": ambiguity_score,
            "depth_opportunity_score": depth_score,
            "expansion_candidate": depth_score >= 0.45,
            "exploratory_intent": exploratory,
            "transactional_query": transactional,
            "mode": cls._mode_hint(text),
        }

    @classmethod
    def _ambiguity_score(cls, text: str, word_count: int) -> float:
        score = 0.0
        if word_count <= 4:
            score += 0.25
        if "?" not in text and word_count <= 6:
            score += 0.15
        if any(token in text.split() for token in cls.AMBIGUITY_PATTERNS):
            score += 0.35
        if text.strip() in {"help", "explain", "details"}:
            score += 0.35
        return min(score, 1.0)

    @classmethod
    def _depth_opportunity_score(cls, text: str, word_count: int, reasons: List[str]) -> float:
        score = 0.15 if word_count > 15 else 0.0
        if "DEPTH_KEYWORD" in reasons:
            score += 0.45
        if "DEEP_CONTEXT" in reasons:
            score += 0.25
        if any(cue in text for cue in cls.EXPLORATORY_CUES):
            score += 0.25
        return min(score, 1.0)

    @classmethod
    def _mode_hint(cls, text: str) -> str:
        if any(cue in text for cue in ("ideas", "what if", "explore", "brainstorm")):
            return "brainstorming"
        if any(cue in text for cue in ("analyze", "analyse", "compare", "deep dive", "evaluate")):
            return "analytical"
        if any(cue in text for cue in ("implement", "write code", "modify", "file", "patch")):
            return "implementation"
        return "casual"
