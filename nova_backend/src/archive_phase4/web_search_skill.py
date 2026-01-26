from ..base_skill import BaseSkill, SkillResult
from ..tools.web_search import run_web_search, get_structured_results


class WebSearchSkill(BaseSkill):
    name = "web_search"

    # -------------------- ROUTING --------------------

    def can_handle(self, query: str) -> bool:
        q = query.lower()

        # HARD EXCLUSIONS — authoritative skills win
        if any(term in q for term in (
            "weather", "temperature", "forecast",
            "news", "headlines"
        )):
            return False

        explicit = (
            "search for", "look up", "search the web",
            "find information about"
        )
        return any(p in q for p in explicit)

    # -------------------- EXECUTION --------------------

    async def handle(self, query: str) -> SkillResult:
        results = run_web_search(query, max_results=3, include_source=True)
        if not results:
            return SkillResult(
                success=False,
                message="No current information found.",
                skill=self.name,
            )

        structured = get_structured_results(query, max_results=3)

        return SkillResult(
            success=True,
            message=results,
            widget_data={
                "type": "web_search",
                "data": structured or [],
            },
            skill=self.name,
        )
