from src.actions.action_request import ActionRequest
from src.base_skill import SkillResult
from src.executors.info_snapshot_executor import (
    CalendarSnapshotExecutor,
    NewsSnapshotExecutor,
    WeatherSnapshotExecutor,
)


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

