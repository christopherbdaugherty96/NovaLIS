"""
NovaLIS General Chat Skill — Phase 3 SAFE / Phase 4.2 cognitive staging.
"""

from __future__ import annotations

import asyncio
import re
from typing import Dict, Optional, Tuple

from src.conversation.complexity_heuristics import ComplexityHeuristics
from src.conversation.deepseek_bridge import DeepSeekBridge
from src.conversation.escalation_policy import EscalationPolicy
from src.conversation.response_formatter import ResponseFormatter
from src.conversation.response_style_router import InputNormalizer, ResponseStyle, ResponseStyleRouter
from src.conversation.safety_filter import SafetyFilter
from src.conversation.deepseek_safety_wrapper import DeepSeekSafetyWrapper
from src.governor.network_mediator import NetworkMediator

from ..base_skill import BaseSkill, SkillResult


class GeneralChatSkill(BaseSkill):
    name = "general_chat"
    description = "General chat (LLM advisory only)"

    BASE_CONTRACT = (
        "You are Nova.\n"
        "\n"
        "Core constraints:\n"
        "- Speak calmly, with composed, butler-like courtesy.\n"
        "- Use complete, polished sentences with natural flow.\n"
        "- Keep language human, concise, and quietly confident.\n"
        "- Avoid slang, hype, or theatrical enthusiasm.\n"
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

    MODE_BLOCKS: Dict[str, str] = {
        "casual": (
            "Communication style: Concise.\n"
            "- Answer in one or two short, complete sentences.\n"
            "- No additional commentary.\n"
        ),
        "brainstorming": (
            "Communication style: Explanatory.\n"
            "- Explain clearly using cause and effect.\n"
            "- Use precise, straightforward language.\n"
            "- Avoid persuasive or motivational tone.\n"
        ),
        "implementation": (
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

    MAX_TOKENS: Dict[str, int] = {
        "casual": 150,
        "brainstorming": 500,
        "implementation": 400,
        "analytical": 600,
    }

    _BANNED_PATTERNS: Tuple[Tuple[re.Pattern, str], ...] = (
        (re.compile(r"\b(as an ai|as a language model)\b", re.IGNORECASE), ""),
        (re.compile(r"\b(i am|i'm)\s+(a\s+)?virtual assistant\b", re.IGNORECASE), ""),
        (re.compile(r"\b(i am|i'm)\s+here\s+to\s+help\b", re.IGNORECASE), ""),
        (re.compile(r"\bhow can i assist\??\b", re.IGNORECASE), ""),
        (re.compile(r"\!+", re.IGNORECASE), "."),
    )

    def __init__(self, policy_config: Optional[dict] = None, network: NetworkMediator | None = None):
        self.heuristics = ComplexityHeuristics()
        self.policy = EscalationPolicy(policy_config)
        self.deepseek = DeepSeekBridge()
        self.safety = SafetyFilter()
        self.analysis_safety = DeepSeekSafetyWrapper()
        self.style_router = ResponseStyleRouter()
        self.formatter = ResponseFormatter()

    def can_handle(self, query: str) -> bool:
        q = InputNormalizer.normalize(query).lower().strip(".?!")
        if not q:
            return False

        tokens = q.split()
        if any(
            token in {"weather", "forecast", "news", "headlines", "time", "date", "system", "status"}
            for token in tokens
        ):
            return False
        return True

    def _detect_mode(self, query: str) -> str:
        q = InputNormalizer.normalize(query).lower().strip(".?!")
        if not q:
            return "casual"

        if any(word in q for word in ("ideas", "what if", "explore", "brainstorm", "directions")):
            return "brainstorming"

        if any(word in q for word in ("analyse", "analyze", "trade-off", "compare", "pros and cons", "evaluate", "strategy", "deep dive")):
            return "analytical"

        if any(phrase in q for phrase in ("step by step", "walk me through", "show me how", "how do i", "modify", "write code", "implement")):
            return "implementation"

        return "casual"

    def _build_system_prompt(self, mode: str, style: ResponseStyle = ResponseStyle.DIRECT) -> str:
        mode_block = self.MODE_BLOCKS.get(mode, self.MODE_BLOCKS["casual"])

        style_blocks = {
            ResponseStyle.DIRECT: "Style: Direct and concise. Prioritize factual precision.",
            ResponseStyle.BRAINSTORM: "Style: Brainstorm mode. Provide structured ideas as bullet points.",
            ResponseStyle.DEEP: "Style: Deep mode. Provide layered reasoning with concise section headers.",
            ResponseStyle.CASUAL: "Style: Conversational mode. Keep response brief, warm, and polished.",
        }

        style_block = style_blocks.get(style, style_blocks[ResponseStyle.DIRECT])
        return f"{self.BASE_CONTRACT}\n{mode_block}\n{style_block}".strip()

    def _sanitize_response(self, text: str) -> str:
        clean = (text or "").strip()
        if not clean:
            return clean

        for pattern, replacement in self._BANNED_PATTERNS:
            clean = pattern.sub(replacement, clean)

        clean = re.sub(r"\s{2,}", " ", clean).strip()
        clean = re.sub(r"\n{3,}", "\n\n", clean).strip()
        clean = re.sub(r"\n+$", "\n", clean).rstrip("\n")
        return clean

    async def _run_local_model(self, query: str) -> SkillResult | None:
        try:
            import ollama
        except Exception:
            return None

        normalized_query = InputNormalizer.normalize(query)
        mode = self._detect_mode(normalized_query)
        style = self.style_router.route(normalized_query)
        system_prompt = self._build_system_prompt(mode, style)
        max_tokens = self.MAX_TOKENS.get(mode, self.MAX_TOKENS["casual"])

        try:
            response = await asyncio.to_thread(
                ollama.chat,
                model="phi3:mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": normalized_query},
                ],
                options={"temperature": 0.3, "num_predict": max_tokens},
            )
            text = self._sanitize_response(response.get("message", {}).get("content", ""))
            if not text:
                text = "I don’t have a response for that."

            return SkillResult(success=True, message=text, data={"mode": mode, "style": style.value}, widget_data=None, skill=self.name)
        except Exception:
            return None

    async def handle(self, query: str, context: Optional[list] = None, session_state: Optional[dict] = None) -> SkillResult | None:
        # Backward compatible path
        if context is None or session_state is None:
            return await self._run_local_model(query)

        normalized_query = InputNormalizer.normalize(query)
        heuristic_result = self.heuristics.assess(normalized_query, context)
        decision = self.policy.decide(heuristic_result, normalized_query, session_state)
        mode = heuristic_result.get("mode") or self._detect_mode(normalized_query)
        initiative = self.policy.conversational_flags(heuristic_result, normalized_query, session_state)

        if decision == "ASK_USER":
            return SkillResult(
                success=True,
                message="Would you like a deeper analysis of that?",
                data={
                    "escalation": {
                        "ask_user": True,
                        "original_query": normalized_query,
                        "context_snapshot": context[-5:],
                        "heuristic_result": heuristic_result,
                    }
                },
                widget_data=None,
                skill=self.name,
            )

        if decision == "ALLOW_ANALYSIS_ONLY":
            thought_data = {
                "decision": "ALLOW_ANALYSIS_ONLY",
                "reason_codes": heuristic_result.get("reason_codes", []),
                "suggested_tokens": heuristic_result.get("suggested_max_tokens", 800),
                "heuristic": heuristic_result,
            }
            raw = await asyncio.to_thread(
                self.deepseek.analyze,
                normalized_query,
                context,
                heuristic_result.get("suggested_max_tokens", 800),
            )
            safe = self.safety.filter(raw)
            safe = self.analysis_safety.sanitize(safe)
            formatted = self.formatter.format(safe)
            return SkillResult(
                success=True,
                message=formatted,
                data={"escalation": {"escalated": True, "thought_data": thought_data}},
                widget_data=None,
                skill=self.name,
            )

        local = await self._run_local_model(normalized_query)
        if local is None:
            return None

        local.message = self.formatter.with_conversational_initiative(
            local.message,
            mode=mode,
            allow_clarification=initiative.get("allow_clarification", False),
            allow_branch_suggestion=initiative.get("allow_branch_suggestion", False),
            allow_depth_prompt=initiative.get("allow_depth_prompt", False),
        )
        if initiative.get("allow_clarification"):
            session_state["last_clarification_turn"] = session_state.get("turn_count", 0)
        local.data = {"escalation": {"escalated": False}}
        return local