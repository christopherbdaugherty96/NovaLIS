# src/skills/news.py

"""
NovaLIS News Skill — Phase 3 Canonical
"""

from __future__ import annotations

from typing import Optional, List, Dict

from src.base_skill import BaseSkill, SkillResult
from src.tools.rss_fetch import fetch_rss_headlines
from src.tools.news_fallback import fallback_headline


class NewsSkill(BaseSkill):
    name = "news"
    description = "Current news headlines"

    SOURCES = [
        {"name": "Reuters", "feed": "https://www.reuters.com/rssFeed/topNews", "domain": "reuters.com"},
        {"name": "Associated Press", "feed": "https://apnews.com/rss", "domain": "apnews.com"},
        {"name": "NPR", "feed": "https://feeds.npr.org/1001/rss.xml", "domain": "npr.org"},
        {"name": "BBC News", "feed": "https://feeds.bbci.co.uk/news/rss.xml", "domain": "bbc.com"},
        {"name": "PBS NewsHour", "feed": "https://www.pbs.org/newshour/feeds/rss/headlines", "domain": "pbs.org"},
        {"name": "ABC News", "feed": "https://abcnews.go.com/abcnews/topstories", "domain": "abcnews.go.com"},
        {"name": "FOX News", "feed": "https://feeds.foxnews.com/foxnews/latest", "domain": "foxnews.com"},
        {"name": "CNN", "feed": "http://rss.cnn.com/rss/cnn_topstories.rss", "domain": "cnn.com"},
    ]

    def __init__(self, network):
        self.network = network

    def can_handle(self, query: str) -> bool:
        q = (query or "").lower()
        return any(term in q for term in ("news", "headlines", "latest news", "current news"))

    async def handle(self, query: str) -> SkillResult:
        items: List[Dict[str, str]] = []

        for source in self.SOURCES:
            item = await self._fetch_one(source)
            if item:
                items.append(item)

        widget = {
            "type": "news",
            "items": items
        }

        return SkillResult(
            success=True,
            message="Here are the latest headlines.",
            data={},
            widget_data=widget,
            skill=self.name,
        )

    async def _fetch_one(self, source: dict) -> Optional[dict]:
        feed_url = source.get("feed")
        name = source.get("name")
        domain = source.get("domain", "")

        if feed_url:
            try:
                items = await fetch_rss_headlines(feed_url, self.network)
                if items:
                    first = items[0]
                    title = first.get("title")
                    url = first.get("url")
                    if title and url:
                        return {
                            "title": title,
                            "url": url,
                            "source": name,
                        }
            except Exception:
                pass

        if domain:
            return fallback_headline(name, domain)

        return None