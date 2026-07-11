"""Regression tests for the "Truthful availability under dashboard refresh" lane.

Guards the two defects behind the false "not configured" labels:
  1. The news skill fans out to ~26 governed network calls; the ~70s dashboard
     refresh re-spent them every cycle and exhausted the cap-56 rate limit. A
     short-lived cache must collapse repeated refreshes onto one fetch.
  2. An empty/rate-limited result must be labeled honestly ("temporarily
     unavailable"), never "not configured", and news must never blame Brave.
"""

from __future__ import annotations

import asyncio
import time

import src.skills.news as news_mod
from src.brief.awareness_brief import build_news_section, build_weather_section
from src.skills.news import NewsSkill, reset_news_result_cache


def _install_fake_feeds(monkeypatch, calls: list[str]) -> None:
    async def _fake_fetch(feed_url, **kwargs):
        calls.append(feed_url)
        return [
            {
                "title": "Headline",
                "url": "https://example.com/a",
                "summary": "Body text.",
                "published": "",
                "video_url": "",
            }
        ]

    monkeypatch.setattr("src.skills.news.fetch_rss_headlines", _fake_fetch)
    monkeypatch.setattr(
        NewsSkill, "SOURCES", [{"name": "S", "feeds": ["https://feed/1.xml"], "domain": "d"}]
    )
    monkeypatch.setattr(NewsSkill, "CATEGORY_GROUPS", [])


def test_single_news_call_returns_headlines(monkeypatch):
    reset_news_result_cache()
    calls: list[str] = []
    _install_fake_feeds(monkeypatch, calls)

    result = asyncio.run(NewsSkill().handle("news"))

    assert (result.widget_data or {}).get("status") == "ok"
    assert len(calls) >= 1


def test_repeated_refresh_does_not_refetch_within_window(monkeypatch):
    """Ten dashboard-style refreshes within the TTL must spend the network once."""
    reset_news_result_cache()
    calls: list[str] = []
    _install_fake_feeds(monkeypatch, calls)
    skill = NewsSkill()

    asyncio.run(skill.handle("news"))
    fetches_after_first = len(calls)
    assert fetches_after_first >= 1

    for _ in range(10):
        result = asyncio.run(skill.handle("news"))
        assert (result.widget_data or {}).get("status") == "ok"
        assert (result.widget_data or {}).get("served_from_cache") is True

    # No further network fetches: the cap-56 budget is not re-hit by refreshes.
    assert len(calls) == fetches_after_first


def test_cache_is_short_lived_not_forever(monkeypatch):
    reset_news_result_cache()
    calls: list[str] = []
    _install_fake_feeds(monkeypatch, calls)
    monkeypatch.setattr(news_mod, "NEWS_CACHE_TTL_SECONDS", 0.05)
    skill = NewsSkill()

    asyncio.run(skill.handle("news"))
    fetches_after_first = len(calls)
    time.sleep(0.12)  # exceed the tiny TTL
    asyncio.run(skill.handle("news"))

    assert len(calls) > fetches_after_first  # refetched after the window elapsed


def test_rate_limited_news_reads_as_unavailable_not_not_configured():
    # An empty result (what a rate-limited fetch produces) must be truthful.
    section = build_news_section([])
    assert section.status == "unavailable"
    text = section.items[0].lower()
    assert "not configured" not in text
    assert "brave" not in text


def test_configured_weather_rate_limited_does_not_ask_for_api_key():
    section = build_weather_section({"connected": False, "status": "unavailable"}, configured=True)
    assert section.status == "unavailable"
    assert "api key" not in section.items[0].lower()
