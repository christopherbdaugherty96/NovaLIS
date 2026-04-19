"""Tests for GeneralChatSkill._extract_relationship_signals().

Validates conservative extraction: only explicit feedback signals, one
insight per query, short messages only, no extraction from task requests.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.skills.general_chat import GeneralChatSkill


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _skill_with_mock_memory():
    """Return a skill instance whose nova_memory is a MagicMock."""
    skill = GeneralChatSkill.__new__(GeneralChatSkill)
    skill._nova_memory = MagicMock()
    return skill


# ---------------------------------------------------------------------------
# Should extract
# ---------------------------------------------------------------------------

class TestInsightExtracted:
    def test_keep_it_short(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Keep it short please")
        skill._nova_memory.record_insight.assert_called_once()
        call_insight = skill._nova_memory.record_insight.call_args[0][0]
        assert "concise" in call_insight.lower()

    def test_too_long(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("That was too long")
        skill._nova_memory.record_insight.assert_called_once()

    def test_more_detail(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Give me more detail on that")
        skill._nova_memory.record_insight.assert_called_once()
        call_insight = skill._nova_memory.record_insight.call_args[0][0]
        assert "detailed" in call_insight.lower()

    def test_no_bullet_points(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("No bullet points please")
        skill._nova_memory.record_insight.assert_called_once()
        call_insight = skill._nova_memory.record_insight.call_args[0][0]
        assert "prose" in call_insight.lower() or "bullet" in call_insight.lower()

    def test_use_bullet_points(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Use bullet points for this")
        skill._nova_memory.record_insight.assert_called_once()

    def test_get_to_the_point(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Get to the point")
        skill._nova_memory.record_insight.assert_called_once()
        call_insight = skill._nova_memory.record_insight.call_args[0][0]
        assert "direct" in call_insight.lower()

    def test_skip_the_disclaimer(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Skip the disclaimer")
        skill._nova_memory.record_insight.assert_called_once()
        call_insight = skill._nova_memory.record_insight.call_args[0][0]
        assert "caveat" in call_insight.lower()

    def test_give_me_an_example(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Give me an example")
        skill._nova_memory.record_insight.assert_called_once()
        call_insight = skill._nova_memory.record_insight.call_args[0][0]
        assert "example" in call_insight.lower()

    def test_source_is_observed(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Keep it brief")
        _, kwargs = skill._nova_memory.record_insight.call_args
        assert kwargs.get("source") == "observed"


# ---------------------------------------------------------------------------
# Should NOT extract (task requests, long messages, no feedback anchor)
# ---------------------------------------------------------------------------

class TestInsightNotExtracted:
    def test_regular_task_request(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("What is the capital of France?")
        skill._nova_memory.record_insight.assert_not_called()

    def test_empty_string(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("")
        skill._nova_memory.record_insight.assert_not_called()

    def test_long_message_skipped(self):
        skill = _skill_with_mock_memory()
        long_query = "keep it short " * 20  # > 200 chars
        skill._extract_relationship_signals(long_query)
        skill._nova_memory.record_insight.assert_not_called()

    def test_no_feedback_anchor(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Hello there")
        skill._nova_memory.record_insight.assert_not_called()

    def test_unrelated_word_match_ignored(self):
        # "more" alone in a task request without feedback anchor context
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Tell me more about Paris")
        # "more" is in feedback anchors — but "Tell me more about X" should still
        # not trigger if no insight pattern matches
        # In this case "more" IS an anchor but no _INSIGHT_PATTERNS regex matches the full phrase
        # "Tell me more about Paris" — no pattern for "more about" without "detail/depth/etc."
        # So record_insight should NOT be called
        skill._nova_memory.record_insight.assert_not_called()


# ---------------------------------------------------------------------------
# One insight per query
# ---------------------------------------------------------------------------

class TestOneInsightPerQuery:
    def test_multiple_signals_only_one_recorded(self):
        skill = _skill_with_mock_memory()
        # Both "short" and "bullet points" in same message
        skill._extract_relationship_signals("Keep it short and no bullet points")
        assert skill._nova_memory.record_insight.call_count == 1

    def test_exception_in_nova_memory_doesnt_raise(self):
        skill = _skill_with_mock_memory()
        skill._nova_memory.record_insight.side_effect = RuntimeError("store error")
        # Should not propagate exception
        skill._extract_relationship_signals("Keep it short")
