from __future__ import annotations

from typing import Any

from src.personality.conversation_personality_agent import ConversationPersonalityAgent


DEFAULT_DELIVERY_MODE_BY_TEMPLATE = {
    "morning_brief": "hybrid",
    "evening_digest": "hybrid",
    "inbox_check": "widget",
}

_OPENER_BY_TEMPLATE = {
    "morning_brief": "Here's your morning.",
    "evening_digest": "End of day.",
    "inbox_check": "I checked your inbox.",
}


def normalize_delivery_mode(template_id: str, delivery_mode: str | None) -> str:
    candidate = str(delivery_mode or "").strip().lower()
    if candidate not in {"widget", "chat", "hybrid"}:
        return DEFAULT_DELIVERY_MODE_BY_TEMPLATE.get(str(template_id or "").strip(), "widget")
    return candidate


def delivery_channels(template_id: str, delivery_mode: str | None) -> dict[str, bool]:
    mode = normalize_delivery_mode(template_id, delivery_mode)
    return {
        "widget": mode in {"widget", "hybrid"},
        "chat": mode in {"chat", "hybrid"},
    }


class OpenClawAgentPersonalityBridge:
    """Nova-owned presentation layer for worker-style task results."""

    def __init__(self, *, presenter: ConversationPersonalityAgent | None = None) -> None:
        self._presenter = presenter or ConversationPersonalityAgent()

    def present_result(self, envelope: Any, raw_result_text: str) -> str:
        template_id = str(getattr(envelope, "template_id", "") or "").strip()
        title = str(getattr(envelope, "title", "") or "").strip()
        opener = _OPENER_BY_TEMPLATE.get(template_id, "")
        return self._presenter.present_agent_result(
            title,
            str(raw_result_text or "").strip(),
            opener=opener,
            domain="daily",
        )

