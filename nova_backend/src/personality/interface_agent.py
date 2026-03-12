from __future__ import annotations

import re


class PersonalityInterfaceAgent:
    """Presentation-only personality layer for outbound chat messages."""

    _SYSTEM_TOKEN_PATTERNS = (
        re.compile(r"<function_call[^>]*>", re.IGNORECASE),
        re.compile(r"\btool_call\b", re.IGNORECASE),
        re.compile(r"\bcapability\s*[_-]?id\s*[:=]?\s*\d+\b", re.IGNORECASE),
        re.compile(r"\bexecutor\s*[_-]?id\s*[:=]?\s*\d+\b", re.IGNORECASE),
    )

    _AUTHORITY_REPLACEMENTS = (
        (re.compile(r"\bi recommend(?:\s+that)?\b", re.IGNORECASE), "A reasonable option is to"),
        (re.compile(r"\byou should\b", re.IGNORECASE), "A useful next step is to"),
        (re.compile(r"\bi think\b", re.IGNORECASE), "The analysis suggests"),
        (re.compile(r"\bi believe\b", re.IGNORECASE), "The analysis suggests"),
        (re.compile(r"\btrust me\b", re.IGNORECASE), "Based on available information"),
    )

    _EMOTIONAL_REPLACEMENTS = (
        (re.compile(r"\bi[' ]?m here for you\b", re.IGNORECASE), "I can help with the task details"),
        (re.compile(r"\bdon[' ]?t worry\b", re.IGNORECASE), "Let's focus on the next step"),
        (re.compile(r"\bthat must be hard\b", re.IGNORECASE), "This can be frustrating"),
        (re.compile(r"\bi understand how you feel\b", re.IGNORECASE), "I can help clarify the situation"),
    )

    def present(self, text: str) -> str:
        clean = (text or "").replace("\r\n", "\n").strip()
        if not clean:
            return ""

        for pattern in self._SYSTEM_TOKEN_PATTERNS:
            clean = pattern.sub("", clean)

        for pattern, replacement in self._AUTHORITY_REPLACEMENTS:
            clean = pattern.sub(replacement, clean)

        for pattern, replacement in self._EMOTIONAL_REPLACEMENTS:
            clean = pattern.sub(replacement, clean)

        clean = re.sub(r"\bto to\b", "to", clean, flags=re.IGNORECASE)
        clean = re.sub(r"\s+\n", "\n", clean)
        clean = re.sub(r"\n\s+", "\n", clean)
        clean = re.sub(r"[ \t]{2,}", " ", clean)
        clean = re.sub(r"\n{3,}", "\n\n", clean)
        clean = re.sub(r"!+", ".", clean)
        clean = re.sub(r"\s{2,}", " ", clean)
        return clean.strip()
