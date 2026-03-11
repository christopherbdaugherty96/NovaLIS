from __future__ import annotations

import re


class SpeechFormatter:
    """Deterministic speech formatting for clearer TTS rendering."""

    @staticmethod
    def split_sentences(text: str) -> list[str]:
        parts = re.split(r"(?<=[.!?])\s+", (text or "").strip())
        return [p.strip() for p in parts if p.strip()]

    def format_for_tts(self, text: str) -> str:
        clean = (text or "").strip()
        if not clean:
            return ""

        # Sanitize raw links and local file system paths before speech rendering.
        clean = re.sub(r"https?://\S+", "the link", clean, flags=re.IGNORECASE)
        clean = re.sub(r"(?:\b[A-Za-z]:\\[^\s]+|/(?:[^\s/]+/)+[^\s]*)", "the file", clean)
        clean = re.sub(
            r"\b(?:request_id|session_id|capability_id|action_result|executeboundary|action_attempted|action_completed)\b[:=\s\-]*\S*",
            "system detail",
            clean,
            flags=re.IGNORECASE,
        )
        clean = clean.replace("`", "")

        # Gentle cadence shaping: pause after labels and list markers.
        clean = re.sub(r":\s+", ": ... ", clean)
        clean = re.sub(r"\n\s*[-*]\s+", " ... ", clean)
        clean = re.sub(r"\n\s*\d+[.)]\s+", " ... ", clean)
        clean = re.sub(r"\b(Weather|System|News|Summary)\b", r"... \1", clean)

        sentences = self.split_sentences(clean)
        if not sentences:
            return ""

        paced = " ... ".join(sentences)
        paced = re.sub(r"\s{2,}", " ", paced).strip()
        return paced
