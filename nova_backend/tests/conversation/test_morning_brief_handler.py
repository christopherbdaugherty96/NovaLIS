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

from src.conversation.morning_brief_handler import (
    MORNING_BRIEF_TRIGGERS,
    MorningBriefResult,
    calendar_result_to_brief_data,
    compose_governed_morning_brief,
    is_morning_brief_request,
    weather_result_to_brief_data,
)


# -------------------------------------------------------------------
# Trigger detection
# -------------------------------------------------------------------

class TestTriggerDetection:
    @pytest.mark.parametrize("trigger", sorted(MORNING_BRIEF_TRIGGERS))
    def test_known_triggers_match(self, trigger: str):
        assert is_morning_brief_request(trigger) is True

    def test_non_trigger_rejected(self):
        assert is_morning_brief_request("hello") is False
        assert is_morning_brief_request("good morning") is False
        assert is_morning_brief_request("") is False

    def test_triggers_are_lowercase(self):
        for t in MORNING_BRIEF_TRIGGERS:
            assert t == t.lower()


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
