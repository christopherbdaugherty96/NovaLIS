from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthorityLanguageCheck:
    ok: bool
    reason: str = ""


class AuthorityLanguageDetector:
    FORBIDDEN = (
        "you should",
        "i recommend",
        "you must",
        "trust me",
        "i think",
        "i believe",
    )

    def validate(self, text: str) -> AuthorityLanguageCheck:
        lowered = (text or "").lower()
        for phrase in self.FORBIDDEN:
            if phrase in lowered:
                return AuthorityLanguageCheck(False, f"forbidden authority phrase: {phrase}")
        return AuthorityLanguageCheck(True)
