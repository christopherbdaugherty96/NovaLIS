"""Tests for the morning brief handler module.

Verifies:
  1. Trigger detection matches the expected keywords
  2. compose_governed_morning_brief calls the RoutineGraph engine
  3. Result formatting produces readable text from sections
  4. weather/calendar data converters handle edge cases
  5. MorningBriefResult.has_content reflects actual section data
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from src.brief.daily_loop import (
    DailyLoopItem,
    DailyLoopProjection,
    DailyLoopSource,
)
from src.conversation.morning_brief_handler import (
    DAILY_BRIEF_TRIGGERS,
    MORNING_BRIEF_TRIGGERS,
    MorningBriefResult,
    calendar_result_to_brief_data,
    compose_governed_morning_brief,
    is_daily_brief_request,
    is_morning_brief_request,
    normalize_brief_text,
    weather_result_to_brief_data,
)

# -------------------------------------------------------------------
# Trigger detection
# -------------------------------------------------------------------

class TestTriggerDetection:
    @pytest.mark.parametrize("trigger", sorted(DAILY_BRIEF_TRIGGERS))
    def test_known_triggers_match(self, trigger: str):
        assert is_daily_brief_request(trigger) is True

    def test_non_trigger_rejected(self):
        assert is_daily_brief_request("hello") is False
        assert is_daily_brief_request("good morning") is False
        assert is_daily_brief_request("") is False
        assert is_daily_brief_request("give me a brief summary of this article") is False
        assert is_daily_brief_request("intelligence brief") is False

    def test_triggers_are_lowercase(self):
        for t in DAILY_BRIEF_TRIGGERS:
            assert t == t.lower()

    def test_compat_aliases_preserved(self):
        assert MORNING_BRIEF_TRIGGERS is DAILY_BRIEF_TRIGGERS
        assert is_morning_brief_request is is_daily_brief_request


class TestTriggerNormalization:
    """One user-facing Daily Brief: phrasing variants must all resolve."""

    @pytest.mark.parametrize("phrase", [
        "Daily Brief",
        "daily brief!",
        "morning brief please",
        "Morning brief.",
        "give me my daily brief",
        "give me the daily brief please",
        "can you run the morning brief",
        "hey nova, daily brief",
        "brief me!",
        "what's my day look like?",
        "What does my day look like today?",
        "what matters today?",
        "what should i focus on today",
        "plan my day",
        "Catch me up.",
    ])
    def test_phrasing_variants_match(self, phrase: str):
        assert is_daily_brief_request(phrase) is True

    @pytest.mark.parametrize("phrase", [
        "brief history of rome",
        "write a brief for the legal team",
        "what should i focus on in my career",
        "daily standup notes",
        "news brief",
    ])
    def test_non_brief_phrases_rejected(self, phrase: str):
        assert is_daily_brief_request(phrase) is False

    def test_normalize_strips_punctuation_and_courtesy(self):
        assert normalize_brief_text("Give me my Daily Brief, please!") == "daily brief"
        assert normalize_brief_text("  morning   brief  ") == "morning brief"


# -------------------------------------------------------------------
# compose_governed_morning_brief
# -------------------------------------------------------------------

def _make_mock_run_and_receipt(brief_dict=None):
    """Build mock RoutineRun and RoutineReceipt for testing."""
    run = MagicMock()
    run.run_id = "run_test_001"
    run.outputs = {"daily_brief": brief_dict or {}}

    receipt = MagicMock()
    receipt.receipt_id = "rcpt_test_001"
    receipt.graph_name = "daily_brief"
    receipt.sources_consulted = frozenset({"session_state"})

    return run, receipt


class TestComposeGoverned:
    @patch("src.conversation.morning_brief_handler.get_recent_receipts")
    @patch("src.conversation.morning_brief_handler.run_daily_brief_routine")
    def test_basic_call(self, mock_routine, mock_receipts):
        mock_receipts.return_value = []
        mock_routine.return_value = _make_mock_run_and_receipt()

        result = compose_governed_morning_brief(session_state={})

        assert isinstance(result, MorningBriefResult)
        mock_routine.assert_called_once()
        assert result.run.run_id == "run_test_001"
        assert result.receipt.receipt_id == "rcpt_test_001"

    @patch("src.conversation.morning_brief_handler.get_recent_receipts")
    @patch("src.conversation.morning_brief_handler.run_daily_brief_routine")
    def test_sections_formatted_to_text(self, mock_routine, mock_receipts):
        mock_receipts.return_value = []
        brief_dict = {
            "summary": "Your morning brief.",
            "sections": [
                {"title": "Weather", "items": ["Sunny", "72F"]},
                {"title": "Calendar", "items": ["Standup at 9am"]},
            ],
        }
        mock_routine.return_value = _make_mock_run_and_receipt(brief_dict)

        result = compose_governed_morning_brief(session_state={})

        assert "**Weather**" in result.text
        assert "**Calendar**" in result.text
        assert "Sunny" in result.text

    @patch("src.conversation.morning_brief_handler.get_recent_receipts")
    @patch("src.conversation.morning_brief_handler.run_daily_brief_routine")
    def test_empty_brief_uses_fallback_text(self, mock_routine, mock_receipts):
        mock_receipts.return_value = []
        mock_routine.return_value = _make_mock_run_and_receipt({})

        result = compose_governed_morning_brief(session_state={})

        assert result.text == "Morning brief assembled."

    @patch("src.conversation.morning_brief_handler.get_recent_receipts")
    @patch("src.conversation.morning_brief_handler.run_daily_brief_routine")
    def test_has_content_true_when_sections_exist(self, mock_routine, mock_receipts):
        mock_receipts.return_value = []
        brief_dict = {"sections": [{"title": "News", "items": ["Item 1"]}]}
        mock_routine.return_value = _make_mock_run_and_receipt(brief_dict)

        result = compose_governed_morning_brief(session_state={})
        assert result.has_content is True

    @patch("src.conversation.morning_brief_handler.get_recent_receipts")
    @patch("src.conversation.morning_brief_handler.run_daily_brief_routine")
    def test_has_content_false_when_empty(self, mock_routine, mock_receipts):
        mock_receipts.return_value = []
        mock_routine.return_value = _make_mock_run_and_receipt({})

        result = compose_governed_morning_brief(session_state={})
        assert result.has_content is False

    @patch("src.conversation.morning_brief_handler.get_recent_receipts")
    @patch("src.conversation.morning_brief_handler.run_daily_brief_routine")
    def test_passes_all_data_through(self, mock_routine, mock_receipts):
        mock_receipts.return_value = [{"id": "r1"}]
        mock_routine.return_value = _make_mock_run_and_receipt()

        compose_governed_morning_brief(
            session_state={"topic": "test"},
            memory_items=[{"m": 1}],
            weather_data={"temp": 72},
            calendar_data={"events": []},
        )

        call_kwargs = mock_routine.call_args.kwargs
        assert call_kwargs["session_state"] == {"topic": "test"}
        assert call_kwargs["memory_items"] == [{"m": 1}]
        assert call_kwargs["weather_data"] == {"temp": 72}
        assert call_kwargs["calendar_data"] == {"events": []}
        assert call_kwargs["recent_receipts"] == [{"id": "r1"}]

    @patch("src.conversation.morning_brief_handler.get_recent_receipts")
    @patch("src.conversation.morning_brief_handler.run_daily_brief_routine")
    def test_daily_loop_guidance_prioritizes_user_day_over_headlines(
        self,
        mock_routine,
        mock_receipts,
    ):
        mock_receipts.return_value = []
        mock_routine.return_value = _make_mock_run_and_receipt(
            {
                "sections": [
                    {"title": "News", "items": ["Headline 1", "Headline 2", "Headline 3"]}
                ]
            }
        )
        projection = DailyLoopProjection(
            next=(DailyLoopItem("Standup at 9 AM", "calendar"),),
            changed=(DailyLoopItem("Completed: Review draft", "receipts"),),
            waiting_on=(DailyLoopItem("Vendor reply", "governed_memory"),),
            open_loops=(),
            completed_today=(),
            unresolved_outcomes=(),
            recommended_next=DailyLoopItem("Standup at 9 AM", "recommendation_from:calendar"),
            context_today=(
                DailyLoopItem("Rain after 3 PM", "weather"),
                DailyLoopItem("Headline 1", "news"),
            ),
            sources=(DailyLoopSource("google_tasks", "not_connected", "Google Tasks is not connected."),),
        )

        result = compose_governed_morning_brief(
            session_state={},
            daily_loop_projection=projection,
        )

        assert result.text.index("Next: Standup at 9 AM") < result.text.index("Waiting on: Vendor reply")
        assert "Meaningful change: Completed: Review draft" in result.text
        assert "Recommendation (derived, not an instruction): Standup at 9 AM" in result.text
        assert "Supporting context: Rain after 3 PM" in result.text
        assert "Headline 1" not in result.text
        assert "Google Tasks is not connected" in result.text
        assert "No action was executed" in result.text

    @patch("src.conversation.morning_brief_handler.get_recent_receipts")
    @patch("src.conversation.morning_brief_handler.run_daily_brief_routine")
    def test_daily_loop_guidance_states_when_priorities_are_unknown(
        self,
        mock_routine,
        mock_receipts,
    ):
        mock_receipts.return_value = []
        mock_routine.return_value = _make_mock_run_and_receipt({"sections": []})
        projection = DailyLoopProjection(
            next=(),
            changed=(),
            waiting_on=(),
            open_loops=(),
            completed_today=(),
            unresolved_outcomes=(),
            recommended_next=None,
            context_today=(),
            sources=(),
        )

        result = compose_governed_morning_brief(
            session_state={},
            daily_loop_projection=projection,
        )

        assert "No upcoming item is known" in result.text
        assert "No waiting item is known" in result.text
        assert "No meaningful user-facing change is known" in result.text
        assert "No recommendation is supported" in result.text


# -------------------------------------------------------------------
# Weather converter
# -------------------------------------------------------------------

class TestWeatherConverter:
    def test_none_returns_none(self):
        assert weather_result_to_brief_data(None, "") is None

    def test_failed_result_returns_none(self):
        result = MagicMock()
        result.success = False
        assert weather_result_to_brief_data(result, "Sunny") is None

    def test_success_extracts_data(self):
        result = MagicMock()
        result.success = True
        result.data = {
            "widget": {
                "data": {"temperature": 72, "condition": "sunny"},
            },
        }
        data = weather_result_to_brief_data(result, "Sunny and warm")
        assert data["connected"] is True
        assert data["summary"] == "Sunny and warm"
        assert data["temperature"] == 72
        assert data["condition"] == "sunny"

    def test_missing_widget_data_returns_none_fields(self):
        result = MagicMock()
        result.success = True
        result.data = {}
        data = weather_result_to_brief_data(result, "Unknown")
        assert data["connected"] is True
        assert data["temperature"] is None


# -------------------------------------------------------------------
# Calendar converter
# -------------------------------------------------------------------

class TestCalendarConverter:
    def test_no_events_returns_none(self):
        assert calendar_result_to_brief_data({}) is None
        assert calendar_result_to_brief_data({"last_calendar_events": []}) is None
        assert calendar_result_to_brief_data({"last_calendar_events": "bad"}) is None

    def test_extracts_events(self):
        state = {
            "last_calendar_events": [
                {"title": "Standup", "time": "9:00 AM"},
                {"title": "Lunch", "time": "12:00 PM"},
            ],
        }
        data = calendar_result_to_brief_data(state)
        assert data["connected"] is True
        assert len(data["events"]) == 2
        assert data["events"][0]["title"] == "Standup"

    def test_limits_to_five_events(self):
        events = [{"title": f"Event {i}", "time": f"{i}:00"} for i in range(10)]
        data = calendar_result_to_brief_data({"last_calendar_events": events})
        assert len(data["events"]) == 5

    def test_skips_non_dict_events(self):
        state = {"last_calendar_events": [{"title": "Real", "time": "9am"}, "bad", 42]}
        data = calendar_result_to_brief_data(state)
        assert len(data["events"]) == 1


# -------------------------------------------------------------------
# MorningBriefResult is frozen
# -------------------------------------------------------------------

class TestMorningBriefResult:
    def test_frozen(self):
        run, receipt = _make_mock_run_and_receipt()
        result = MorningBriefResult(
            text="test", run=run, receipt=receipt, brief_dict={},
        )
        with pytest.raises(AttributeError):
            result.text = "modified"
