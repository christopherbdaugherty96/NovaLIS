"""
NovaLIS News Skill (v1)

Provides current news headlines from a fixed, trusted source list.

Design constraints (LOCKED):
- Exactly 8 headlines
- One per approved source
- No per-outlet APIs
- No background updates
- No summaries by default
- Clickable links only
"""

from ..base_skill import BaseSkill, SkillResult
from ..tools.web_search import get_structured_results


class NewsSkill(BaseSkill):
    name = "news"
    description = "Current news headlines"

    SOURCES = [
        {"name": "Reuters", "domain": "reuters.com"},
        {"name": "Associated Press", "domain": "apnews.com"},
        {"name": "NPR", "domain": "npr.org"},
        {"name": "BBC News", "domain": "bbc.com/news"},
        {"name": "PBS NewsHour", "domain": "pbs.org/newshour"},
        {"name": "ABC News", "domain": "abcnews.go.com"},
        {"name": "FOX News", "domain": "foxnews.com"},
        {"name": "CNN", "domain": "cnn.com"},
    ]

    # ==================== ROUTING ====================

    def can_handle(self, query: str) -> bool:
        q = query.lower().strip()
        return any(term in q for term in (
            "news",
            "headlines",
            "latest news",
            "current news",
        ))

    # ==================== EXECUTION ====================

    async def handle(self, query: str) -> SkillResult:
        headlines = []

        for source in self.SOURCES:
            item = self._fetch_one_headline(source)
            if item:
                headlines.append(item)

        if not headlines:
            return SkillResult(
                success=False,
                message="No headlines are available right now.",
                skill=self.name,
            )

        return SkillResult(
            success=True,
            message="Here are the latest headlines.",
            data={"headlines": headlines},
            widget_data={
                "type": "news",
                "data": headlines,
            },
            skill=self.name,
        )

    # ==================== FETCH ====================

    def _fetch_one_headline(self, source: dict):
        query = f"site:{source['domain']} latest news"

        results = get_structured_results(
            query=query,
            max_results=1,
        )

        if not results:
            return None

        r = results[0]

        if not r.get("title") or not r.get("url"):
            return None

        return {
            "title": r["title"],
            "source": source["name"],
            "url": r["url"],
        }
