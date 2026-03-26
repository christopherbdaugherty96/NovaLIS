from __future__ import annotations

import re

from src.conversation.response_formatter import ResponseFormatter
from src.personality.nova_style_contract import NovaStyleContract
from src.voice.stt_pipeline import STTAckConfig, build_ack_payload


class VoiceExperienceAgent:
    """Lightweight voice presentation layer for acknowledgements and spoken output."""

    _VOICE_CHECK_PREFIX = "nova voice check complete."
    _ACK_BY_MODE = {
        "analysis": "Okay.",
        "brainstorm": "Gotcha.",
        "action": "Okay.",
        "work": "Okay.",
        "direct": "Gotcha.",
        "casual": "Gotcha.",
        "unknown": "Okay.",
    }
    _INITIATIVE_SPLIT_RE = re.compile(r"\n\n(?:If useful, I can|If you want, I can)\b", re.IGNORECASE)
    _TRY_NEXT_SPLIT_RE = re.compile(r"\n\nTry next:\s*", re.IGNORECASE)
    _SUMMARY_RE = re.compile(r"Summary:\s*(.+?)(?:(?<=\.)\s|$)", re.IGNORECASE)
    _SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")

    def build_ack_payload(self, config: STTAckConfig, *, mode: str = "direct") -> dict | None:
        payload = build_ack_payload(config)
        if payload is None:
            return None

        base_text = str(payload.get("message") or "").strip()
        if not base_text:
            return payload

        if base_text.lower().rstrip(".!?") == "got it":
            payload["message"] = self._ACK_BY_MODE.get(str(mode or "").strip().lower(), "Okay.")
        else:
            payload["message"] = ResponseFormatter.format(base_text, mode="casual")
        return payload

    def prepare_spoken_reply(self, text: str, *, mode: str = "casual") -> str:
        raw = str(text or "").replace("\r\n", "\n").strip()
        if not raw:
            return ""

        if raw.lower().startswith(self._VOICE_CHECK_PREFIX):
            return ResponseFormatter.to_speakable_text(raw)

        raw = self._trim_visual_only_sections(raw)
        speakable = ResponseFormatter.to_speakable_text(raw)
        if not speakable:
            return ""

        summary_match = self._SUMMARY_RE.search(speakable)
        if summary_match:
            summary = ResponseFormatter.to_speakable_text(summary_match.group(1))
            trailing = speakable[summary_match.end() :].strip()
            if trailing:
                return f"{summary} I also put the full answer on screen."
            return summary

        if self._should_summarize_for_voice(speakable):
            summary = self._summarize_for_voice(speakable)
            if summary and summary != speakable:
                return f"{summary} I also put the full answer on screen."

        if self._is_brief_status(speakable):
            lowered = speakable.lower()
            if not lowered.startswith(("okay.", "gotcha.", "sure thing.", "hello.", "good ")):
                return f"{NovaStyleContract.spoken_acknowledgement('neutral')} {speakable}".strip()

        return speakable

    def _trim_visual_only_sections(self, text: str) -> str:
        trimmed = self._TRY_NEXT_SPLIT_RE.split(text, maxsplit=1)[0]
        trimmed = self._INITIATIVE_SPLIT_RE.split(trimmed, maxsplit=1)[0]
        return trimmed.strip()

    def _should_summarize_for_voice(self, text: str) -> bool:
        if "\n" in text:
            return True
        sentences = [part.strip() for part in self._SENTENCE_RE.split(text) if part.strip()]
        return len(sentences) >= 4 or len(text) > 260

    def _summarize_for_voice(self, text: str) -> str:
        summary_match = self._SUMMARY_RE.search(text)
        if summary_match:
            summary = ResponseFormatter.to_speakable_text(summary_match.group(1))
            if summary:
                return summary

        sentences = [part.strip() for part in self._SENTENCE_RE.split(text) if part.strip()]
        if not sentences:
            return ""
        spoken = " ".join(sentences[:2]).strip()
        if len(spoken) > 220:
            spoken = spoken[:217].rstrip() + "..."
        return spoken

    @staticmethod
    def _is_brief_status(text: str) -> bool:
        clean = str(text or "").strip()
        if not clean or clean.endswith("?") or "\n" in clean:
            return False
        if len(clean) > 72:
            return False
        sentence_count = len([part for part in re.split(r"(?<=[.!?])\s+", clean) if part.strip()])
        return sentence_count <= 2
