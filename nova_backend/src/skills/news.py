# src/skills/news.py

"""
NovaLIS News Skill — Phase 3 Canonical
"""

from __future__ import annotations

from typing import Optional, List, Dict

from src.base_skill import BaseSkill, SkillResult
from src.tools.rss_fetch import fetch_rss_headlines
from src.tools.news_fallback import fallback_headline
from src.governor.network_mediator import NetworkMediator


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

    def __init__(self, network: NetworkMediator | None = None):
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
            "items": items,
            "summary": self._summarize_headlines(items),
        }

        return SkillResult(
            success=True,
            message="Here are the latest headlines.",
            data={},
            widget_data=widget,
            skill=self.name,
        )

    def _summarize_headlines(self, items: List[Dict[str, str]]) -> str:
        """Create a deterministic 1-2 sentence summary from fetched headlines."""
        if not items:
            return "No headlines are available to summarize right now."

        top_titles = [item.get("title", "").strip() for item in items[:3] if item.get("title")]
        if not top_titles:
            return "I pulled headlines, but there was not enough detail to summarize them."

        if len(top_titles) == 1:
            return f"Top story right now: {top_titles[0]}."

        if len(top_titles) == 2:
            return f"Current news focus: {top_titles[0]}; alongside {top_titles[1]}."

        return (
            f"Current news focus: {top_titles[0]}; {top_titles[1]}; and {top_titles[2]}."
        )

    async def _fetch_one(self, source: dict) -> Optional[dict]:
        feed_url = source.get("feed")
        name = source.get("name")
        domain = source.get("domain", "")

        if feed_url:
            try:
                items = await fetch_rss_headlines(feed_url, network=self.network)
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
