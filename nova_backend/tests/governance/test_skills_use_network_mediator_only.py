from __future__ import annotations

from pathlib import Path
import sys
import asyncio

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from unittest.mock import patch

from src.skills.weather import WeatherSkill
from src.skills.news import NewsSkill
from src.governor.network_mediator import NetworkMediator


def test_skill_network_calls_are_mediator_intercepted(monkeypatch):
    calls: list[dict] = []

    def fake_mediator_request(self, capability_id, method, url, json_payload=None, params=None, headers=None, **kwargs):
        calls.append({"capability_id": capability_id, "method": method, "url": url})
        if "visualcrossing" in url:
            return {
                "status_code": 200,
                "data": {
                    "currentConditions": {"temp": 72, "conditions": "Clear"},
                    "resolvedAddress": "Ann Arbor, MI, USA",
                },
            }
        # RSS text payload
        return {
            "status_code": 200,
            "text": """<rss><channel><item><title>Headline</title><link>https://example.com/h</link></item></channel></rss>""",
        }

    def fail_direct_requests(*args, **kwargs):
        raise AssertionError("Direct requests call detected outside NetworkMediator")

    monkeypatch.setenv("WEATHER_API_KEY", "test-key")

    with patch.object(NetworkMediator, "request", new=fake_mediator_request), patch("requests.request", new=fail_direct_requests):
        weather = WeatherSkill()
        weather_result = asyncio.run(weather.handle("weather"))
        assert weather_result is not None

        news = NewsSkill()
        news_result = asyncio.run(news.handle("news"))
        assert news_result is not None

    assert calls, "Expected at least one mediator network call from skill paths"
    assert all(call["method"].upper() == "GET" for call in calls), f"Non read-only skill network method detected: {calls}"
