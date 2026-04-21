# tests/conversation/test_meta_intent_handler.py
"""
Unit tests for MetaIntentHandler.

Covers every intent branch:
  - Greetings            → short warm response, no LLM
  - What can you do      → grouped capability list from registry
  - Out of scope         → calm redirect with "what can you do" / "what's planned"
  - Phase query          → tier/status line
  - What's planned       → roadmap summary
  - Non-meta queries     → returns None (pass-through to general chat)
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import pytest

from src.conversation.meta_intent_handler import MetaIntentHandler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _handle(text: str) -> str | None:
    return MetaIntentHandler().handle(text)


# ---------------------------------------------------------------------------
# Greeting tests
# ---------------------------------------------------------------------------

class TestGreetings:
    @pytest.mark.parametrize("text", [
        "hello",
        "Hello",
        "hi",
        "Hi there",
        "hey",
        "hey nova",
        "Hey Nova!",
        "good morning",
        "Good afternoon",
        "good evening nova",
        "morning",
        "howdy",
        "greetings",
        "helo",
        "hii",
        "heya",
        "what's up",
        "wassup",
        "sup nova",
    ])
    def test_greeting_returns_response(self, text):
        result = _handle(text)
        assert result is not None
        assert len(result) > 0

    def test_greeting_is_short(self):
        result = _handle("hello")
        assert result is not None
        assert len(result) < 100

    def test_non_greeting_not_matched(self):
        # "hello" embedded in a sentence should not match
        result = _handle("hello can you help me book a flight")
        # out-of-scope or None, but NOT a bare greeting response
        assert result is None or "That's not something" in result


# ---------------------------------------------------------------------------
# What can you do
# ---------------------------------------------------------------------------

class TestIdentity:
    @pytest.mark.parametrize("text", [
        "who are you",
        "what are you",
        "what is nova",
        "what's nova",
        "tell me about yourself",
        "tell me about nova",
        "explain nova",
        "describe yourself",
        "who made you",
        "who built you",
        "who created you",
        "who created nova",
        "who designed you",
        "who owns you",
        "who runs nova",
        "who is behind nova",
        "where do you come from",
        "are you an ai",
        "are you a ai",
        "what kind of ai are you",
        "what kind of assistant is nova",
        "is nova open source",
        "is nova private",
        "how does nova work",
        "how do you work",
        "about nova",
        "nova info",
    ])
    def test_recognized(self, text):
        result = _handle(text)
        assert result is not None, f"Expected identity response for {text!r}"

    def test_mentions_creator(self):
        result = _handle("who made you")
        assert result is not None
        assert "Christopher Daugherty" in result

    def test_mentions_local(self):
        result = _handle("what is nova")
        assert result is not None
        assert "local" in result.lower() or "your" in result.lower()

    def test_mentions_privacy(self):
        result = _handle("is nova private")
        assert result is not None
        assert "cloud" in result.lower() or "data" in result.lower() or "private" in result.lower()

    def test_ends_with_next_step(self):
        result = _handle("tell me about yourself")
        assert result is not None
        assert "what can you do" in result.lower() or "tell me" in result.lower()

    def test_does_not_conflict_with_capabilities(self):
        # "what can you do" should still go to capability handler, not identity
        result_identity = _handle("who are you")
        result_caps = _handle("what can you do")
        assert result_identity != result_caps

    def test_does_not_conflict_with_greeting(self):
        # "hi" should still be a greeting, not identity
        result_greeting = _handle("hi")
        result_identity = _handle("who are you")
        assert result_greeting != result_identity


class TestWhatCanYouDo:
    @pytest.mark.parametrize("text", [
        "what can you do",
        "What can you do?",
        "what can Nova do",
        "what are your capabilities",
        "list capabilities",
        "help",
        "commands",
        "show me what you can do",
        "what do you support",
        "what should I ask",
        "what can I ask",
        # non-tech phrasings
        "what are you good at",
        "what do you do",
        "who are you",
        "what is nova",
        "can you help me",
        "help me",
        "i need help",
        "get started",
        "how do i use this",
        "what's available",
    ])
    def test_recognized(self, text):
        result = _handle(text)
        assert result is not None

    def test_response_contains_groups(self):
        result = _handle("what can you do")
        assert result is not None
        # Should contain at least one group-level section
        assert any(label in result for label in [
            "Research", "Computer", "Voice", "Email", "System", "Other",
            "Diagnostics", "Home", "communication", "intelligence",
        ])

    def test_response_contains_capability(self):
        result = _handle("what can you do")
        assert result is not None
        # Should mention at least one real capability label
        assert any(cap in result for cap in [
            "Web search", "Weather", "News", "Screenshot", "Email", "Memory",
            "Volume", "Weather", "Intelligence"
        ])

    def test_response_shows_active_status(self):
        result = _handle("what can you do")
        assert result is not None
        assert "[on]" in result

    def test_response_shows_total_count(self):
        result = _handle("what can you do")
        assert result is not None
        assert any(str(n) in result for n in range(25, 35)) or "capabilities" in result.lower()

    def test_response_has_follow_up_hint(self):
        result = _handle("what can you do")
        assert result is not None
        assert "what" in result.lower()  # points to "what's planned" or another action

    def test_inactive_caps_shown_as_off(self):
        """Disabled caps must appear as [off] not be silently hidden."""
        fake_reg = {
            "capability_groups": {"intelligence": [99]},
            "capabilities": [{
                "id": 99, "name": "future_cap", "enabled": False, "status": "inactive"
            }],
        }
        with patch("src.conversation.meta_intent_handler._load_registry", return_value=fake_reg):
            # Reset cache so patch takes effect
            import src.conversation.meta_intent_handler as m
            m._registry_cache = None
            result = _handle("what can you do")
            m._registry_cache = None  # clean up
            assert result is not None
            assert "[off]" in result

    def test_registry_missing_graceful(self):
        """If registry is missing, should still return something useful."""
        import src.conversation.meta_intent_handler as m
        m._registry_cache = None
        with patch("src.conversation.meta_intent_handler._load_registry", return_value={}):
            result = _handle("what can you do")
        m._registry_cache = None
        assert result is not None  # does not crash


# ---------------------------------------------------------------------------
# Out of scope
# ---------------------------------------------------------------------------

class TestOutOfScope:
    @pytest.mark.parametrize("text", [
        "can you send a text message",
        "can you book me a flight",
        "could you order food",
        "will you write to a file",
        "why can't you send emails",
        "why can't nova book appointments",
        "why doesn't it work",
        "i wish you could send messages",
        "i want nova to post on twitter",
    ])
    def test_recognized(self, text):
        result = _handle(text)
        assert result is not None
        # New specific messages use "yet", "can't", "isn't" rather than the
        # old generic "can't do that" or bare "not".
        assert (
            "can't do that" in result
            or "not" in result.lower()
            or "yet" in result.lower()
            or "can't" in result.lower()
            or "isn't" in result.lower()
        )

    def test_response_redirects(self):
        result = _handle("can you book a flight")
        assert result is not None
        assert "what can you do" in result.lower() or "coming" in result.lower()

    def test_response_is_calm(self):
        result = _handle("why can't you send emails")
        assert result is not None
        # Should not be terse or harsh
        assert len(result) > 60


# ---------------------------------------------------------------------------
# Phase / tier query
# ---------------------------------------------------------------------------

class TestPhaseQuery:
    @pytest.mark.parametrize("text", [
        "what phase are you in",
        "what tier is this",
        "what phase is nova in",
        "current phase",
        "current tier",
        "build status",
        "phase status",
        "which stage are you at",
    ])
    def test_recognized(self, text):
        result = _handle(text)
        assert result is not None
        assert "Tier" in result or "tier" in result.lower() or "phase" in result.lower()

    def test_contains_current_status(self):
        result = _handle("what phase are you in")
        assert result is not None
        assert "Tier 2" in result


# ---------------------------------------------------------------------------
# What's planned
# ---------------------------------------------------------------------------

class TestWhatsPlanned:
    @pytest.mark.parametrize("text", [
        "what's coming next",
        "what is planned",
        "what's on the roadmap",
        "roadmap",
        "future features",
        "upcoming capabilities",
        "what will you be able to do",
        "what's nova working on next",
    ])
    def test_recognized(self, text):
        result = _handle(text)
        assert result is not None

    def test_contains_next_tier(self):
        result = _handle("what's planned")
        assert result is not None
        assert "2.5" in result or "backup" in result.lower() or "Tier" in result


# ---------------------------------------------------------------------------
# Pass-through (should return None)
# ---------------------------------------------------------------------------

class TestPassThrough:
    @pytest.mark.parametrize("text", [
        "search for quantum computing papers",
        "what's the weather today",
        "open github",
        "volume up",
        "draft an email to john@example.com",
        "second opinion",
        "remember this: the meeting is at 3pm",
        "system status",
        "",
        "   ",
    ])
    def test_non_meta_returns_none(self, text):
        result = _handle(text)
        assert result is None, f"Expected None for {text!r}, got {result!r}"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_string(self):
        assert _handle("") is None

    def test_whitespace_only(self):
        assert _handle("   ") is None

    def test_case_insensitive_greeting(self):
        assert _handle("HELLO") is not None

    def test_case_insensitive_capability_query(self):
        assert _handle("WHAT CAN YOU DO") is not None

    def test_trailing_punctuation_greeting(self):
        assert _handle("hi!") is not None

    def test_trailing_punctuation_capability(self):
        assert _handle("what can you do?") is not None
