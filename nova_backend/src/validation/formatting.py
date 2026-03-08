from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FormattingCheck:
    ok: bool
    reason: str = ""


class FormattingValidator:
    FORBIDDEN_SYMBOLS = ("⭐", "⚠️", "❗")

    def validate(self, text: str) -> FormattingCheck:
        body = text or ""
        for symbol in self.FORBIDDEN_SYMBOLS:
            if symbol in body:
                return FormattingCheck(False, f"implicit prioritization symbol: {symbol}")
        return FormattingCheck(True)
