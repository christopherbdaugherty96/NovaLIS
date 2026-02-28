from __future__ import annotations

from enum import Enum


class ResponseStyle(str, Enum):
    DIRECT = "direct"
    BRAINSTORM = "brainstorm"
    DEEP = "deep"
    CASUAL = "casual"


class ResponseStyleRouter:
    CASUAL_OPENERS = {
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "how are you",
    }

    @classmethod
    def route(cls, user_message: str) -> ResponseStyle:
        text = (user_message or "").strip().lower()
        if not text:
            return ResponseStyle.DIRECT

        if text in cls.CASUAL_OPENERS and len(text.split()) <= 4:
            return ResponseStyle.CASUAL

        if "brainstorm" in text or "ideas" in text:
            return ResponseStyle.BRAINSTORM

        if "deep analysis" in text or len(text.split()) >= 40:
            return ResponseStyle.DEEP

        return ResponseStyle.DIRECT
