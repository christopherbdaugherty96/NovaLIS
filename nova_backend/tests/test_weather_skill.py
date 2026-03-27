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


def test_weather_skill_handles_forecast_style_queries():
    skill = WeatherSkill()

    assert skill.can_handle("what's the forecast today") is True
    assert skill.can_handle("temperature outside right now") is True
    assert skill.can_handle("is it going to rain today") is True
    assert skill.can_handle("what is the cpu temperature") is False


def test_weather_skill_returns_setup_hint_when_provider_not_configured(monkeypatch):
    async def fake_weather(self):
        raise RuntimeError("Missing WEATHER_API_KEY")

    monkeypatch.setattr(WeatherService, "get_current_weather", fake_weather)
    result = asyncio.run(WeatherSkill().handle("weather"))

    assert result.success is True
    assert "no provider key is configured" in result.message.lower()
    widget_data = (result.widget_data or {}).get("data") or {}
    assert widget_data["status"] == "not_configured"
    assert widget_data["connected"] is False
    assert "WEATHER_API_KEY" in widget_data["setup_hint"]
