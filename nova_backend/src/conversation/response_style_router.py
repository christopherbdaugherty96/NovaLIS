from __future__ import annotations

import re
from enum import Enum


class ResponseStyle(str, Enum):
    DIRECT = "direct"
    BRAINSTORM = "brainstorm"
    DEEP = "deep"
    CASUAL = "casual"


class InputNormalizer:

    """Deterministic input cleanup for invocation-safe normalization."""

    TYPO_REPLACEMENTS = (
        # Weather
        (r"\bwether\b", "weather"),
        (r"\bwaether\b", "weather"),
        (r"\bweahter\b", "weather"),
        # Contractions / shorthand
        (r"\bwhats\b", "what's"),
        (r"\bwats\b", "what's"),
        (r"\bim\b", "i'm"),
        (r"\bdont\b", "don't"),
        (r"\bdoesnt\b", "doesn't"),
        (r"\bcant\b", "can't"),
        (r"\bwont\b", "won't"),
        (r"\bisnt\b", "isn't"),
        (r"\barent\b", "aren't"),
        (r"\bwouldnt\b", "wouldn't"),
        (r"\bcouldnt\b", "couldn't"),
        (r"\bshouldnt\b", "shouldn't"),
        (r"\bhavent\b", "haven't"),
        (r"\bhasnt\b", "hasn't"),
        (r"\bdidn't\b", "didn't"),
        # Text-speak shorthand
        (r"\bu\b", "you"),
        (r"\bur\b", "your"),
        (r"\br\b", "are"),
        (r"\bthx\b", "thanks"),
        (r"\bthnx\b", "thanks"),
        (r"\bty\b", "thank you"),
        (r"\bplz\b", "please"),
        (r"\bpls\b", "please"),
        (r"\bok\b", "okay"),
        (r"\bngl\b", "honestly"),
        (r"\bbtw\b", "by the way"),
        (r"\bidk\b", "i don't know"),
        (r"\bidc\b", "i don't care"),
        (r"\blmk\b", "let me know"),
        (r"\bgimme\b", "give me"),
        (r"\bwanna\b", "want to"),
        (r"\bgonna\b", "going to"),
        (r"\bgotta\b", "got to"),
        (r"\bkinda\b", "kind of"),
        (r"\bsorta\b", "sort of"),
        (r"\bngl\b", "not gonna lie"),
        # Common misspellings
        (r"\bhedlines\b", "headlines"),
        (r"\bheadines\b", "headlines"),
        (r"\bserch\b", "search"),
        (r"\bseach\b", "search"),
        (r"\breseach\b", "research"),
        (r"\bsumarize\b", "summarize"),
        (r"\bsummarise\b", "summarize"),
        (r"\bcomparision\b", "comparison"),
        (r"\bartical\b", "article"),
        (r"\barticals\b", "articles"),
        (r"\bconfrim\b", "confirm"),
        (r"\bschedual\b", "schedule"),
        (r"\bcalander\b", "calendar"),
        (r"\bcalender\b", "calendar"),
        (r"\bemail\b", "email"),
        (r"\bemial\b", "email"),
        (r"\bemali\b", "email"),
        (r"\bbrightnes\b", "brightness"),
        (r"\bvolumn\b", "volume"),
        (r"\bvolume\b", "volume"),
        (r"\bremeber\b", "remember"),
        (r"\bremebmer\b", "remember"),
        (r"\bsettigns\b", "settings"),
    )

    PHRASE_NORMALIZATION = (
        # --- Capability / identity queries ---
        (r"^\s*(?:tell me|show me)\s+what you can do\s*$", "what can you do"),
        (r"^\s*what capabilities do you have\s*$", "what can you do"),
        (r"^\s*what capabilities can you do\s*$", "what can you do"),
        (r"^\s*one capabilities can you do\s*$", "what can you do"),
        (r"^\s*what can you di(?:[.?!])?\s*$", "what can you do"),
        (r"^\s*what can you doo(?:[.?!])?\s*$", "what can you do"),
        (r"^\s*what are you good at\s*[.?!]*$", "what can you do"),
        (r"^\s*what do you know(?: how to do)?\s*[.?!]*$", "what can you do"),
        (r"^\s*what do you do\s*[.?!]*$", "what can you do"),
        (r"^\s*(?:can|could) you help(?: me)?\s*[.?!]*$", "what can you do"),
        (r"^\s*(?:i need|i want)\s+(?:some\s+)?help\s*[.?!]*$", "what can you do"),
        (r"^\s*help me\s*[.?!]*$", "what can you do"),
        # Note: "who are you", "what is nova" are handled by the identity intent — not normalized here
        (r"^\s*(?:show|list|tell me)\s+(?:your\s+)?(?:skills|features|options|commands|menu)\s*[.?!]*$", "what can you do"),
        (r"^\s*what(?:'s| is)\s+(?:available|possible)\s*[.?!]*$", "what can you do"),
        (r"^\s*(?:how do i|how can i)\s+use\s+(?:you|nova|this)\s*[.?!]*$", "what can you do"),
        (r"^\s*(?:get started|where do i start|how do i start)\s*[.?!]*$", "what can you do"),
        (r"^\s*what(?:'s| is)\s+(?:the\s+)?time\s*$", "what time is it"),
        (r"^\s*time now\s*$", "what time is it"),
        (r"\bmake it louder\b", "volume up"),
        (r"\bturn (?:my )?sound up\b", "volume up"),
        (r"\bturn (?:the )?volume up\b", "volume up"),
        (r"\bincrease volume\b", "volume up"),
        (r"\bunmute (?:the )?(?:audio|sound|volume)\b", "unmute"),
        (r"\bmute (?:the )?(?:audio|sound|volume)\b", "mute"),
        (r"\bturn (?:my )?sound down\b", "volume down"),
        (r"\blower the volume\b", "volume down"),
        (r"\bturn (?:the )?volume down\b", "volume down"),
        (r"\bmake (?:the )?screen brighter\b", "brightness up"),
        (r"\bturn (?:the )?brightness up\b", "brightness up"),
        (r"\bincrease brightness\b", "brightness up"),
        (r"\bdim (?:the )?screen\b", "brightness down"),
        (r"\bturn (?:the )?brightness down\b", "brightness down"),
        (r"\blower brightness\b", "brightness down"),
        (r"\bopen my downloads\b", "open downloads"),
        (r"\bopen my documents\b", "open documents"),
        (r"\bopen downloads folder\b", "open downloads"),
        (r"\bopen documents folder\b", "open documents"),
        (r"^\s*(?:what(?:'s| is)\s+)?the weather(?:\s+today)?\s*$", "weather"),
        (r"^\s*what(?:'s| is)\s+the weather tomorrow\s*$", "weather forecast"),
        (r"^\s*(?:what(?:'s| is)\s+)?today(?:'s)? news\s*$", "today's news"),
        (r"^\s*(?:give me|show me)\s+(?:today(?:'s)?\s+)?news\s*$", "today's news"),
        (r"^\s*read\s+(?:me\s+)?(?:today(?:'s)?\s+)?news\s*$", "today's news"),
        (r"^\s*summarize\s+(?:all\s+)?(?:today(?:'s)?\s+)?news\s*$", "summarize all headlines"),
        (r"^\s*(?:say|tell|show)(?: me)?(?: that| it)? again\s*$", "repeat"),
        (r"\bwhat(?:'s| is) going on in tech today\b", "daily brief tech"),
        (r"^\s*what(?:'s| is)\s+going on with\s+(.+?)\s+today\s*$", r"research \1 latest updates"),
        (r"^\s*what(?:'s| is)\s+going on with\s+(.+?)\s*$", r"research \1"),
        (r"^\s*tell me about\s+(.+?)\s+instead\s*$", r"\1"),
        (r"^\s*tell me about\s+(.+?)\s*$", r"research \1"),
        (r"^\s*i want to know about\s+(.+?)\s*$", r"research \1"),
        (r"^\s*i need info(?:rmation)? on\s+(.+?)\s*$", r"research \1"),
        (r"^\s*why is\s+(.+?)\s+(?:down|dropping|falling)\s*$", r"research why \1 is down"),
        (r"\bwithin in local disk\b", "within local disk"),
        (r"\babc\s+new\b", "abc news"),
        (r"\babc\s+news\b", "abc news"),
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

        deep_markers = (
            "deep analysis",
            "deep thought",
            "deep think",
            "go deeper",
            "think deeper",
            "challenge this",
            "pressure test",
            "orthogonal analysis",
            "phase42:",
        )
        if any(marker in text for marker in deep_markers) or len(text.split()) >= 40:
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
