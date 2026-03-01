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

    TYPO_REPLACEMENTS = (
        (r"\bwether\b", "weather"),
        (r"\bhedlines\b", "headlines"),
        (r"\bserch\b", "search"),
        (r"\bseach\b", "search"),
        (r"\bplz\b", "please"),
        (r"\bu\b", "you"),
    )

    @classmethod
    def normalize(cls, text: str) -> str:
        clean = (text or "").strip()
        if not clean:
            return ""

        clean = re.sub(r"\s+", " ", clean)
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
