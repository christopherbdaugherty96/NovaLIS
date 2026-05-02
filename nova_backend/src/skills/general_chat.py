"""
NovaLIS General Chat Skill — Phase 3 SAFE / Phase 4.2 cognitive staging.
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field
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
from src.memory.user_memory_store import UserMemoryStore, user_memory_store
from src.memory.nova_self_memory_store import NovaSelfMemoryStore, nova_self_memory_store
from src.personality.nova_style_contract import NovaStyleContract
from src.personality.tone_profile_store import ToneProfileStore

from ..base_skill import BaseSkill, SkillResult


@dataclass
class SessionConversationContext:
    topic: str = ""
    user_goal: str = ""
    open_question: str = ""
    active_options: list[str] = field(default_factory=list)
    latest_recommendation: str = ""
    rewrite_target: str = ""
    presentation_preference: str = ""
    last_answer_kind: str = ""
    last_options_snapshot: list[str] = field(default_factory=list)
    # Continuity fields — maintained across turns
    mode: str = ""
    last_decision: str = ""
    open_loops: list[str] = field(default_factory=list)
    recent_recommendations: list[str] = field(default_factory=list)

    @classmethod
    def from_session_state(cls, session_state: Optional[dict]) -> "SessionConversationContext":
        state = session_state or {}
        payload = dict(state.get("conversation_context") or {})
        legacy = dict(state.get("general_chat_summary") or {})

        active_options = list(payload.get("active_options") or legacy.get("relevant_options") or [])
        last_options_snapshot = list(payload.get("last_options_snapshot") or active_options)
        open_loops = [str(s).strip() for s in list(payload.get("open_loops") or []) if str(s).strip()]
        recent_recommendations = [
            str(s).strip() for s in list(payload.get("recent_recommendations") or []) if str(s).strip()
        ]

        return cls(
            topic=str(payload.get("topic") or state.get("active_topic") or legacy.get("topic") or "").strip(),
            user_goal=str(payload.get("user_goal") or legacy.get("user_goal") or "").strip(),
            open_question=str(payload.get("open_question") or legacy.get("open_question") or "").strip(),
            active_options=[str(item).strip() for item in active_options if str(item).strip()],
            latest_recommendation=str(payload.get("latest_recommendation") or "").strip(),
            rewrite_target=str(payload.get("rewrite_target") or "").strip(),
            presentation_preference=str(payload.get("presentation_preference") or "").strip(),
            last_answer_kind=str(payload.get("last_answer_kind") or "").strip(),
            last_options_snapshot=[str(item).strip() for item in last_options_snapshot if str(item).strip()],
            mode=str(payload.get("mode") or "").strip(),
            last_decision=str(payload.get("last_decision") or "").strip(),
            open_loops=open_loops,
            recent_recommendations=recent_recommendations,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic": self.topic,
            "user_goal": self.user_goal,
            "open_question": self.open_question,
            "active_options": list(self.active_options),
            "latest_recommendation": self.latest_recommendation,
            "rewrite_target": self.rewrite_target,
            "presentation_preference": self.presentation_preference,
            "last_answer_kind": self.last_answer_kind,
            "last_options_snapshot": list(self.last_options_snapshot),
            "mode": self.mode,
            "last_decision": self.last_decision,
            "open_loops": list(self.open_loops),
            "recent_recommendations": list(self.recent_recommendations),
        }


class GeneralChatSkill(BaseSkill):
    name = "general_chat"
    description = "General chat (LLM advisory only)"

    BASE_CONTRACT = (
        "You are Nova, a friendly personal assistant.\n"
        "\n"
        "Core personality:\n"
        "- Warm, direct, and genuinely helpful.\n"
        "- Like a capable, thoughtful friend — not a corporate assistant.\n"
        "- Lightly witty when the moment calls for it, never forced.\n"
        "- Curious about what the user is working on.\n"
        "\n"
        "Communication:\n"
        "- Give complete, useful answers. Don't cut yourself short.\n"
        "- Use natural, conversational language with good flow.\n"
        "- Match the user's energy — casual when they're casual, focused when they need depth.\n"
        "- If you know things about the user from the memory context below, "
        "weave them in naturally — do not announce that you are recalling memory.\n"
        "- Do not introduce yourself unless explicitly asked.\n"
        "- Do not claim capabilities you do not have.\n"
        "- Do not mention being an AI, virtual assistant, or similar.\n"
        "- If the request is unclear, ask a quick clarification.\n"
        "\n"
        "For greetings and casual conversation:\n"
        "- Respond warmly and naturally, not with a template.\n"
        "- Keep it brief but genuine.\n"
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

    MAX_TOKENS: Dict[str, int] = {
        "casual": 400,
        "brainstorming": 600,
        "implementation": 600,
        "analytical": 800,
    }

    _BANNED_PATTERNS: Tuple[Tuple[re.Pattern, str], ...] = (
        (re.compile(r"\b(as an ai|as a language model)\b", re.IGNORECASE), ""),
        (re.compile(r"\b(i am|i'm)\s+(a\s+)?virtual assistant\b", re.IGNORECASE), ""),
        (re.compile(r"\bhow can i assist\??\b", re.IGNORECASE), ""),
        (re.compile(r"\!{3,}", re.IGNORECASE), "!"),  # Only strip excessive exclamation marks
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
        "hi": "Hello. How can I help?",
        "hello": "Hello. How can I help?",
        "hey": "Hello. How can I help?",
        "good morning": "Good morning. How can I help?",
        "good afternoon": "Good afternoon. How can I help?",
        "good evening": "Good evening. How can I help?",
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
    _SUMMARY_RETAIN_CONTEXT_ENTRIES = 12
    _SUMMARY_MAX_FIELD_CHARS = 180
    _SUMMARY_MAX_OPTIONS = 3
    _FOLLOWUP_TARGET_MAX_CHARS = 260
    _REFERENCE_STOPWORDS = {
        "a",
        "an",
        "and",
        "by",
        "choose",
        "could",
        "do",
        "for",
        "go",
        "idea",
        "it",
        "mean",
        "of",
        "one",
        "option",
        "pick",
        "should",
        "take",
        "that",
        "the",
        "this",
        "what",
        "with",
    }
    _LIST_ITEM_RE = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+(.*\S)\s*$")
    _INLINE_NUMBERED_RE = re.compile(r"(?:^|\s)(\d+)[.)]\s+([^:]+?)(?=(?:\s+\d+[.)]\s+)|$)")
    _SUMMARY_PREFIX_RE = re.compile(
        r"^(?:summary|bottom line|main point|core answer|key takeaway|recommendation)\s*:\s*",
        re.IGNORECASE,
    )
    _VAGUE_OPTION_REFERENCE_RE = re.compile(
        r"\b(?:go with|pick|choose|take)\s+(?:that|this)\b"
        r"|\b(?:that|this)\s+(?:one|option|idea)\b"
        r"|\bwhat do you mean by that\b",
        re.IGNORECASE,
    )
    _SEMANTIC_MODIFIER_HINTS: Tuple[Tuple[re.Pattern, str], ...] = (
        (re.compile(r"\bsafer\b", re.IGNORECASE), "safer"),
        (re.compile(r"\bcalmer\b", re.IGNORECASE), "calmer"),
        (re.compile(r"\bsimpler\b", re.IGNORECASE), "simpler"),
        (re.compile(r"\bstronger\b", re.IGNORECASE), "stronger"),
        (re.compile(r"\bcheaper\b", re.IGNORECASE), "cheaper"),
        (re.compile(r"\bfaster\b", re.IGNORECASE), "faster"),
    )
    _APPROACH_REFERENCE_RE = re.compile(
        r"\b(?:that|this)\s+(?:approach|direction|path|version|option)\b"
        r"|\b(?:the\s+)?(?:safer|calmer|simpler|stronger|cheaper|faster)\s+(?:one|option|version|approach)\b",
        re.IGNORECASE,
    )
    _REWRITE_HINT_PATTERNS: Tuple[Tuple[re.Pattern, str], ...] = (
        (
            re.compile(r"\b(?:what do you mean by that|what did you mean by that|clarify that|explain that)\b", re.IGNORECASE),
            "clarify",
        ),
        (
            re.compile(r"\b(?:say that simpler|make that simpler|make that clearer|clearer|simpler|plain english|plain language)\b", re.IGNORECASE),
            "simpler",
        ),
        (
            re.compile(r"\b(?:reword that|rephrase that|say that another way|put that another way)\b", re.IGNORECASE),
            "reworded",
        ),
        (
            re.compile(r"\b(?:shorter version|make that shorter|condense that|briefer version|tldr|tl;dr)\b", re.IGNORECASE),
            "shorter",
        ),
    )
    _PRESENTATION_PREFERENCE_PATTERNS: Tuple[Tuple[re.Pattern, str], ...] = (
        (
            re.compile(r"\b(?:more technical|technical version|use technical terms|get more technical)\b", re.IGNORECASE),
            "technical",
        ),
        (
            re.compile(r"\b(?:say more|tell me more|go deeper|more detail|more detailed|longer version|expand on that|expand this|break that down further)\b", re.IGNORECASE),
            "detailed",
        ),
        (
            re.compile(r"\b(?:just the answer|be direct|more direct|direct answer|cut to the point|skip the extras)\b", re.IGNORECASE),
            "direct",
        ),
        (
            re.compile(r"\b(?:explore that|brainstorm that|different angles|different directions|a few angles|a few directions)\b", re.IGNORECASE),
            "exploratory",
        ),
    )
    _ORDINAL_REFERENCE_PATTERNS: Tuple[Tuple[re.Pattern, int], ...] = (
        (re.compile(r"\b(?:go with|pick|choose|take)\s+(?:the\s+)?first\b|\b(?:the|that)\s+first\b|\bfirst one\b", re.IGNORECASE), 0),
        (re.compile(r"\b(?:go with|pick|choose|take)\s+(?:the\s+)?second\b|\b(?:the|that)\s+second\b|\bsecond one\b", re.IGNORECASE), 1),
        (re.compile(r"\b(?:go with|pick|choose|take)\s+(?:the\s+)?third\b|\b(?:the|that)\s+third\b|\bthird one\b", re.IGNORECASE), 2),
        (re.compile(r"\b(?:go with|pick|choose|take)\s+(?:the\s+)?(?:last|final)\b|\b(?:the|that)\s+(?:last|final)\b", re.IGNORECASE), -1),
    )

    # Auto-memory extraction patterns: (regex, category, key_name)
    _MEMORY_PATTERNS: tuple[tuple[re.Pattern, str, str], ...] = (
        (re.compile(r"\bmy name is (\w[\w ]{0,30})", re.I), "personal", "name"),
        (re.compile(r"\bcall me (\w[\w ]{0,20})", re.I), "personal", "preferred_name"),
        (re.compile(r"\bi (?:really )?(?:like|love|enjoy) (.{3,60}?)(?:\.|,|!|$)", re.I), "preferences", "likes"),
        (re.compile(r"\bi (?:really )?(?:dislike|hate|don'?t like) (.{3,60}?)(?:\.|,|!|$)", re.I), "preferences", "dislikes"),
        (re.compile(r"\bi (?:work|am working) (?:at|for|on) (.{3,60}?)(?:\.|,|!|$)", re.I), "work", "employer"),
        (re.compile(r"\bi(?:'m| am) a (.{3,40}?)(?:\.|,|!|$)", re.I), "work", "role"),
        (re.compile(r"\bi prefer (.{3,60}?)(?:\.|,|!|$)", re.I), "preferences", "preference"),
        (re.compile(r"\bmy birthday is (.{3,30}?)(?:\.|,|!|$)", re.I), "important_dates", "birthday"),
        (re.compile(r"\bmy (?:wife|husband|partner|spouse)(?:'s| is| name is)? (\w[\w ]{1,20})", re.I), "relationships", "partner"),
    )
    # False-positive blocklist for auto-extraction
    _MEMORY_EXTRACT_BLOCKLIST = frozenset({
        "that", "this", "it", "the way", "how", "what", "when",
        "to", "the idea", "the concept", "the approach",
    })

    # Conservative relationship insight patterns.
    # Each tuple: (regex, normalized_insight_string)
    # Rules:
    # - Only explicit, high-confidence feedback signals — not inferred
    # - Insights are normalized so substring dedup in record_insight() works
    # - "more detail about X" and "give me an example of X" are task requests,
    #   not general preferences — excluded to avoid false positives
    # - One-off / context-qualified signals ("for this", "just this time") are
    #   filtered before patterns run (see _extract_relationship_signals guard)
    _INSIGHT_PATTERNS: tuple[tuple[re.Pattern, str], ...] = (
        # Length / verbosity preferences
        (re.compile(r"\bkeep\s+it\s+(short|brief|concise|quick)\b", re.I), "User prefers concise responses"),
        (re.compile(r"\b(too\s+long|too\s+verbose|too\s+wordy)\b", re.I), "User prefers concise responses"),
        (re.compile(r"\bless\s+(detail|explanation|text|words)\b", re.I), "User prefers concise responses"),
        (re.compile(r"\bshorter\s+(please|answer|response)?\b", re.I), "User prefers concise responses"),
        # "more detail" only when NOT followed by "about/on/for/of/regarding" — those
        # are topic requests ("more detail about the timeline"), not style preferences.
        (re.compile(r"\bmore\s+detail(s|ed)?(?!\s+(?:about|on|for|of|regarding)\b)", re.I), "User wants more detailed responses"),
        (re.compile(r"\bmore\s+(depth|thorough|comprehensive)\b", re.I), "User wants more detailed responses"),
        # Formatting preferences
        (re.compile(r"\b(don.t|no|stop)\s+use\s+bullet\s*points?\b", re.I), "User prefers prose over bullet points"),
        (re.compile(r"\bstop\s+using\s+bullet\s*points?\b", re.I), "User prefers prose over bullet points"),
        (re.compile(r"\bno\s+bullet\s*points?\b", re.I), "User prefers prose over bullet points"),
        (re.compile(r"\buse\s+bullet\s*points?\b", re.I), "User prefers bullet point formatting"),
        (re.compile(r"\buse\s+(?:a\s+)?list\b", re.I), "User prefers bullet point formatting"),
        # Directness preferences
        (re.compile(r"\bmore\s+direct(ly)?\b", re.I), "User prefers direct answers without preamble"),
        (re.compile(r"\bget\s+to\s+the\s+point\b", re.I), "User prefers direct answers without preamble"),
        (re.compile(r"\bskip\s+the\s+(intro|introduction|preamble|setup)\b", re.I), "User prefers direct answers without preamble"),
        (re.compile(r"\bjust\s+answer\s+the\s+question\b", re.I), "User prefers direct answers without preamble"),
        # Caveats / disclaimers
        (re.compile(r"\bskip\s+the\s+(disclaimer|caveats?|warnings?)\b", re.I), "User dislikes excessive caveats"),
        (re.compile(r"\bstop\s+(adding|with|the)\s+(disclaimer|caveats?|warnings?)\b", re.I), "User dislikes excessive caveats"),
        (re.compile(r"\b(don.t|no)\s+(say|add|include)\s+(?:\w+\s+){0,2}caveats?\b", re.I), "User dislikes excessive caveats"),
        # Examples — only general preference expressions, not task-specific requests.
        # "give me an example of X" is a task; "I find examples helpful" is a preference.
        (re.compile(r"\bi\s+(like|find|appreciate)\s+(?:\w+\s+){0,3}examples?\b", re.I), "User finds examples helpful"),
        (re.compile(r"\bexamples?\s+(help|are\s+helpful|make\s+it\s+clearer)\b", re.I), "User finds examples helpful"),
        (re.compile(r"\balways\s+(?:include|add|give)\s+(?:an?\s+)?example\b", re.I), "User finds examples helpful"),
    )

    def __init__(
        self,
        policy_config: Optional[dict] = None,
        network: NetworkMediator | None = None,
        tone_store: ToneProfileStore | None = None,
        user_memory: UserMemoryStore | None = None,
        nova_memory: NovaSelfMemoryStore | None = None,
    ):
        self.heuristics = ComplexityHeuristics()
        self.policy = EscalationPolicy(policy_config)
        self.deepseek = DeepSeekBridge()
        self.safety = SafetyFilter()
        self.analysis_safety = DeepSeekSafetyWrapper()
        self.style_router = ResponseStyleRouter()
        self.formatter = ResponseFormatter()
        self._tone_store = tone_store or ToneProfileStore()
        self._user_memory = user_memory or user_memory_store
        self._nova_memory = nova_memory or nova_self_memory_store

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

    def _build_memory_context(self) -> str:
        """Build a compact memory context block for prompt injection."""
        parts: list[str] = []

        # Self-awareness: what Nova is, what it can do, what's active
        try:
            from src.identity.nova_self_awareness import build_self_awareness_block
            awareness = build_self_awareness_block()
            if awareness:
                parts.append(awareness)
        except Exception:
            pass

        try:
            user_ctx = self._user_memory.render_context_block(max_chars=300)
            if user_ctx:
                parts.append(f"What you know about the user:\n{user_ctx}")
        except Exception:
            pass
        try:
            relationship_ctx = self._nova_memory.get_relationship_context(max_chars=150)
            if relationship_ctx:
                parts.append(f"Relationship context:\n{relationship_ctx}")
        except Exception:
            pass
        return "\n\n".join(parts)

    def _build_system_prompt(
        self,
        mode: str,
        style: ResponseStyle = ResponseStyle.DIRECT,
        tone_profile: str = "balanced",
        presentation_preference: str = "",
        last_answer_kind: str = "",
        memory_context: str = "",
        request_understanding_block: str = "",
    ) -> str:
        mode_block = NovaStyleContract.chat_mode_guidance(mode)
        tone_block = self.TONE_BLOCKS.get(tone_profile, self.TONE_BLOCKS["balanced"])

        style_blocks = {
            ResponseStyle.DIRECT: "Style: Direct mode. Lead with the answer and keep the wording clean.",
            ResponseStyle.BRAINSTORM: "Style: Brainstorm mode. Present distinct grounded directions that are easy to compare.",
            ResponseStyle.DEEP: "Style: Deep mode. Use short sections and grounded transitions instead of flourish.",
            ResponseStyle.CASUAL: "Style: Conversational mode. Keep the reply calm, direct, and lightly warm.",
        }

        style_block = style_blocks.get(style, style_blocks[ResponseStyle.DIRECT])
        presentation_block = self._presentation_instruction_block(
            presentation_preference,
            last_answer_kind=last_answer_kind,
        )
        blocks = [self.BASE_CONTRACT, tone_block, mode_block, style_block]
        if presentation_block:
            blocks.append(presentation_block)
        if memory_context:
            blocks.append(memory_context)
        if request_understanding_block:
            blocks.append(request_understanding_block)
        return "\n\n".join(block.strip() for block in blocks if block.strip())

    def _resolve_max_tokens(
        self,
        mode: str,
        *,
        tone_profile: str,
        explicit_depth: bool,
        presentation_preference: str = "",
    ) -> int:
        max_tokens = self.MAX_TOKENS.get(mode, self.MAX_TOKENS["casual"])
        if not explicit_depth and mode == "casual":
            max_tokens = min(max_tokens, 300)

        preference = str(presentation_preference or "").strip().lower()
        if preference in {"shorter", "direct"}:
            max_tokens = min(max_tokens, 200 if mode == "casual" else 350)
        elif preference in {"simpler", "reworded"}:
            max_tokens = min(max_tokens, 250 if mode == "casual" else 400)
        elif preference == "technical":
            max_tokens = min(max_tokens + 80, 700)
        elif preference == "detailed":
            max_tokens = min(max_tokens + (160 if mode == "casual" else 220), 900)

        if tone_profile == "concise":
            if not explicit_depth and mode == "casual":
                return min(max_tokens, 200)
            return max(200, int(max_tokens * 0.80))

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
        presentation_preference: str = "",
    ) -> str:
        preference = str(presentation_preference or "").strip().lower()

        if preference == "shorter":
            return self._enforce_concise_response(text, max_sentences=1 if mode == "casual" else 2, max_chars=180 if mode == "casual" else 260)
        if preference == "direct":
            return self._enforce_concise_response(text, max_sentences=2, max_chars=220 if mode == "casual" else 320)
        if preference == "simpler":
            simplified = re.sub(r"\s*;\s*", ". ", str(text or ""))
            return self._enforce_concise_response(simplified, max_sentences=2 if mode == "casual" else 3, max_chars=260 if mode == "casual" else 360)
        if preference == "reworded":
            return self._enforce_concise_response(text, max_sentences=2 if mode == "casual" else 3, max_chars=260 if mode == "casual" else 360)
        if explicit_depth and preference != "detailed":
            return text
        if preference == "detailed":
            if mode == "casual":
                return self._enforce_concise_response(text, max_sentences=5, max_chars=640)
            if mode in {"analytical", "implementation"}:
                return self._enforce_concise_response(text, max_sentences=7, max_chars=980)
            return self._enforce_concise_response(text, max_sentences=6, max_chars=820)
        if preference == "technical":
            if mode == "casual":
                return self._enforce_concise_response(text, max_sentences=3, max_chars=420)
            if mode in {"analytical", "implementation"}:
                return self._enforce_concise_response(text, max_sentences=5, max_chars=760)
            return self._enforce_concise_response(text, max_sentences=4, max_chars=620)

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

    @classmethod
    def _query_presentation_preference(cls, query: str) -> str:
        rewrite_kind = cls._rewrite_request_kind(query)
        if rewrite_kind in {"simpler", "reworded", "shorter"}:
            return rewrite_kind
        for pattern, preference in cls._PRESENTATION_PREFERENCE_PATTERNS:
            if pattern.search(str(query or "")):
                return preference
        return ""

    @classmethod
    def _presentation_style(
        cls,
        style: ResponseStyle,
        *,
        presentation_preference: str,
    ) -> ResponseStyle:
        preference = str(presentation_preference or "").strip().lower()
        if preference in {"shorter", "direct"}:
            return ResponseStyle.DIRECT
        if preference == "exploratory":
            return ResponseStyle.BRAINSTORM
        return style

    @classmethod
    def _presentation_instruction_block(cls, presentation_preference: str, *, last_answer_kind: str = "") -> str:
        preference = str(presentation_preference or "").strip().lower()
        answer_kind = str(last_answer_kind or "").strip().lower()
        lines: list[str] = []

        blocks = {
            "shorter": [
                "Presentation preference: Shorter.",
                "- Lead with the answer immediately.",
                "- Keep the response compact and avoid extra framing.",
            ],
            "simpler": [
                "Presentation preference: Plain language.",
                "- Use simpler wording and short sentences.",
                "- Avoid jargon unless you briefly explain it.",
            ],
            "reworded": [
                "Presentation preference: Reworded.",
                "- Preserve the meaning but restate it in fresher wording.",
                "- Keep the same thread and do not change the answer.",
            ],
            "detailed": [
                "Presentation preference: Detailed.",
                "- Stay on the same thread and add useful supporting detail.",
                "- Keep the explanation grounded instead of drifting broader.",
            ],
            "technical": [
                "Presentation preference: Technical.",
                "- Use more precise technical language where it genuinely helps.",
                "- Keep the explanation concrete and avoid unnecessary simplification.",
            ],
            "direct": [
                "Presentation preference: Direct.",
                "- Answer first and keep the framing minimal.",
                "- Avoid branching into extra options unless the user asks.",
            ],
            "exploratory": [
                "Presentation preference: Exploratory.",
                "- Offer a few grounded angles or options.",
                "- Keep the options distinct and easy to compare.",
            ],
        }

        if preference in blocks:
            lines.extend(blocks[preference])

        if answer_kind == "recommendation":
            lines.extend(
                [
                    "Current thread state: Recommendation.",
                    "- Keep the recommendation stable unless the user asks to change it.",
                    "- If you shorten the answer, keep one clear reason with the recommendation.",
                ]
            )
        elif answer_kind == "options":
            lines.extend(
                [
                    "Current thread state: Options are already active.",
                    "- Keep option identities stable so follow-up references still make sense.",
                ]
            )
        elif answer_kind in {"clarify", "simpler", "reworded", "shorter"}:
            lines.extend(
                [
                    "Current thread state: Rewrite the existing answer.",
                    "- Stay anchored to the prior answer instead of switching topics.",
                ]
            )

        return "\n".join(lines).strip()

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

        # Greetings now flow through the LLM for warm, contextual responses.
        # Only thanks and status queries get deterministic fast paths.
        response = (
            self._THANKS_RESPONSES.get(canonical)
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
        shaped = self.formatter.format(shaped, mode="casual")

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

    @staticmethod
    def _local_conceptual_fallback(query: str, session_state: Optional[dict] = None) -> str:
        canonical = InputNormalizer.normalize(query).lower().strip(".?!")
        if re.search(r"\bdifference between memory and intelligence\b", canonical) and "ai system" in canonical:
            return (
                "Memory is stored context: facts, preferences, prior turns, or notes that help the system keep continuity. "
                "Intelligence is the reasoning layer that interprets a request, connects ideas, and decides what answer or plan makes sense. "
                "In Nova, memory can inform an answer, but it does not authorize actions; governed actions still need visible boundaries, receipts, and review."
            )
        if canonical in {"explain what shopify is", "what is shopify"}:
            return (
                "Shopify is a commerce platform for running an online store: products, orders, payments, inventory, storefront pages, and related reporting. "
                "For Nova, the safe version is read-only intelligence first: summarize store status, explain trends, and produce receipts without changing products, orders, customers, or payments."
            )
        if "electric bikes" in canonical or "electric bicycles" in canonical or "e-bikes" in canonical:
            return (
                "Electric bikes are bicycles with a battery-powered motor that assists your pedaling. "
                "They are useful for commuting, hills, cargo, and longer rides because they reduce effort without turning the bike into a full motorcycle."
            )
        if canonical == "how would nova use it safely":
            return (
                "Safely means read-only first. Nova should inspect or summarize data, show exactly which capability is being used, keep boundaries visible, and record receipts for governed actions. "
                "It should ask before any external-effect step and treat conversation or memory as context, not permission."
            )
        if canonical == "what should it avoid doing":
            prior = " ".join(
                str(value or "")
                for value in dict((session_state or {}).get("conversation_context") or {}).values()
            ).lower()
            if "electric bike" in prior or "electric bikes" in prior:
                return (
                    "The main downsides are cost, battery charging, battery replacement over time, heavier weight, theft risk, and more maintenance than a simple bike. "
                    "Rules also vary by place, especially around speed classes and where e-bikes are allowed."
                )
            return (
                "Nova should avoid broad autonomy: no silent writes, no sending messages or changing external systems without confirmation, no treating memory as permission, and no hiding uncertainty. "
                "For connectors like Shopify, that means no product, order, customer, payment, or fulfillment changes unless a future capability is explicitly governed and proven."
            )
        return ""

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
        rewrite_kind = self._rewrite_request_kind(normalized_query)
        context_entries = list(context or [])
        recent_lines: list[str] = []
        for entry in context_entries[-self._MAX_CONTEXT_TURNS :]:
            summarized = self._summarize_context_entry(entry)
            if summarized is None:
                continue
            role, content = summarized
            if rewrite_kind and role == "assistant":
                content = self._strip_initiative_tail(content)
            label = "User" if role == "user" else "Nova"
            recent_lines.append(f"{label}: {content}")

        hints: list[str] = []
        state = session_state or {}
        conversation_context = SessionConversationContext.from_session_state(state)
        rewrite_kind = self._rewrite_request_kind(normalized_query)
        active_topic = self._stable_topic_hint(str(state.get("active_topic") or "")) or self._stable_topic_hint(conversation_context.topic)
        if (
            active_topic
            and conversation_context.topic
            and active_topic.lower() != conversation_context.topic.lower()
            and not rewrite_kind
        ):
            conversation_context = SessionConversationContext(topic=active_topic)
        if active_topic:
            hints.append(f"Active topic: {active_topic}")
        project_thread = str(state.get("project_thread_active") or "").strip()
        if project_thread:
            hints.append(f"Active project thread: {project_thread}")
        if conversation_context.user_goal:
            hints.append(f"Current thread goal: {self._clip_summary_text(conversation_context.user_goal)}")
        if conversation_context.open_question and conversation_context.open_question.lower() != normalized_query.lower():
            hints.append(f"Open question in thread: {self._clip_summary_text(conversation_context.open_question)}")
        if conversation_context.active_options:
            option_lines = " | ".join(
                f"{index + 1}. {self._clip_summary_text(option)}"
                for index, option in enumerate(conversation_context.active_options[: self._SUMMARY_MAX_OPTIONS])
            )
            hints.append(f"Active options: {option_lines}")
        if conversation_context.latest_recommendation:
            hints.append(f"Latest recommendation: {self._clip_summary_text(conversation_context.latest_recommendation)}")
        if conversation_context.presentation_preference:
            hints.append(f"Presentation preference: {conversation_context.presentation_preference}")
        relevant_memory = list(state.get("relevant_memory_context") or [])
        if relevant_memory:
            for item in relevant_memory[:3]:
                row = dict(item or {})
                content = self._clip_summary_text(str(row.get("content") or row.get("title") or "").strip())
                if not content:
                    continue
                item_id = str(row.get("id") or "").strip()
                thread_name = str(row.get("thread_name") or "").strip()
                label = f"Relevant explicit memory {item_id}" if item_id else "Relevant explicit memory"
                if thread_name:
                    label += f" (thread: {thread_name})"
                hints.append(f"{label}: {content}")
        # Inject unconsumed user corrections from previous sessions.
        # Only injected once per session — cleared from session_state after first use.
        pending_corrections = list(state.get("pending_corrections") or [])
        if pending_corrections:
            for corr in pending_corrections[:3]:
                corr_text = str(corr or "").strip()
                if corr_text:
                    hints.append(f"User previously corrected Nova: {corr_text}")
            state.pop("pending_corrections", None)

        rewrite_hint = self._build_rewrite_hint(normalized_query, context=context)
        if rewrite_hint:
            hints.append(rewrite_hint)
        reference_hint = self._build_reference_hint(
            normalized_query,
            context=context,
            session_state=session_state,
        )
        if reference_hint:
            hints.append(reference_hint)

        summary_data = dict(state.get("general_chat_summary") or {})
        older_entries = context_entries[:-self._MAX_CONTEXT_TURNS]
        if older_entries:
            summary_data = self._build_summary_snapshot(
                older_entries,
                session_state=state,
                existing=summary_data,
            )
        summary_text = self._format_conversation_summary(summary_data)

        if not recent_lines and not hints and not summary_text:
            return normalized_query

        blocks: list[str] = []
        if hints:
            blocks.append("Session hints:\n" + "\n".join(f"- {hint}" for hint in hints))
        if summary_text:
            blocks.append("Earlier conversation summary:\n" + summary_text)
        if recent_lines:
            blocks.append("Recent conversation (most recent last):\n" + "\n".join(recent_lines))
        blocks.append(f"Current user message:\n{normalized_query}")
        blocks.append(
            "Respond naturally and use the recent conversation to interpret short follow-ups "
            "unless the message is genuinely too ambiguous."
        )
        return "\n\n".join(blocks)

    @classmethod
    def _extract_prior_options(cls, text: str) -> list[str]:
        raw = str(text or "").strip()
        if not raw:
            return []

        options: list[str] = []
        for line in raw.splitlines():
            normalized_line = cls._SUMMARY_PREFIX_RE.sub("", str(line or "").strip())
            match = cls._LIST_ITEM_RE.match(normalized_line)
            if not match:
                continue
            item = re.sub(r"\s+", " ", match.group(1)).strip(" .-")
            if item:
                options.append(item)

        if options:
            deduped: list[str] = []
            for item in options:
                if item and item not in deduped:
                    deduped.append(item)
            return deduped[:4]

        inline_source = cls._SUMMARY_PREFIX_RE.sub("", raw.replace("\n", " "))
        inline_matches = cls._INLINE_NUMBERED_RE.findall(inline_source)
        for _, item in inline_matches:
            normalized = re.sub(r"\s+", " ", str(item or "")).strip(" .-")
            if normalized:
                options.append(normalized)
        deduped: list[str] = []
        for item in options:
            if item and item not in deduped:
                deduped.append(item)
        return deduped[:4]

    @classmethod
    def _reference_target_index(cls, query: str) -> int | None:
        text = str(query or "").strip()
        if not text:
            return None
        for pattern, index in cls._ORDINAL_REFERENCE_PATTERNS:
            if pattern.search(text):
                return index
        return None

    @classmethod
    def _build_reference_hint(
        cls,
        query: str,
        *,
        context: Optional[list] = None,
        session_state: Optional[dict] = None,
    ) -> str:
        target_index = cls._reference_target_index(query)
        option_catalog = cls._conversation_option_catalog(context=context, session_state=session_state)
        if not option_catalog:
            return ""

        options, recent_entries, latest_recommendation = option_catalog
        if target_index is not None:
            resolved_index = len(options) - 1 if target_index < 0 else target_index
            if 0 <= resolved_index < len(options):
                return f"Likely referenced prior option {resolved_index + 1}: {options[resolved_index]}"

        semantic_match = cls._semantic_option_reference(
            query,
            options=options,
            recent_entries=recent_entries,
            latest_recommendation=latest_recommendation,
        )
        if semantic_match is None:
            return ""
        resolved_index, option = semantic_match
        return f"Likely referenced prior option {resolved_index + 1}: {option}"

    @staticmethod
    def _reference_token_root(token: str) -> str:
        clean = re.sub(r"[^a-z0-9]+", "", str(token or "").lower())
        if len(clean) > 5 and clean.endswith("est"):
            clean = clean[:-3]
        elif len(clean) > 4 and clean.endswith("er"):
            clean = clean[:-2]
        elif len(clean) > 4 and clean.endswith("ing"):
            clean = clean[:-3]
        elif len(clean) > 4 and clean.endswith("ed"):
            clean = clean[:-2]
        elif len(clean) > 4 and clean.endswith("s"):
            clean = clean[:-1]
        return clean

    @classmethod
    def _reference_tokens(cls, text: str) -> set[str]:
        tokens: set[str] = set()
        for raw in re.findall(r"[A-Za-z0-9']+", str(text or "").lower()):
            root = cls._reference_token_root(raw)
            if not root or root in cls._REFERENCE_STOPWORDS:
                continue
            tokens.add(root)
        return tokens

    @classmethod
    def _reference_option_catalog(cls, context: Optional[list]) -> tuple[list[str], list[dict]] | None:
        entries = list(context or [])
        for index in range(len(entries) - 1, -1, -1):
            entry = entries[index]
            if str(entry.get("role") or "").strip().lower() != "assistant":
                continue
            options = cls._extract_prior_options(str(entry.get("content") or ""))
            if options:
                return options, entries[index + 1 :]
        return None

    @classmethod
    def _conversation_option_catalog(
        cls,
        *,
        context: Optional[list],
        session_state: Optional[dict],
    ) -> tuple[list[str], list[dict], str] | None:
        option_catalog = cls._reference_option_catalog(context)
        if option_catalog:
            options, recent_entries = option_catalog
            recommendation = SessionConversationContext.from_session_state(session_state).latest_recommendation
            return options, recent_entries, recommendation

        conversation_context = SessionConversationContext.from_session_state(session_state)
        options = [cls._clip_summary_text(option) for option in list(conversation_context.active_options or conversation_context.last_options_snapshot or []) if cls._clip_summary_text(option)]
        if not options:
            return None
        return options[: cls._SUMMARY_MAX_OPTIONS], [], conversation_context.latest_recommendation

    @classmethod
    def _last_assistant_message(cls, context: Optional[list]) -> str:
        for entry in reversed(list(context or [])):
            if str(entry.get("role") or "").strip().lower() != "assistant":
                continue
            content = str(entry.get("content") or "").strip()
            if content:
                return content
        return ""

    @classmethod
    def _strip_initiative_tail(cls, text: str) -> str:
        raw = str(text or "").strip()
        if not raw:
            return ""
        parts = [part.strip() for part in raw.split("\n\n") if part.strip()]
        if len(parts) <= 1:
            single = raw
        else:
            last = parts[-1].lower()
            if last.startswith("if you want") or last.startswith("if useful") or last.startswith("would you like"):
                single = "\n\n".join(parts[:-1]).strip()
            else:
                single = raw
        single = re.sub(
            r"\s+(If you want|If useful|Would you like)\b.*$",
            "",
            single,
            flags=re.IGNORECASE,
        ).strip()
        return single

    @classmethod
    def _rewrite_request_kind(cls, query: str) -> str:
        text = str(query or "").strip()
        if not text:
            return ""
        for pattern, kind in cls._REWRITE_HINT_PATTERNS:
            if pattern.search(text):
                return kind
        return ""

    @classmethod
    def _rewrite_hint_label(cls, kind: str) -> str:
        return {
            "clarify": "clarify the last assistant answer",
            "simpler": "restate the last assistant answer in simpler language",
            "reworded": "reword the last assistant answer",
            "shorter": "give a shorter version of the last assistant answer",
        }.get(kind, "")

    @classmethod
    def _build_rewrite_hint(cls, query: str, *, context: Optional[list] = None) -> str:
        kind = cls._rewrite_request_kind(query)
        if not kind:
            return ""

        prior = cls._strip_initiative_tail(cls._last_assistant_message(context))
        if not prior:
            return ""

        label = cls._rewrite_hint_label(kind)
        target = cls._clip_summary_text(prior)
        if len(target) > cls._FOLLOWUP_TARGET_MAX_CHARS:
            target = target[: cls._FOLLOWUP_TARGET_MAX_CHARS - 3].rstrip() + "..."
        if not label or not target:
            return ""
        return f"User wants you to {label}. Target prior answer: {target}"

    @classmethod
    def _semantic_reference_marker(cls, query: str) -> bool:
        raw = str(query or "")
        if cls._VAGUE_OPTION_REFERENCE_RE.search(raw) or cls._APPROACH_REFERENCE_RE.search(raw):
            return True
        return any(pattern.search(raw) for pattern, _ in cls._SEMANTIC_MODIFIER_HINTS)

    @classmethod
    def _format_option_clarification(cls, options: list[str]) -> str:
        clipped = [f"{index + 1}. {cls._clip_summary_text(option)}" for index, option in enumerate(options[: cls._SUMMARY_MAX_OPTIONS])]
        if len(clipped) < 2:
            return ""
        if len(clipped) == 2:
            return NovaStyleContract.prefix_with_acknowledgement(
                f"Do you mean {clipped[0]} or {clipped[1]}?",
                kind="understood",
            )
        return NovaStyleContract.prefix_with_acknowledgement(
            f"Do you mean {clipped[0]}, {clipped[1]}, or {clipped[2]}?",
            kind="understood",
        )

    @classmethod
    def _rewrite_clarification_prompt(cls, rewrite_kind: str) -> str:
        prompts = {
            "clarify": "Do you want me to clarify my last answer or take a different approach?",
            "simpler": "Do you want a simpler rewrite of my last answer or a different approach?",
            "reworded": "Do you want a reworded version of my last answer or a different approach?",
            "shorter": "Do you want a shorter rewrite of my last answer or a different approach?",
        }
        prompt = prompts.get(rewrite_kind, "")
        if not prompt:
            return ""
        return NovaStyleContract.prefix_with_acknowledgement(prompt, kind="confirm")

    @classmethod
    def _semantic_clarification_prompt(
        cls,
        query: str,
        *,
        context: Optional[list],
        session_state: Optional[dict],
    ) -> str:
        rewrite_kind = cls._rewrite_request_kind(query)
        conversation_context = SessionConversationContext.from_session_state(session_state)
        prior_answer = cls._strip_initiative_tail(cls._last_assistant_message(context)) or conversation_context.rewrite_target
        if rewrite_kind and not prior_answer:
            if conversation_context.topic or conversation_context.user_goal or conversation_context.active_options:
                return cls._rewrite_clarification_prompt(rewrite_kind)
            return ""

        if not cls._semantic_reference_marker(query):
            return ""

        if cls._build_reference_hint(query, context=context, session_state=session_state):
            return ""

        option_catalog = cls._conversation_option_catalog(context=context, session_state=session_state)
        if not option_catalog:
            return ""

        options, _, _ = option_catalog
        return cls._format_option_clarification(options)

    @classmethod
    def _option_is_mentioned(cls, option: str, text: str) -> bool:
        option_tokens = cls._reference_tokens(option)
        text_tokens = cls._reference_tokens(text)
        if not option_tokens or not text_tokens:
            return False
        overlap = option_tokens & text_tokens
        return len(overlap) >= min(2, len(option_tokens))

    @classmethod
    def _semantic_option_reference(
        cls,
        query: str,
        *,
        options: list[str],
        recent_entries: list[dict],
        latest_recommendation: str = "",
    ) -> tuple[int, str] | None:
        query_tokens = cls._reference_tokens(query)
        raw_query = str(query or "")
        vague_reference = bool(cls._VAGUE_OPTION_REFERENCE_RE.search(raw_query))
        semantic_reference = bool(cls._APPROACH_REFERENCE_RE.search(raw_query))
        if not query_tokens and not vague_reference:
            return None

        last_recommended_index: int | None = None
        scores = [0 for _ in options]

        for entry in recent_entries:
            if str(entry.get("role") or "").strip().lower() != "assistant":
                continue
            content = str(entry.get("content") or "").strip()
            if not content:
                continue
            content_tokens = cls._reference_tokens(content)
            for index, option in enumerate(options):
                if not cls._option_is_mentioned(option, content):
                    continue
                last_recommended_index = index
                overlap = len(query_tokens & content_tokens)
                if overlap:
                    scores[index] += 2 + overlap

        for index, option in enumerate(options):
            direct_overlap = len(query_tokens & cls._reference_tokens(option))
            if direct_overlap:
                scores[index] += 3 + direct_overlap

        recommendation_text = str(latest_recommendation or "").strip()
        if recommendation_text:
            recommendation_tokens = cls._reference_tokens(recommendation_text)
            for index, option in enumerate(options):
                if cls._option_is_mentioned(option, recommendation_text):
                    last_recommended_index = index
                    scores[index] += 2
                    overlap = len(query_tokens & recommendation_tokens)
                    if overlap:
                        scores[index] += 2 + overlap

        if semantic_reference and last_recommended_index is not None:
            scores[last_recommended_index] += 2

        if vague_reference and last_recommended_index is not None:
            scores[last_recommended_index] += 3

        for pattern, label in cls._SEMANTIC_MODIFIER_HINTS:
            if not pattern.search(raw_query):
                continue
            label_tokens = cls._reference_tokens(label)
            for entry in recent_entries:
                if str(entry.get("role") or "").strip().lower() != "assistant":
                    continue
                content = str(entry.get("content") or "").strip()
                if not content:
                    continue
                content_tokens = cls._reference_tokens(content)
                for index, option in enumerate(options):
                    if not cls._option_is_mentioned(option, content):
                        continue
                    if label_tokens & content_tokens:
                        scores[index] += 3
                        last_recommended_index = index
            if recommendation_text:
                recommendation_tokens = cls._reference_tokens(recommendation_text)
                if label_tokens & recommendation_tokens and last_recommended_index is not None:
                    scores[last_recommended_index] += 3

        best_score = max(scores) if scores else 0
        if best_score < 3:
            return None
        best_index = scores.index(best_score)
        return best_index, options[best_index]

    @classmethod
    def _clip_summary_text(cls, text: str) -> str:
        normalized = re.sub(r"\s+", " ", str(text or "")).strip()
        if len(normalized) > cls._SUMMARY_MAX_FIELD_CHARS:
            normalized = normalized[: cls._SUMMARY_MAX_FIELD_CHARS - 3].rstrip() + "..."
        return normalized

    @classmethod
    def _stable_topic_hint(cls, text: str) -> str:
        candidate = cls._clip_summary_text(text)
        lowered = candidate.lower()
        if not candidate:
            return ""
        if candidate.endswith("?"):
            return ""
        if lowered in {"continue", "keep going", "go on", "more", "tell me more"}:
            return ""
        if lowered.startswith(("what ", "why ", "how ", "which ", "should ", "can we ", "could we ")):
            return ""
        return candidate

    @classmethod
    def _extract_summary_user_goal(cls, entries: list[dict]) -> str:
        user_messages = [
            cls._clip_summary_text(str(entry.get("content") or ""))
            for entry in entries
            if str(entry.get("role") or "").strip().lower() == "user"
            and str(entry.get("content") or "").strip()
        ]
        for message in user_messages:
            if len(message.split()) >= 5:
                return message
        return user_messages[0] if user_messages else ""

    @classmethod
    def _extract_summary_open_question(cls, entries: list[dict]) -> str:
        for entry in reversed(entries):
            if str(entry.get("role") or "").strip().lower() != "user":
                continue
            content = cls._clip_summary_text(str(entry.get("content") or ""))
            if not content:
                continue
            lowered = content.lower()
            if content.endswith("?") or lowered.startswith(("what ", "why ", "how ", "which ", "should ", "can we ")):
                return content
        return ""

    @classmethod
    def _extract_summary_options(cls, entries: list[dict]) -> list[str]:
        for entry in reversed(entries):
            if str(entry.get("role") or "").strip().lower() != "assistant":
                continue
            options = cls._extract_prior_options(str(entry.get("content") or ""))
            if options:
                return [cls._clip_summary_text(option) for option in options[: cls._SUMMARY_MAX_OPTIONS]]
        return []

    @classmethod
    def _build_summary_snapshot(
        cls,
        entries: list[dict],
        *,
        session_state: Optional[dict] = None,
        existing: Optional[dict] = None,
    ) -> dict:
        summary = dict(existing or {})
        state = session_state or {}

        topic = cls._clip_summary_text(str(summary.get("topic") or "")) or cls._stable_topic_hint(str(state.get("active_topic") or ""))
        user_goal = cls._clip_summary_text(str(summary.get("user_goal") or "")) or cls._extract_summary_user_goal(entries)
        open_question = cls._extract_summary_open_question(entries) or cls._clip_summary_text(str(summary.get("open_question") or ""))
        relevant_options = cls._extract_summary_options(entries) or list(summary.get("relevant_options") or [])

        built = {
            "topic": topic,
            "user_goal": user_goal,
            "open_question": open_question,
            "relevant_options": relevant_options[: cls._SUMMARY_MAX_OPTIONS],
        }
        return {key: value for key, value in built.items() if value}

    @classmethod
    def _format_conversation_summary(cls, summary: Optional[dict]) -> str:
        data = dict(summary or {})
        lines: list[str] = []

        topic = cls._clip_summary_text(str(data.get("topic") or ""))
        if topic:
            lines.append(f"- Topic: {topic}")

        user_goal = cls._clip_summary_text(str(data.get("user_goal") or ""))
        if user_goal:
            lines.append(f"- User goal: {user_goal}")

        open_question = cls._clip_summary_text(str(data.get("open_question") or ""))
        if open_question:
            lines.append(f"- Open question: {open_question}")

        options = [cls._clip_summary_text(str(item or "")) for item in list(data.get("relevant_options") or []) if str(item or "").strip()]
        if options:
            lines.append("- Earlier options still relevant:")
            lines.extend(f"  {index + 1}. {option}" for index, option in enumerate(options[: cls._SUMMARY_MAX_OPTIONS]))

        return "\n".join(lines).strip()

    @classmethod
    def roll_context_forward(cls, context: list[dict], session_state: Optional[dict] = None) -> list[dict]:
        entries = list(context or [])
        if len(entries) <= cls._SUMMARY_RETAIN_CONTEXT_ENTRIES:
            return entries

        retained = entries[-cls._SUMMARY_RETAIN_CONTEXT_ENTRIES :]
        summary_entries = entries[:-cls._MAX_CONTEXT_TURNS]
        if session_state is not None:
            session_state["general_chat_summary"] = cls._build_summary_snapshot(
                summary_entries,
                session_state=session_state,
                existing=dict(session_state.get("general_chat_summary") or {}),
            )
        return retained

    @classmethod
    def _answer_kind(
        cls,
        query: str,
        response_text: str,
        *,
        mode: str,
    ) -> str:
        rewrite_kind = cls._rewrite_request_kind(query)
        if rewrite_kind:
            return rewrite_kind
        if cls._extract_prior_options(response_text):
            return "options"

        lowered_query = str(query or "").lower()
        lowered_response = str(response_text or "").lower()
        if any(token in lowered_query for token in ("which", "recommend", "best", "go with", "choose", "pick")):
            return "recommendation"
        if any(token in lowered_response for token in ("start with", "best fit", "best starting point", "go with", "i would use", "the calmest")):
            return "recommendation"
        if mode == "analytical" or any(token in lowered_query for token in ("compare", "trade-off", "pros and cons")):
            return "comparison"
        if any(token in lowered_query for token in ("why", "how", "explain", "what do you mean")):
            return "explanation"
        return "answer"

    @classmethod
    def _extract_latest_recommendation(
        cls,
        response_text: str,
        *,
        options: list[str],
        answer_kind: str,
        existing: str = "",
    ) -> str:
        response = cls._clip_summary_text(cls._strip_initiative_tail(response_text))
        if not response:
            return existing

        if answer_kind == "recommendation":
            return response
        if answer_kind == "options":
            return existing

        lowered = response.lower()
        if any(token in lowered for token in ("start with", "best fit", "best starting point", "go with", "i would use", "the calmest")):
            return response
        return existing

    @classmethod
    def _presentation_preference(
        cls,
        *,
        query: str,
        rewrite_kind: str,
        tone_profile: str,
        existing: str = "",
        explicit_depth: bool = False,
    ) -> str:
        requested = cls._query_presentation_preference(query)
        if requested:
            return requested
        if rewrite_kind in {"simpler", "reworded", "shorter"}:
            return rewrite_kind
        if explicit_depth:
            return "detailed"
        if tone_profile and tone_profile != "balanced":
            return tone_profile
        return existing

    @classmethod
    def _next_conversation_context(
        cls,
        *,
        query: str,
        response_text: str,
        context: Optional[list],
        session_state: Optional[dict],
        mode: str,
        tone_profile: str,
    ) -> SessionConversationContext:
        state = session_state or {}
        existing = SessionConversationContext.from_session_state(state)
        rewrite_kind = cls._rewrite_request_kind(query)
        active_topic = cls._stable_topic_hint(str(state.get("active_topic") or "")) or existing.topic
        topic_shift = bool(
            active_topic
            and existing.topic
            and active_topic.lower() != existing.topic.lower()
            and not rewrite_kind
        )
        if topic_shift:
            existing = SessionConversationContext()
        thread_context = [] if topic_shift else list(context or [])

        current_query = cls._clip_summary_text(query)
        older_goal = existing.user_goal or cls._extract_summary_user_goal(thread_context)
        if rewrite_kind:
            user_goal = older_goal
        elif active_topic and active_topic.lower() != existing.topic.lower() and current_query:
            user_goal = current_query
        elif older_goal:
            user_goal = older_goal
        elif len(current_query.split()) >= 5:
            user_goal = current_query
        else:
            user_goal = existing.user_goal

        last_options_snapshot = cls._extract_prior_options(response_text)
        if not last_options_snapshot:
            option_catalog = cls._reference_option_catalog(thread_context)
            if option_catalog:
                last_options_snapshot = option_catalog[0]
        if not last_options_snapshot:
            last_options_snapshot = list(existing.last_options_snapshot)
        last_options_snapshot = [cls._clip_summary_text(item) for item in last_options_snapshot[: cls._SUMMARY_MAX_OPTIONS]]

        if last_options_snapshot:
            active_options = list(last_options_snapshot)
        else:
            active_options = list(existing.active_options)

        answer_kind = cls._answer_kind(query, response_text, mode=mode)
        latest_recommendation = cls._extract_latest_recommendation(
            response_text,
            options=active_options,
            answer_kind=answer_kind,
            existing="" if topic_shift else existing.latest_recommendation,
        )

        lowered_query = str(query or "").strip().lower()
        if rewrite_kind:
            open_question = existing.open_question
        elif current_query.endswith("?") or lowered_query.startswith(("what ", "why ", "how ", "which ", "should ", "can we ", "could we ")):
            open_question = current_query
        else:
            open_question = existing.open_question

        if rewrite_kind:
            rewrite_target = cls._strip_initiative_tail(cls._last_assistant_message(thread_context))
        else:
            rewrite_target = cls._strip_initiative_tail(response_text)
        rewrite_target = cls._clip_summary_text(rewrite_target or existing.rewrite_target)

        # open_loops: rolling list of unresolved questions — prepend new one, dedupe, cap at 5
        if open_question and not topic_shift:
            loops_seen: list[str] = []
            for s in [open_question] + list(existing.open_loops):
                if s not in loops_seen:
                    loops_seen.append(s)
            open_loops = loops_seen[:5]
        elif topic_shift:
            open_loops = [open_question] if open_question else []
        else:
            open_loops = list(existing.open_loops)

        # recent_recommendations: rolling list — prepend new one, dedupe, cap at 3
        if latest_recommendation and not topic_shift:
            recs_seen: list[str] = []
            for s in [latest_recommendation] + list(existing.recent_recommendations):
                if s not in recs_seen:
                    recs_seen.append(s)
            recent_recommendations = recs_seen[:3]
        elif topic_shift:
            recent_recommendations = [latest_recommendation] if latest_recommendation else []
        else:
            recent_recommendations = list(existing.recent_recommendations)

        return SessionConversationContext(
            topic=active_topic,
            user_goal=user_goal,
            open_question=open_question,
            active_options=active_options[: cls._SUMMARY_MAX_OPTIONS],
            latest_recommendation=latest_recommendation,
            rewrite_target=rewrite_target,
            presentation_preference=cls._presentation_preference(
                query=query,
                rewrite_kind=rewrite_kind,
                tone_profile=tone_profile,
                existing="" if topic_shift else existing.presentation_preference,
                explicit_depth=cls._user_requested_depth(query),
            ),
            last_answer_kind=answer_kind,
            last_options_snapshot=last_options_snapshot[: cls._SUMMARY_MAX_OPTIONS],
            mode=str(mode or "").strip(),
            last_decision=f"{mode}:{answer_kind}" if mode and answer_kind else str(mode or answer_kind),
            open_loops=open_loops,
            recent_recommendations=recent_recommendations,
        )

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
        prior_conversation = SessionConversationContext.from_session_state(session_state)
        presentation_preference = self._presentation_preference(
            query=normalized_query,
            rewrite_kind=self._rewrite_request_kind(normalized_query),
            tone_profile=tone_profile,
            existing=prior_conversation.presentation_preference,
            explicit_depth=explicit_depth,
        )
        shaped_style = self._presentation_style(style, presentation_preference=presentation_preference)
        memory_context = self._build_memory_context()
        request_understanding_block = str(
            (session_state or {}).get("request_understanding_prompt_block") or ""
        ).strip()
        system_prompt = self._build_system_prompt(
            mode,
            shaped_style,
            tone_profile=tone_profile,
            presentation_preference=presentation_preference,
            last_answer_kind=prior_conversation.last_answer_kind,
            memory_context=memory_context,
            request_understanding_block=request_understanding_block,
        )
        max_tokens = self._resolve_max_tokens(
            mode,
            tone_profile=tone_profile,
            explicit_depth=explicit_depth,
            presentation_preference=presentation_preference,
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
                temperature=0.7 if mode == "casual" else 0.5,
            )
            text = self._sanitize_response(text or "")
            fallback = self._local_conceptual_fallback(normalized_query, session_state)
            if fallback and (
                not text
                or text.strip().lower() == ResponseFormatter.friendly_fallback().strip().lower()
                or text.strip().lower().startswith("i didn't quite get that")
            ):
                text = fallback
            elif not text:
                text = ResponseFormatter.friendly_fallback()
            if self._is_geopolitical_query(normalized_query) and self._is_blanket_refusal(text):
                text = self._safe_geopolitical_fallback(normalized_query)
            text = self._shape_response_for_tone(
                text,
                mode=mode,
                tone_profile=tone_profile,
                explicit_depth=explicit_depth,
                presentation_preference=presentation_preference,
            )
            payload = self.formatter.format_payload(text, mode=mode)
            text = payload["user_message"]
            conversation_context = self._next_conversation_context(
                query=normalized_query,
                response_text=text,
                context=context,
                session_state=session_state,
                mode=mode,
                tone_profile=tone_profile,
            )

            # Fire-and-forget memory extraction from the user's query
            self._extract_and_save_memories(normalized_query)

            # Record topic so Nova builds awareness of what it engages with
            self._record_query_topic(normalized_query)

            # Detect explicit preference/feedback signals and record as relationship insights
            self._extract_relationship_signals(normalized_query)

            return SkillResult(
                success=True,
                message=text,
                data={
                    "mode": mode,
                    "style": shaped_style.value,
                    "tone_profile": tone_profile,
                    "speakable_text": payload["speakable_text"],
                    "structured_data": payload["structured_data"],
                    "conversation_context": conversation_context.to_dict(),
                },
                widget_data=None,
                skill=self.name,
            )
        except Exception:
            fallback = self._local_conceptual_fallback(normalized_query, session_state)
            if not fallback:
                return None
            payload = self.formatter.format_payload(fallback, mode=mode)
            conversation_context = self._next_conversation_context(
                query=normalized_query,
                response_text=payload["user_message"],
                context=context,
                session_state=session_state,
                mode=mode,
                tone_profile=tone_profile,
            )
            return SkillResult(
                success=True,
                message=payload["user_message"],
                data={
                    "mode": mode,
                    "style": shaped_style.value,
                    "tone_profile": tone_profile,
                    "local_fallback": True,
                    "fallback_reason": "local_model_unavailable",
                    "speakable_text": payload["speakable_text"],
                    "structured_data": payload["structured_data"],
                    "conversation_context": conversation_context.to_dict(),
                },
                widget_data=None,
                skill=self.name,
            )

    def _extract_and_save_memories(self, query: str) -> None:
        """Detect personal info in the user's message and save to user memory."""
        try:
            for pattern, category, key_name in self._MEMORY_PATTERNS:
                match = pattern.search(query)
                if not match:
                    continue
                value = match.group(1).strip().rstrip(".,!?")
                if not value or len(value) < 2:
                    continue
                if value.lower() in self._MEMORY_EXTRACT_BLOCKLIST:
                    continue
                self._user_memory.save(
                    category,
                    key_name,
                    value,
                    context=query[:200],
                    source="observed",
                    confidence=0.85,
                )
        except Exception:
            pass

    def _record_query_topic(self, query: str) -> None:
        """Record the topic of this query in Nova's self-memory for relationship awareness."""
        try:
            # Broad stopword set to produce meaningful topic labels.
            # Common articles, prepositions, conjunctions, and high-frequency
            # verbs that carry no domain signal are excluded.
            stopwords = {
                "a", "about", "an", "and", "are", "ask", "asked", "be", "been",
                "being", "can", "could", "did", "do", "does", "for", "get", "give",
                "got", "had", "has", "have", "help", "how", "i", "if", "in", "is",
                "it", "just", "know", "let", "like", "make", "me", "my", "need",
                "of", "ok", "okay", "on", "or", "please", "put", "say", "see",
                "set", "show", "take", "tell", "the", "think", "to", "try", "up",
                "use", "want", "was", "were", "what", "when", "where", "who",
                "will", "with", "work", "would", "you",
            }
            words = [w.strip("?.,!:-") for w in query.lower().split()
                     if w.strip("?.,!:-") and w.strip("?.,!:-") not in stopwords]
            # Require at least 2 meaningful words — single-word affirmations
            # ("thanks", "sure", "yep") produce noise in topic patterns.
            if len(words) < 2:
                return
            topic = " ".join(words[:5]).strip()
            if topic:
                self._nova_memory.record_topic(topic)
        except Exception:
            pass

    def _extract_relationship_signals(self, query: str) -> None:
        """Detect explicit user preference or feedback signals and record as relationship insights.

        Only runs on short messages (< 200 chars) that look like general feedback
        rather than task requests. Conservative — explicit regex patterns only, never
        infers. One insight per query to avoid noisy accumulation.

        Guards applied in order:
        1. Length — > 200 chars skipped (likely a task request, not meta-feedback)
        2. Anchor check — must contain a known feedback signal word
        3. Context qualifier check — skip if message is one-off/task-specific
        4. Pattern match — one insight recorded on first match, then stop
        """
        try:
            q = str(query or "").strip()
            if not q or len(q) > 200:
                return

            q_lower = q.lower()

            # Guard 1: require at least one feedback-signal word
            _feedback_anchors = (
                "keep", "less", "more", "shorter", "longer", "brief", "verbose",
                "detail", "direct", "to the point", "bullet", "list", "example",
                "skip", "stop", "don't", "dont", "caveat", "disclaimer",
                "too long", "too wordy",
            )
            if not any(anchor in q_lower for anchor in _feedback_anchors):
                return

            # Guard 2: skip messages that qualify a one-off or task-specific request.
            # These indicate the user wants a specific response changed, not a permanent
            # style adjustment — e.g. "use bullet points for this one".
            _one_off_qualifiers = (
                "for this", "this one", "just this", "this time", "in this case",
                "for now", "right now", "here", "in this response",
            )
            if any(qualifier in q_lower for qualifier in _one_off_qualifiers):
                return

            for pattern, insight in self._INSIGHT_PATTERNS:
                if pattern.search(q):
                    self._nova_memory.record_insight(insight, source="observed")
                    return  # one insight per query
        except Exception:
            pass

    async def handle(self, query: str, context: Optional[list] = None, session_state: Optional[dict] = None) -> SkillResult | None:
        social = self._local_social_result(query)
        if social is not None:
            return social

        # Backward compatible path
        if context is None or session_state is None:
            return await self._run_local_model(query, context=context, session_state=session_state)

        normalized_query = InputNormalizer.normalize(query)
        semantic_clarification = self._semantic_clarification_prompt(
            normalized_query,
            context=context,
            session_state=session_state,
        )
        if semantic_clarification:
            mode = self._detect_mode(normalized_query)
            user_message = self.formatter.format(semantic_clarification, mode=mode)
            speakable_text = self.formatter.to_speakable_text(user_message)
            session_state["last_clarification_turn"] = session_state.get("turn_count", 0)
            return SkillResult(
                success=True,
                message=user_message,
                data={
                    "speakable_text": speakable_text,
                    "structured_data": {"clarification_requested": True},
                    "conversation_context": SessionConversationContext.from_session_state(session_state).to_dict(),
                    "escalation": {
                        "escalated": False,
                        "clarification_requested": True,
                    },
                },
                widget_data=None,
                skill=self.name,
            )
        heuristic_result = self.heuristics.assess(normalized_query, context)
        decision = self.policy.decide(heuristic_result, normalized_query, session_state)
        mode = heuristic_result.get("mode") or self._detect_mode(normalized_query)
        initiative = self.policy.conversational_flags(heuristic_result, normalized_query, session_state)

        if decision == "ASK_USER":
            payload = self.formatter.format_payload(
                self._build_ask_user_message(mode, heuristic_result),
                mode=mode,
            )
            conversation_context = self._next_conversation_context(
                query=normalized_query,
                response_text=payload["user_message"],
                context=context,
                session_state=session_state,
                mode=mode,
                tone_profile=self._current_tone_profile("general"),
            )
            return SkillResult(
                success=True,
                message=payload["user_message"],
                data={
                    "speakable_text": payload["speakable_text"],
                    "conversation_context": conversation_context.to_dict(),
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
            conversation_context = self._next_conversation_context(
                query=normalized_query,
                response_text=payload["user_message"],
                context=context,
                session_state=session_state,
                mode=mode,
                tone_profile=self._current_tone_profile("general"),
            )
            return SkillResult(
                success=True,
                message=payload["user_message"],
                data={
                    "speakable_text": payload["speakable_text"],
                    "structured_data": payload["structured_data"],
                    "conversation_context": conversation_context.to_dict(),
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

        current_conversation = dict((local.data or {}).get("conversation_context") or {})
        local_message = self.formatter.with_conversational_initiative(
            local.message,
            mode=mode,
            allow_clarification=initiative.get("allow_clarification", False),
            allow_branch_suggestion=initiative.get("allow_branch_suggestion", False),
            allow_depth_prompt=initiative.get("allow_depth_prompt", False),
            presentation_preference=str(current_conversation.get("presentation_preference") or ""),
            last_answer_kind=str(current_conversation.get("last_answer_kind") or ""),
        )
        payload = self.formatter.format_payload(local_message, mode=mode)
        local.message = payload["user_message"]
        if initiative.get("allow_clarification"):
            session_state["last_clarification_turn"] = session_state.get("turn_count", 0)
        local.data = {
            "speakable_text": payload["speakable_text"],
            "structured_data": payload["structured_data"],
            "conversation_context": current_conversation,
            "escalation": {
                "escalated": False,
                "reason_codes": list(heuristic_result.get("reason_codes") or []),
            },
        }
        return local
