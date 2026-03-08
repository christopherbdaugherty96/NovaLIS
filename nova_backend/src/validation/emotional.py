from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmotionalBoundaryCheck:
    ok: bool
    reason: str = ""


class EmotionalBoundaryEnforcer:
    FORBIDDEN = (
        "i'm here for you",
        "i care about",
        "don't worry",
        "that must be hard",
        "we'll get through this",
        "i understand how you feel",
    )

    def validate(self, text: str) -> EmotionalBoundaryCheck:
        lowered = (text or "").lower()
        for phrase in self.FORBIDDEN:
            if phrase in lowered:
                return EmotionalBoundaryCheck(False, f"emotional dependency phrase: {phrase}")
        return EmotionalBoundaryCheck(True)
