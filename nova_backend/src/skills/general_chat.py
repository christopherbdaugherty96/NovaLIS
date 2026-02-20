"""
NovaLIS General Chat Skill — Phase 3 SAFE / Phase 4 Ready (Constitutional)
Refined with safe butler cadence: composed, precise, slightly formal, no initiative.

Rules:
- User-initiated only
- Stateless (session-only; no persistence)
- No memory writes
- No streaming
- No execution
- Optional dependency must NOT crash startup
- Deterministic, bounded communication frames (invisible/automatic)
- Tone is composed, professional, and courteous across all modes.
- Direct address used only in instructional contexts.
- No persuasion, no emotional simulation, no initiative.
"""

from __future__ import annotations

import re
from typing import Dict, Tuple

from ..base_skill import BaseSkill, SkillResult


class GeneralChatSkill(BaseSkill):
    name = "general_chat"
    description = "General chat (LLM advisory only)"

    # -------------------------
    # Constitutional base contract with butler cadence
    # -------------------------
    BASE_CONTRACT = (
        "You are Nova.\n"
        "\n"
        "Core constraints:\n"
        "- Speak calmly, with restrained professional courtesy.\n"
        "- Use complete, well‑structured sentences.\n"
        "- Avoid slang, casual fillers, and enthusiasm markers.\n"
        "- Maintain composed and precise phrasing.\n"
        "- No emotional simulation. No therapy tone. No flattery.\n"
        "- No marketing language. No brand voice.\n"
        "- Do not introduce yourself unless explicitly asked.\n"
        "- Do not describe what Nova is unless explicitly asked.\n"
        "- Do not claim capabilities you do not have.\n"
        "- Do not mention being a 'virtual assistant' or similar.\n"
        "- Answer directly. Keep it short unless the user asks for depth.\n"
        "- When giving instructions, address the user directly with 'you'.\n"
        "- If the request is unclear, ask ONE brief clarification question.\n"
    )

    # -------------------------
    # Structural mode blocks – tone remains composed throughout
    # -------------------------
    MODE_BLOCKS: Dict[str, str] = {
        "concise": (
            "Communication style: Concise.\n"
            "- Answer in one or two short, complete sentences.\n"
            "- No additional commentary.\n"
        ),
        "explanatory": (
            "Communication style: Explanatory.\n"
            "- Explain clearly using cause and effect.\n"
            "- Use precise, straightforward language.\n"
            "- Avoid persuasive or motivational tone.\n"
        ),
        "procedural": (
            "Communication style: Procedural.\n"
            "- Provide ordered steps using direct address ('you').\n"
            "- Use composed, precise language.\n"
            "- Keep each instruction self-contained.\n"
            "- Do not add commentary beyond the steps.\n"
        ),
        "analytical": (
            "Communication style: Analytical.\n"
            "- Present reasoning clearly and concisely.\n"
            "- Use structured breakdowns if helpful.\n"
            "- State conclusions directly without embellishment.\n"
        ),
    }

    # Per‑mode output bounds
    MAX_TOKENS: Dict[str, int] = {
        "concise": 150,
        "explanatory": 500,
        "procedural": 400,
        "analytical": 600,
    }

    # Light drift prevention
    _BANNED_PATTERNS: Tuple[Tuple[re.Pattern, str], ...] = (
        (re.compile(r"\b(as an ai|as a language model)\b", re.IGNORECASE), ""),
        (re.compile(r"\b(i am|i'm)\s+(a\s+)?virtual assistant\b", re.IGNORECASE), ""),
        (re.compile(r"\b(i am|i'm)\s+here\s+to\s+help\b", re.IGNORECASE), ""),
        (re.compile(r"\bhow can i assist\??\b", re.IGNORECASE), ""),
        (re.compile(r"\!+", re.IGNORECASE), "."),
    )

    # -------------------------
    # Skill interface
    # -------------------------
    def can_handle(self, query: str) -> bool:
        q = (query or "").strip().lower()
        if not q:
            return False

        tokens = q.split()

        # Authoritative skills must win (token‑based, deterministic)
        if any(
            token
            in {
                "weather",
                "forecast",
                "news",
                "headlines",
                "time",
                "date",
                "system",
                "status",
            }
            for token in tokens
        ):
            return False

        return True

    # -------------------------
    # Deterministic frame selection (invisible)
    # -------------------------
    def _detect_mode(self, query: str) -> str:
        q = (query or "").strip().lower()
        if not q:
            return "concise"

        # Procedural (step‑by‑step)
        if any(
            phrase in q
            for phrase in (
                "step by step",
                "walk me through",
                "show me how",
                "what should i do",
                "how do i",
            )
        ):
            return "procedural"

        # Analytical (trade‑offs, reasoning)
        if any(
            word in q
            for word in (
                "analyse",
                "analyze",
                "trade-off",
                "compare",
                "pros and cons",
                "evaluate",
                "strategy",
                "why would",
            )
        ):
            return "analytical"

        # Explanatory (cause and effect)
        if any(
            word in q
            for word in (
                "explain",
                "why does",
                "how does",
                "what causes",
                "reason",
                "mechanism",
                "architecture",
                "design",
            )
        ):
            return "explanatory"

        return "concise"

    def _build_system_prompt(self, mode: str) -> str:
        mode_block = self.MODE_BLOCKS.get(mode, self.MODE_BLOCKS["concise"])
        return f"{self.BASE_CONTRACT}\n{mode_block}".strip()

    def _sanitize_response(self, text: str) -> str:
        t = (text or "").strip()
        if not t:
            return t

        for pat, repl in self._BANNED_PATTERNS:
            t = pat.sub(repl, t)

        t = re.sub(r"\s{2,}", " ", t).strip()
        t = re.sub(r"\n{3,}", "\n\n", t).strip()
        t = re.sub(r"\n+$", "\n", t).rstrip("\n")
        return t

    async def handle(self, query: str) -> SkillResult | None:
        try:
            import ollama
        except Exception:
            return None

        mode = self._detect_mode(query)
        system_prompt = self._build_system_prompt(mode)
        max_tokens = self.MAX_TOKENS.get(mode, self.MAX_TOKENS["concise"])

        try:
            response = ollama.chat(
                model="phi3:mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
                options={
                    "temperature": 0.3,
                    "num_predict": max_tokens,
                },
            )

            text = response.get("message", {}).get("content", "")
            text = self._sanitize_response(text)

            if not text:
                text = "I don’t have a response for that."

            return SkillResult(
                success=True,
                message=text,
                data={"mode": mode},
                widget_data=None,
                skill=self.name,
            )

        except Exception:
            return None