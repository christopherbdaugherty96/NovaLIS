"""
Base skill classes and result structure for NovaLIS.

This is a foundational module.
Changes here affect all skills and must remain conservative.

Responsibilities:
- Unified SkillResult contract
- Safe tone normalization
- Lightweight response validation
- Optional routing observability
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ==================== RESULT CONTRACT ====================

@dataclass
class SkillResult:
    """
    Unified result returned by all NovaLIS skills.
    """

    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    widget_data: Optional[Dict[str, Any]] = None
    skill: Optional[str] = None

    # LLM / streaming support (used only by LLM-backed skills)
    use_llm: bool = False
    llm_model: str = ""
    streaming: bool = False
    context_messages: List[Dict[str, Any]] = field(default_factory=list)


# ==================== BASE SKILL ====================

class BaseSkill(ABC):
    """
    Abstract base class for all NovaLIS skills.

    This class provides:
    - Safe tone normalization
    - Minimal response validation
    - Optional routing observability

    It does NOT:
    - Enforce personalities
    - Modify intent logic
    - Perform reasoning
    """

    name: str = "base"
    description: str = "NovaLIS skill"

    # ==================== TONE NORMALIZATION ====================

    def normalize_message(self, text: str) -> str:
        """
        Apply NovaLIS tone normalization.

        Design rules:
        - Never change meaning
        - Never add personality
        - Voice-safe
        - Deterministic
        """
        if not text:
            return text

        # Remove emojis only (preserve normal Unicode)
        text = re.sub(
            r'[\U0001F600-\U0001F64F'
            r'\U0001F300-\U0001F5FF'
            r'\U0001F680-\U0001F6FF'
            r'\U0001F1E0-\U0001F1FF]',
            '',
            text
        )

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Ensure terminal punctuation
        if text and text[-1] not in ".!?":
            text += "."

        # Capitalize first letter (voice-friendly)
        if text and text[0].islower():
            text = text[0].upper() + text[1:]

        return text

    # ==================== RESPONSE VALIDATION ====================

    def validate_response(self, message: str) -> bool:
        """
        Minimal sanity check.

        This is NOT a content filter.
        It only blocks obvious violations.
        """
        if not message or len(message) < 2:
            return False

        lower = message.lower()

        # Excessive enthusiasm
        if message.count("!") > 1:
            return False

        # Self-reference (should never appear in skills)
        if any(p in lower for p in ("as an ai", "i am an ai", "i'm an ai")):
            return False

        return True

    # ==================== OBSERVABILITY ====================

    def log_handling(self, query: str, handled: bool) -> None:
        """
        Optional routing log.
        Active only when DEBUG_MODE is enabled.
        """
        try:
            from nova_config import DEBUG_MODE
            if not DEBUG_MODE:
                return

            import logging
            logger = logging.getLogger(self.name)
            action = "handling" if handled else "skipped"
            logger.debug(f"[{self.name}] {action}: '{query[:60]}'")

        except Exception:
            # Never allow logging to break execution
            pass

    # ==================== SKILL INTERFACE ====================

    async def can_handle(self, query: str) -> bool:
        return False

    @abstractmethod
    async def handle(self, query: str) -> SkillResult:
        """
        Execute the skill.

        Implementation rules:
        - Generate raw message
        - normalize_message()
        - Optionally validate_response()
        - Always include skill=self.name
        """
        raise NotImplementedError
