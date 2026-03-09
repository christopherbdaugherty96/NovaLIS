# src/skills/news.py

"""
NovaLIS News Skill — Phase 3 Canonical
"""

from __future__ import annotations

import asyncio
from typing import Optional, List, Dict, Any

from src.base_skill import BaseSkill, SkillResult
from src.tools.rss_fetch import fetch_rss_headlines
from src.tools.news_fallback import fallback_headline
from src.governor.network_mediator import NetworkMediator


class NewsSkill(BaseSkill):
    name = "news"
    description = "Current news headlines"
    SUMMARY_CHAR_LIMIT = 210
    MAX_CONCURRENT_FEEDS = 4

    SOURCES = [
        {
            "name": "Reuters",
            "feeds": [
                "https://www.reuters.com/rssFeed/topNews",
                "https://www.reuters.com/world/rss",
            ],
            "domain": "reuters.com",
        },
        {
            "name": "Associated Press",
            "feeds": [
                "https://apnews.com/rss",
                "https://feeds.apnews.com/apnews/topnews",
            ],
            "domain": "apnews.com",
        },
        {"name": "NPR", "feeds": ["https://feeds.npr.org/1001/rss.xml"], "domain": "npr.org"},
        {"name": "BBC News", "feeds": ["https://feeds.bbci.co.uk/news/rss.xml"], "domain": "bbc.com"},
        {"name": "PBS NewsHour", "feeds": ["https://www.pbs.org/newshour/feeds/rss/headlines"], "domain": "pbs.org"},
        {"name": "ABC News", "feeds": ["https://abcnews.go.com/abcnews/topstories"], "domain": "abcnews.go.com"},
        {"name": "FOX News", "feeds": ["https://feeds.foxnews.com/foxnews/latest"], "domain": "foxnews.com"},
        {"name": "CNN", "feeds": ["https://rss.cnn.com/rss/cnn_topstories.rss"], "domain": "cnn.com"},
    ]

    CATEGORY_GROUPS = [
        {
            "key": "global",
            "title": "Global News",
            "sources": [
                {"name": "Reuters World", "feeds": ["https://www.reuters.com/world/rss"], "domain": "reuters.com"},
                {"name": "BBC World", "feeds": ["https://feeds.bbci.co.uk/news/world/rss.xml"], "domain": "bbc.com"},
                {"name": "Al Jazeera", "feeds": ["https://www.aljazeera.com/xml/rss/all.xml"], "domain": "aljazeera.com"},
            ],
        },
        {
            "key": "political",
            "title": "Political News",
            "sources": [
                {"name": "NPR Politics", "feeds": ["https://feeds.npr.org/1014/rss.xml"], "domain": "npr.org"},
                {"name": "BBC Politics", "feeds": ["https://feeds.bbci.co.uk/news/politics/rss.xml"], "domain": "bbc.com"},
                {"name": "POLITICO", "feeds": ["https://www.politico.com/rss/politicopicks.xml"], "domain": "politico.com"},
            ],
        },
        {
            "key": "breaking",
            "title": "Breaking News",
            "sources": [
                {"name": "Reuters", "feeds": ["https://www.reuters.com/rssFeed/topNews"], "domain": "reuters.com"},
                {"name": "Associated Press", "feeds": ["https://apnews.com/rss"], "domain": "apnews.com"},
                {"name": "CNN", "feeds": ["https://rss.cnn.com/rss/cnn_topstories.rss"], "domain": "cnn.com"},
            ],
        },
        {
            "key": "tech",
            "title": "Tech News",
            "sources": [
                {"name": "The Verge", "feeds": ["https://www.theverge.com/rss/index.xml"], "domain": "theverge.com"},
                {"name": "Ars Technica", "feeds": ["https://feeds.arstechnica.com/arstechnica/index"], "domain": "arstechnica.com"},
                {"name": "TechCrunch", "feeds": ["https://techcrunch.com/feed/"], "domain": "techcrunch.com"},
            ],
        },
        {
            "key": "markets",
            "title": "Crypto & Stocks",
            "sources": [
                {"name": "CoinDesk", "feeds": ["https://www.coindesk.com/arc/outboundfeeds/rss/"], "domain": "coindesk.com"},
                {"name": "CNBC Markets", "feeds": ["https://www.cnbc.com/id/100003114/device/rss/rss.html"], "domain": "cnbc.com"},
                {"name": "MarketWatch", "feeds": ["https://feeds.content.dowjones.io/public/rss/mw_topstories"], "domain": "marketwatch.com"},
            ],
        },
    ]

    def __init__(self, network: NetworkMediator | None = None):
        self.network = network

    def can_handle(self, query: str) -> bool:
        q = (query or "").lower()
        return any(term in q for term in ("news", "headlines", "latest news", "current news"))

    async def _fetch_many(
        self,
        sources: list[dict[str, Any]],
        *,
        semaphore: asyncio.Semaphore,
    ) -> list[dict[str, str]]:
        async def _fetch_bounded(source: dict[str, Any]) -> Optional[dict[str, str]]:
            async with semaphore:
                return await self._fetch_one(source)

        fetched = await asyncio.gather(
            *(_fetch_bounded(source) for source in sources),
            return_exceptions=True,
        )
        return [item for item in fetched if isinstance(item, dict)]

    async def _fetch_category_groups(
        self,
        *,
        semaphore: asyncio.Semaphore,
    ) -> dict[str, dict[str, Any]]:
        categories: dict[str, dict[str, Any]] = {}
        for group in self.CATEGORY_GROUPS:
            key = str(group.get("key") or "").strip().lower()
            title = str(group.get("title") or "").strip() or key.title()
            sources = list(group.get("sources") or [])
            if not key or not sources:
                continue
            items = await self._fetch_many(sources, semaphore=semaphore)
            categories[key] = {
                "title": title,
                "items": items[:3],
                "summary": self._summarize_headlines(items[:3]),
            }
        return categories

    async def handle(self, query: str) -> SkillResult:
        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_FEEDS)
        items = await self._fetch_many(self.SOURCES, semaphore=semaphore)
        categories = await self._fetch_category_groups(semaphore=semaphore)

        widget = {
            "type": "news",
            "items": items,
            "summary": self._summarize_headlines(items),
            "categories": categories,
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

        source_count = len([item for item in items if item.get("title")])
        if len(top_titles) == 1:
            return f"Loaded {source_count} source. Top story: {top_titles[0]}."

        if len(top_titles) == 2:
            return f"Loaded {source_count} sources. Top focus: {top_titles[0]}; alongside {top_titles[1]}."

        return (
            f"Loaded {source_count} sources. Top focus: {top_titles[0]}; {top_titles[1]}; and {top_titles[2]}."
        )

    def _build_item_summary(self, title: str, raw_summary: str) -> str:
        clean_title = (title or "").strip()
        summary = " ".join((raw_summary or "").split()).strip()
        if summary:
            lowered_title = clean_title.lower()
            lowered_summary = summary.lower()
            if lowered_title and lowered_summary.startswith(lowered_title):
                summary = summary[len(clean_title):].lstrip(" .:-")
            if summary:
                if len(summary) > self.SUMMARY_CHAR_LIMIT:
                    summary = summary[: self.SUMMARY_CHAR_LIMIT - 3].rstrip() + "..."
                return summary
        if not clean_title:
            return "Headline detail unavailable."
        fallback = f"Headline indicates: {clean_title}."
        if len(fallback) > self.SUMMARY_CHAR_LIMIT:
            fallback = fallback[: self.SUMMARY_CHAR_LIMIT - 3].rstrip() + "..."
        return fallback

    @staticmethod
    def _source_feed_urls(source: dict) -> list[str]:
        urls: list[str] = []
        feeds = source.get("feeds")
        if isinstance(feeds, list):
            urls.extend(str(url).strip() for url in feeds if str(url).strip())
        fallback_feed = str(source.get("feed") or "").strip()
        if fallback_feed:
            urls.append(fallback_feed)

        ordered: list[str] = []
        for url in urls:
            if url not in ordered:
                ordered.append(url)
        return ordered

    async def _fetch_one(self, source: dict) -> Optional[dict]:
        name = source.get("name")
        domain = source.get("domain", "")

        for feed_url in self._source_feed_urls(source):
            try:
                items = await fetch_rss_headlines(feed_url, network=self.network)
                if not items:
                    continue
                first = items[0]
                title = first.get("title")
                url = first.get("url")
                if title and url:
                    summary = self._build_item_summary(title, str(first.get("summary") or ""))
                    return {
                        "title": title,
                        "url": url,
                        "source": name,
                        "summary": summary,
                        "published": str(first.get("published") or "").strip(),
                    }
            except Exception:
                continue

        if domain:
            return fallback_headline(name, domain)

        return None
