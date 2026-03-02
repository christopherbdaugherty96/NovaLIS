from __future__ import annotations

import os

from src.actions.action_result import ActionResult
from src.conversation.response_style_router import ResponseTemplates


class MultiSourceReportingExecutor:
    """Single-invocation multi-source reporting built on governed search endpoint."""

    def __init__(self, network):
        self.network = network

    def execute(self, request) -> ActionResult:
        query = (request.params or {}).get("query", "").strip()
        if not query:
            return ActionResult.failure("No report query provided.", request_id=request.request_id)

        brave_key = os.getenv("BRAVE_API_KEY")
        if not brave_key:
            return ActionResult.failure("Search service is not configured.", request_id=request.request_id)

        try:
            response = self.network.request(
                capability_id=16,
                method="GET",
                url="https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": 5},
                headers={"Accept": "application/json", "X-Subscription-Token": brave_key},
                as_json=True,
                timeout=5,
            )
        except Exception:
            return ActionResult.failure("I couldn't build the report due to a network issue.", request_id=request.request_id)

        if response.get("status_code") != 200:
            return ActionResult.failure("I couldn't build the report right now.", request_id=request.request_id)

        results = ((response.get("data") or {}).get("web") or {}).get("results") or []
        titles = [item.get("title", "").strip() for item in results[:3] if item.get("title")]
        domains = []
        for item in results[:3]:
            url = item.get("url", "")
            dom = url.split("//")[-1].split("/")[0].strip().lower()
            if dom and dom not in domains:
                domains.append(dom)

        message = "\n\n".join(
            [
                ResponseTemplates.bounded_research_intro(query[:80]),
                ResponseTemplates.top_findings_block(titles),
                ResponseTemplates.sources_block(domains),
            ]
        )

        widget_results = [{"title": i.get("title", "")[:100], "url": i.get("url", "")} for i in results[:5]]
        return ActionResult.ok(
            message=message,
            data={"widget": {"type": "search", "data": {"results": widget_results}}},
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )
