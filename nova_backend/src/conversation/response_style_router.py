from __future__ import annotations

import re
from enum import Enum


class ResponseStyle(str, Enum):
    DIRECT = "direct"
    BRAINSTORM = "brainstorm"
    DEEP = "deep"
    CASUAL = "casual"


class InputNormalizer:

    """Deterministic input cleanup for spelling, punctuation, and STT fragments."""

    """Deterministic input cleanup for invocation-safe normalization."""

    TYPO_REPLACEMENTS = (
        (r"\bwether\b", "weather"),
        (r"\bwaether\b", "weather"),
        (r"\bhedlines\b", "headlines"),
        (r"\bheadines\b", "headlines"),
        (r"\bserch\b", "search"),
        (r"\bseach\b", "search"),
        (r"\breseach\b", "research"),
        (r"\bsumarize\b", "summarize"),
        (r"\bsummarise\b", "summarize"),
        (r"\bcomparision\b", "comparison"),
        (r"\bplz\b", "please"),
        (r"\bpls\b", "please"),
        (r"\bu\b", "you"),
    )

    PHRASE_NORMALIZATION = (
        (r"\bmake it louder\b", "volume up"),
        (r"\bturn (?:my )?sound up\b", "volume up"),
        (r"\bturn (?:the )?volume up\b", "volume up"),
        (r"\bincrease volume\b", "volume up"),
        (r"\bturn (?:my )?sound down\b", "volume down"),
        (r"\blower the volume\b", "volume down"),
        (r"\bturn (?:the )?volume down\b", "volume down"),
        (r"\bopen my downloads\b", "open downloads"),
        (r"\bopen my documents\b", "open documents"),
        (r"\bopen downloads folder\b", "open downloads"),
        (r"\bopen documents folder\b", "open documents"),
        (r"\bwhat(?:'s| is) going on in tech today\b", "daily brief tech"),
        (r"^\s*what(?:'s| is)\s+going on with\s+(.+?)\s+today\s*$", r"research \1 latest updates"),
        (r"^\s*what(?:'s| is)\s+going on with\s+(.+?)\s*$", r"research \1"),
        (r"^\s*tell me about\s+(.+?)\s*$", r"research \1"),
        (r"^\s*i want to know about\s+(.+?)\s*$", r"research \1"),
        (r"^\s*i need info(?:rmation)? on\s+(.+?)\s*$", r"research \1"),
        (r"^\s*why is\s+(.+?)\s+(?:down|dropping|falling)\s*$", r"research why \1 is down"),
        (r"\babc\s+new\b", "abc news"),
    )
    POLITE_PREFIX_RE = re.compile(
        r"^\s*(?:hey\s+nova[, ]*|ok(?:ay)?\s+nova[, ]*|nova[, ]*|please[, ]*|"
        r"can you\s+|could you\s+|would you\s+|can u\s+|could u\s+|would u\s+|"
        r"i need to\s+)",
        re.IGNORECASE,
    )
    POLITE_SUFFIX_RE = re.compile(r"(?:,\s*please|\s+please)\s*$", re.IGNORECASE)

    @staticmethod
    def _collapse_spaced_acronyms(text: str) -> str:
        # Example: "A B C news" -> "ABC news"
        def _join(match: re.Match) -> str:
            token = match.group(0)
            return re.sub(r"\s+", "", token)

        return re.sub(r"\b(?:[A-Za-z]\s+){1,}[A-Za-z]\b", _join, text)

    @classmethod
    def normalize(cls, text: str) -> str:
        clean = (text or "").strip()
        if not clean:
            return ""

        clean = re.sub(r"\s+", " ", clean)
        for _ in range(3):
            updated = re.sub(cls.POLITE_PREFIX_RE, "", clean).strip()
            if updated == clean:
                break
            clean = updated
        clean = re.sub(cls.POLITE_SUFFIX_RE, "", clean).strip()
        clean = cls._collapse_spaced_acronyms(clean)

        clean = clean.replace(" ,", ",").replace(" .", ".")

        # deterministic phrase-level normalization for common STT artifact
        clean = re.sub(
            r"\bsearch\s+food\s+near\s+me\s+mi\s+ann\s+arbor\b",
            "search for food near me in Ann Arbor, MI",
            clean,
            flags=re.IGNORECASE,
        )

        for pattern, replacement in cls.TYPO_REPLACEMENTS:
            clean = re.sub(pattern, replacement, clean, flags=re.IGNORECASE)

        for pattern, replacement in cls.PHRASE_NORMALIZATION:
            clean = re.sub(pattern, replacement, clean, flags=re.IGNORECASE)

        if clean and clean[0].islower():
            clean = clean[0].upper() + clean[1:]

        if re.search(r"[A-Za-z0-9]$", clean):
            clean += "."

        return clean


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
        text = (user_message or "").strip().lower().rstrip(".!?")
        if not text:
            return ResponseStyle.DIRECT

        if text in cls.CASUAL_OPENERS and len(text.split()) <= 4:
            return ResponseStyle.CASUAL

        if "brainstorm" in text or "ideas" in text:
            return ResponseStyle.BRAINSTORM

        if "deep analysis" in text or len(text.split()) >= 40:
            return ResponseStyle.DEEP

        return ResponseStyle.DIRECT


class ResponseTemplates:
    """Deterministic phrasing templates for calm, premium output style."""

    @staticmethod
    def bounded_research_intro(query: str = "") -> str:
        context = (query or "").strip()
        if context:
            return f"I checked the latest sources for \"{context}\". Here are the top findings."
        return "I checked the latest sources. Here are the top findings."

    @staticmethod
    def top_findings_block(lines: list[str]) -> str:
        if not lines:
            return "Top Findings\n- I couldn't find reliable results for that."
        findings = "\n".join(f"- {line}" for line in lines)
        return f"Top Findings\n{findings}"

    @staticmethod
    def sources_block(domains: list[str]) -> str:
        if not domains:
            return "Sources\n1. multiple online sources"

        numbered = "\n".join(f"{idx}. {domain}" for idx, domain in enumerate(domains, start=1))
        return f"Sources\n{numbered}"

    @staticmethod
    def concise_acknowledgement(text: str) -> str:
        clean = (text or "").strip()
        return clean or "You're welcome."
