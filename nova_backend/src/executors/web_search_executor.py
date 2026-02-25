# src/executors/web_search_executor.py

import logging
import time
from typing import Any, Dict

from src.actions.action_result import ActionResult

logger = logging.getLogger(__name__)


class WebSearchExecutor:
    """
    Executes a governed web search using the DuckDuckGo Instant Answer API.
    All outbound HTTP is routed through NetworkMediator.
    """

    def __init__(self, network_mediator):
        self.network = network_mediator
        # No execute_boundary – Governor owns lifecycle

    def _empty_widget(self) -> Dict[str, Any]:
        return {"widget": {"type": "search", "data": {"results": []}}}

    def execute(self, request_id: str, params: dict) -> ActionResult:
        query = params.get("query", "").strip()
        if not query:
            return ActionResult.failure(
                "Sure – what would you like me to search for?",
                request_id=request_id
            )

        boundary_notice = "I'm checking online."
        capability_id = params.get("capability_id")
        if not capability_id:
            return ActionResult.failure(
                "Internal configuration error: missing capability ID.",
                request_id=request_id
            )

        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                response = self.network.request(
                    capability_id=capability_id,
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
                break
            except Exception as e:
                logger.debug("Attempt %d failed: %s", attempt + 1, e)
                if attempt == max_retries:
                    return ActionResult.failure(
                        f"{boundary_notice} I'm having trouble reaching the search service right now. "
                        "Please try again in a moment.",
                        request_id=request_id
                    )
                time.sleep(0.5)

        status_code = response.get("status_code")
        data = response.get("data") or {}

        if status_code != 200:
            if status_code == 202:
                return ActionResult.failure(
                    f"{boundary_notice} The search service is temporarily busy. Please try again shortly.",
                    request_id=request_id
                )
            return ActionResult.failure(
                f"{boundary_notice} I received an unexpected response from the search service. This might be temporary.",
                request_id=request_id
            )

        # ----- Parse DuckDuckGo response -----
        results = []

        abstract = data.get("Abstract", "")
        abstract_url = data.get("AbstractURL", "")
        if abstract and abstract_url:
            results.append({
                "title": (abstract[:97] + "…") if len(abstract) > 100 else abstract,
                "url": abstract_url,
                "snippet": "",
            })

        related = data.get("RelatedTopics", [])
        for item in related:
            if isinstance(item, dict):
                if "Topics" in item:
                    for sub in item["Topics"]:
                        if isinstance(sub, dict) and sub.get("FirstURL"):
                            text = sub.get("Text", "")
                            results.append({
                                "title": (text[:97] + "…") if len(text) > 100 else text,
                                "url": sub.get("FirstURL", ""),
                                "snippet": "",
                            })
                elif item.get("FirstURL"):
                    text = item.get("Text", "")
                    results.append({
                        "title": (text[:97] + "…") if len(text) > 100 else text,
                        "url": item.get("FirstURL", ""),
                        "snippet": "",
                    })

        results = results[:5]

        if not results:
            answer = data.get("Answer") or data.get("Abstract")
            if answer:
                results.append({
                    "title": (answer[:97] + "…") if len(answer) > 100 else answer,
                    "url": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
                    "snippet": "Instant Answer"
                })

        if not results:
            return ActionResult.ok(
                message=f"{boundary_notice} I couldn't find any results for that.",
                data=self._empty_widget(),
                request_id=request_id
            )

        numbered_lines = [f"{i+1}. {r['title']}" for i, r in enumerate(results[:3])]
        user_message = f"Here are the top results:\n\n" + "\n".join(numbered_lines)

        widget_payload = {
            "type": "search",
            "data": {"results": results},
        }

        return ActionResult.ok(
            message=user_message,
            data={"widget": widget_payload},
            request_id=request_id
        )