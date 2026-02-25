import re


class SafetyFilter:
    FORBIDDEN_PATTERNS = [
        r"\bsearch for\b",
        r"\blook up\b",
        r"\bopen\b",
        r"\bI can (search|look up|open|find)\b",
        r"\bwould you like me to\b",
        r"\byou could (search|look up|open)\b",
        r"\bI'll remember\b",
        r"\bnext time\b",
        r"\bI'll keep an eye\b",
        r"\bI'll remind you\b",
    ]

    DISCLAIMER = " (Note: I cannot perform actions myself; you would need to ask Nova explicitly.)"

    @classmethod
    def filter(cls, text: str) -> str:
        clean = text or ""
        if any(re.search(pattern, clean, re.IGNORECASE) for pattern in cls.FORBIDDEN_PATTERNS):
            if cls.DISCLAIMER not in clean:
                clean += cls.DISCLAIMER
        return clean
