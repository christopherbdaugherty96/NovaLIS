import asyncio

from src.skills.news import NewsSkill


def test_news_skill_uses_feed_summary_and_published(monkeypatch):
    async def _fake_fetch(*args, **kwargs):
        return [
            {
                "title": "Oil prices rise after regional escalation",
                "url": "https://example.com/story-1",
                "summary": "Energy markets moved higher after overnight escalation and supply concerns.",
                "published": "Mon, 09 Mar 2026 01:00:00 GMT",
            }
        ]

    monkeypatch.setattr("src.skills.news.fetch_rss_headlines", _fake_fetch)
    monkeypatch.setattr(
        NewsSkill,
        "SOURCES",
        [{"name": "Example Source", "feed": "https://example.com/rss", "domain": "example.com"}],
    )

    result = asyncio.run(NewsSkill().handle("news"))
    assert result.success is True
    widget = result.widget_data or {}
    items = widget.get("items") or []
    assert len(items) == 1
    assert items[0]["source"] == "Example Source"
    assert "Energy markets moved higher" in items[0]["summary"]
    assert items[0]["published"] == "Mon, 09 Mar 2026 01:00:00 GMT"


def test_news_skill_falls_back_to_title_based_summary(monkeypatch):
    async def _fake_fetch(*args, **kwargs):
        return [
            {
                "title": "City council approves transit overhaul",
                "url": "https://example.com/story-2",
                "summary": "",
                "published": "",
            }
        ]

    monkeypatch.setattr("src.skills.news.fetch_rss_headlines", _fake_fetch)
    monkeypatch.setattr(
        NewsSkill,
        "SOURCES",
        [{"name": "Metro Wire", "feed": "https://example.com/rss", "domain": "example.com"}],
    )

    result = asyncio.run(NewsSkill().handle("latest news"))
    assert result.success is True
    widget = result.widget_data or {}
    items = widget.get("items") or []
    assert len(items) == 1
    assert items[0]["summary"].startswith("Headline indicates:")
