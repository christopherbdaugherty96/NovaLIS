from datetime import datetime, timedelta

from src.actions.action_request import ActionRequest
from src.base_skill import SkillResult
from src.executors.info_snapshot_executor import (
    CalendarSnapshotExecutor,
    NewsSnapshotExecutor,
    WeatherSnapshotExecutor,
)
from src.governor.governor_mediator import GovernorMediator, Invocation


def test_weather_snapshot_executor_success(monkeypatch):
    async def fake_handle(self, query: str):
        del self
        assert query == "weather"
        return SkillResult(
            success=True,
            message="From the last update: 52 degrees and clear skies.",
            widget_data={
                "type": "weather",
                "data": {
                    "summary": "From the last update: 52 degrees and clear skies.",
                    "temperature": 52,
                    "condition": "Clear",
                    "location": "Ann Arbor",
                    "forecast": "Today sunny.",
                    "alerts": [],
                },
            },
            skill="weather",
        )

    monkeypatch.setattr("src.skills.weather.WeatherSkill.handle", fake_handle)
    result = WeatherSnapshotExecutor().execute(ActionRequest(capability_id=55, params={}))

    assert result.success is True
    assert isinstance(result.data, dict)
    assert result.data["widget"]["type"] == "weather"
    assert "Location: Ann Arbor" in result.message
    assert result.data["follow_up_prompts"]


def test_weather_snapshot_executor_failure_includes_fallback_widget(monkeypatch):
    async def fake_handle(self, query: str):
        del self, query
        return SkillResult(success=False, message="Weather is currently unavailable.", skill="weather")

    monkeypatch.setattr("src.skills.weather.WeatherSkill.handle", fake_handle)
    result = WeatherSnapshotExecutor().execute(ActionRequest(capability_id=55, params={}))

    assert result.success is False
    assert isinstance(result.data, dict)
    assert result.data["widget"]["type"] == "weather"
    assert "unavailable" in str(result.data["widget"]["data"]["summary"]).lower()


def test_weather_snapshot_executor_failure_preserves_skill_widget(monkeypatch):
    widget = {
        "type": "weather",
        "data": {
            "summary": "Weather is available, but no provider key is configured yet.",
            "status": "not_configured",
            "connected": False,
            "setup_hint": "Add WEATHER_API_KEY to enable live weather.",
        },
    }

    async def fake_handle(self, query: str):
        del self, query
        return SkillResult(
            success=False,
            message=widget["data"]["summary"],
            widget_data=widget,
            skill="weather",
        )

    monkeypatch.setattr("src.skills.weather.WeatherSkill.handle", fake_handle)
    result = WeatherSnapshotExecutor().execute(ActionRequest(capability_id=55, params={}))

    assert result.success is False
    assert result.external_effect is False
    assert result.data["widget"] == widget


def test_news_snapshot_executor_success(monkeypatch):
    async def fake_handle(self, query: str):
        del self
        assert query == "news"
        return SkillResult(
            success=True,
            message="Here are the latest headlines.",
            widget_data={
                "type": "news",
                "items": [{"title": "Top headline", "url": "https://example.com"}],
                "summary": "Top focus: headline one.",
                "categories": {},
            },
            skill="news",
        )

    monkeypatch.setattr("src.skills.news.NewsSkill.handle", fake_handle)
    result = NewsSnapshotExecutor().execute(ActionRequest(capability_id=56, params={}))

    assert result.success is True
    assert isinstance(result.data, dict)
    assert result.data["widget"]["type"] == "news"
    assert len(result.data["widget"]["items"]) == 1
    assert "summarize headline 1" in result.message.lower()
    assert result.data["follow_up_prompts"]


def test_news_snapshot_executor_failure_preserves_skill_widget(monkeypatch):
    widget = {
        "type": "news",
        "items": [],
        "summary": "News unavailable right now.",
        "categories": {},
        "status": "unavailable",
    }

    async def fake_handle(self, query: str):
        del self, query
        return SkillResult(
            success=False,
            message="I couldn't pull fresh headlines right now.",
            widget_data=widget,
            skill="news",
        )

    monkeypatch.setattr("src.skills.news.NewsSkill.handle", fake_handle)
    result = NewsSnapshotExecutor().execute(ActionRequest(capability_id=56, params={}))

    assert result.success is False
    assert result.external_effect is False
    assert result.data["widget"] == widget


def test_calendar_snapshot_executor_success(monkeypatch):
    async def fake_handle(self, query: str):
        del self
        assert query == "calendar"
        return SkillResult(
            success=True,
            message="Today's calendar: 9:00 AM Standup.",
            widget_data={
                "type": "calendar",
                "summary": "9:00 AM Standup",
                "events": [{"title": "Standup", "time": "9:00 AM"}],
            },
            skill="calendar",
        )

    monkeypatch.setattr("src.skills.calendar.CalendarSkill.handle", fake_handle)
    result = CalendarSnapshotExecutor().execute(ActionRequest(capability_id=57, params={}))

    assert result.success is True
    assert isinstance(result.data, dict)
    assert result.data["widget"]["type"] == "calendar"
    assert result.data["widget"]["events"][0]["title"] == "Standup"
    assert "Upcoming events loaded: 1" in result.message
    assert result.data["follow_up_prompts"]


def test_calendar_snapshot_executor_preserves_mediator_temporal_scope(monkeypatch, tmp_path):
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    later = today + timedelta(days=3)
    ics_path = tmp_path / "calendar.ics"
    ics_path.write_text(
        "BEGIN:VCALENDAR\n"
        "BEGIN:VEVENT\n"
        f"DTSTART:{today.strftime('%Y%m%dT090000')}\n"
        "SUMMARY:Today Only\n"
        "END:VEVENT\n"
        "BEGIN:VEVENT\n"
        f"DTSTART:{tomorrow.strftime('%Y%m%dT143000')}\n"
        "SUMMARY:Tomorrow Only\n"
        "END:VEVENT\n"
        "BEGIN:VEVENT\n"
        f"DTSTART:{later.strftime('%Y%m%dT110000')}\n"
        "SUMMARY:Later Only\n"
        "END:VEVENT\n"
        "END:VCALENDAR\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("NOVA_CALENDAR_ICS_PATH", str(ics_path))

    cases = (
        ("calendar", "today", ["Today Only"]),
        ("calendar tomorrow", "tomorrow", ["Tomorrow Only"]),
        ("tomorrow's schedule", "tomorrow", ["Tomorrow Only"]),
        ("what do i have tomorrow", "tomorrow", ["Tomorrow Only"]),
        ("upcoming events", "upcoming", ["Today Only", "Tomorrow Only", "Later Only"]),
    )
    for command, expected_scope, expected_titles in cases:
        invocation = GovernorMediator.parse_governed_invocation(command)
        assert isinstance(invocation, Invocation)
        result = CalendarSnapshotExecutor().execute(
            ActionRequest(capability_id=57, params=invocation.params)
        )

        assert result.success is True
        widget = result.data["widget"]
        assert widget["scope"] == expected_scope
        assert [event["title"] for event in widget["events"]] == expected_titles


def test_calendar_snapshot_executor_rejects_unknown_scope_by_falling_back_to_today(monkeypatch):
    async def fake_handle(self, query: str):
        del self
        assert query == "calendar"
        return SkillResult(
            success=True,
            message="You're clear today.",
            widget_data={"type": "calendar", "scope": "today", "events": []},
            skill="calendar",
        )

    monkeypatch.setattr("src.skills.calendar.CalendarSkill.handle", fake_handle)
    result = CalendarSnapshotExecutor().execute(
        ActionRequest(capability_id=57, params={"scope": "arbitrary"})
    )

    assert result.success is True
    assert result.data["widget"]["scope"] == "today"


def test_calendar_snapshot_executor_failure_preserves_skill_widget(monkeypatch):
    widget = {
        "type": "calendar",
        "summary": "Not connected.",
        "events": [],
        "connected": False,
        "status": "not_connected",
        "setup_hint": "Add a local .ics file in Settings.",
    }

    async def fake_handle(self, query: str):
        del self, query
        return SkillResult(
            success=False,
            message="Calendar is ready when you are.",
            widget_data=widget,
            skill="calendar",
        )

    monkeypatch.setattr("src.skills.calendar.CalendarSkill.handle", fake_handle)
    result = CalendarSnapshotExecutor().execute(ActionRequest(capability_id=57, params={}))

    assert result.success is False
    assert result.external_effect is False
    assert result.data["widget"] == widget
