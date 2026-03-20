from __future__ import annotations

import re


class NovaStyleContract:
    """Shared fixed style rules for Nova-facing presentation surfaces."""

    _LEADING_OPENERS = (
        (re.compile(r"^\s*(?:absolutely|certainly|sure(?!\s+thing\b)|of course)[,!.:\s]+", re.IGNORECASE), ""),
    )

    _INLINE_REPLACEMENTS = (
        (re.compile(r"\bi can absolutely\b", re.IGNORECASE), "I can"),
        (re.compile(r"\bgladly\b", re.IGNORECASE), ""),
        (re.compile(r"\bas an ai\b", re.IGNORECASE), ""),
    )
    _SPOKEN_ACKNOWLEDGEMENTS = {
        "neutral": "Okay.",
        "understood": "Gotcha.",
        "confirm": "Sure thing.",
    }

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

    @classmethod
    def spoken_acknowledgement(cls, kind: str = "neutral") -> str:
        return cls._SPOKEN_ACKNOWLEDGEMENTS.get(str(kind or "").strip().lower(), cls._SPOKEN_ACKNOWLEDGEMENTS["neutral"])

    @classmethod
    def prefix_with_acknowledgement(cls, text: str, *, kind: str = "neutral") -> str:
        body = str(text or "").strip()
        acknowledgement = cls.spoken_acknowledgement(kind)
        if not body:
            return acknowledgement
        lowered_body = body.lower().rstrip()
        lowered_ack = acknowledgement.lower().rstrip(".!?")
        if lowered_body.startswith(lowered_ack):
            return body
        return f"{acknowledgement} {body}".strip()

    @staticmethod
    def spoken_repeat_prompt() -> str:
        return "Say that again?"
