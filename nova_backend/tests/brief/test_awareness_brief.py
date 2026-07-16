"""Tests for the Daily Awareness Brief module."""

from __future__ import annotations

import pytest

from src.brief.awareness_brief import (
    AwarenessBrief,
    AwarenessSection,
    build_calendar_section,
    build_changes_section,
    build_news_section,
    build_printify_section,
    build_project_section,
    build_shopify_section,
    build_weather_section,
    compose_awareness_brief,
)


class TestAwarenessSection:
    def test_available_when_ok_with_items(self):
        s = AwarenessSection(key="test", title="Test", items=("a",), status="ok")
        assert s.available is True

    def test_not_available_when_not_configured(self):
        s = AwarenessSection(key="test", title="Test", items=("a",), status="not_configured")
        assert s.available is False

    def test_not_available_when_empty_items(self):
        s = AwarenessSection(key="test", title="Test", items=(), status="ok")
        assert s.available is False

    def test_to_dict_shape(self):
        s = AwarenessSection(key="k", title="T", items=("x",), status="ok", source="s")
        d = s.to_dict()
        assert d["key"] == "k"
        assert d["title"] == "T"
        assert d["items"] == ["x"]
        assert d["status"] == "ok"
        assert d["source"] == "s"


class TestWeatherSection:
    def test_not_configured_when_none(self):
        s = build_weather_section(None)
        assert s.status == "not_configured"
        assert "Settings" in s.items[0]

    def test_not_configured_when_disconnected(self):
        s = build_weather_section({"connected": False})
        assert s.status == "not_configured"

    def test_ok_with_connected_data(self):
        s = build_weather_section({
            "connected": True,
            "summary": "Sunny, 72°F",
            "forecast": "Clear all day",
        })
        assert s.status == "ok"
        assert s.available is True
        assert "Sunny" in s.items[0]

    def test_alerts_included(self):
        s = build_weather_section({
            "connected": True,
            "summary": "Cloudy",
            "alerts": ["Heat advisory"],
        })
        assert any("Alert" in item for item in s.items)

    def test_configured_but_failed_is_unavailable_not_not_configured(self):
        # Key present, fetch failed/rate-limited: must NOT tell the user to add a
        # key they already have.
        s = build_weather_section({"connected": False, "status": "unavailable"}, configured=True)
        assert s.status == "unavailable"
        assert "temporarily unavailable" in s.items[0].lower()
        assert "api key" not in s.items[0].lower()

    def test_not_configured_only_when_key_absent(self):
        s = build_weather_section({"connected": False}, configured=False)
        assert s.status == "not_configured"
        assert "api key" in s.items[0].lower()

    def test_infers_unavailable_from_widget_status_without_flag(self):
        # Even without the explicit flag, a widget status of "unavailable" must not
        # degrade into "not configured".
        s = build_weather_section({"connected": False, "status": "unavailable"})
        assert s.status == "unavailable"
        assert "api key" not in s.items[0].lower()

    def test_unwraps_widget_envelope_with_nested_data(self):
        # The brief passes the skill's widget envelope; a working forecast nested
        # under "data" must render as available, not "not configured".
        s = build_weather_section(
            {"type": "weather", "data": {"connected": True, "summary": "76°F and Clear"}},
            configured=True,
        )
        assert s.status == "ok"
        assert s.available is True
        assert "76°F" in s.items[0]


class TestNewsSection:
    def test_temporarily_unavailable_when_none(self):
        # News is RSS-sourced (no key), so an empty result is a transient
        # availability issue, never a misconfiguration, and must not blame Brave.
        s = build_news_section(None)
        assert s.status == "unavailable"
        assert "temporarily unavailable" in s.items[0].lower()
        assert "not configured" not in s.items[0].lower()
        assert "brave" not in s.items[0].lower()

    def test_temporarily_unavailable_when_empty(self):
        s = build_news_section([])
        assert s.status == "unavailable"
        assert "not configured" not in s.items[0].lower()
        assert "brave" not in s.items[0].lower()

    def test_ok_with_items(self):
        items = [{"title": "Tech news headline"}]
        s = build_news_section(items)
        assert s.status == "ok"
        assert "Tech news headline" in s.items[0]

    def test_grouped_by_categories(self):
        items = [{"title": "A"}]
        cats = {"Technology": [{"title": "AI breakthrough"}], "Business": [{"title": "Market up"}]}
        s = build_news_section(items, cats)
        assert s.status == "ok"
        assert any("Technology" in item for item in s.items)


class TestCalendarSection:
    def test_not_configured_when_none(self):
        s = build_calendar_section(None)
        assert s.status == "not_configured"

    def test_no_events_message(self):
        s = build_calendar_section({"connected": True, "events": []})
        assert s.status == "ok"
        assert "Nothing on your calendar" in s.items[0]

    def test_events_rendered(self):
        s = build_calendar_section({
            "connected": True,
            "events": [{"time": "9:00 AM", "title": "Standup"}],
        })
        assert "Standup" in s.items[0]


class TestProjectSection:
    def test_empty_when_no_state(self):
        s = build_project_section(None)
        assert s.status == "empty"

    def test_pulls_topic_from_conversation_context(self):
        s = build_project_section({
            "conversation_context": {"topic": "Fix auth bug"},
        })
        assert s.status == "ok"
        assert "Fix auth bug" in s.items[0]


class TestShopifySection:
    def test_not_configured_when_none(self):
        s = build_shopify_section(None)
        assert s.status == "not_configured"
        assert "Settings" in s.items[0]

    def test_read_only_snapshot(self):
        s = build_shopify_section({
            "shop_name": "My Store",
            "orders": {
                "order_count": 42,
                "total_revenue": "1,234.56",
                "period_label": "last_7_days",
            },
            "products": {
                "active_products": 15,
                "out_of_stock_count": 2,
                "low_stock_count": 3,
            },
        })
        assert s.status == "ok"
        assert "My Store" in s.items[0]
        assert any("42 orders" in item for item in s.items)
        assert any("2 out of stock" in item for item in s.items)


class TestPrintifySection:
    def test_stub_message(self):
        s = build_printify_section()
        assert s.status == "not_available"
        assert "not built yet" in s.items[0]


class TestChangesSection:
    def test_empty_when_no_receipts(self):
        s = build_changes_section(None)
        assert s.status == "empty"

    def test_formats_receipts(self):
        s = build_changes_section([
            {
                "event_type": "ACTION_COMPLETED",
                "capability_name": "weather_check",
                "timestamp_utc": "2026-06-18T10:30:00+00:00",
            },
        ])
        assert s.status == "ok"
        assert any("weather_check" in item for item in s.items)


class TestComposeAwarenessBrief:
    def test_returns_all_seven_sections(self):
        brief = compose_awareness_brief()
        assert len(brief.sections) == 7

    def test_to_dict_shape(self):
        brief = compose_awareness_brief()
        d = brief.to_dict()
        assert d["type"] == "awareness_brief"
        assert "date" in d
        assert "timestamp_utc" in d
        assert "greeting" in d
        assert "sections" in d
        assert "available_count" in d
        assert "total_count" in d
        assert d["total_count"] == 7

    def test_graceful_degradation_all_missing(self):
        brief = compose_awareness_brief()
        d = brief.to_dict()
        assert d["available_count"] == 0
        for section in d["sections"]:
            assert section["status"] in {"not_configured", "not_available", "empty", "unavailable"}
            assert len(section["items"]) > 0

    def test_partial_data(self):
        brief = compose_awareness_brief(
            weather_data={"connected": True, "summary": "Sunny"},
            news_items=[{"title": "Headlines"}],
        )
        d = brief.to_dict()
        assert d["available_count"] == 2

    def test_unavailable_source_remains_visible_in_rendered_brief(self):
        brief = compose_awareness_brief(
            weather_data={
                "type": "weather",
                "data": {
                    "connected": False,
                    "status": "unavailable",
                    "summary": "Weather is unavailable right now.",
                },
            },
            weather_configured=True,
        )

        rendered_sections = brief.to_dict()["sections"]
        weather = next(section for section in rendered_sections if section["key"] == "weather")

        assert weather["status"] == "unavailable"
        assert weather["items"]
        assert "unavailable" in weather["items"][0].lower()

    def test_no_write_operations(self):
        """The awareness brief module must be read-only."""
        import ast
        import inspect
        import src.brief.awareness_brief as mod

        source = inspect.getsource(mod)
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = ""
                if isinstance(func, ast.Attribute):
                    name = func.attr
                elif isinstance(func, ast.Name):
                    name = func.id
                assert name not in {
                    "create", "update", "delete", "put", "post",
                    "mutation", "fulfill", "cancel_order",
                }, f"Potential write operation found: {name}"
