"""Tests for GeneralChatSkill._extract_relationship_signals().

Validates conservative extraction: only explicit feedback signals, one
insight per query, short messages only, no extraction from task requests
or one-off context-specific requests.
"""
from __future__ import annotations

from unittest.mock import MagicMock

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
# Should extract — clear general preference signals
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

    def test_more_detail_general(self):
        # "more detail" without a topic qualifier — general preference
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Can you give me more detail")
        skill._nova_memory.record_insight.assert_called_once()
        call_insight = skill._nova_memory.record_insight.call_args[0][0]
        assert "detailed" in call_insight.lower()

    def test_no_bullet_points(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("No bullet points please")
        skill._nova_memory.record_insight.assert_called_once()
        call_insight = skill._nova_memory.record_insight.call_args[0][0]
        assert "prose" in call_insight.lower() or "bullet" in call_insight.lower()

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

    def test_i_like_examples(self):
        # General preference expression — not a task request
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("I like when you give examples")
        skill._nova_memory.record_insight.assert_called_once()
        call_insight = skill._nova_memory.record_insight.call_args[0][0]
        assert "example" in call_insight.lower()

    def test_examples_help(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Examples help me understand better")
        skill._nova_memory.record_insight.assert_called_once()

    def test_source_is_observed(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Keep it brief")
        _, kwargs = skill._nova_memory.record_insight.call_args
        assert kwargs.get("source") == "observed"


# ---------------------------------------------------------------------------
# Should NOT extract — task requests, long messages, no anchor
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

    def test_more_detail_about_topic_is_task(self):
        # "more detail about X" is asking for topic information, not a style preference
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("I need more detail about the project timeline")
        skill._nova_memory.record_insight.assert_not_called()

    def test_more_detail_on_topic_is_task(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Give me more detail on the budget")
        skill._nova_memory.record_insight.assert_not_called()

    def test_more_detail_for_topic_is_task(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("I need more detail for the proposal")
        skill._nova_memory.record_insight.assert_not_called()

    def test_give_me_an_example_of_is_task(self):
        # Task request — specific example requested, not a general preference
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Give me an example of how taxes work")
        skill._nova_memory.record_insight.assert_not_called()

    def test_more_examples_of_topic_is_task(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Give me more examples of French recipes")
        skill._nova_memory.record_insight.assert_not_called()

    def test_tell_me_more_about_is_task(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Tell me more about Paris")
        skill._nova_memory.record_insight.assert_not_called()


# ---------------------------------------------------------------------------
# Should NOT extract — one-off / context-specific qualifiers
# ---------------------------------------------------------------------------

class TestOneOffQualifiersSkipped:
    def test_use_bullets_for_this(self):
        # "for this" marks a one-off formatting request, not a permanent preference
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Use bullet points for this")
        skill._nova_memory.record_insight.assert_not_called()

    def test_use_bullets_this_one(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Use bullet points for this one")
        skill._nova_memory.record_insight.assert_not_called()

    def test_shorter_just_this_time(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("Can you make it shorter just this time")
        skill._nova_memory.record_insight.assert_not_called()

    def test_more_detail_in_this_case(self):
        skill = _skill_with_mock_memory()
        skill._extract_relationship_signals("More detail in this case please")
        skill._nova_memory.record_insight.assert_not_called()


# ---------------------------------------------------------------------------
# One insight per query
# ---------------------------------------------------------------------------

class TestOneInsightPerQuery:
    def test_multiple_signals_only_one_recorded(self):
        skill = _skill_with_mock_memory()
        # Both "short" and "bullet points" in same message — only first pattern fires
        skill._extract_relationship_signals("Keep it short and no bullet points")
        assert skill._nova_memory.record_insight.call_count == 1

    def test_exception_in_nova_memory_doesnt_raise(self):
        skill = _skill_with_mock_memory()
        skill._nova_memory.record_insight.side_effect = RuntimeError("store error")
        # Should not propagate exception
        skill._extract_relationship_signals("Keep it short")
