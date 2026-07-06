"""Awareness Brief trigger matching.

The Awareness Brief is the current one-surface daily view. It includes the C1
Auralis Today section when trusted business inputs exist, so dogfood phrasing
that asks "what should I do today?" must reach this path instead of generic
chat or web search.

Read-only: matching a phrase here only selects the existing awareness brief
render path. It does not grant execution authority or add a capability.
"""

from __future__ import annotations

import re

_AWARENESS_BRIEF_TRIGGERS = frozenset({
    "awareness",
    "awareness brief",
    "daily awareness",
})

_AWARENESS_BRIEF_PATTERNS = (
    re.compile(r"^what should i do today$"),
    re.compile(r"^what should i do for auralis today$"),
    re.compile(r"^what(?:'s| is) my brief$"),
    re.compile(r"^read me my brief$"),
    re.compile(r"^give me (?:the )?rundown$"),
    re.compile(r"^what matters for auralis today$"),
    re.compile(r"^what(?:'s| is) my auralis move today$"),
)


def is_awareness_brief_request(text: str) -> bool:
    """True when a user asks for the current daily awareness surface."""
    lowered = str(text or "").strip().lower().rstrip(".?!")
    lowered = re.sub(r"\bwhats\b", "what's", lowered)
    lowered = re.sub(r"\s+", " ", lowered)
    if lowered in _AWARENESS_BRIEF_TRIGGERS:
        return True
    return any(pattern.match(lowered) for pattern in _AWARENESS_BRIEF_PATTERNS)
