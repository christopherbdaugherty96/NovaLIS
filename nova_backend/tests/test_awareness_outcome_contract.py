import asyncio
import types

import pytest

from src.services.weather_service import WeatherService
from src.skills.calendar import CalendarSkill
from src.skills.news import NewsSkill, reset_news_result_cache
from src.skills.weather import WeatherSkill


@pytest.mark.parametrize(
    ("source", "expected_status"),
    [
        ("weather", "unavailable"),
        ("news", "unavailable"),
        ("calendar", "not_connected"),
    ],
)
def test_degraded_awareness_status_never_reports_success(
    source,
    expected_status,
    monkeypatch,
):
    reset_news_result_cache()

    if source == "weather":
        async def fail_weather(self):
            raise RuntimeError("provider unavailable")

        monkeypatch.setattr(WeatherService, "get_current_weather", fail_weather)
        result = asyncio.run(WeatherSkill().handle("weather"))
        widget = (result.widget_data or {}).get("data") or {}
    elif source == "news":
        async def no_headlines(*args, **kwargs):
            return []

        monkeypatch.setattr("src.skills.news.fetch_rss_headlines", no_headlines)
        monkeypatch.setattr(
            NewsSkill,
            "SOURCES",
            [{"name": "Unavailable", "feed": "https://example.invalid/rss", "domain": ""}],
        )
        monkeypatch.setattr(NewsSkill, "CATEGORY_GROUPS", [])
        result = asyncio.run(NewsSkill().handle("news"))
        widget = result.widget_data or {}
    else:
        monkeypatch.delenv("NOVA_CALENDAR_ICS_PATH", raising=False)
        result = asyncio.run(CalendarSkill().handle("calendar"))
        widget = result.widget_data or {}

    assert result.success is False
    assert widget["status"] == expected_status
    assert result.message


def test_degraded_awareness_action_writes_failed_completion_receipt(monkeypatch):
    from src.actions.action_result import ActionResult
    from src.governor.governor import Governor

    class FakeRegistry:
        def get(self, capability_id):
            return types.SimpleNamespace(name="weather_snapshot")

        def is_enabled(self, capability_id):
            return True

    class FakeLedger:
        def __init__(self):
            self.events = []

        def log_event(self, event_type, metadata):
            self.events.append((event_type, metadata))

    governor = Governor()
    governor._registry = FakeRegistry()
    governor._ledger = FakeLedger()
    monkeypatch.setattr(
        governor,
        "_dispatch_capability",
        lambda request: ActionResult.failure(
            "Weather is unavailable right now.",
            request_id=request.request_id,
            data={
                "widget": {
                    "type": "weather",
                    "data": {"status": "unavailable", "connected": False},
                }
            },
            external_effect=False,
            reversible=True,
        ),
    )
    monkeypatch.setattr(
        governor._execute_boundary,
        "run_with_timeout",
        lambda operation, timeout_seconds=None: operation(),
    )
    monkeypatch.setattr(governor._execute_boundary, "enforce_memory_limits", lambda: None)
    monkeypatch.setattr(governor._execute_boundary, "enforce_cpu_limits", lambda: None)

    result = governor.handle_governed_invocation(55, {})
    completion = next(
        metadata
        for event_type, metadata in governor._ledger.events
        if event_type == "ACTION_COMPLETED"
    )

    assert result.success is False
    assert completion["success"] is False
    assert completion["status"] == "failed"
    assert "unavailable" in completion["failure_reason"].lower()
