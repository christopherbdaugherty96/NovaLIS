import asyncio

from src.services.weather_service import WeatherService
from src.skills.weather import WeatherSkill


def test_weather_skill_widget_contains_forecast_and_alerts(monkeypatch):
    async def fake_weather(self):
        return {
            "temperature": 68,
            "condition": "Rain",
            "location": "Ann Arbor",
            "forecast": "Today: 70F/58F, Rain showers | Tomorrow: 64F/49F, Windy",
            "alerts": ["Flood Watch remains in effect"],
        }

    monkeypatch.setattr(WeatherService, "get_current_weather", fake_weather)
    result = asyncio.run(WeatherSkill().handle("weather"))

    assert result.success is True
    widget_data = (result.widget_data or {}).get("data") or {}
    assert widget_data["forecast"].startswith("Today:")
    assert widget_data["alerts"] == ["Flood Watch remains in effect"]
    assert "Alert active:" in result.message


def test_weather_skill_handles_no_alerts(monkeypatch):
    async def fake_weather(self):
        return {
            "temperature": 59,
            "condition": "Clear",
            "location": "Ann Arbor",
            "forecast": "Today: 61F/42F, Clear",
            "alerts": [],
        }

    monkeypatch.setattr(WeatherService, "get_current_weather", fake_weather)
    result = asyncio.run(WeatherSkill().handle("weather"))

    assert result.success is True
    widget_data = (result.widget_data or {}).get("data") or {}
    assert widget_data["alerts"] == []
    assert "Alert active:" not in result.message

