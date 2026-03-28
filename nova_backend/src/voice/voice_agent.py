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
    _RECOMMENDED_ACTIONS_SPLIT_RE = re.compile(r"\n\n(?:Recommended actions|Recommended next steps):\s*", re.IGNORECASE)
    _BOTTOM_LINE_RE = re.compile(r"Bottom line:\s*(.+?)(?:(?<=\.)\s|$)", re.IGNORECASE)
    _SUMMARY_RE = re.compile(r"Summary:\s*(.+?)(?:(?<=\.)\s|$)", re.IGNORECASE)
    _SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
    _SECOND_OPINION_HEADINGS = ("Governed Second Opinion", "DeepSeek Second Opinion")
    _STRUCTURED_REPORT_HEADINGS = (
        "INTELLIGENCE BRIEF",
        "NOVA INTELLIGENCE BRIEF",
        "NOVA MULTI-SOURCE REPORT",
        "DETAILED STORY ANALYSIS",
    )
    _REVIEW_LINE_PATTERNS = {
        "bottom_line": re.compile(r"(?im)^Bottom line:\s*(.+)$"),
        "agreement": re.compile(r"(?im)^(?:Agreement Level|Claim Reliability):\s*(.+)$"),
        "confidence": re.compile(r"(?im)^(?:Review Confidence|Report Confidence):\s*(.+)$"),
        "main_gap": re.compile(r"(?im)^Main gap:\s*(.+)$"),
        "best_correction": re.compile(r"(?im)^Best correction:\s*(.+)$"),
        "recommendation": re.compile(r"(?im)^Recommendation:\s*(.+)$"),
    }

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
        review_summary = self._extract_structured_review_summary(raw)
        if review_summary:
            return review_summary
        report_summary = self._extract_structured_report_summary(raw)
        if report_summary:
            return report_summary

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
        trimmed = self._RECOMMENDED_ACTIONS_SPLIT_RE.split(trimmed, maxsplit=1)[0]
        trimmed = self._INITIATIVE_SPLIT_RE.split(trimmed, maxsplit=1)[0]
        return trimmed.strip()

    def _extract_structured_review_summary(self, text: str) -> str:
        clean = str(text or "").strip()
        if not clean:
            return ""

        is_second_opinion = any(clean.startswith(heading) for heading in self._SECOND_OPINION_HEADINGS)
        if not is_second_opinion and not clean.startswith("Verification Report"):
            return ""

        bottom_line = self._extract_review_line(clean, "bottom_line")
        agreement = self._extract_review_line(clean, "agreement")
        confidence = self._extract_review_line(clean, "confidence")
        main_gap = self._extract_review_line(clean, "main_gap")
        best_correction = self._extract_review_line(clean, "best_correction")
        recommendation = self._extract_review_line(clean, "recommendation")

        parts = ["Second opinion ready." if is_second_opinion else "Verification ready."]
        if bottom_line:
            parts.append(f"Bottom line: {bottom_line}.")
        if agreement:
            label = "Agreement level" if is_second_opinion else "Claim reliability"
            parts.append(f"{label} {agreement}.")
        if confidence:
            label = "Review confidence" if is_second_opinion else "Report confidence"
            parts.append(f"{label} {confidence}.")
        if main_gap:
            parts.append(f"Main gap: {main_gap}.")
        if best_correction:
            parts.append(f"Best correction: {best_correction}.")
        elif recommendation:
            parts.append(f"{recommendation}.")
        parts.append("I also put the full review on screen.")
        return " ".join(part.strip() for part in parts if part.strip()).strip()

    def _extract_review_line(self, text: str, key: str) -> str:
        pattern = self._REVIEW_LINE_PATTERNS[key]
        match = pattern.search(text)
        if not match:
            return ""
        value = re.sub(r"\s+", " ", match.group(1)).strip(" .")
        if not value:
            return ""
        return value

    def _extract_structured_report_summary(self, text: str) -> str:
        clean = str(text or "").strip()
        if not clean:
            return ""

        heading = clean.splitlines()[0].strip() if clean.splitlines() else ""
        is_structured_report = (
            heading in self._STRUCTURED_REPORT_HEADINGS
            or heading.startswith("Analysis document created")
            or heading.startswith("Document Summary - Doc")
            or heading.startswith("Section Explanation - Doc")
            or heading.startswith("STORY TRACKER - ")
        )
        if not is_structured_report:
            return ""

        bottom_line = self._extract_first_match(clean, self._BOTTOM_LINE_RE)
        if not bottom_line:
            bottom_line = self._extract_first_match(clean, self._SUMMARY_RE)
        if not bottom_line:
            return ""

        if heading.startswith("Analysis document created"):
            prefix = "Analysis document ready."
        elif heading.startswith("Document Summary - Doc"):
            prefix = "Document summary ready."
        elif heading.startswith("Section Explanation - Doc"):
            prefix = "Section explanation ready."
        elif heading.startswith("STORY TRACKER - "):
            prefix = "Story tracker update ready."
        elif heading == "DETAILED STORY ANALYSIS":
            prefix = "Detailed story analysis ready."
        else:
            prefix = "Report ready."
        return f"{prefix} {bottom_line}. I also put the full answer on screen."

    @staticmethod
    def _extract_first_match(text: str, pattern: re.Pattern[str]) -> str:
        match = pattern.search(text)
        if not match:
            return ""
        value = ResponseFormatter.to_speakable_text(match.group(1))
        return value.strip(" .")

    def _should_summarize_for_voice(self, text: str) -> bool:
        if "\n" in text:
            return True
        sentences = [part.strip() for part in self._SENTENCE_RE.split(text) if part.strip()]
        return len(sentences) >= 4 or len(text) > 260

    def _summarize_for_voice(self, text: str) -> str:
        bottom_line_match = self._BOTTOM_LINE_RE.search(text)
        if bottom_line_match:
            summary = ResponseFormatter.to_speakable_text(bottom_line_match.group(1))
            if summary:
                return summary

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
