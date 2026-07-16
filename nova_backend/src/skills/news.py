# src/skills/news.py

"""
NovaLIS News Skill — Phase 3 Canonical
"""

from __future__ import annotations

import asyncio
import re
import threading
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.base_skill import BaseSkill, SkillResult
from src.governor.network_mediator import NetworkMediator
from src.tools.news_fallback import fallback_headline
from src.tools.rss_fetch import fetch_rss_headlines

# ---------------------------------------------------------------------------
# Short-lived result cache.
#
# A single news call fans out to ~26 governed network requests (cap 56). The
# dashboard re-requests the brief roughly every 70s, so without caching the
# repeated fetches exhaust the mediator's per-minute rate limit and every later
# fetch returns empty — which the UI then mislabels as "not configured". A short
# TTL keeps the brief fresh while collapsing repeated refreshes onto one fetch.
# Only successful fetches are cached, so a transient failure retries next time.
# ---------------------------------------------------------------------------
NEWS_CACHE_TTL_SECONDS = 180.0
_result_cache: dict[str, tuple[float, str, dict]] = {}
_result_cache_lock = threading.Lock()


def reset_news_result_cache() -> None:
    """Clear the cache. Used by test isolation; safe at runtime."""
    with _result_cache_lock:
        _result_cache.clear()


class NewsSkill(BaseSkill):
    name = "news"
    description = "Current news headlines"
    SUMMARY_CHAR_LIMIT = 210
    MAX_CONCURRENT_FEEDS = 4
    SUMMARY_MAX_LENGTH = 360

    THEME_KEYWORDS = {
        "global security": {"war", "conflict", "ceasefire", "strike", "missile", "military", "gaza", "ukraine", "iran", "israel"},
        "policy and government": {"election", "congress", "senate", "policy", "regulation", "law", "court", "bill"},
        "economy and markets": {"inflation", "economy", "market", "stocks", "bond", "rates", "jobs", "gdp"},
        "technology": {"ai", "chip", "semiconductor", "software", "platform", "cyber", "tech"},
        "energy and climate": {"oil", "gas", "energy", "climate", "carbon", "emissions"},
    }
    THEME_STOPWORDS = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "that",
        "this",
        "after",
        "over",
        "under",
        "amid",
        "into",
        "latest",
        "update",
        "news",
        "today",
    }

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
            "key": "politics",
            "title": "Politics News",
            "sources": [
                {"name": "NPR Politics", "feeds": ["https://feeds.npr.org/1014/rss.xml"], "domain": "npr.org"},
                {"name": "BBC Politics", "feeds": ["https://feeds.bbci.co.uk/news/politics/rss.xml"], "domain": "bbc.com"},
                {"name": "POLITICO", "feeds": ["https://www.politico.com/rss/politicopicks.xml"], "domain": "politico.com"},
                {"name": "FOX Politics", "feeds": ["https://moxie.foxnews.com/google-publisher/politics.xml"], "domain": "foxnews.com"},
            ],
        },
        {
            "key": "local",
            "title": "Local News",
            "sources": [
                {"name": "Associated Press", "feeds": ["https://apnews.com/rss"], "domain": "apnews.com"},
                {"name": "NPR", "feeds": ["https://feeds.npr.org/1001/rss.xml"], "domain": "npr.org"},
                {"name": "ABC News", "feeds": ["https://abcnews.go.com/abcnews/topstories"], "domain": "abcnews.go.com"},
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
            "key": "crypto",
            "title": "Crypto News",
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
        cached = self._cached_result()
        if cached is not None:
            return cached

        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_FEEDS)
        items = await self._fetch_many(self.SOURCES, semaphore=semaphore)
        categories = await self._fetch_category_groups(semaphore=semaphore)
        source_count = len(
            {
                str(item.get("source") or "").strip()
                for item in items
                if str(item.get("source") or "").strip()
            }
        )
        category_count = sum(
            1
            for bucket in categories.values()
            if isinstance(bucket, dict) and list(bucket.get("items") or [])
        )
        if items:
            summary = self._summarize_headlines(items)
            message = summary
            status = "ok"
        else:
            summary = "News unavailable right now."
            message = "I couldn't pull fresh headlines right now."
            status = "unavailable"

        widget = {
            "type": "news",
            "items": items,
            "summary": summary,
            "categories": categories,
            "status": status,
            "source_count": source_count,
            "category_count": category_count,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "cache_ttl_seconds": NEWS_CACHE_TTL_SECONDS,
        }

        # Cache only real fetches (never a transient failure), so repeated brief
        # refreshes within the window reuse this instead of re-spending cap 56.
        if items:
            with _result_cache_lock:
                _result_cache[self._CACHE_KEY] = (
                    time.time() + NEWS_CACHE_TTL_SECONDS,
                    message,
                    dict(widget),
                )

        return SkillResult(
            success=bool(items),
            message=message,
            data={},
            widget_data=widget,
            skill=self.name,
        )

    # A single key is valid only because handle() ignores `query` and always
    # fetches the same SOURCES + CATEGORY_GROUPS. If news ever becomes query- or
    # category-specific, this key MUST include that dimension, or callers will be
    # served results for the wrong query.
    _CACHE_KEY = "news"

    def _cached_result(self) -> Optional[SkillResult]:
        with _result_cache_lock:
            entry = _result_cache.get(self._CACHE_KEY)
        if not entry:
            return None
        expiry, message, widget = entry
        if expiry <= time.time():
            return None
        cached_widget = dict(widget)
        cached_widget["served_from_cache"] = True
        return SkillResult(
            success=True,
            message=message,
            data={},
            widget_data=cached_widget,
            skill=self.name,
        )

    def _summarize_headlines(self, items: List[Dict[str, str]]) -> str:
        """Create a deterministic 1-2 sentence summary from fetched headlines."""
        if not items:
            return "No headlines are available to summarize right now."

        unique_items = self._unique_headline_items(items)
        top_titles = [item.get("title", "").strip() for item in unique_items[:3] if item.get("title")]
        if not top_titles:
            return "I pulled headlines, but there was not enough detail to summarize them."

        source_count = len(
            {
                str(item.get("source") or "").strip()
                for item in unique_items
                if str(item.get("source") or "").strip()
            }
        )
        source_count = source_count or len(top_titles)
        theme_clause = self._theme_clause(unique_items)

        if len(top_titles) == 1:
            summary = f"Loaded {source_count} source. {theme_clause} Top story: {top_titles[0]}."
            return self._truncate_summary(summary)

        if len(top_titles) == 2:
            summary = (
                f"Loaded {source_count} sources. {theme_clause} "
                f"Top focus: {top_titles[0]}; alongside {top_titles[1]}."
            )
            return self._truncate_summary(summary)

        summary = (
            f"Loaded {source_count} sources. {theme_clause} "
            f"Top focus: {top_titles[0]}; {top_titles[1]}; and {top_titles[2]}."
        )
        return self._truncate_summary(summary)

    def _theme_clause(self, items: List[Dict[str, str]]) -> str:
        if not items:
            return "Theme mix is broad."
        text = " ".join(
            f"{str(item.get('title') or '').lower()} {str(item.get('summary') or '').lower()}"
            for item in items[:6]
        )
        tokens = [
            token
            for token in re.findall(r"[a-zA-Z]{3,}", text)
            if token not in self.THEME_STOPWORDS
        ]
        counts = Counter(tokens)

        scored: list[tuple[int, str]] = []
        for theme, keywords in self.THEME_KEYWORDS.items():
            score = sum(int(counts.get(keyword, 0)) for keyword in keywords)
            if score > 0:
                scored.append((score, theme))
        if not scored:
            return "Theme mix is broad."
        scored.sort(key=lambda item: item[0], reverse=True)
        top_labels = [label for _, label in scored[:2]]
        if len(top_labels) == 1:
            return f"Theme: {top_labels[0]}."
        return f"Themes: {top_labels[0]} and {top_labels[1]}."

    def _unique_headline_items(self, items: List[Dict[str, str]]) -> List[Dict[str, str]]:
        unique: List[Dict[str, str]] = []
        seen: set[str] = set()
        for item in items:
            title = str(item.get("title") or "").strip()
            if not title:
                continue
            key = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
            if not key or key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique

    def _truncate_summary(self, summary: str) -> str:
        text = " ".join(str(summary or "").split()).strip()
        if len(text) <= self.SUMMARY_MAX_LENGTH:
            return text
        trimmed = text[: self.SUMMARY_MAX_LENGTH - 3].rstrip()
        return trimmed + "..."

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
                        "video_url": str(first.get("video_url") or "").strip(),
                    }
            except Exception:
                continue

        if domain:
            return fallback_headline(name, domain)

        return None
