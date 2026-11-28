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
                "video_url": "https://video.example.com/story-1.mp4",
            }
        ]

    monkeypatch.setattr("src.skills.news.fetch_rss_headlines", _fake_fetch)
    monkeypatch.setattr(
        NewsSkill,
        "SOURCES",
        [{"name": "Example Source", "feed": "https://example.com/rss", "domain": "example.com"}],
    )
    monkeypatch.setattr(NewsSkill, "CATEGORY_GROUPS", [])

    result = asyncio.run(NewsSkill().handle("news"))
    assert result.success is True
    widget = result.widget_data or {}
    items = widget.get("items") or []
    assert len(items) == 1
    assert items[0]["source"] == "Example Source"
    assert "Energy markets moved higher" in items[0]["summary"]
    assert items[0]["published"] == "Mon, 09 Mar 2026 01:00:00 GMT"
    assert items[0]["video_url"] == "https://video.example.com/story-1.mp4"


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
    monkeypatch.setattr(NewsSkill, "CATEGORY_GROUPS", [])

    result = asyncio.run(NewsSkill().handle("latest news"))
    assert result.success is True
    widget = result.widget_data or {}
    items = widget.get("items") or []
    assert len(items) == 1
    assert items[0]["summary"].startswith("Headline indicates:")
    assert items[0]["video_url"] == ""


def test_news_skill_tries_multiple_feeds_per_source(monkeypatch):
    calls = []

    async def _fake_fetch(feed_url, **kwargs):
        del kwargs
        calls.append(feed_url)
        if feed_url.endswith("primary.xml"):
            return []
        return [
            {
                "title": "Fallback feed story",
                "url": "https://example.com/fallback-story",
                "summary": "Recovered via secondary feed.",
                "published": "Mon, 09 Mar 2026 02:00:00 GMT",
            }
        ]

    monkeypatch.setattr("src.skills.news.fetch_rss_headlines", _fake_fetch)
    monkeypatch.setattr(
        NewsSkill,
        "SOURCES",
        [
            {
                "name": "Example",
                "feeds": ["https://feed.example.com/primary.xml", "https://feed.example.com/secondary.xml"],
                "domain": "example.com",
            }
        ],
    )
    monkeypatch.setattr(NewsSkill, "CATEGORY_GROUPS", [])

    result = asyncio.run(NewsSkill().handle("news"))
    assert result.success is True
    items = (result.widget_data or {}).get("items") or []
    assert len(items) == 1
    assert items[0]["title"] == "Fallback feed story"
    assert calls == [
        "https://feed.example.com/primary.xml",
        "https://feed.example.com/secondary.xml",
    ]


def test_news_skill_returns_category_groups(monkeypatch):
    async def _fake_fetch(feed_url, **kwargs):
        del kwargs
        return [
            {
                "title": f"Story for {feed_url}",
                "url": f"{feed_url}/story",
                "summary": "Category summary text.",
                "published": "Mon, 09 Mar 2026 02:00:00 GMT",
            }
        ]

    monkeypatch.setattr("src.skills.news.fetch_rss_headlines", _fake_fetch)
    monkeypatch.setattr(
        NewsSkill,
        "SOURCES",
        [{"name": "Top Source", "feed": "https://example.com/top.xml", "domain": "example.com"}],
    )
    monkeypatch.setattr(
        NewsSkill,
        "CATEGORY_GROUPS",
        [
            {
                "key": "global",
                "title": "Global News",
                "sources": [{"name": "Global One", "feed": "https://example.com/global.xml", "domain": "example.com"}],
            },
            {
                "key": "tech",
                "title": "Tech News",
                "sources": [{"name": "Tech One", "feed": "https://example.com/tech.xml", "domain": "example.com"}],
            },
        ],
    )

    result = asyncio.run(NewsSkill().handle("news"))
    assert result.success is True
    widget = result.widget_data or {}
    categories = widget.get("categories") or {}
    assert "global" in categories
    assert "tech" in categories
    assert categories["global"]["title"] == "Global News"
    assert isinstance(categories["global"]["items"], list)
    assert categories["global"]["items"][0]["source"] == "Global One"


def test_news_skill_reports_unavailable_when_feeds_return_nothing(monkeypatch):
    async def _fake_fetch(*args, **kwargs):
        return []

    monkeypatch.setattr("src.skills.news.fetch_rss_headlines", _fake_fetch)
    monkeypatch.setattr(
        NewsSkill,
        "SOURCES",
        [{"name": "Example Source", "feed": "https://example.com/rss", "domain": "example.com"}],
    )
    monkeypatch.setattr(NewsSkill, "CATEGORY_GROUPS", [])

    result = asyncio.run(NewsSkill().handle("news"))

    assert result.success is False
    assert result.message == "The news sources returned no headlines."
    widget = result.widget_data or {}
    assert widget["status"] == "empty"
    assert widget["source_count"] == 0
    assert widget["category_count"] == 0
    assert widget["summary"] == result.message


def test_news_skill_summary_dedupes_duplicate_titles_and_adds_theme():
    skill = NewsSkill()
    items = [
        {
            "title": "AI chip exports tighten after policy shift",
            "source": "Source A",
            "summary": "Semiconductor controls were expanded overnight.",
        },
        {
            "title": "AI chip exports tighten after policy shift",
            "source": "Source B",
            "summary": "Duplicate title from another feed.",
        },
        {
            "title": "Senate advances AI policy bill",
            "source": "Source C",
            "summary": "Legislation moved out of committee.",
        },
    ]

    summary = skill._summarize_headlines(items)
    assert "Loaded 2 sources." in summary
    assert "Theme:" in summary or "Themes:" in summary
    assert summary.count("AI chip exports tighten after policy shift") == 1


def test_news_reports_denied_without_serving_cached_headlines(monkeypatch):
    import time

    from src.governor.exceptions import DisclosureDeniedError
    from src.skills import news

    async def denied(*_args, **_kwargs):
        raise DisclosureDeniedError("policy")

    monkeypatch.setattr(news, "_result_cache", {
        "news": (time.time() - 1, "Previous headlines", {"items": [{"title": "Old story"}], "status": "ok"}),
    })
    monkeypatch.setattr(news, "fetch_rss_headlines", denied)
    monkeypatch.setattr(NewsSkill, "SOURCES", [{"name": "Example", "feed": "https://example.com/rss"}])
    monkeypatch.setattr(NewsSkill, "CATEGORY_GROUPS", [])
    result = asyncio.run(NewsSkill().handle("news"))
    assert not result.success
    assert result.widget_data["status"] == "denied"
    assert result.widget_data["items"] == []


def test_news_labels_recent_expired_cache_during_outage(monkeypatch):
    import time

    from src.governor.exceptions import NetworkMediatorError
    from src.skills import news

    async def unavailable(*_args, **_kwargs):
        raise NetworkMediatorError("offline")

    item = {"title": "A previously retrieved story", "source_retrieved": True}
    monkeypatch.setattr(news, "_result_cache", {
        "news": (time.time() - 1, "Previous headlines", {"items": [item], "status": "ok"}),
    })
    monkeypatch.setattr(news, "fetch_rss_headlines", unavailable)
    monkeypatch.setattr(NewsSkill, "SOURCES", [{"name": "Example", "feed": "https://example.com/rss"}])
    monkeypatch.setattr(NewsSkill, "CATEGORY_GROUPS", [])
    result = asyncio.run(NewsSkill().handle("news"))
    assert result.success
    assert result.widget_data["status"] == "stale"
    assert result.widget_data["items"] == [item]


def test_transport_failure_does_not_turn_publisher_homepage_into_headline(monkeypatch):
    from src.governor.exceptions import NetworkMediatorError

    async def unavailable(*_args, **_kwargs):
        raise NetworkMediatorError("offline")

    monkeypatch.setattr("src.skills.news.fetch_rss_headlines", unavailable)
    monkeypatch.setattr(NewsSkill, "SOURCES", [
        {"name": "Example", "domain": "example.com", "feed": "https://example.com/rss"},
    ])
    monkeypatch.setattr(NewsSkill, "CATEGORY_GROUPS", [])
    result = asyncio.run(NewsSkill().handle("news"))
    assert not result.success
    assert result.widget_data["status"] == "unavailable"
    assert result.widget_data["items"] == []
    assert result.widget_data["source_count"] == 0
