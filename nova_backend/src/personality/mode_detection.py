"""Context-aware mode detection for the Chief of Staff personality layer.

Detects whether the user is in home, business, or development
context based on time of day, topic keywords, recent capability
usage, and explicit user overrides.

Governance boundaries:
  - No imports from src.governor, src.executors, src.ledger
  - Mode changes tone and initiative ceiling only
  - Approval gates identical across all modes
  - Enforced by import boundary test
"""
from __future__ import annotations

import re
from dataclasses import dataclass

VALID_MODES = frozenset({"home", "business", "development"})

_BUSINESS_KEYWORDS = re.compile(
    r"\b("
    r"shopify|revenue|order[s]?|inventory|store|metric[s]?"
    r"|client|meeting|quarter|q[1-4]|invoice|sales"
    r"|budget|forecast|pipeline|deal|contract"
    r")\b",
    re.IGNORECASE,
)

_DEVELOPMENT_KEYWORDS = re.compile(
    r"\b("
    r"branch|commit|deploy(?:ment)?|test suite|git|repo|debug"
    r"|pull request|merge|build|ci|pipeline|lint"
    r"|refactor|migration|sprint|ticket|jira"
    r")\b",
    re.IGNORECASE,
)

_BUSINESS_CAPABILITIES = frozenset({65})  # Shopify
_DEVELOPMENT_CAPABILITIES = frozenset()   # None currently mapped


@dataclass(frozen=True)
class ModeDetectionResult:
    """Immutable snapshot of detected mode. No authority flags."""

    mode: str
    confidence: str
    reason: str
    override_active: bool


class ModeDetector:
    """Detects user context mode from available signals.

    Pure presentation logic. Does not call capabilities,
    executors, or governance components.
    """

    def detect(
        self,
        *,
        user_text: str = "",
        hour: int | None = None,
        recent_capabilities: list[int] | None = None,
        explicit_override: str | None = None,
    ) -> ModeDetectionResult:
        # 1. Explicit override wins
        if explicit_override is not None:
            cleaned = str(explicit_override).strip().lower()
            if cleaned in VALID_MODES:
                return ModeDetectionResult(
                    mode=cleaned,
                    confidence="explicit",
                    reason=f"User explicitly set {cleaned} mode",
                    override_active=True,
                )
            # Invalid override → fall through to signals
            return self._default()

        # 2. Keyword signals from user text
        text = str(user_text or "").strip()
        if text:
            keyword_mode = self._detect_from_keywords(text)
            if keyword_mode is not None:
                return keyword_mode

        # 3. Recent capability signals
        caps = list(recent_capabilities or [])
        if caps:
            cap_mode = self._detect_from_capabilities(caps)
            if cap_mode is not None:
                return cap_mode

        # 4. Time-of-day signal (weak — only applies to home)
        if hour is not None:
            time_mode = self._detect_from_time(hour)
            if time_mode is not None:
                return time_mode

        # 5. Default: home
        return self._default()

    def clear_override(self) -> ModeDetectionResult:
        return self._default()

    def _default(self) -> ModeDetectionResult:
        return ModeDetectionResult(
            mode="home",
            confidence="default",
            reason="No signals available",
            override_active=False,
        )

    def _detect_from_keywords(self, text: str) -> ModeDetectionResult | None:
        if _BUSINESS_KEYWORDS.search(text):
            return ModeDetectionResult(
                mode="business",
                confidence="inferred",
                reason="Business keywords detected in input",
                override_active=False,
            )
        if _DEVELOPMENT_KEYWORDS.search(text):
            return ModeDetectionResult(
                mode="development",
                confidence="inferred",
                reason="Development keywords detected in input",
                override_active=False,
            )
        return None

    def _detect_from_capabilities(
        self, caps: list[int],
    ) -> ModeDetectionResult | None:
        business_count = sum(
            1 for c in caps if c in _BUSINESS_CAPABILITIES
        )
        dev_count = sum(
            1 for c in caps if c in _DEVELOPMENT_CAPABILITIES
        )
        if business_count >= 2 or (
            business_count >= 1 and len(caps) <= 3
        ):
            return ModeDetectionResult(
                mode="business",
                confidence="inferred",
                reason="Recent capability usage suggests business context",
                override_active=False,
            )
        if dev_count >= 2:
            return ModeDetectionResult(
                mode="development",
                confidence="inferred",
                reason="Recent capability usage suggests development context",
                override_active=False,
            )
        return None

    def _detect_from_time(self, hour: int) -> ModeDetectionResult | None:
        if hour < 7 or hour >= 20:
            return ModeDetectionResult(
                mode="home",
                confidence="inferred",
                reason="Time of day suggests home context",
                override_active=False,
            )
        return None
