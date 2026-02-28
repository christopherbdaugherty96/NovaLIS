from __future__ import annotations

import re


class DeepSeekSafetyWrapper:
    _PHRASE_PATTERNS = (
        re.compile(r"\byou should\b", re.IGNORECASE),
        re.compile(r"\bi recommend\b", re.IGNORECASE),
        re.compile(r"\bexecute\b", re.IGNORECASE),
        re.compile(r"\brun\b", re.IGNORECASE),
        re.compile(r"\bopen\b", re.IGNORECASE),
    )

    _FUNCTION_CALL_PATTERNS = (
        re.compile(r"<function_call[^>]*>", re.IGNORECASE),
        re.compile(r"\btool_call\b", re.IGNORECASE),
        re.compile(r"\bfunction\s*:\s*", re.IGNORECASE),
    )

    _CAPABILITY_PATTERN = re.compile(r"\bcapability\s*[_-]?id\s*[:=]?\s*\d+\b", re.IGNORECASE)

    def sanitize(self, text: str) -> str:
        clean = (text or "").strip()
        if not clean:
            return clean

        for pattern in self._PHRASE_PATTERNS + self._FUNCTION_CALL_PATTERNS:
            clean = pattern.sub("", clean)

        clean = self._CAPABILITY_PATTERN.sub("", clean)
        clean = re.sub(r"\s{2,}", " ", clean)
        clean = re.sub(r"\n{3,}", "\n\n", clean)
        return clean.strip()
