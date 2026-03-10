import re
from typing import Any, Dict, List


class ComplexityHeuristics:
    """Deterministic heuristics for Stage-1 escalation decisions."""

    DEPTH_KEYWORDS = {
        "analyze",
        "analyse",
        "explain",
        "explanation",
        "why",
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
        "implication",
        "root cause",
        "drivers",
        "risks",
        "benefits",
        "assumptions",
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
    MULTI_PART_CUES = {" and ", " versus ", " vs ", " compared to ", " implications ", " tradeoff ", " trade-off "}

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

        if cls._is_multi_part_query(text, word_count):
            reasons.append("MULTI_PART_QUERY")

        if (user_message or "").strip().lower() in cls.SIMPLE_GREETINGS:
            reasons = []
            escalate = False
        else:
            escalate = len(reasons) > 0

        ambiguity_score = cls._ambiguity_score(text, word_count)
        depth_score = cls._depth_opportunity_score(text, word_count, reasons)
        exploratory = any(cue in text for cue in cls.EXPLORATORY_CUES)
        transactional = text.strip() in cls.TRANSACTIONAL_CUES
        complexity_score = cls._complexity_score(word_count, reasons, text)
        suggested_tokens = cls._suggested_tokens(escalate, reasons, complexity_score)

        return {
            "escalate": escalate,
            "reason_codes": reasons,
            "confidence": min(0.95, 0.65 + (0.08 * len(reasons))) if escalate else 0.0,
            "suggested_max_tokens": suggested_tokens,
            "ambiguity_score": ambiguity_score,
            "depth_opportunity_score": depth_score,
            "expansion_candidate": depth_score >= 0.45,
            "exploratory_intent": exploratory,
            "transactional_query": transactional,
            "complexity_score": complexity_score,
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

    @classmethod
    def _is_multi_part_query(cls, text: str, word_count: int) -> bool:
        if word_count < 10:
            return False
        if ";" in text or ":" in text:
            return True
        return any(cue in text for cue in cls.MULTI_PART_CUES)

    @classmethod
    def _complexity_score(cls, word_count: int, reasons: List[str], text: str) -> float:
        score = 0.1 if word_count > 14 else 0.0
        score += 0.2 if "LONG_QUERY" in reasons else 0.0
        score += 0.28 if "DEPTH_KEYWORD" in reasons else 0.0
        score += 0.25 if "CODE_BLOCK" in reasons else 0.0
        score += 0.15 if "DEEP_CONTEXT" in reasons else 0.0
        score += 0.18 if "MULTI_PART_QUERY" in reasons else 0.0
        if text.count("?") >= 2:
            score += 0.12
        return min(score, 1.0)

    @staticmethod
    def _suggested_tokens(escalate: bool, reasons: List[str], complexity_score: float) -> int:
        if not escalate:
            return 0
        budget = 640
        if "CODE_BLOCK" in reasons:
            budget += 140
        if "DEEP_CONTEXT" in reasons:
            budget += 90
        if "LONG_QUERY" in reasons or "MULTI_PART_QUERY" in reasons:
            budget += 80
        if complexity_score >= 0.75:
            budget += 60
        return min(budget, 980)
