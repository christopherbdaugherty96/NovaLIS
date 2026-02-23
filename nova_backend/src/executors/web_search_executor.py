# src/executors/web_search_executor.py

import logging

from src.actions.action_request import ActionRequest
from src.actions.action_result import ActionResult
from src.governor.network_mediator import NetworkMediator

logger = logging.getLogger(__name__)


class WebSearchExecutor:
    """
    Executes a governed web search using the DuckDuckGo Instant Answer API.
    All outbound HTTP is routed through NetworkMediator.
    """

    def __init__(self, network: NetworkMediator):
        self.network = network

    def execute(self, request: ActionRequest) -> ActionResult:
        query = request.params.get("query", "").strip()
        if not query:
            return ActionResult.failure(
                "No search query provided.",
                request_id=request.request_id
            )

        boundary_notice = "I'm checking online."

        try:
            # Perform the search via NetworkMediator
            response = self.network.request(
                capability_id=request.capability_id,
                method="GET",
                url="https://api.duckduckgo.com/",
                params={
                    "q": query,
                    "format": "json",
                    "no_redirect": "1",
                    "no_html": "1",
                },
                headers={"User-Agent": "Nova/1.0"},
                as_json=True,
                timeout=5,
            )

            data = response.get("data", {})

        except Exception as e:
            logger.debug(f"DuckDuckGo API request failed: {e}")
            return ActionResult.failure(
                f"{boundary_notice} I couldn't complete the search due to a network issue.",
                request_id=request.request_id
            )

        # ----- Parse DuckDuckGo response -----
        results = []

        abstract = data.get("Abstract", "")
        abstract_url = data.get("AbstractURL", "")
        if abstract and abstract_url:
            results.append({
                "title": abstract[:100] + ("…" if len(abstract) > 100 else ""),
                "url": abstract_url,
                "snippet": "",
            })

        related = data.get("RelatedTopics", [])
        for item in related:
            if isinstance(item, dict):
                if "Topics" in item:
                    for sub in item["Topics"]:
                        if isinstance(sub, dict) and sub.get("FirstURL"):
                            results.append({
                                "title": sub.get("Text", "")[:100],
                                "url": sub.get("FirstURL", ""),
                                "snippet": "",
                            })
                elif item.get("FirstURL"):
                    results.append({
                        "title": item.get("Text", "")[:100],
                        "url": item.get("FirstURL", ""),
                        "snippet": "",
                    })

        results = results[:5]

        if not results:
            answer = data.get("Answer") or data.get("Abstract")
            if answer:
                results.append({
                    "title": answer,
                    "url": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
                    "snippet": "Instant Answer"
                })

        if not results:
            return ActionResult.ok(
                message=f"{boundary_notice} No results found.",
                data={"widget": {"type": "search", "data": {"results": []}}},
                request_id=request.request_id
            )

        summary_lines = [f"- {r['title']}" for r in results[:3]]
        user_message = f"{boundary_notice} I found {len(results)} results.\n" + "\n".join(summary_lines)

        widget_payload = {
            "type": "search",
            "data": {"results": results},
        }

        return ActionResult.ok(
            message=user_message,
            data={"widget": widget_payload},
            request_id=request.request_id
        )
