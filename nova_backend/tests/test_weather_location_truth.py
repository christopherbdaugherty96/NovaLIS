import asyncio

import pytest
from src import brain_server
from src.actions.action_request import ActionRequest
from src.executors.info_snapshot_executor import WeatherSnapshotExecutor
from src.governor.governor_mediator import GovernorMediator, Invocation
from src.services.weather_service import WeatherService

from tests.phase45._websocket_test_helpers import _chat_messages, _ScriptedWebSocket


@pytest.mark.parametrize(
    ("text", "location"),
    [
        ("weather in Detroit", "Detroit"),
        ("weather in Chicago", "Chicago"),
        ("weather in Battle Creek", "Battle Creek"),
        ("what's the weather in Detroit?", "Detroit"),
    ],
)
def test_explicit_weather_location_survives_governed_routing(text, location):
    invocation = GovernorMediator.parse_governed_invocation(text)

    assert isinstance(invocation, Invocation)
    assert invocation.capability_id == 55
    assert invocation.params == {"location": location}


def test_weather_without_explicit_location_preserves_default_behavior():
    invocation = GovernorMediator.parse_governed_invocation("what's the weather?")

    assert isinstance(invocation, Invocation)
    assert invocation.capability_id == 55
    assert invocation.params == {}


@pytest.mark.parametrize("location", ["Detroit", "Chicago", "Battle Creek"])
def test_weather_executor_queries_and_reports_explicit_location(monkeypatch, location):
    observed_locations = []

    async def fake_weather(self):
        observed_locations.append(self.location)
        return {
            "temperature": 68,
            "condition": "Clear",
            "location": location,
            "forecast": "Today: clear",
            "alerts": [],
        }

    monkeypatch.setattr(WeatherService, "get_current_weather", fake_weather)

    result = WeatherSnapshotExecutor().execute(
        ActionRequest(capability_id=55, params={"location": location})
    )

    assert result.success is True
    assert observed_locations == [location]
    assert result.data["widget"]["data"]["location"] == location
    assert f"Location: {location}" in result.message
    assert "Ann Arbor" not in result.message


def test_explicit_location_provider_failure_does_not_fall_back(monkeypatch):
    observed_locations = []

    async def fail_weather(self):
        observed_locations.append(self.location)
        raise RuntimeError("provider rejected the requested location")

    monkeypatch.setattr(WeatherService, "get_current_weather", fail_weather)

    result = WeatherSnapshotExecutor().execute(
        ActionRequest(capability_id=55, params={"location": "Detroit"})
    )

    assert result.success is False
    assert observed_locations == ["Detroit"]
    assert "Detroit" in result.message
    assert "Ann Arbor" not in result.message
    assert result.data["widget"]["data"]["location"] == "Detroit"


def test_weather_service_uses_explicit_location_in_provider_request(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "test-key")
    requested_urls = []

    def fake_request(self, capability_id, method, url, **kwargs):
        del self, capability_id, method, kwargs
        requested_urls.append(url)
        return {
            "status_code": 200,
            "data": {
                "currentConditions": {"temp": 64, "conditions": "Cloudy"},
                "resolvedAddress": "Battle Creek, MI, USA",
                "days": [],
                "alerts": [],
            },
        }

    monkeypatch.setattr("src.governor.network_mediator.NetworkMediator.request", fake_request)

    data = asyncio.run(WeatherService(location="Battle Creek").get_current_weather())

    assert len(requested_urls) == 1
    assert "Battle%20Creek/today" in requested_urls[0]
    assert "Ann%20Arbor" not in requested_urls[0]
    assert data["location"] == "Battle Creek"


def test_explicit_location_provider_error_never_retries_with_default(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "test-key")
    monkeypatch.setattr("src.services.weather_service.WEATHER_MAX_RETRIES", 0)
    requested_urls = []

    def fail_request(self, capability_id, method, url, **kwargs):
        del self, capability_id, method, kwargs
        requested_urls.append(url)
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr("src.governor.network_mediator.NetworkMediator.request", fail_request)

    with pytest.raises(RuntimeError, match="Weather API failed"):
        asyncio.run(WeatherService(location="Detroit").get_current_weather())

    assert len(requested_urls) == 1
    assert "Detroit/today" in requested_urls[0]
    assert "Ann%20Arbor" not in requested_urls[0]


def _weather_widgets(ws: _ScriptedWebSocket) -> list[dict]:
    return [message for message in ws.sent_messages if message.get("type") == "weather"]


@pytest.mark.slow
@pytest.mark.parametrize("location", ["Detroit", "Chicago", "Battle Creek"])
def test_explicit_weather_location_survives_full_websocket_path(monkeypatch, location):
    observed_locations = []

    async def fake_weather(self):
        observed_locations.append(self.location)
        return {
            "temperature": 68,
            "condition": "Clear",
            "location": location,
            "forecast": "Today: clear",
            "alerts": [],
        }

    async def must_not_run(*args, **kwargs):
        raise AssertionError("GeneralChat must not run for a deterministic weather request.")

    monkeypatch.setattr(WeatherService, "get_current_weather", fake_weather)
    monkeypatch.setattr(brain_server, "run_general_chat_fallback", must_not_run)
    ws = _ScriptedWebSocket([f"weather in {location}"])

    asyncio.run(brain_server.websocket_endpoint(ws))

    chats = _chat_messages(ws)
    widgets = _weather_widgets(ws)
    assert observed_locations == [location]
    assert any(f"Location: {location}" in message for message in chats)
    assert all("Ann Arbor" not in message for message in chats)
    assert widgets[-1]["data"]["location"] == location


@pytest.mark.slow
def test_default_weather_still_uses_configured_location_through_websocket(monkeypatch):
    observed_locations = []

    async def fake_weather(self):
        observed_locations.append(self.location)
        return {
            "temperature": 68,
            "condition": "Clear",
            "location": self.location,
            "forecast": "Today: clear",
            "alerts": [],
        }

    monkeypatch.setattr(WeatherService, "get_current_weather", fake_weather)
    ws = _ScriptedWebSocket(["weather"])

    asyncio.run(brain_server.websocket_endpoint(ws))

    assert observed_locations == [WeatherService.DEFAULT_LOCATION]
    assert _weather_widgets(ws)[-1]["data"]["location"] == WeatherService.DEFAULT_LOCATION


@pytest.mark.slow
def test_explicit_weather_failure_never_falls_back_in_full_websocket_path(monkeypatch):
    observed_locations = []

    async def fail_weather(self):
        observed_locations.append(self.location)
        raise RuntimeError("provider rejected the requested location")

    async def must_not_run(*args, **kwargs):
        raise AssertionError("GeneralChat must not run for a deterministic weather request.")

    monkeypatch.setattr(WeatherService, "get_current_weather", fail_weather)
    monkeypatch.setattr(brain_server, "run_general_chat_fallback", must_not_run)
    ws = _ScriptedWebSocket(["weather in Zzyzx Invalid Place"])

    asyncio.run(brain_server.websocket_endpoint(ws))

    chats = _chat_messages(ws)
    widgets = _weather_widgets(ws)
    assert observed_locations == ["Zzyzx Invalid Place"]
    assert any(
        "Weather for Zzyzx Invalid Place is unavailable right now." in message
        for message in chats
    )
    assert all("Ann Arbor" not in message for message in chats)
    assert widgets[-1]["data"]["location"] == "Zzyzx Invalid Place"
