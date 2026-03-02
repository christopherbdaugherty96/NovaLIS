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

        # Gentle cadence shaping: pause after labels and list markers.
        clean = re.sub(r":\s+", ": … ", clean)
        clean = re.sub(r"\n\s*[-•]\s+", " … ", clean)
        clean = re.sub(r"\n\s*\d+[.)]\s+", " … ", clean)

        sentences = self.split_sentences(clean)
        if not sentences:
            return ""

        paced = " … ".join(sentences)
        paced = re.sub(r"\s{2,}", " ", paced).strip()
        return paced
