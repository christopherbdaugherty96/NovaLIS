import re
from typing import Any

from src.conversation.clarify_prompts import CLARIFY_PROMPTS
from src.personality.nova_style_contract import NovaStyleContract


class ResponseFormatter:
    ACK_REPLACEMENTS = {
        "operation completed": "That's done.",
        "task executed": "Completed.",
        "execution successful": "Completed.",
        "volume increased": "Volume up.",
        "volume decreased": "Volume down.",
        "audio muted": "Muted.",
        "audio unmuted": "Unmuted.",
        "media paused successfully": "Paused.",
        "the brightness has been adjusted": "Brightness adjusted.",
        "current weather retrieved": "Here's the current weather.",
        "here are the results": "Here's what I found.",
    }

    URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
    PATH_PATTERN = re.compile(r"(?:\b[A-Za-z]:\\[^\s]+|/(?:[^\s/]+/)+[^\s]*)")
    _EXPLICIT_SUMMARY_PREFIXES = (
        "bottom line:",
        "summary:",
        "main point:",
        "core answer:",
        "key takeaway:",
        "recommendation:",
    )
    _HEADING_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9\s:.\-\"'/()]{5,}$")

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
        clean = NovaStyleContract.normalize(clean)
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
                user_message = (
                    f"{executive}\n\n{user_message}"
                    if executive.lower() not in user_message.lower()
                    else user_message
                )

        raw_speakable = (speakable_text or user_message).strip()
        data["speakable_text"] = cls.to_speakable_text(raw_speakable)
        return {
            "user_message": user_message,
            "speakable_text": data["speakable_text"],
            "structured_data": data.get("structured_data", {}),
            "data": data,
        }

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
            "I didn't quite catch that. "
            "Try one of these: what can you do, what time is it, today's news, or open documents."
        )

    @staticmethod
    def with_conversational_initiative(
        base_text: str,
        mode: str,
        allow_clarification: bool = False,
        allow_branch_suggestion: bool = False,
        allow_depth_prompt: bool = False,
        presentation_preference: str = "",
        last_answer_kind: str = "",
    ) -> str:
        text = ResponseFormatter.format(base_text, mode=mode)
        preference = str(presentation_preference or "").strip().lower()
        prior_kind = str(last_answer_kind or "").strip().lower()
        if preference in {"shorter", "simpler", "reworded", "direct"}:
            return text.strip()
        if prior_kind in {"clarify", "simpler", "reworded", "shorter"}:
            return text.strip()
        add_ons = []

        if allow_clarification:
            add_ons.append(
                NovaStyleContract.initiative_tail(mode, "clarify")
                or CLARIFY_PROMPTS["brief_or_deep"]
            )
        elif allow_branch_suggestion and allow_depth_prompt:
            add_ons.append(
                NovaStyleContract.initiative_tail(mode, "combined")
                or NovaStyleContract.initiative_tail("casual", "combined")
            )
        elif allow_branch_suggestion:
            add_ons.append(
                NovaStyleContract.initiative_tail(mode, "branch")
                or NovaStyleContract.initiative_tail("casual", "branch")
            )
        elif allow_depth_prompt:
            add_ons.append(
                NovaStyleContract.initiative_tail(mode, "depth")
                or NovaStyleContract.initiative_tail("casual", "depth")
            )

        if add_ons:
            text = f"{text}\n\n" + "\n".join(add_ons[:1])

        return text.strip()

    @staticmethod
    def _tone_shape(text: str, mode: str) -> str:
        text = NovaStyleContract.apply_mode_wording(text, mode)
        if mode == "analytical":
            return text
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
        if ResponseFormatter._looks_like_plain_numbered_option_list(text):
            return False
        if "\n" in text:
            return True
        sentence_count = len([s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()])
        return sentence_count >= 4

    @classmethod
    def _build_executive_summary(cls, text: str) -> str:
        lines = [line.strip(" -•") for line in text.splitlines() if line.strip()]
        if not lines:
            return ""
        explicit = cls._explicit_summary_line(lines)
        if explicit:
            return explicit
        first = cls._first_informative_line(lines)
        if not first:
            return ""
        if len(first) > 120:
            first = first[:117].rstrip() + "..."
        return f"Summary: {first}"

    @classmethod
    def _explicit_summary_line(cls, lines: list[str]) -> str:
        for line in lines:
            normalized = re.sub(r"\s+", " ", line).strip()
            lowered = normalized.lower()
            if any(lowered.startswith(prefix) for prefix in cls._EXPLICIT_SUMMARY_PREFIXES):
                return normalized

        for idx, raw_line in enumerate(lines):
            normalized = re.sub(r"\s+", " ", raw_line).strip()
            lowered = normalized.lower()
            if lowered in {"top headlines", "key developments", "signals to watch"}:
                follow_up = cls._first_bullet_like_line(lines[idx + 1 :])
                if follow_up:
                    return f"Summary: {follow_up}"
        return ""

    @classmethod
    def _first_informative_line(cls, lines: list[str]) -> str:
        for line in lines:
            normalized = re.sub(r"\s+", " ", line).strip()
            if not normalized:
                continue
            if normalized.lower() in {"top headlines", "key developments", "signals to watch"}:
                continue
            if cls._looks_like_heading(normalized):
                continue
            return normalized
        return re.sub(r"\s+", " ", lines[0]).strip() if lines else ""

    @staticmethod
    def _first_bullet_like_line(lines: list[str]) -> str:
        for line in lines:
            normalized = re.sub(r"\s+", " ", line).strip(" -•")
            if not normalized:
                continue
            normalized = re.sub(r"^\d+[.)]?\s+", "", normalized).strip()
            if normalized:
                return normalized
        return ""

    @classmethod
    def _looks_like_heading(cls, line: str) -> bool:
        normalized = re.sub(r"\s+", " ", line).strip()
        if not normalized:
            return False
        if cls._HEADING_PATTERN.match(normalized) and normalized.upper() == normalized:
            return True
        return normalized.endswith(("BRIEF", "SUMMARY")) and normalized == normalized.upper()

    @staticmethod
    def _looks_like_plain_numbered_option_list(text: str) -> bool:
        lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
        if len(lines) < 2:
            return False
        numbered = 0
        for line in lines:
            if re.match(r"^\d+[.)]\s+\S", line):
                numbered += 1
                continue
            return False
        return numbered >= 2
