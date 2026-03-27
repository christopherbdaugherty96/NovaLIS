from __future__ import annotations

import re

from src.personality.interface_agent import PersonalityInterfaceAgent
from src.personality.nova_style_contract import NovaStyleContract


class ConversationPersonalityAgent:
    """Presentation-only runtime layer for smoother chat delivery."""

    _SOFT_STATUS_REWRITES = (
        (
            re.compile(r"^Cancelled website open request\.$", re.IGNORECASE),
            "Okay. I canceled the website open request.",
        ),
        (
            re.compile(r"^Cancelled\.$", re.IGNORECASE),
            "Okay. Canceled.",
        ),
        (
            re.compile(r"^Canceled\.$", re.IGNORECASE),
            "Okay. Canceled.",
        ),
        (
            re.compile(
                r"^Deep analysis is unavailable right now\.\s+Please answer ['\"]yes['\"], ['\"]no['\"], or ['\"]cancel['\"]\.$",
                re.IGNORECASE,
            ),
            "Deep analysis is unavailable right now. Reply 'yes', 'no', or 'cancel'.",
        ),
        (
            re.compile(
                r"^Thanks\.\s+I lost the interpreted command\.\s+Please say it again\.$",
                re.IGNORECASE,
            ),
            "Okay. I lost that command. Say it again.",
        ),
    )
    _SHORT_STATUS_PREFIXES = (
        "completed",
        "done",
        "saved",
        "locked",
        "unlocked",
        "deleted",
        "deferred",
        "paused",
        "muted",
        "unmuted",
        "brightness adjusted",
        "volume up",
        "volume down",
        "canceled",
        "cancelled",
        "updated",
        "opened",
    )
    _ALREADY_SOFT_OPENERS = (
        "okay.",
        "gotcha.",
        "sure thing.",
        "hello.",
        "good morning.",
        "good afternoon.",
        "good evening.",
        "you're welcome.",
        "i can't",
        "i could not",
    )

    def __init__(self, *, interface_agent: PersonalityInterfaceAgent | None = None) -> None:
        self._interface_agent = interface_agent or PersonalityInterfaceAgent()

    def present(self, text: str, *, domain: str = "general") -> str:
        clean = str(text or "").strip()
        if not clean:
            return ""

        clean = self._rewrite_known_status_messages(clean)
        clean = self._soften_short_status(clean)
        clean = self._rewrite_fallbacks(clean)
        clean = self._interface_agent.present(clean, domain=domain)
        clean = NovaStyleContract.normalize(clean)
        return clean.strip()

    def present_agent_result(
        self,
        task_title: str,
        result_text: str,
        *,
        opener: str = "",
        domain: str = "daily",
    ) -> str:
        return self._interface_agent.present_agent_result(
            task_title,
            result_text,
            opener=opener,
            domain=domain,
        )

    def _rewrite_known_status_messages(self, text: str) -> str:
        updated = str(text or "").strip()
        for pattern, replacement in self._SOFT_STATUS_REWRITES:
            updated = pattern.sub(replacement, updated)
        return updated

    def _soften_short_status(self, text: str) -> str:
        clean = str(text or "").strip()
        lowered = clean.lower()
        if (
            not clean
            or len(clean) > 64
            or clean.endswith("?")
            or "\n" in clean
            or any(lowered.startswith(opener) for opener in self._ALREADY_SOFT_OPENERS)
        ):
            return clean

        if any(lowered.startswith(prefix) for prefix in self._SHORT_STATUS_PREFIXES):
            return f"Okay. {clean}"
        return clean

    @staticmethod
    def _rewrite_fallbacks(text: str) -> str:
        clean = str(text or "").strip()
        lowered = clean.lower()
        if lowered.startswith("i might have misunderstood that. try one of these:"):
            return (
                "I didn't quite catch that. Try one of these: "
                "what can you do, what time is it, today's news, or open documents."
            )
        return clean
