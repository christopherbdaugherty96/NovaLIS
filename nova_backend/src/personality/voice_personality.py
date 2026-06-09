"""Voice personality rules for the Chief of Staff personality layer.

Formats text for TTS delivery with mode-aware tone, shortened
output, and visual confirmation requirements for high-authority
actions.

Governance boundaries:
  - No imports from src.governor, src.executors, src.ledger
  - Voice may make Nova sound more natural
  - Voice may not lower confirmation requirements
  - High-authority actions require visual confirmation
  - Enforced by import boundary test
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.personality.chief_of_staff_profile import ChiefOfStaffProfile


_ALARM_WORDS = re.compile(
    r"\b(ERROR|CRITICAL|ALERT|FATAL|PANIC|FAILURE)\b",
    re.IGNORECASE,
)

_MARKDOWN = re.compile(r"\*{1,3}|`{1,3}|^#{1,6}\s+", re.MULTILINE)
_LIST_MARKERS = re.compile(r"^\s*[-*]\s+", re.MULTILINE)
_NUMBERED_LIST = re.compile(r"^\s*\d+[.)]\s+", re.MULTILINE)

_HIGH_AUTHORITY_CAPS = frozenset({22, 64})

_MAX_VOICE_SENTENCES = 3
_MAX_VOICE_CHARS = 300


@dataclass(frozen=True)
class VoicePersonalityResult:
    """Immutable voice output. No authority flags."""

    spoken_text: str
    display_text: str
    requires_visual_confirmation: bool
    mode: str


class VoicePersonality:
    """Formats text for voice (TTS) delivery.

    Presentation-only. Does not call capabilities, executors,
    or governance components.
    """

    def format_for_voice(
        self,
        text: str,
        *,
        mode: str = "home",
        is_confirmation: bool = False,
        is_failure: bool = False,
        confirmation_cap_id: int | None = None,
        profile: ChiefOfStaffProfile | None = None,
    ) -> VoicePersonalityResult:
        from src.personality.chief_of_staff_profile import (
            ChiefOfStaffProfile as _P,
        )
        p = profile or _P()

        raw = str(text or "").strip()
        display = raw

        requires_visual = (
            is_confirmation
            and confirmation_cap_id is not None
            and confirmation_cap_id in _HIGH_AUTHORITY_CAPS
        )

        if is_failure:
            spoken = self._format_failure(raw, p)
        elif is_confirmation:
            spoken = self._format_confirmation(raw, requires_visual)
        else:
            spoken = self._shorten(raw)

        spoken = self._clean_for_speech(spoken)

        return VoicePersonalityResult(
            spoken_text=spoken,
            display_text=display,
            requires_visual_confirmation=requires_visual,
            mode=mode,
        )

    def _shorten(self, text: str) -> str:
        clean = self._strip_markdown(text)
        sentences = [
            s.strip()
            for s in re.split(r"(?<=[.!?])\s+", clean)
            if s.strip()
        ]
        if not sentences:
            return clean[:_MAX_VOICE_CHARS].strip()
        short = " ".join(sentences[:_MAX_VOICE_SENTENCES])
        if len(short) > _MAX_VOICE_CHARS:
            short = short[:_MAX_VOICE_CHARS - 3].rstrip() + "..."
        return short

    def _strip_markdown(self, text: str) -> str:
        clean = _MARKDOWN.sub("", text)
        clean = _LIST_MARKERS.sub("", clean)
        clean = _NUMBERED_LIST.sub("", clean)
        clean = re.sub(r"\n{2,}", ". ", clean)
        clean = re.sub(r"\n", " ", clean)
        clean = re.sub(r"\s{2,}", " ", clean)
        return clean.strip()

    def _format_failure(
        self,
        text: str,
        profile: ChiefOfStaffProfile,
    ) -> str:
        cleaned = _ALARM_WORDS.sub("", text).strip()
        cleaned = re.sub(r"\s{2,}", " ", cleaned)
        if not cleaned:
            cleaned = "Something did not work as expected."
        suggestion = profile.permitted_suggestion_language[0]
        return (
            f"It looks like something ran into a problem. "
            f"{suggestion} try again, or we can look at alternatives."
        )

    def _format_confirmation(
        self,
        text: str,
        requires_visual: bool,
    ) -> str:
        short = self._shorten(text)
        if requires_visual:
            return (
                f"{short} "
                f"Please confirm this on screen before I proceed."
            )
        return short

    def _clean_for_speech(self, text: str) -> str:
        clean = self._strip_markdown(text)
        clean = re.sub(
            r"https?://\S+", "the link", clean, flags=re.IGNORECASE,
        )
        clean = re.sub(r"\s{2,}", " ", clean)
        return clean.strip()
