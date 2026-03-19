"""
NovaLIS General Chat Skill — Phase 3 SAFE / Phase 4.2 cognitive staging.
"""

from __future__ import annotations

import asyncio
import re
from typing import Any, Dict, Optional, Tuple

from src.conversation.complexity_heuristics import ComplexityHeuristics
from src.conversation.deepseek_bridge import DeepSeekBridge
from src.conversation.escalation_policy import EscalationPolicy
from src.conversation.response_formatter import ResponseFormatter
from src.conversation.response_style_router import InputNormalizer, ResponseStyle, ResponseStyleRouter
from src.conversation.safety_filter import SafetyFilter
from src.conversation.deepseek_safety_wrapper import DeepSeekSafetyWrapper
from src.governor.network_mediator import NetworkMediator
from src.llm.llm_gateway import generate_chat
from src.personality.tone_profile_store import ToneProfileStore

from ..base_skill import BaseSkill, SkillResult


class GeneralChatSkill(BaseSkill):
    name = "general_chat"
    description = "General chat (LLM advisory only)"

    BASE_CONTRACT = (
        "You are Nova.\n"
        "\n"
        "Core constraints:\n"
        "- Sound calm, grounded, and collaborative.\n"
        "- Use direct, human language with natural flow.\n"
        "- Be warm without theatrical enthusiasm.\n"
        "- No emotional simulation. No therapy tone. No flattery.\n"
        "- No marketing language. No brand voice.\n"
        "- Do not introduce yourself unless explicitly asked.\n"
        "- Do not describe what Nova is unless explicitly asked.\n"
        "- Do not claim capabilities you do not have.\n"
        "- Do not mention being a 'virtual assistant' or similar.\n"
        "- Answer directly. Add detail only when it helps or the user asks for it.\n"
        "- When giving instructions, address the user directly with 'you'.\n"
        "- If the request is unclear, ask ONE brief clarification question.\n"
    )

    TONE_BLOCKS: Dict[str, str] = {
        "balanced": (
            "Tone profile: Balanced.\n"
            "- Keep the response calm, clear, and collaborative.\n"
            "- Be direct without sounding stiff.\n"
            "- Prefer useful clarity over polish for its own sake.\n"
        ),
        "concise": (
            "Tone profile: Concise.\n"
            "- Keep the response tight and to the point.\n"
            "- Use the shortest complete answer that still helps.\n"
            "- Minimize extra commentary unless the user asks for more.\n"
        ),
        "detailed": (
            "Tone profile: Detailed.\n"
            "- Give a fuller explanation when it improves clarity.\n"
            "- Preserve useful nuance, structure, and follow-up detail.\n"
            "- Do not compress the response so aggressively that key context is lost.\n"
        ),
        "formal": (
            "Tone profile: Formal.\n"
            "- Use slightly more formal wording while staying plain and direct.\n"
            "- Avoid stiff ceremonial phrasing.\n"
        ),
    }

    MODE_BLOCKS: Dict[str, str] = {
        "casual": (
            "Communication style: Concise.\n"
            "- Answer briefly in a short paragraph or two short sentences.\n"
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
    _GEO_KEYWORDS = ("war", "ukraine", "russia", "gaza", "israel", "conflict", "ceasefire")
    _REFUSAL_HINTS = (
        "i'm sorry",
        "cannot assist with that topic",
        "not appropriate for discussion",
        "i can't assist with that topic",
    )
    _DEPTH_HINTS = (
        "in detail",
        "go deeper",
        "deep dive",
        "step by step",
        "full analysis",
        "long version",
        "expand this",
        "break this down",
        "explain deeply",
    )
    _GREETING_RESPONSES: Dict[str, str] = {
        "hi": "Hello. What do you want to work on?",
        "hello": "Hello. What do you want to work on?",
        "hey": "Hello. What do you want to work on?",
        "good morning": "Good morning. What do you want to work on?",
        "good afternoon": "Good afternoon. What do you want to work on?",
        "good evening": "Good evening. What do you want to work on?",
    }
    _THANKS_RESPONSES: Dict[str, str] = {
        "thanks": "You're welcome.",
        "thank you": "You're welcome.",
    }
    _STATUS_RESPONSES: Dict[str, str] = {
        "how are you": "Ready to help. What do you want to work on?",
        "how are you doing": "Ready to help. What do you want to work on?",
        "how's it going": "Ready to help. What do you want to work on?",
        "hows it going": "Ready to help. What do you want to work on?",
    }
    _MAX_CONTEXT_TURNS = 6
    _MAX_CONTEXT_CHARS_PER_TURN = 220

    def __init__(
        self,
        policy_config: Optional[dict] = None,
        network: NetworkMediator | None = None,
        tone_store: ToneProfileStore | None = None,
    ):
        self.heuristics = ComplexityHeuristics()
        self.policy = EscalationPolicy(policy_config)
        self.deepseek = DeepSeekBridge()
        self.safety = SafetyFilter()
        self.analysis_safety = DeepSeekSafetyWrapper()
        self.style_router = ResponseStyleRouter()
        self.formatter = ResponseFormatter()
        self._tone_store = tone_store or ToneProfileStore()

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

    def _current_tone_profile(self, domain: str = "general") -> str:
        try:
            profile = self._tone_store.effective_profile(domain)
        except Exception:
            return "balanced"
        if profile not in self.TONE_BLOCKS:
            return "balanced"
        return profile

    def _build_system_prompt(
        self,
        mode: str,
        style: ResponseStyle = ResponseStyle.DIRECT,
        tone_profile: str = "balanced",
    ) -> str:
        mode_block = self.MODE_BLOCKS.get(mode, self.MODE_BLOCKS["casual"])
        tone_block = self.TONE_BLOCKS.get(tone_profile, self.TONE_BLOCKS["balanced"])

        style_blocks = {
            ResponseStyle.DIRECT: "Style: Direct and concise. Prioritize factual precision.",
            ResponseStyle.BRAINSTORM: "Style: Brainstorm mode. Provide structured ideas as bullet points.",
            ResponseStyle.DEEP: "Style: Deep mode. Provide layered reasoning with concise section headers.",
            ResponseStyle.CASUAL: "Style: Conversational mode. Keep response brief, warm, and polished.",
        }

        style_block = style_blocks.get(style, style_blocks[ResponseStyle.DIRECT])
        return f"{self.BASE_CONTRACT}\n\n{tone_block}\n\n{mode_block}\n\n{style_block}".strip()

    def _resolve_max_tokens(self, mode: str, *, tone_profile: str, explicit_depth: bool) -> int:
        max_tokens = self.MAX_TOKENS.get(mode, self.MAX_TOKENS["casual"])
        if not explicit_depth and mode == "casual":
            max_tokens = min(max_tokens, 90)

        if tone_profile == "concise":
            if not explicit_depth and mode == "casual":
                return min(max_tokens, 70)
            return max(120, int(max_tokens * 0.75))

        if tone_profile == "detailed":
            expanded = max_tokens + (120 if mode == "casual" else 180)
            return min(expanded, 900)

        return max_tokens

    def _shape_response_for_tone(
        self,
        text: str,
        *,
        mode: str,
        tone_profile: str,
        explicit_depth: bool,
    ) -> str:
        if explicit_depth:
            return text

        if tone_profile == "concise":
            if mode == "casual":
                return self._enforce_concise_response(text, max_sentences=1, max_chars=180)
            if mode in {"analytical", "implementation"}:
                return self._enforce_concise_response(text, max_sentences=3, max_chars=420)
            return self._enforce_concise_response(text, max_sentences=2, max_chars=260)

        if tone_profile == "detailed":
            if mode == "casual":
                return self._enforce_concise_response(text, max_sentences=4, max_chars=560)
            if mode in {"analytical", "implementation"}:
                return self._enforce_concise_response(text, max_sentences=6, max_chars=900)
            return self._enforce_concise_response(text, max_sentences=5, max_chars=760)

        if mode == "casual":
            return self._enforce_concise_response(text, max_sentences=2, max_chars=260)
        if mode in {"analytical", "implementation"}:
            return self._enforce_concise_response(text, max_sentences=4, max_chars=520)
        return text

    def _build_ask_user_message(self, mode: str, heuristic_result: Dict[str, Any]) -> str:
        reason = self.policy.summarize_reason(heuristic_result)
        if mode == "implementation":
            return (
                "I can run a deeper implementation analysis with edge cases and ordered steps. "
                f"{reason} Continue?"
            )
        if mode == "brainstorming":
            return (
                "I can run a deeper option analysis with trade-offs and constraints. "
                f"{reason} Continue?"
            )
        return (
            "I can run a deeper analysis with key drivers, risks, and uncertainties. "
            f"{reason} Continue?"
        )

    def _build_thought_data(
        self,
        *,
        query: str,
        mode: str,
        context: list[dict],
        heuristic_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        reason_codes = list(heuristic_result.get("reason_codes") or [])
        return {
            "decision": "ALLOW_ANALYSIS_ONLY",
            "reason_codes": reason_codes,
            "reason_summary": self.policy.summarize_reason(heuristic_result),
            "suggested_tokens": int(heuristic_result.get("suggested_max_tokens", 800)),
            "mode": mode,
            "query_word_count": len((query or "").split()),
            "context_turns_used": min(len(context or []), 6),
            "heuristic": {
                "complexity_score": float(heuristic_result.get("complexity_score", 0.0)),
                "depth_opportunity_score": float(heuristic_result.get("depth_opportunity_score", 0.0)),
                "ambiguity_score": float(heuristic_result.get("ambiguity_score", 0.0)),
                "exploratory_intent": bool(heuristic_result.get("exploratory_intent", False)),
            },
        }

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

    @staticmethod
    def _canonical_social_query(query: str) -> str:
        normalized = InputNormalizer.normalize(query).lower().strip().rstrip(".?!")
        normalized = re.sub(r"\bnova\b", " ", normalized, flags=re.IGNORECASE)
        normalized = re.sub(r"\s+", " ", normalized).strip(" ,")
        return normalized

    def _local_social_result(self, query: str) -> SkillResult | None:
        canonical = self._canonical_social_query(query)
        if not canonical:
            return None

        response = (
            self._GREETING_RESPONSES.get(canonical)
            or self._THANKS_RESPONSES.get(canonical)
            or self._STATUS_RESPONSES.get(canonical)
        )
        if not response:
            return None

        tone_profile = self._current_tone_profile("general")
        shaped = self._shape_response_for_tone(
            response,
            mode="casual",
            tone_profile=tone_profile,
            explicit_depth=False,
        )

        return SkillResult(
            success=True,
            message=shaped,
            data={
                "mode": "casual",
                "style": ResponseStyle.CASUAL.value,
                "tone_profile": tone_profile,
                "speakable_text": shaped,
                "structured_data": {"deterministic_social": True},
            },
            widget_data=None,
            skill=self.name,
        )

    @classmethod
    def _summarize_context_entry(cls, entry: dict) -> tuple[str, str] | None:
        if not isinstance(entry, dict):
            return None

        role = str(entry.get("role") or "").strip().lower()
        if role not in {"user", "assistant"}:
            return None

        content = str(entry.get("content") or "").strip()
        if not content:
            return None

        normalized = re.sub(r"\s+", " ", content).strip()
        if len(normalized) > cls._MAX_CONTEXT_CHARS_PER_TURN:
            normalized = normalized[: cls._MAX_CONTEXT_CHARS_PER_TURN - 3].rstrip() + "..."
        return role, normalized

    def _build_conversational_prompt(
        self,
        query: str,
        *,
        context: Optional[list] = None,
        session_state: Optional[dict] = None,
    ) -> str:
        normalized_query = InputNormalizer.normalize(query)
        recent_lines: list[str] = []
        for entry in list(context or [])[-self._MAX_CONTEXT_TURNS :]:
            summarized = self._summarize_context_entry(entry)
            if summarized is None:
                continue
            role, content = summarized
            label = "User" if role == "user" else "Nova"
            recent_lines.append(f"{label}: {content}")

        hints: list[str] = []
        state = session_state or {}
        active_topic = str(state.get("active_topic") or "").strip()
        if active_topic:
            hints.append(f"Active topic: {active_topic}")
        project_thread = str(state.get("project_thread_active") or "").strip()
        if project_thread:
            hints.append(f"Active project thread: {project_thread}")

        if not recent_lines and not hints:
            return normalized_query

        blocks: list[str] = []
        if hints:
            blocks.append("Session hints:\n" + "\n".join(f"- {hint}" for hint in hints))
        if recent_lines:
            blocks.append("Recent conversation (most recent last):\n" + "\n".join(recent_lines))
        blocks.append(f"Current user message:\n{normalized_query}")
        blocks.append(
            "Respond naturally and use the recent conversation to interpret short follow-ups "
            "unless the message is genuinely too ambiguous."
        )
        return "\n\n".join(blocks)

    @classmethod
    def _is_geopolitical_query(cls, query: str) -> bool:
        q = (query or "").lower()
        return any(k in q for k in cls._GEO_KEYWORDS)

    @classmethod
    def _is_blanket_refusal(cls, text: str) -> bool:
        t = (text or "").lower()
        return any(h in t for h in cls._REFUSAL_HINTS)

    @staticmethod
    def _safe_geopolitical_fallback(query: str) -> str:
        topic = (query or "that topic").strip(".?! ")
        return (
            f"Here is a neutral overview of {topic}: "
            "current reporting indicates active developments and differing claims across sources. "
            "For accuracy, rely on primary outlets and compare multiple reports before drawing conclusions."
        )

    @classmethod
    def _user_requested_depth(cls, query: str) -> bool:
        q = (query or "").lower()
        return any(hint in q for hint in cls._DEPTH_HINTS)

    @staticmethod
    def _enforce_concise_response(text: str, max_sentences: int = 2, max_chars: int = 320) -> str:
        raw = (text or "").strip()
        if not raw:
            return raw
        normalized = re.sub(r"\s+", " ", raw).strip()
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", normalized) if s.strip()]
        concise = " ".join(sentences[:max_sentences]).strip() if sentences else normalized
        concise = re.sub(r"(Summary:\s*){2,}", "Summary: ", concise, flags=re.IGNORECASE).strip()
        if len(concise) > max_chars:
            concise = concise[: max_chars - 3].rstrip() + "..."
        return concise

    async def _run_local_model(
        self,
        query: str,
        *,
        context: Optional[list] = None,
        session_state: Optional[dict] = None,
    ) -> SkillResult | None:
        social = self._local_social_result(query)
        if social is not None:
            return social

        normalized_query = InputNormalizer.normalize(query)
        mode = self._detect_mode(normalized_query)
        style = self.style_router.route(normalized_query)
        explicit_depth = self._user_requested_depth(normalized_query)
        tone_profile = self._current_tone_profile("general")
        system_prompt = self._build_system_prompt(mode, style, tone_profile=tone_profile)
        max_tokens = self._resolve_max_tokens(
            mode,
            tone_profile=tone_profile,
            explicit_depth=explicit_depth,
        )
        prompt = self._build_conversational_prompt(
            normalized_query,
            context=context,
            session_state=session_state,
        )
        session_id = str((session_state or {}).get("session_id") or "").strip() or None

        try:
            text = await asyncio.to_thread(
                generate_chat,
                prompt,
                mode=mode,
                safety_profile="general_chat",
                request_id=f"general_chat:{mode}",
                session_id=session_id,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=0.3,
            )
            text = self._sanitize_response(text or "")
            if not text:
                text = ResponseFormatter.friendly_fallback()
            if self._is_geopolitical_query(normalized_query) and self._is_blanket_refusal(text):
                text = self._safe_geopolitical_fallback(normalized_query)
            text = self._shape_response_for_tone(
                text,
                mode=mode,
                tone_profile=tone_profile,
                explicit_depth=explicit_depth,
            )

            return SkillResult(
                success=True,
                message=text,
                data={"mode": mode, "style": style.value, "tone_profile": tone_profile},
                widget_data=None,
                skill=self.name,
            )
        except Exception:
            return None

    async def handle(self, query: str, context: Optional[list] = None, session_state: Optional[dict] = None) -> SkillResult | None:
        social = self._local_social_result(query)
        if social is not None:
            return social

        # Backward compatible path
        if context is None or session_state is None:
            return await self._run_local_model(query, context=context, session_state=session_state)

        normalized_query = InputNormalizer.normalize(query)
        heuristic_result = self.heuristics.assess(normalized_query, context)
        decision = self.policy.decide(heuristic_result, normalized_query, session_state)
        mode = heuristic_result.get("mode") or self._detect_mode(normalized_query)
        initiative = self.policy.conversational_flags(heuristic_result, normalized_query, session_state)

        if decision == "ASK_USER":
            payload = self.formatter.format_payload(
                self._build_ask_user_message(mode, heuristic_result),
                mode=mode,
            )
            return SkillResult(
                success=True,
                message=payload["user_message"],
                data={
                    "speakable_text": payload["speakable_text"],
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
            thought_data = self._build_thought_data(
                query=normalized_query,
                mode=mode,
                context=context,
                heuristic_result=heuristic_result,
            )
            raw = await asyncio.to_thread(
                self.deepseek.analyze,
                normalized_query,
                context,
                heuristic_result.get("suggested_max_tokens", 800),
                analysis_profile="deep_reason",
            )
            safe = self.safety.filter(raw)
            safe = self.analysis_safety.sanitize(safe)
            if not safe:
                safe = "I could not produce a stable deep analysis right now. Please retry with a narrower question."
            payload = self.formatter.format_payload(safe, mode=mode)
            return SkillResult(
                success=True,
                message=payload["user_message"],
                data={
                    "speakable_text": payload["speakable_text"],
                    "structured_data": payload["structured_data"],
                    "escalation": {"escalated": True, "thought_data": thought_data},
                },
                widget_data=None,
                skill=self.name,
            )

        local = await self._run_local_model(
            normalized_query,
            context=context,
            session_state=session_state,
        )
        if local is None:
            return None

        local_message = self.formatter.with_conversational_initiative(
            local.message,
            mode=mode,
            allow_clarification=initiative.get("allow_clarification", False),
            allow_branch_suggestion=initiative.get("allow_branch_suggestion", False),
            allow_depth_prompt=initiative.get("allow_depth_prompt", False),
        )
        payload = self.formatter.format_payload(local_message, mode=mode)
        local.message = payload["user_message"]
        if initiative.get("allow_clarification"):
            session_state["last_clarification_turn"] = session_state.get("turn_count", 0)
        local.data = {
            "speakable_text": payload["speakable_text"],
            "structured_data": payload["structured_data"],
            "escalation": {
                "escalated": False,
                "reason_codes": list(heuristic_result.get("reason_codes") or []),
            },
        }
        return local




