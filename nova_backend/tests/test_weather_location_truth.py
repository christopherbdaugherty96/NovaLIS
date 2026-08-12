import asyncio

import pytest
from src.actions.action_request import ActionRequest
from src.executors.info_snapshot_executor import WeatherSnapshotExecutor
from src.governor.governor_mediator import GovernorMediator, Invocation
from src.services.weather_service import WeatherService


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
