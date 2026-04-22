from __future__ import annotations

import re
from typing import Any

from src.conversation.conversation_decision import ConversationDecision, ConversationMode


class ConversationRouter:
    """Deterministic pre-routing for conversational UX (non-authorizing)."""

    COMMAND_PREFIXES = (
        "open",
        "set",
        "show",
        "search",
        "look up",
        "research",
        "track",
        "update",
        "compare",
        "volume",
        "brightness",
        "play",
        "pause",
    )
    QUESTION_HINTS = ("what", "when", "where", "who", "how", "why")
    ANALYSIS_HINTS = ("analyze", "analysis", "explain", "break down", "evaluate", "trade-off", "compare")
    BRAINSTORM_HINTS = ("ideas", "brainstorm", "options", "directions", "concepts")
    HEAVY_HINTS = ("brief", "news", "search", "analyze", "analysis", "compare", "research")
    REFERENCE_PATTERNS = (
        re.compile(r"\b(open|show)\s+(that|it)\b", re.IGNORECASE),
        re.compile(r"\bthat file\b", re.IGNORECASE),
        re.compile(r"\bthat folder\b", re.IGNORECASE),
    )
    MEDIA_PLAY_INTENT_RE = re.compile(
        r"\b(?:play|start|put on)\b.{0,32}\b(?:music|song|songs|something)\b"
        r"|\b(?:need|want)\s+(?:some\s+)?music\b",
        re.IGNORECASE,
    )
    MEDIA_PAUSE_INTENT_RE = re.compile(r"\b(?:pause|stop)\s+(?:it|music|playback|song)\b", re.IGNORECASE)
    MUSIC_TOPIC_RE = re.compile(r"^\s*music[\s.?!]*$", re.IGNORECASE)
    FOLDER_CLARIFICATION_RE = re.compile(r"^\s*(?:the\s+)?(documents|downloads)(?:\s+folder)?\s*$", re.IGNORECASE)
    SPECIFIC_OPEN_FOLDER_RE = re.compile(
        r"^\s*be\s+specific\s*:\s*open\s+(?P<folder>documents|downloads|desktop|pictures)\s*$",
        re.IGNORECASE,
    )
    VAGUE_ACTION_RE = re.compile(r"^\s*(?:do|handle|run)\s+(?:the\s+)?(?:thing|stuff|task)\s*$", re.IGNORECASE)

    MICRO_ACK = {
        ConversationMode.ANALYSIS: "Okay. Let me think that through.",
        ConversationMode.BRAINSTORM: "Okay. Let's map a few directions.",
        ConversationMode.ACTION: "Okay. I'm on it.",
        ConversationMode.DIRECT: "Okay. Let me check.",
    }
    NEVER_ESCALATE_PATTERNS = (
        re.compile(r"^\s*(hi|hello|hey|good morning|good afternoon|good evening)\b", re.IGNORECASE),
        re.compile(r"\bhow are you\b", re.IGNORECASE),
        re.compile(r"\bwhat can you do\b", re.IGNORECASE),
    )
    POLICY_BLOCK_PATTERNS = (
        re.compile(r"\bbypass (the )?governor\b", re.IGNORECASE),
        re.compile(r"\bignore (your|the) (safety|policy|policies|guardrails|instructions|rules)\b", re.IGNORECASE),
        re.compile(r"\bignore (your|the) rules\b", re.IGNORECASE),
        re.compile(r"\bexecute (python|shell|command)\b", re.IGNORECASE),
        re.compile(r"\bdelete all files\b", re.IGNORECASE),
        re.compile(r"\b(?:steal|exfiltrate|dump|extract)\b.{0,48}\b(?:password|passwords|credential|credentials|token|tokens|api keys?)\b", re.IGNORECASE),
        re.compile(r"\b(?:browser|saved)\s+passwords?\b", re.IGNORECASE),
        re.compile(r"\b(?:write|create|build|make)\b.{0,64}\b(?:malware|ransomware|keylogger|rootkit|trojan)\b", re.IGNORECASE),
        re.compile(r"\b(?:persist|persistence|startup)\b.{0,64}\b(?:malware|payload|backdoor)\b", re.IGNORECASE),
        re.compile(r"\b(?:invest|trade|buy|sell)\b.{0,64}\b(?:all|everything|life savings|my money)\b", re.IGNORECASE),
    )
    FOLLOWUP_MARKERS = (
        "that",
        "this",
        "it",
        "them",
        "those",
        "that one",
        "this one",
        "what about",
        "and what about",
        "compare with",
        "the other one",
        "the first",
        "the second",
        "the third",
        "the last",
        "go with",
        "continue that",
        "say more",
        "what do you mean by that",
        "the result",
        "the article",
        "the report",
        "summarize",
        "explain",
        "compare",
        "expand",
        "verify",
    )
    CONTEXT_RESET_MARKERS = (
        "new topic",
        "start over",
        "different question",
        "another thing",
    )
    RESEARCH_HINTS = ("research", "look into", "look up", "investigate", "analyze", "analysis")
    TASK_HINTS = ("open", "run", "check", "show", "set", "play", "pause", "search")
    WORK_HINTS = ("debug", "fix", "implement", "step by step", "plan", "design", "refactor")
    OVERRIDE_MODE_MAP = {
        "brainstorm mode": ConversationMode.BRAINSTORM,
        "work mode": ConversationMode.WORK,
        "analysis mode": ConversationMode.ANALYSIS,
        "casual mode": ConversationMode.CASUAL,
        "social mode": ConversationMode.CASUAL,
    }
    OVERRIDE_RESET_COMMANDS = {"reset mode", "default mode", "stop mode"}
    ORDINAL_REFERENCE_RE = re.compile(
        r"\b(?:go with|pick|choose|take)\s+(?:the\s+)?(first|second|third|last|final)\b"
        r"|\b(?:the|that)\s+(first|second|third|last|final)\b",
        re.IGNORECASE,
    )

    @classmethod
    def route(cls, user_text: str, session_state: dict[str, Any] | None = None) -> ConversationDecision:
        text = (user_text or "").strip()
        lowered = text.lower().rstrip(".?!")
        state = session_state or {}
        session_override = cls._coerce_mode(str(state.get("session_mode_override") or "").strip().lower())

        # Policy check first so blocked prompts never participate in escalation logic.
        blocked_by_policy = any(p.search(text) for p in cls.POLICY_BLOCK_PATTERNS)
        policy_reason = "policy_blocked_phrase" if blocked_by_policy else None

        override_applied = False
        override_cleared = False
        override_mode: str | None = None
        override_confirmation: str | None = None
        if lowered in cls.OVERRIDE_MODE_MAP:
            override_applied = True
            selected_mode = cls.OVERRIDE_MODE_MAP[lowered]
            override_mode = selected_mode.value
            mode_label = "Brainstorming" if selected_mode == ConversationMode.BRAINSTORM else selected_mode.value.title()
            override_confirmation = f"Okay. {mode_label} mode."
        elif lowered in cls.OVERRIDE_RESET_COMMANDS:
            override_cleared = True
            override_mode = "default"
            override_confirmation = "Okay. Back to default."

        continuation_detected = cls._is_followup(lowered, state) if not blocked_by_policy else False
        intent_family = cls._classify_intent_family(text, lowered, continuation_detected) if not blocked_by_policy else "unknown"
        mode = cls._map_intent_to_mode(intent_family, lowered, state) if not blocked_by_policy else ConversationMode.UNKNOWN
        if session_override is not None and not override_applied and not override_cleared and not blocked_by_policy:
            mode = session_override

        needs_clarification = False
        clarification = ""
        resolved_text = text
        if not lowered:
            needs_clarification = True
            clarification = (
                "I might have misheard that. "
                "Did you want me to search the web, open something, or show today's brief?"
            )
        elif cls.VAGUE_ACTION_RE.match(lowered):
            needs_clarification = True
            clarification = "What thing should I do? For example: open documents, search the web, or show today's brief."
        if any(p.search(text) for p in cls.REFERENCE_PATTERNS):
            last_object = str(state.get("last_object") or "").strip()
            if last_object:
                resolved_text = re.sub(
                    r"\bthat file\b|\bthat folder\b|\bthat\b|\bit\b",
                    last_object,
                    text,
                    flags=re.IGNORECASE,
                )
            else:
                needs_clarification = True
                clarification = "Which file or folder do you mean?"
        folder_match = cls.FOLDER_CLARIFICATION_RE.match(lowered)
        if (
            folder_match
            and not needs_clarification
            and "which file or folder" in str(state.get("last_response") or "").lower()
        ):
            resolved_text = f"open {folder_match.group(1).lower()}"
            intent_family = "task"
            mode = ConversationMode.ACTION
        specific_folder_match = cls.SPECIFIC_OPEN_FOLDER_RE.match(lowered)
        if specific_folder_match and not needs_clarification:
            resolved_text = f"open {specific_folder_match.group('folder').lower()}"
            intent_family = "task"
            mode = ConversationMode.ACTION
        if cls.MUSIC_TOPIC_RE.match(text) and not needs_clarification:
            needs_clarification = True
            clarification = "Did you want me to play music, or talk about music?"
        elif cls.MEDIA_PLAY_INTENT_RE.search(text) and not needs_clarification:
            resolved_text = "play"
            intent_family = "task"
            mode = ConversationMode.ACTION
        elif cls.MEDIA_PAUSE_INTENT_RE.search(text) and not needs_clarification:
            resolved_text = "pause"
            intent_family = "task"
            mode = ConversationMode.ACTION
        if cls._looks_overloaded(lowered) and not needs_clarification:
            needs_clarification = True
            clarification = "That includes a few different actions. Which one should I do first?"
        if continuation_detected and not state.get("last_response"):
            needs_clarification = True
            clarification = "What should I continue from?"
        if mode == ConversationMode.UNKNOWN and not needs_clarification:
            tokens = [tok for tok in lowered.split() if tok]
            if len(tokens) <= 3:
                needs_clarification = True
                clarification = (
                    "I might have misheard that. "
                    "Did you want me to search the web, open something, or show today's brief?"
                )

        never_escalate = any(p.search(text) for p in cls.NEVER_ESCALATE_PATTERNS)
        should_escalate = cls._determine_escalation(mode, text, needs_clarification, blocked_by_policy, never_escalate)
        escalation_reason = "analysis_query" if should_escalate else None
        response_template = mode.value
        if mode == ConversationMode.UNKNOWN:
            response_template = "direct"
        should_ack = mode in {ConversationMode.ANALYSIS, ConversationMode.BRAINSTORM} or any(
            h in lowered for h in cls.HEAVY_HINTS
        )

        return ConversationDecision(
            mode=mode,
            intent_family=intent_family,
            continuation_detected=continuation_detected,
            override_applied=override_applied,
            override_cleared=override_cleared,
            override_mode=override_mode,
            override_confirmation=override_confirmation,
            should_escalate=should_escalate,
            escalation_reason=escalation_reason,
            response_template=response_template,
            needs_clarification=needs_clarification,
            clarification_prompt=clarification or None,
            blocked_by_policy=blocked_by_policy,
            policy_reason=policy_reason,
            micro_ack=cls.MICRO_ACK.get(mode, "") if should_ack else "",
            resolved_text=resolved_text,
        )

    @staticmethod
    def _coerce_mode(mode_value: str) -> ConversationMode | None:
        if not mode_value:
            return None
        for mode in ConversationMode:
            if mode.value == mode_value:
                return mode
        return None

    @classmethod
    def _classify_intent_family(cls, text: str, lowered: str, continuation_detected: bool) -> str:
        if any(marker in lowered for marker in cls.CONTEXT_RESET_MARKERS):
            return "question"
        if lowered.startswith(("hi", "hello", "hey", "good morning", "good afternoon", "good evening")):
            return "casual"
        if "how are you" in lowered:
            return "casual"
        if continuation_detected:
            return "followup"
        if "?" in text or any(h in lowered.split() for h in cls.QUESTION_HINTS):
            return "question"
        if any(h in lowered for h in cls.BRAINSTORM_HINTS):
            return "brainstorm"
        if any(v in lowered for v in cls.WORK_HINTS):
            return "work"
        if any(v in lowered for v in cls.RESEARCH_HINTS):
            return "research"
        if lowered.startswith(cls.COMMAND_PREFIXES) or any(v in lowered for v in cls.TASK_HINTS):
            return "task"
        return "unknown"

    @classmethod
    def _map_intent_to_mode(cls, intent_family: str, lowered: str, state: dict[str, Any]) -> ConversationMode:
        if any(h in lowered for h in cls.BRAINSTORM_HINTS):
            return ConversationMode.BRAINSTORM
        if any(h in lowered for h in cls.ANALYSIS_HINTS):
            return ConversationMode.ANALYSIS
        # Continuation inherits prior family when available.
        if intent_family == "followup":
            previous_family = str(state.get("last_intent_family") or "").strip().lower()
            inherited = {
                "research": ConversationMode.ANALYSIS,
                "analysis": ConversationMode.ANALYSIS,
                "brainstorm": ConversationMode.BRAINSTORM,
                "task": ConversationMode.ACTION,
                "action": ConversationMode.ACTION,
                "question": ConversationMode.DIRECT,
                "direct": ConversationMode.DIRECT,
                "work": ConversationMode.WORK,
                "casual": ConversationMode.CASUAL,
            }.get(previous_family)
            if inherited is not None:
                return inherited
        mapping = {
            "casual": ConversationMode.CASUAL,
            "question": ConversationMode.DIRECT,
            "research": ConversationMode.ANALYSIS,
            "task": ConversationMode.ACTION,
            "followup": ConversationMode.DIRECT,
            "work": ConversationMode.WORK,
            "brainstorm": ConversationMode.BRAINSTORM,
            "unknown": ConversationMode.DIRECT,
        }
        return mapping.get(intent_family, ConversationMode.DIRECT)

    @classmethod
    def _determine_escalation(
        cls,
        mode: ConversationMode,
        text: str,
        needs_clarification: bool,
        blocked_by_policy: bool,
        never_escalate: bool,
    ) -> bool:
        if mode != ConversationMode.ANALYSIS:
            return False
        if len((text or "").split()) < 4:
            return False
        if needs_clarification or blocked_by_policy or never_escalate:
            return False
        return True

    @classmethod
    def _is_followup(cls, lowered: str, state: dict[str, Any]) -> bool:
        if not lowered:
            return False
        if any(marker in lowered for marker in cls.CONTEXT_RESET_MARKERS):
            return False
        has_context = bool(state.get("last_response")) or bool(state.get("last_object"))
        if not has_context:
            return False
        if any(re.search(rf"(?<!\w){re.escape(marker)}(?!\w)", lowered) for marker in cls.FOLLOWUP_MARKERS):
            return True
        if cls.ORDINAL_REFERENCE_RE.search(lowered):
            return True
        return len(lowered.split()) <= 3

    @classmethod
    def _looks_overloaded(cls, lowered: str) -> bool:
        command_hits = 0
        for prefix in cls.COMMAND_PREFIXES:
            if re.search(rf"(?<!\w){re.escape(prefix)}(?!\w)", lowered):
                command_hits += 1
        return command_hits >= 3
