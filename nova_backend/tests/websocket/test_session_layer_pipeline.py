# tests/websocket/test_session_layer_pipeline.py
"""
Full-pipeline routing tests: InputNormalizer → session-layer patterns → governor.

These tests simulate the production path that a raw user phrase travels through:

  1. InputNormalizer.normalize()        (SessionRouter.normalize_and_route)
  2. command_text strip [.?!]+$        (session_handler line 971)
  3. Session-layer pattern checks       (HELP_ORIENT_RE, EMAIL_INBOX_RE, etc.)
  4. GovernorMediator fallback          (if no session-layer match)

Tests that skip InputNormalizer will miss bugs like the RC-7/PHRASE_NORMALIZATION
collision, where phrases are transformed before session-layer patterns ever fire.
"""
from __future__ import annotations

import re

import pytest

from src.conversation.response_style_router import InputNormalizer
from src.governor.governor_mediator import GovernorMediator
from src.websocket.intent_patterns import (
    AMBIENT_CLARIFICATION_PATTERNS,
    CAPABILITY_HELP_RE,
    EMAIL_INBOX_RE,
    HELP_ORIENT_RE,
    REMIND_ME_TIMELESS_RE,
    TIME_QUERY_RE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pipeline(raw: str) -> str | int | None:
    """
    Simulate the full production routing path for a raw user phrase.
    Returns a string label (session-layer) or int capability_id (governor)
    or None (LLM fallthrough).
    """
    # Step 1: normalize (InputNormalizer runs in SessionRouter.normalize_and_route)
    normalized = InputNormalizer.normalize(raw)

    # Step 2: strip trailing punctuation (session_handler line 971)
    command_text = re.sub(r"[.?!]+$", "", normalized).strip()

    # Step 3: session-layer checks (order matches session_handler)
    if TIME_QUERY_RE.match(command_text):
        return "TIME_QUERY"
    if EMAIL_INBOX_RE.match(command_text):
        return "EMAIL_INBOX"
    if HELP_ORIENT_RE.match(command_text):
        return "HELP_ORIENT"
    if CAPABILITY_HELP_RE.match(command_text):
        return "CAPABILITY_HELP"
    if REMIND_ME_TIMELESS_RE.match(command_text):
        return "REMIND_TIMELESS"
    for pat, _ in AMBIENT_CLARIFICATION_PATTERNS:
        if pat.match(command_text):
            return "AMBIENT_CLARIFICATION"

    # Step 4: governor
    result = GovernorMediator.parse_governed_invocation(command_text)
    if result is None:
        return None
    return getattr(result, "capability_id", None)


# ---------------------------------------------------------------------------
# RC-7: "help me" forms → HELP_ORIENT (warm orienting question)
# These were previously broken: PHRASE_NORMALIZATION mapped them to
# "what can you do", causing CAPABILITY_HELP to fire instead.
# ---------------------------------------------------------------------------

class TestRC7HelpOrient:
    """Verify RC-7 routes to HELP_ORIENT through the full pipeline."""

    @pytest.mark.parametrize("raw", [
        "help me",
        "Help me",
        "HELP ME",
        "help me!",           # trailing punct stripped
        "i need help",
        "i need some help",
        "can you help me",
        "could you help me",
        "i could use some help",
        "not sure what to ask",
        "not sure what to do",
        "where do i start",
        "where do i begin",
        # nova-prefix stripped by POLITE_PREFIX_RE in InputNormalizer
        "nova help me",
        "nova i need help",
        "nova where do i start",
        "hey nova help me",
        "ok nova help me",
        # "i want help" forms — distinct from "i need help", same intent
        "i want help",
        "i want some help",
        "nova i want help",
    ])
    def test_routes_to_help_orient(self, raw: str):
        assert _pipeline(raw) == "HELP_ORIENT", (
            f"{repr(raw)} should route to HELP_ORIENT; "
            f"got {_pipeline(raw)!r}. "
            f"Check PHRASE_NORMALIZATION in response_style_router.py — "
            f"normalizing these phrases to 'what can you do' bypasses RC-7."
        )

    @pytest.mark.parametrize("raw", [
        # These start with "help me" but have a task suffix — should fall through to
        # governor or LLM, not fire the short orienting question.
        "help me write a letter",
        "help me draft an email",
        "help me plan my day",
    ])
    def test_help_with_task_does_not_route_to_help_orient(self, raw: str):
        result = _pipeline(raw)
        assert result != "HELP_ORIENT", (
            f"{repr(raw)} has a task suffix — should NOT route to HELP_ORIENT; "
            f"got {result!r}"
        )


# ---------------------------------------------------------------------------
# Capability list → CAPABILITY_HELP (explicit list requests, not "I'm lost")
# ---------------------------------------------------------------------------

class TestCapabilityHelp:
    """Verify explicit capability-list requests stay in CAPABILITY_HELP."""

    @pytest.mark.parametrize("raw", [
        "what can you do",
        "what can u do",
        "what are you good at",
        "what do you do",
        "tell me what you can do",
        "show me what you can do",
        "show capabilities",
        "show me your capabilities",
        "what capabilities do you have",
        "get started",
        "how do i start",
        "how do i use you",
        "how can i use nova",
        "what's available",
        # nova-prefix
        "nova what can you do",
    ])
    def test_routes_to_capability_help(self, raw: str):
        assert _pipeline(raw) == "CAPABILITY_HELP", (
            f"{repr(raw)} should route to CAPABILITY_HELP; got {_pipeline(raw)!r}"
        )


# ---------------------------------------------------------------------------
# Email inbox boundary
# ---------------------------------------------------------------------------

class TestEmailInbox:
    """RC-1: email inbox phrases → EMAIL_INBOX (not Cap 17 or LLM)."""

    @pytest.mark.parametrize("raw", [
        "open my email",
        "check my email",
        "check email",
        "my inbox",
        "show me my emails",
        "nova open my email",
        "hey nova check my email",
    ])
    def test_inbox_routes_correctly(self, raw: str):
        assert _pipeline(raw) == "EMAIL_INBOX", (
            f"{repr(raw)} should route to EMAIL_INBOX; got {_pipeline(raw)!r}"
        )

    @pytest.mark.parametrize("raw", [
        "email John about the meeting",
        "write an email to Sarah",
        "draft an email",
        "send an email to mom",
    ])
    def test_email_draft_does_not_hit_inbox(self, raw: str):
        result = _pipeline(raw)
        assert result != "EMAIL_INBOX", (
            f"{repr(raw)} should NOT route to EMAIL_INBOX (it's a draft request); "
            f"got {result!r}"
        )


# ---------------------------------------------------------------------------
# Time / date queries
# ---------------------------------------------------------------------------

class TestTimeQuery:
    """Time and date queries handled by session layer."""

    @pytest.mark.parametrize("raw", [
        "what time is it",
        "what time is it?",
        "what day is it",
        "what's today's date",
        "what's the date",
        "current time",
        "nova what time is it",
        "hey nova what time is it",
    ])
    def test_routes_to_time_query(self, raw: str):
        assert _pipeline(raw) == "TIME_QUERY", (
            f"{repr(raw)} should route to TIME_QUERY; got {_pipeline(raw)!r}"
        )


# ---------------------------------------------------------------------------
# Timeless reminder boundary
# ---------------------------------------------------------------------------

class TestRemindMeTimeless:
    """Timeless remind-me forms → clarification; full form passes through."""

    @pytest.mark.parametrize("raw", [
        "remind me to call mom",
        "remind me to exercise",
        "set a reminder",
        "nova remind me to call mom",
    ])
    def test_timeless_routes_to_clarification(self, raw: str):
        assert _pipeline(raw) == "REMIND_TIMELESS", (
            f"{repr(raw)} should route to REMIND_TIMELESS; got {_pipeline(raw)!r}"
        )

    @pytest.mark.parametrize("raw", [
        "remind me at 3pm to call mom",
        "remind me daily at 9am to check email",
    ])
    def test_full_form_does_not_hit_timeless(self, raw: str):
        result = _pipeline(raw)
        assert result != "REMIND_TIMELESS", (
            f"{repr(raw)} has a time spec — should NOT route to REMIND_TIMELESS; "
            f"got {result!r}"
        )


# ---------------------------------------------------------------------------
# Core governor routing through full pipeline
# ---------------------------------------------------------------------------

class TestGovernorRoutingPipeline:
    """Key governor routes verified through the full InputNormalizer pipeline."""

    @pytest.mark.parametrize("raw,expected_cap", [
        ("what's the news", 56),
        ("show me the news", 56),
        ("morning news", 56),
        ("catch me up", 56),
        ("what did i miss", 56),
        ("today's news", 50),
        ("what's the weather", 55),
        ("check weather", 55),
        ("will it snow tomorrow", 55),
        ("should i bring an umbrella", 55),
        ("search for AI news", 16),
        ("look up quantum computing", 16),
        ("find me a recipe for pasta", 16),
        ("verify this", 31),
        ("fact check the moon has an atmosphere", 31),
        ("what have you saved for me", 61),
        ("what have i saved", 61),
        ("how is the AI story doing", 52),
        ("send an email", 64),
        ("can you help me write an email", 64),
    ])
    def test_governor_cap(self, raw: str, expected_cap: int):
        assert _pipeline(raw) == expected_cap, (
            f"{repr(raw)} should route to Cap {expected_cap}; got {_pipeline(raw)!r}"
        )


# ---------------------------------------------------------------------------
# Ambient clarification — only fires without prior context
# (context guard tested at the handler level; here we test pattern matching)
# ---------------------------------------------------------------------------

class TestAmbientClarificationPatterns:
    """Ambient patterns match correctly (context guard tested separately)."""

    @pytest.mark.parametrize("raw", [
        "tell me more",
        "tell me more about that",
        "go deeper",
        "elaborate",
        "what went wrong",
        "why didn't that work",
        "idk what to do",
        "i'm lost",
        "i'm stuck",
        "why did that fail",
        "what should i do today",
    ])
    def test_matches_ambient_pattern(self, raw: str):
        # These should match AMBIENT_CLARIFICATION_PATTERNS directly
        # (pipeline may or may not fire depending on session state in production)
        normalized = InputNormalizer.normalize(raw)
        command_text = re.sub(r"[.?!]+$", "", normalized).strip()
        matched = any(pat.match(command_text) for pat, _ in AMBIENT_CLARIFICATION_PATTERNS)
        assert matched, (
            f"{repr(raw)} (normalized to {repr(command_text)!r}) "
            f"should match an AMBIENT_CLARIFICATION_PATTERNS entry"
        )

    @pytest.mark.parametrize("raw", [
        # These have prior-context intent but should NOT be in ambient patterns
        "what's the weather",
        "search for AI news",
        "what can you do",
    ])
    def test_does_not_match_ambient_pattern(self, raw: str):
        normalized = InputNormalizer.normalize(raw)
        command_text = re.sub(r"[.?!]+$", "", normalized).strip()
        matched = any(pat.match(command_text) for pat, _ in AMBIENT_CLARIFICATION_PATTERNS)
        assert not matched, (
            f"{repr(raw)} should NOT match AMBIENT_CLARIFICATION_PATTERNS; "
            f"got a match on {repr(command_text)}"
        )


# ---------------------------------------------------------------------------
# Session-state-aware ambient context guard (Issue #143)
#
# Production behavior (session_handler ~line 1263):
#   if not (session_state.get("last_response") or "").strip():
#       <check AMBIENT_CLARIFICATION_PATTERNS>
#
# With prior context, the ambient block is skipped entirely and the
# phrase falls through to the LLM as a follow-up.
# ---------------------------------------------------------------------------

def _pipeline_with_session_state(
    raw: str,
    session_state: dict | None = None,
) -> str | int | None:
    """
    Like _pipeline but models the session_state context guard around
    AMBIENT_CLARIFICATION_PATTERNS.

    When session_state["last_response"] is non-empty the ambient block
    is skipped — matching production behavior.
    """
    if session_state is None:
        session_state = {}

    normalized = InputNormalizer.normalize(raw)
    command_text = re.sub(r"[.?!]+$", "", normalized).strip()

    # Session-layer checks (same order as _pipeline / session_handler)
    if TIME_QUERY_RE.match(command_text):
        return "TIME_QUERY"
    if EMAIL_INBOX_RE.match(command_text):
        return "EMAIL_INBOX"
    if HELP_ORIENT_RE.match(command_text):
        return "HELP_ORIENT"
    if CAPABILITY_HELP_RE.match(command_text):
        return "CAPABILITY_HELP"
    if REMIND_ME_TIMELESS_RE.match(command_text):
        return "REMIND_TIMELESS"

    # Context guard: only check ambient patterns when no prior response
    if not (session_state.get("last_response") or "").strip():
        for pat, _ in AMBIENT_CLARIFICATION_PATTERNS:
            if pat.match(command_text):
                return "AMBIENT_CLARIFICATION"

    # Governor fallback
    result = GovernorMediator.parse_governed_invocation(command_text)
    if result is None:
        return None
    return getattr(result, "capability_id", None)


class TestAmbientContextGuard:
    """
    Issue #143: with prior session context, ambient follow-up phrases
    must NOT fire AMBIENT_CLARIFICATION — they fall through to the LLM.
    """

    _PRIOR_RESPONSE = (
        "Here are the latest headlines about AI regulation: "
        "The EU AI Act entered its enforcement phase this month."
    )

    @pytest.mark.parametrize("raw", [
        "tell me more",
        "tell me more about that",
        "go deeper",
        "elaborate",
    ])
    def test_with_context_does_not_fire_ambient(self, raw: str):
        """With last_response set, the phrase bypasses ambient patterns."""
        session_state = {"last_response": self._PRIOR_RESPONSE}
        result = _pipeline_with_session_state(raw, session_state)
        assert result != "AMBIENT_CLARIFICATION", (
            f"{repr(raw)} should NOT fire AMBIENT_CLARIFICATION when "
            f"session has prior context — it should fall through to LLM"
        )

    @pytest.mark.parametrize("raw", [
        "tell me more",
        "tell me more about that",
        "go deeper",
        "elaborate",
    ])
    def test_without_context_fires_ambient(self, raw: str):
        """Without last_response, the phrase fires ambient clarification."""
        session_state = {"last_response": ""}
        result = _pipeline_with_session_state(raw, session_state)
        assert result == "AMBIENT_CLARIFICATION", (
            f"{repr(raw)} should fire AMBIENT_CLARIFICATION when "
            f"session has no prior context"
        )

    def test_empty_last_response_fires_ambient(self):
        """Whitespace-only last_response counts as empty."""
        session_state = {"last_response": "   "}
        result = _pipeline_with_session_state(
            "tell me more", session_state
        )
        assert result == "AMBIENT_CLARIFICATION"

    def test_no_session_state_fires_ambient(self):
        """Missing session_state entirely counts as no context."""
        result = _pipeline_with_session_state("tell me more")
        assert result == "AMBIENT_CLARIFICATION"

    def test_context_does_not_affect_non_ambient_routes(self):
        """Prior context should not interfere with other routing."""
        session_state = {"last_response": self._PRIOR_RESPONSE}
        assert _pipeline_with_session_state(
            "what time is it", session_state
        ) == "TIME_QUERY"
        assert _pipeline_with_session_state(
            "what can you do", session_state
        ) == "CAPABILITY_HELP"
