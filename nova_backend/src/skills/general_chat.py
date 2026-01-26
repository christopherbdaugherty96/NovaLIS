"""
NovaLIS General Chat Skill — Phase 3 SAFE

Rules:
- User-initiated only
- Stateless
- No memory
- No streaming
- No execution
- Optional dependency must NOT crash startup
"""

from __future__ import annotations

from ..base_skill import BaseSkill, SkillResult


class GeneralChatSkill(BaseSkill):
    name = "general_chat"
    description = "General chat (LLM advisory only)"

    def can_handle(self, query: str) -> bool:
        q = (query or "").strip().lower()
        if not q:
            return False

        tokens = q.split()

        # Authoritative skills must win (token-based)
        if any(token in {
            "weather",
            "forecast",
            "news",
            "headlines",
            "time",
            "date",
            "system",
            "status",
        } for token in tokens):
            return False

        return len(tokens) >= 1

    async def handle(self, query: str) -> SkillResult | None:
        # Lazy import — NEVER crash boot
        try:
            import ollama
        except Exception:
            return None

        SYSTEM_PROMPT = (
            "You are Nova, a local-first personal assistant system called NovaLIS. "
            "NovaLIS is a privacy-first, offline-capable home assistant platform "
            "designed to provide weather, news, system status, and advisory responses. "
            "Nova does not invent facts about itself. "
            "If asked about NovaLIS, explain it as a local personal AI system created by the user, "
            "not a public product or company. "
            "If unsure, say so plainly."
        )

        try:
            response = ollama.chat(
                model="phi3:mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": query},
                ],
            )

            text = response.get("message", {}).get("content", "").strip()
            if not text:
                text = "I don’t have a response for that."

            return SkillResult(
                success=True,
                message=text,
                data={},
                widget_data=None,
                skill=self.name,
            )

        except Exception:
            return None
