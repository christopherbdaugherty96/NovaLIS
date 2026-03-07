import re
from typing import Any

from src.conversation.clarify_prompts import CLARIFY_PROMPTS


class ResponseFormatter:
    CLARIFICATION_TEMPLATES = {
        "casual": CLARIFY_PROMPTS["brief_or_deep"],
        "analytical": CLARIFY_PROMPTS["high_level_or_detail"],
        "implementation": CLARIFY_PROMPTS["concept_or_steps"],
        "brainstorming": CLARIFY_PROMPTS["broad_or_narrow"],
    }

    ACK_REPLACEMENTS = {
        "operation completed": "That's done.",
        "task executed": "Completed.",
        "execution successful": "Completed.",
        "volume increased": "Volume up.",
        "volume decreased": "Volume down.",
        "media paused successfully": "Paused.",
        "the brightness has been adjusted": "Brightness adjusted.",
        "current weather retrieved": "Here's the current weather.",
        "here are the results": "Here's what I found.",
    }

    URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
    PATH_PATTERN = re.compile(r"(?:\b[A-Za-z]:\\[^\s]+|/(?:[^\s/]+/)+[^\s]*)")

    @staticmethod
    def format(text: str, mode: str = "casual") -> str:
        clean = (text or "").strip().replace("\r\n", "\n")
        clean = re.sub(r"[ \t]+", " ", clean)
        clean = re.sub(r"\n{3,}", "\n\n", clean)
        clean = re.sub(r"!+", ".", clean)
        clean = re.sub(r"([.!?])([A-Z])", r"\1 \2", clean)

        for filler in [r"\bwell\b", r"\bso\b", r"\byou see\b", r"\blet me think\b"]:
            clean = re.sub(filler, "", clean, flags=re.IGNORECASE)

        clean = ResponseFormatter._apply_ack_replacements(clean)
        clean = ResponseFormatter._tone_shape(clean, mode)
        clean = re.sub(r"[ \t]{2,}", " ", clean).strip()
        return clean.strip()

    @classmethod
    def format_payload(
        cls,
        message: str,
        *,
        mode: str = "casual",
        speakable_text: str = "",
        structured_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        user_message = cls.format(message, mode=mode)
        data = dict(structured_data or {})
        data.setdefault("structured_data", structured_data or {})

        if cls._needs_executive_summary(user_message):
            executive = cls._build_executive_summary(user_message)
            if executive:
                user_message = f"{executive}\n\n{user_message}" if executive.lower() not in user_message.lower() else user_message

        raw_speakable = (speakable_text or user_message).strip()
        data["speakable_text"] = cls.to_speakable_text(raw_speakable)
        return {"user_message": user_message, "speakable_text": data["speakable_text"], "structured_data": data.get("structured_data", {}), "data": data}

    @staticmethod
    def to_speakable_text(text: str) -> str:
        clean = ResponseFormatter.format(text)
        clean = ResponseFormatter.URL_PATTERN.sub("I have opened the link", clean)
        clean = ResponseFormatter.PATH_PATTERN.sub("the selected file", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    @staticmethod
    def friendly_fallback() -> str:
        return (
            "I'm not sure what you'd like me to do with that. "
            "You can ask me to open files, search the web, or show today's brief."
        )

    @staticmethod
    def with_conversational_initiative(
        base_text: str,
        mode: str,
        allow_clarification: bool = False,
        allow_branch_suggestion: bool = False,
        allow_depth_prompt: bool = False,
    ) -> str:
        text = ResponseFormatter.format(base_text, mode=mode)
        add_ons = []

        if allow_clarification:
            add_ons.append(ResponseFormatter.CLARIFICATION_TEMPLATES.get(mode, ResponseFormatter.CLARIFICATION_TEMPLATES["casual"]))

        _ = allow_depth_prompt
        _ = allow_branch_suggestion

        if add_ons:
            text = f"{text}\n\n" + "\n".join(add_ons[:1])

        return text.strip()

    @staticmethod
    def _tone_shape(text: str, mode: str) -> str:
        if mode == "analytical":
            return text.replace("I think", "The analysis indicates")
        if mode == "implementation" and "\n" not in text and ". " in text:
            return text.replace(". ", ".\n")
        return text

    @classmethod
    def _apply_ack_replacements(cls, text: str) -> str:
        out = text
        for old, new in cls.ACK_REPLACEMENTS.items():
            out = re.sub(rf"\b{re.escape(old)}\b", new, out, flags=re.IGNORECASE)
        return out

    @staticmethod
    def _needs_executive_summary(text: str) -> bool:
        if "\n" in text:
            return True
        sentence_count = len([s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()])
        return sentence_count >= 4

    @staticmethod
    def _build_executive_summary(text: str) -> str:
        lines = [line.strip(" -•") for line in text.splitlines() if line.strip()]
        if not lines:
            return ""
        first = lines[0]
        first = re.sub(r"\s+", " ", first).strip()
        if len(first) > 120:
            first = first[:117].rstrip() + "..."
        return f"Summary: {first}"
