# tests/brief/test_daily_brief.py
"""Tests for the Daily Brief synthesis module.

All tests are fully isolated: no LLM calls, no external I/O,
no capability invocations, no filesystem access.
"""

from __future__ import annotations

import pytest

from src.brief.daily_brief import (
    BriefConfidence,
    BriefSection,
    DailyBrief,
    brief_to_action_result,
    brief_to_cognitive_result,
    compose_daily_brief,
    is_daily_brief_request,
)


# ---------------------------------------------------------------------------
# BriefSection
# ---------------------------------------------------------------------------

class TestBriefSection:
    def test_minimal_construction(self):
        s = BriefSection(title="Focus", items=("do something",))
        assert s.title == "Focus"
        assert s.items == ("do something",)
        assert s.confidence == BriefConfidence.MEDIUM

    def test_empty_items_allowed(self):
        s = BriefSection(title="Focus", items=())
        assert s.is_empty is True

    def test_empty_title_raises(self):
        with pytest.raises(ValueError, match="title must not be empty"):
            BriefSection(title="   ", items=())

    def test_to_dict_structure(self):
        s = BriefSection(
            title="Next Actions",
            items=("fix bug", "write test"),
            confidence=BriefConfidence.HIGH,
            source_label="memory",
        )
        d = s.to_dict()
        assert d["title"] == "Next Actions"
        assert d["items"] == ["fix bug", "write test"]
        assert d["confidence"] == "high"
        assert d["source_label"] == "memory"

    def test_immutable(self):
        s = BriefSection(title="X", items=("a",))
        with pytest.raises((AttributeError, TypeError)):
            s.title = "Y"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# DailyBrief
# ---------------------------------------------------------------------------

class TestDailyBrief:
    def _make(self, **kwargs) -> DailyBrief:
        defaults = {
            "date_covered": "2026-05-01",
            "timestamp_utc": "2026-05-01T12:00:00+00:00",
            "sections": (BriefSection(title="Focus", items=("do something",)),),
        }
        defaults.update(kwargs)
        return DailyBrief(**defaults)

    def test_construction(self):
        brief = self._make()
        assert brief.date_covered == "2026-05-01"
        assert brief.execution_performed is False
        assert brief.authorization_granted is False

    def test_non_authorizing_enforced(self):
        with pytest.raises(ValueError, match="non-authorizing"):
            self._make(execution_performed=True)
        with pytest.raises(ValueError, match="non-authorizing"):
            self._make(authorization_granted=True)

    def test_empty_date_raises(self):
        with pytest.raises(ValueError, match="date_covered"):
            self._make(date_covered="  ")

    def test_to_dict_always_false_authority(self):
        brief = self._make()
        d = brief.to_dict()
        assert d["execution_performed"] is False
        assert d["authorization_granted"] is False

    def test_to_dict_structure(self):
        brief = self._make(
            sections=(
                BriefSection(title="Focus", items=("write code",)),
                BriefSection(title="Open Loops", items=()),
            ),
            summary="Today: write code.",
            confidence=BriefConfidence.HIGH,
            sources_consulted=("memory", "session"),
        )
        d = brief.to_dict()
        assert d["summary"] == "Today: write code."
        assert d["confidence"] == "high"
        assert d["sources_consulted"] == ["memory", "session"]
        assert len(d["sections"]) == 2

    def test_has_content_false_when_all_empty(self):
        brief = self._make(
            sections=(BriefSection(title="X", items=()),)
        )
        assert brief.has_content is False

    def test_has_content_true_when_any_filled(self):
        brief = self._make(
            sections=(
                BriefSection(title="X", items=()),
                BriefSection(title="Y", items=("item",)),
            )
        )
        assert brief.has_content is True

    def test_to_speakable_uses_summary(self):
        brief = self._make(summary="Focus: write code.")
        assert brief.to_speakable() == "Focus: write code."

    def test_to_speakable_fallback(self):
        brief = self._make(
            summary="",
            sections=(BriefSection(title="Focus", items=("do this",)),),
        )
        text = brief.to_speakable()
        assert "do this" in text

    def test_to_speakable_empty_brief(self):
        brief = self._make(summary="", sections=())
        assert brief.to_speakable() == "No brief data available."


# ---------------------------------------------------------------------------
# compose_daily_brief
# ---------------------------------------------------------------------------

class TestComposeDailyBrief:
    def test_empty_inputs_returns_valid_brief(self):
        brief = compose_daily_brief()
        assert isinstance(brief, DailyBrief)
        assert brief.date_covered
        assert brief.execution_performed is False
        assert brief.authorization_granted is False

    def test_today_focus_from_session_topic(self):
        brief = compose_daily_brief(
            session_state={"active_topic": "search synthesis refactor"}
        )
        focus = next(s for s in brief.sections if s.title == "Today's Focus")
        assert any("search synthesis refactor" in item for item in focus.items)

    def test_today_focus_from_conversation_context(self):
        brief = compose_daily_brief(
            session_state={"conversation_context": {"topic": "daily brief MVP"}}
        )
        focus = next(s for s in brief.sections if s.title == "Today's Focus")
        assert any("daily brief MVP" in item for item in focus.items)

    def test_working_context_task_goal(self):
        brief = compose_daily_brief(
            working_context={"task_goal": "implement daily brief", "active_app": "VSCode"}
        )
        focus = next(s for s in brief.sections if s.title == "Today's Focus")
        assert any("implement daily brief" in item for item in focus.items)
        assert any("VSCode" in item for item in focus.items)

    def test_next_actions_from_memory(self):
        memory = [
            {"category": "action", "content": "fix the config bug"},
            {"category": "task", "content": "write tests"},
            {"category": "note", "content": "some note"},
        ]
        brief = compose_daily_brief(memory_items=memory)
        section = next(s for s in brief.sections if s.title == "Top Next Actions")
        assert "fix the config bug" in section.items
        assert "write tests" in section.items
        assert "some note" not in section.items

    def test_open_loops_from_memory(self):
        memory = [
            {"category": "open_loop", "content": "decide on architecture"},
            {"category": "pending", "content": "waiting for API keys"},
        ]
        brief = compose_daily_brief(memory_items=memory)
        section = next(s for s in brief.sections if s.title == "Open Loops")
        assert "decide on architecture" in section.items
        assert "waiting for API keys" in section.items

    def test_decisions_from_memory(self):
        memory = [{"category": "decision", "content": "use frozen dataclasses"}]
        brief = compose_daily_brief(memory_items=memory)
        section = next(s for s in brief.sections if s.title == "Recent Decisions")
        assert "use frozen dataclasses" in section.items

    def test_memory_reminders(self):
        memory = [{"category": "reminder", "content": "check daily brief branch"}]
        brief = compose_daily_brief(memory_items=memory)
        section = next(s for s in brief.sections if s.title == "Memory Reminders")
        assert "check daily brief branch" in section.items

    def test_blocked_items_from_memory(self):
        memory = [{"category": "blocked", "content": "waiting on external API"}]
        brief = compose_daily_brief(memory_items=memory)
        section = next(s for s in brief.sections if s.title == "Blocked Items")
        assert "waiting on external API" in section.items

    def test_recent_receipts_section(self):
        receipts = [
            {
                "event_type": "ACTION_COMPLETED",
                "timestamp_utc": "2026-05-01T10:30:00+00:00",
                "capability_name": "governed_web_search",
            },
            {
                "event_type": "MEMORY_ITEM_SAVED",
                "timestamp_utc": "2026-05-01T09:15:00+00:00",
            },
        ]
        brief = compose_daily_brief(recent_receipts=receipts)
        section = next(s for s in brief.sections if s.title == "Recent Actions")
        assert len(section.items) == 2
        assert any("action completed" in item for item in section.items)
        assert any("memory saved" in item for item in section.items)

    def test_recommended_next_step_prefers_action(self):
        memory = [
            {"category": "action", "content": "refactor executor"},
            {"category": "open_loop", "content": "open loop item"},
        ]
        brief = compose_daily_brief(memory_items=memory)
        section = next(s for s in brief.sections if s.title == "Recommended Next Step")
        assert section.items
        assert "refactor executor" in section.items[0]

    def test_recommended_next_step_falls_back_to_loop(self):
        memory = [{"category": "open_loop", "content": "resolve arch question"}]
        brief = compose_daily_brief(memory_items=memory)
        section = next(s for s in brief.sections if s.title == "Recommended Next Step")
        assert section.items
        assert "resolve arch question" in section.items[0]

    def test_recommended_next_step_empty_when_no_data(self):
        brief = compose_daily_brief()
        section = next(s for s in brief.sections if s.title == "Recommended Next Step")
        assert section.is_empty

    def test_sources_consulted_populated(self):
        brief = compose_daily_brief(
            session_state={"active_topic": "x"},
            memory_items=[{"category": "action", "content": "y"}],
            recent_receipts=[{"event_type": "ACTION_COMPLETED"}],
        )
        assert "memory" in brief.sources_consulted
        assert "receipts" in brief.sources_consulted
        assert "session" in brief.sources_consulted

    def test_confidence_high_with_rich_data(self):
        memory = [
            {"category": "action", "content": f"action {i}"} for i in range(3)
        ] + [
            {"category": "open_loop", "content": f"loop {i}"} for i in range(3)
        ]
        receipts = [
            {"event_type": "ACTION_COMPLETED", "capability_name": f"cap{i}"}
            for i in range(3)
        ]
        brief = compose_daily_brief(memory_items=memory, recent_receipts=receipts)
        assert brief.confidence == BriefConfidence.HIGH

    def test_confidence_low_with_no_data(self):
        brief = compose_daily_brief()
        assert brief.confidence == BriefConfidence.LOW

    def test_malformed_memory_items_skipped(self):
        memory = [
            None,
            {"category": "action"},  # no content
            {"content": ""},  # empty content
            {"category": "action", "content": "valid item"},
        ]
        brief = compose_daily_brief(memory_items=memory)  # type: ignore[arg-type]
        section = next(s for s in brief.sections if s.title == "Top Next Actions")
        assert "valid item" in section.items
        assert len(section.items) == 1

    def test_section_item_cap(self):
        memory = [{"category": "action", "content": f"action {i}"} for i in range(20)]
        brief = compose_daily_brief(memory_items=memory)
        section = next(s for s in brief.sections if s.title == "Top Next Actions")
        assert len(section.items) <= 5


# ---------------------------------------------------------------------------
# Weather, Calendar, Important Emails sections
# ---------------------------------------------------------------------------

class TestWeatherSection:
    def test_live_weather_data(self):
        weather = {
            "connected": True,
            "status": "ok",
            "summary": "72 degrees F and sunny in Detroit.",
            "forecast": "Partly cloudy later.",
            "alerts": [],
        }
        brief = compose_daily_brief(weather_data=weather)
        section = next(s for s in brief.sections if s.title == "Weather")
        assert not section.is_empty
        assert any("72 degrees" in item for item in section.items)
        assert section.confidence == BriefConfidence.HIGH
        assert section.source_label == "weather"

    def test_weather_with_alert(self):
        weather = {
            "connected": True,
            "status": "ok",
            "summary": "55 F and windy.",
            "forecast": "",
            "alerts": ["Severe thunderstorm warning"],
        }
        brief = compose_daily_brief(weather_data=weather)
        section = next(s for s in brief.sections if s.title == "Weather")
        assert any("Alert:" in item for item in section.items)

    def test_weather_not_configured(self):
        weather = {
            "connected": False,
            "status": "not_configured",
            "setup_hint": "Add WEATHER_API_KEY to enable live weather.",
            "message": "",
        }
        brief = compose_daily_brief(weather_data=weather)
        section = next(s for s in brief.sections if s.title == "Weather")
        assert section.confidence == BriefConfidence.LOW
        assert any("WEATHER_API_KEY" in item for item in section.items)

    def test_weather_unavailable(self):
        weather = {"connected": False, "status": "unavailable"}
        brief = compose_daily_brief(weather_data=weather)
        section = next(s for s in brief.sections if s.title == "Weather")
        assert section.confidence == BriefConfidence.LOW

    def test_weather_none_returns_empty_section(self):
        brief = compose_daily_brief(weather_data=None)
        section = next(s for s in brief.sections if s.title == "Weather")
        assert section.is_empty

    def test_weather_in_sources_when_connected(self):
        brief = compose_daily_brief(
            weather_data={"connected": True, "status": "ok", "summary": "Sunny."}
        )
        assert "weather" in brief.sources_consulted

    def test_weather_not_in_sources_when_not_connected(self):
        brief = compose_daily_brief(
            weather_data={"connected": False, "status": "not_configured"}
        )
        assert "weather" not in brief.sources_consulted


class TestCalendarSection:
    def test_calendar_with_events(self):
        calendar = {
            "connected": True,
            "status": "ok",
            "events": [
                {"title": "Team standup", "time": "9:00 AM"},
                {"title": "Lunch with client", "time": "12:30 PM"},
            ],
            "scope": "today",
            "source_label": "work.ics",
            "setup_hint": "",
        }
        brief = compose_daily_brief(calendar_data=calendar)
        section = next(s for s in brief.sections if s.title == "Calendar")
        assert not section.is_empty
        assert any("Team standup" in item for item in section.items)
        assert any("Lunch with client" in item for item in section.items)
        assert section.confidence == BriefConfidence.HIGH
        assert section.source_label == "work.ics"

    def test_calendar_empty_day(self):
        calendar = {
            "connected": True,
            "status": "ok",
            "events": [],
            "scope": "today",
            "source_label": "personal.ics",
            "setup_hint": "",
        }
        brief = compose_daily_brief(calendar_data=calendar)
        section = next(s for s in brief.sections if s.title == "Calendar")
        assert not section.is_empty
        assert any("Nothing on your calendar" in item for item in section.items)

    def test_calendar_not_connected(self):
        calendar = {
            "connected": False,
            "status": "not_connected",
            "events": [],
            "scope": "today",
            "source_label": "",
            "setup_hint": "Add a local .ics file in Settings.",
        }
        brief = compose_daily_brief(calendar_data=calendar)
        section = next(s for s in brief.sections if s.title == "Calendar")
        assert section.confidence == BriefConfidence.LOW
        assert any(".ics" in item for item in section.items)

    def test_calendar_none_returns_empty_section(self):
        brief = compose_daily_brief(calendar_data=None)
        section = next(s for s in brief.sections if s.title == "Calendar")
        assert section.is_empty

    def test_calendar_in_sources_when_connected(self):
        brief = compose_daily_brief(
            calendar_data={"connected": True, "status": "ok", "events": [], "scope": "today", "source_label": "x.ics"}
        )
        assert "calendar" in brief.sources_consulted

    def test_calendar_not_in_sources_when_not_connected(self):
        brief = compose_daily_brief(
            calendar_data={"connected": False, "status": "not_connected"}
        )
        assert "calendar" not in brief.sources_consulted


class TestImportantEmailsSection:
    def test_placeholder_when_none(self):
        brief = compose_daily_brief(important_emails=None)
        section = next(s for s in brief.sections if s.title == "Important Emails")
        assert not section.is_empty
        assert section.source_label == "email_placeholder"
        assert section.confidence == BriefConfidence.LOW
        assert any("not configured" in item.lower() for item in section.items)

    def test_placeholder_when_empty_list(self):
        brief = compose_daily_brief(important_emails=[])
        section = next(s for s in brief.sections if s.title == "Important Emails")
        assert section.source_label == "email_placeholder"

    def test_live_emails(self):
        emails = [
            {"sender": "alice@example.com", "subject": "Project update"},
            {"sender": "bob@example.com", "subject": "Invoice due"},
        ]
        brief = compose_daily_brief(important_emails=emails)
        section = next(s for s in brief.sections if s.title == "Important Emails")
        assert section.source_label == "email"
        assert section.confidence == BriefConfidence.HIGH
        assert any("Project update" in item for item in section.items)
        assert any("Invoice due" in item for item in section.items)

    def test_email_cap_at_max_items(self):
        emails = [{"sender": f"u{i}@x.com", "subject": f"Subject {i}"} for i in range(10)]
        brief = compose_daily_brief(important_emails=emails)
        section = next(s for s in brief.sections if s.title == "Important Emails")
        assert len(section.items) <= 5


# ---------------------------------------------------------------------------
# Output adapters
# ---------------------------------------------------------------------------

class TestBriefAdapters:
    def _brief(self) -> DailyBrief:
        return compose_daily_brief(
            session_state={"active_topic": "daily operating baseline"},
            memory_items=[
                {"category": "action", "content": "build daily brief"},
                {"category": "open_loop", "content": "wire into runtime"},
            ],
        )

    def test_cognitive_result_structure(self):
        brief = self._brief()
        result = brief_to_cognitive_result(brief)
        assert result.summary
        assert result.module_name == "daily_brief"
        assert 0.0 <= result.confidence <= 1.0
        assert result.key_points

    def test_cognitive_result_passes_validation(self):
        from src.cognition.cognitive_layer_contract import validate_cognitive_result
        result = brief_to_cognitive_result(self._brief())
        validate_cognitive_result(result)  # must not raise

    def test_cognitive_result_empty_brief(self):
        brief = compose_daily_brief()
        result = brief_to_cognitive_result(brief)
        assert isinstance(result.summary, str)

    def test_action_result_is_read_only(self):
        result = brief_to_action_result(self._brief(), request_id="test-001")
        assert result.success is True
        assert result.authority_class == "read_only"
        assert result.external_effect is False
        assert result.reversible is True
        assert result.risk_level == "low"

    def test_action_result_structured_data(self):
        brief = self._brief()
        result = brief_to_action_result(brief)
        sd = result.structured_data
        assert "sections" in sd
        assert "date_covered" in sd
        assert sd["execution_performed"] is False
        assert sd["authorization_granted"] is False

    def test_action_result_speakable(self):
        result = brief_to_action_result(self._brief())
        assert result.speakable_text

    def test_action_result_no_capability_id(self):
        result = brief_to_action_result(self._brief())
        assert result.capability_id is None


# ---------------------------------------------------------------------------
# Intent detection
# ---------------------------------------------------------------------------

class TestIsDailyBriefRequest:
    @pytest.mark.parametrize("query", [
        "give me my daily brief",
        "Daily Brief please",
        "morning brief",
        "what's on my agenda today",
        "what's on my plate",
        "brief me",
        "catch me up",
        "where am I",
        "what should I focus on",
        "what are my open loops",
        "what's open",
        "what's pending",
    ])
    def test_matches(self, query: str):
        assert is_daily_brief_request(query) is True

    @pytest.mark.parametrize("query", [
        "search for Python docs",
        "what is the weather",
        "write an email",
        "hello",
        "how does governed search work",
    ])
    def test_no_match(self, query: str):
        assert is_daily_brief_request(query) is False

    def test_empty_string(self):
        assert is_daily_brief_request("") is False

    def test_none_safe(self):
        assert is_daily_brief_request(None) is False  # type: ignore[arg-type]
