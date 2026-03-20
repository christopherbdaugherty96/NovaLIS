from __future__ import annotations

import re


class NovaStyleContract:
    """Shared fixed style rules for Nova-facing presentation surfaces."""

    _LEADING_OPENERS = (
        (re.compile(r"^\s*(?:absolutely|certainly|sure|of course)[,!.:\s]+", re.IGNORECASE), ""),
        (re.compile(r"^\s*great question[,!.:\s]+", re.IGNORECASE), ""),
        (re.compile(r"^\s*happy to help[,!.:\s]+", re.IGNORECASE), ""),
    )

    _INLINE_REPLACEMENTS = (
        (re.compile(r"\bi(?: would|'d) be happy to\b", re.IGNORECASE), "I can"),
        (re.compile(r"\bi(?: am|'m) happy to\b", re.IGNORECASE), "I can"),
        (re.compile(r"\bi can absolutely\b", re.IGNORECASE), "I can"),
        (re.compile(r"\bgladly\b", re.IGNORECASE), ""),
        (re.compile(r"\bas an ai\b", re.IGNORECASE), ""),
    )

    @classmethod
    def normalize(cls, text: str) -> str:
        clean = str(text or "").strip()
        if not clean:
            return ""

        while True:
            updated = clean
            for pattern, replacement in cls._LEADING_OPENERS:
                updated = pattern.sub(replacement, updated).lstrip()
            if updated == clean:
                break
            clean = updated

        for pattern, replacement in cls._INLINE_REPLACEMENTS:
            clean = pattern.sub(replacement, clean)

        clean = re.sub(r"^[,!.:\-\s]+", "", clean)
        clean = re.sub(r"\s{2,}", " ", clean)
        clean = re.sub(r"\s+([,.!?])", r"\1", clean)
        clean = re.sub(r"\.{2,}", ".", clean)
        clean = re.sub(r"\n{3,}", "\n\n", clean)
        return clean.strip()
