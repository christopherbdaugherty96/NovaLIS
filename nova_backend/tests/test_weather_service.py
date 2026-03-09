import asyncio

from src.governor.network_mediator import NetworkMediator
from src.services.weather_service import WeatherService


def test_weather_service_returns_forecast_and_alerts(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "test-key")

    def fake_request(self, capability_id, method, url, json_payload=None, params=None, headers=None, **kwargs):
        return {
            "status_code": 200,
            "data": {
                "currentConditions": {"temp": 67, "conditions": "Cloudy"},
                "resolvedAddress": "Ann Arbor, MI, USA",
                "days": [
                    {"tempmax": 71, "tempmin": 55, "conditions": "Showers likely"},
                    {"tempmax": 64, "tempmin": 48, "conditions": "Windy"},
                ],
                "alerts": [
                    {"headline": "Flood Watch remains in effect"},
                ],
            },
        }

    monkeypatch.setattr(NetworkMediator, "request", fake_request)

    service = WeatherService(network=NetworkMediator())
    data = asyncio.run(service.get_current_weather())

    assert data["temperature"] == 67
    assert data["condition"] == "Cloudy"
    assert data["location"] == "Ann Arbor"
    assert data["forecast"].startswith("Today:")
    assert "Tomorrow:" in data["forecast"]
    assert data["alerts"] == ["Flood Watch remains in effect"]


def test_weather_service_retries_once_on_network_error(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "test-key")
    call_state = {"count": 0}

    def fake_request(self, capability_id, method, url, json_payload=None, params=None, headers=None, **kwargs):
        del capability_id, method, json_payload, params, headers, kwargs
        call_state["count"] += 1
        if call_state["count"] == 1:
            raise RuntimeError("temporary network issue")
        assert "Ann%20Arbor,%20MI" in url
        return {
            "status_code": 200,
            "data": {
                "currentConditions": {"temp": 63, "conditions": "Partly cloudy"},
                "resolvedAddress": "Ann Arbor, MI, USA",
                "days": [{"tempmax": 65, "tempmin": 50, "conditions": "Partly cloudy"}],
                "alerts": [],
            },
        }

    monkeypatch.setattr(NetworkMediator, "request", fake_request)

    service = WeatherService(network=NetworkMediator())
    data = asyncio.run(service.get_current_weather())
    assert call_state["count"] == 2
    assert data["temperature"] == 63
    assert data["location"] == "Ann Arbor"
