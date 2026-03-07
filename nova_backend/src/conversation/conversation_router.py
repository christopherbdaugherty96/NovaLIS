from __future__ import annotations

import re
from typing import Any


class ConversationRouter:
    """Deterministic pre-routing for conversational UX (non-authorizing)."""

    COMMAND_PREFIXES = (
        "open",
        "set",
        "show",
        "search",
        "look up",
        "research",
        "track",
        "update",
        "compare",
        "volume",
        "brightness",
        "play",
        "pause",
    )
    QUESTION_HINTS = ("what", "when", "where", "who", "how", "why")
    ANALYSIS_HINTS = ("analyze", "analysis", "explain", "break down", "evaluate", "trade-off", "compare")
    BRAINSTORM_HINTS = ("ideas", "brainstorm", "options", "directions", "concepts")
    HEAVY_HINTS = ("brief", "news", "search", "analyze", "analysis", "compare", "research")
    REFERENCE_PATTERNS = (
        re.compile(r"\b(open|show)\s+(that|it)\b", re.IGNORECASE),
        re.compile(r"\bthat file\b", re.IGNORECASE),
        re.compile(r"\bthat folder\b", re.IGNORECASE),
    )

    MICRO_ACK = {
        "analysis": "One moment. I'll break that down.",
        "brainstorm": "Okay. I'll give you structured options.",
        "command": "Okay. Working on that.",
        "question": "Let me check.",
    }

    @classmethod
    def route(cls, user_text: str, session_state: dict[str, Any] | None = None) -> dict[str, Any]:
        text = (user_text or "").strip()
        lowered = text.lower().rstrip(".?!")
        state = session_state or {}

        mode = "conversation"
        if lowered.startswith(cls.COMMAND_PREFIXES):
            mode = "command"
        elif any(h in lowered.split() for h in cls.QUESTION_HINTS) or "?" in text:
            mode = "question"
        if any(h in lowered for h in cls.ANALYSIS_HINTS):
            mode = "analysis"
        if any(h in lowered for h in cls.BRAINSTORM_HINTS):
            mode = "brainstorm"

        needs_clarification = False
        clarification = ""
        resolved_text = text
        if any(p.search(text) for p in cls.REFERENCE_PATTERNS):
            last_object = str(state.get("last_object") or "").strip()
            if last_object:
                resolved_text = re.sub(
                    r"\bthat file\b|\bthat folder\b|\bthat\b|\bit\b",
                    last_object,
                    text,
                    flags=re.IGNORECASE,
                )
            else:
                needs_clarification = True
                clarification = "Which file or folder do you mean?"

        should_ack = mode in {"analysis", "brainstorm"} or any(h in lowered for h in cls.HEAVY_HINTS)
        return {
            "mode": mode,
            "micro_ack": cls.MICRO_ACK.get(mode, "") if should_ack else "",
            "needs_clarification": needs_clarification,
            "clarification": clarification,
            "resolved_text": resolved_text,
        }
