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

SURFACE_AWARENESS_BRIEF = "awareness_brief"
SURFACE_AURALIS_TODAY = "auralis_today"
SURFACE_AMBIGUOUS = "ambiguous"

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

_DIRECT_AWARENESS_REQUEST_RE = re.compile(
    r"^(?:(?:can|could|would) you )?"
    r"(?:give|show|open|load|read|run|start)(?: me)?(?: my| the)? "
    r"(?:daily )?awareness brief(?: please)?$"
)
_DIRECT_AURALIS_REQUEST_RE = re.compile(
    r"^(?:(?:can|could|would) you )?"
    r"(?:give|show|open|load|read)(?: me)?(?: my| the)? "
    r"auralis today(?: section)?(?: please)?$"
)
_REQUEST_SHAPE_RE = re.compile(
    r"^(?:(?:can|could|would) you )?"
    r"(?:give|show|open|load|read|run|start)\b"
)
_KNOWN_SURFACE_REFERENCE_RE = re.compile(
    r"\b(?:awareness brief|daily awareness|auralis today)\b"
)


def _normalize_surface_text(text: str) -> str:
    lowered = str(text or "").strip().lower()
    lowered = re.sub(r"[^a-z' ]+", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return re.sub(r"\bwhats\b", "what's", lowered)


def classify_governed_surface_request(text: str) -> str:
    """Classify request-shaped references owned by the Awareness Brief surface.

    This is the single vocabulary boundary shared by deterministic routing and
    the GeneralChat backstop. Mere mentions are deliberately not classified.
    """
    lowered = _normalize_surface_text(text)
    if not lowered:
        return ""
    if lowered in _AWARENESS_BRIEF_TRIGGERS:
        return SURFACE_AWARENESS_BRIEF
    if _DIRECT_AWARENESS_REQUEST_RE.match(lowered):
        return SURFACE_AWARENESS_BRIEF
    if _DIRECT_AURALIS_REQUEST_RE.match(lowered):
        return SURFACE_AURALIS_TODAY
    if any(pattern.match(lowered) for pattern in _AWARENESS_BRIEF_PATTERNS):
        if "auralis" in lowered:
            return SURFACE_AURALIS_TODAY
        return SURFACE_AWARENESS_BRIEF
    if _REQUEST_SHAPE_RE.match(lowered) and _KNOWN_SURFACE_REFERENCE_RE.search(lowered):
        return SURFACE_AMBIGUOUS
    return ""


def is_awareness_brief_request(text: str) -> bool:
    """True when a user asks for the current daily awareness surface."""
    return classify_governed_surface_request(text) in {
        SURFACE_AWARENESS_BRIEF,
        SURFACE_AURALIS_TODAY,
    }


def governed_surface_request_guard_response(text: str) -> str:
    """Fail safely when a request-shaped known surface reference is ambiguous."""
    if classify_governed_surface_request(text) != SURFACE_AMBIGUOUS:
        return ""
    return (
        "I can open your Daily Awareness Brief, including its Auralis Today section "
        "when trusted business inputs are available. Which one did you mean?"
    )
