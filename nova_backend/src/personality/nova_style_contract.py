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
    _CHAT_MODE_GUIDANCE = {
        "casual": (
            "Communication style: Direct-first.\n"
            "- Lead with the point.\n"
            "- Use one short paragraph or two short sentences.\n"
            "- Keep the tone calm and lightly warm.\n"
            "- Avoid filler or ornamental framing.\n"
        ),
        "brainstorming": (
            "Communication style: Exploratory and grounded.\n"
            "- Present a few distinct directions with short labels.\n"
            "- Keep the options easy to compare.\n"
            "- Avoid hype or fuzzy brainstorming.\n"
        ),
        "implementation": (
            "Communication style: Practical and procedural.\n"
            "- Give clear steps using direct address ('you').\n"
            "- Keep each step concrete and self-contained.\n"
            "- Avoid side commentary that does not help the task.\n"
        ),
        "analytical": (
            "Communication style: Analytical and grounded.\n"
            "- Lead with the main point or conclusion.\n"
            "- Use clear cause-and-effect language.\n"
            "- Avoid ornamental framing or academic showiness.\n"
        ),
    }
    _INITIATIVE_TEMPLATES = {
        "casual": {
            "clarify": "If you want, I can keep it short or go a bit deeper.",
            "branch": "If you want, I can keep going on this or take it a different direction.",
            "depth": "If you want, I can go a bit deeper on one part.",
            "combined": "If you want, I can go a bit deeper on one part or take this in a different direction.",
        },
        "analytical": {
            "clarify": "If useful, I can keep this high-level or break down one part.",
            "branch": "If useful, I can compare the trade-offs or pressure-test one path.",
            "depth": "If useful, I can go deeper on one part or tighten this into the short version.",
            "combined": "If useful, I can compare the trade-offs or go deeper on one part.",
        },
        "implementation": {
            "clarify": "If useful, I can keep this high-level or turn it into steps.",
            "branch": "If useful, I can turn this into clear steps or adapt it to your setup.",
            "depth": "If useful, I can expand one step or compress this into a quick checklist.",
            "combined": "If useful, I can expand one step or adapt this to a different setup.",
        },
        "brainstorming": {
            "clarify": "If you want, I can keep this broad or narrow it to one path.",
            "branch": "If you want, I can map two or three directions and compare them.",
            "depth": "If you want, I can go deeper on one path or keep it broad.",
            "combined": "If you want, I can compare two or three directions or go deeper on one path.",
        },
    }
    _MODE_WORDING_REPLACEMENTS = {
        "casual": (
            (re.compile(r"^\s*(?:the short answer is|basically)\b[:,]?\s*", re.IGNORECASE), "The main point is "),
        ),
        "analytical": (
            (re.compile(r"^\s*i think\s+", re.IGNORECASE), "The clearest read is that "),
            (re.compile(r"^\s*in my view\s+", re.IGNORECASE), "The clearest read is that "),
        ),
        "brainstorming": (
            (re.compile(r"^\s*here are (?:some|a few) ideas\b", re.IGNORECASE), "Here are a few grounded directions"),
        ),
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

    @classmethod
    def chat_mode_guidance(cls, mode: str) -> str:
        return cls._CHAT_MODE_GUIDANCE.get(str(mode or "").strip().lower(), cls._CHAT_MODE_GUIDANCE["casual"])

    @classmethod
    def initiative_tail(cls, mode: str, kind: str) -> str:
        normalized_mode = str(mode or "").strip().lower()
        normalized_kind = str(kind or "").strip().lower()
        mode_templates = cls._INITIATIVE_TEMPLATES.get(normalized_mode, cls._INITIATIVE_TEMPLATES["casual"])
        return mode_templates.get(normalized_kind, "")

    @classmethod
    def apply_mode_wording(cls, text: str, mode: str) -> str:
        clean = str(text or "").strip()
        replacements = cls._MODE_WORDING_REPLACEMENTS.get(str(mode or "").strip().lower(), ())
        for pattern, replacement in replacements:
            clean = pattern.sub(replacement, clean)
        return clean.strip()
