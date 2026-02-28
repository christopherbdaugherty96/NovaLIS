from __future__ import annotations

import re


class SpeechFormatter:
    """Deterministic speech formatting for clearer TTS rendering."""

    @staticmethod
    def split_sentences(text: str) -> list[str]:
        parts = re.split(r"(?<=[.!?])\s+", (text or "").strip())
        return [p.strip() for p in parts if p.strip()]

    def format_for_tts(self, text: str) -> str:
        sentences = self.split_sentences(text)
        if not sentences:
            return ""

        # Insert short pause marker between sentences.
        paced = " … ".join(sentences)
        paced = re.sub(r"\s{2,}", " ", paced).strip()
        return paced
