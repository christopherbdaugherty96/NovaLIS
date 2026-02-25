# src/executors/web_search_executor.py

import logging
import time

from src.actions.action_result import ActionResult

logger = logging.getLogger(__name__)


class WebSearchExecutor:
    """
    Executes a governed web search using the DuckDuckGo Instant Answer API.
    All outbound HTTP is routed through NetworkMediator.
    """

    def __init__(self, network, execute_boundary):
        self.network = network
        self.execute_boundary = execute_boundary

    def _empty_widget(self) -> dict:
        """Return a stable empty search widget."""
        return {"widget": {"type": "search", "data": {"results": []}}}

    def execute(self, request) -> ActionResult:
        query = request.params.get("query", "").strip()
        if not query:
            return ActionResult(
                success=False,
                message="No search query provided.",
                request_id=request.request_id,
                data=self._empty_widget(),
            )

        boundary_notice = "I'm checking online."

        max_retries = 1
        for attempt in range(max_retries + 1):
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
                break
            except Exception as error:
                if error.__class__.__name__ != "NetworkMediatorError":
                    raise
                logger.debug("Attempt %s failed: %s", attempt + 1, error)
                if attempt == max_retries:
                    return ActionResult(
                        success=False,
                        message=f"{boundary_notice} I couldn't complete the search due to a network issue.",
                        request_id=request.request_id,
                        data=self._empty_widget(),
                    )
                # Simple fixed backoff is acceptable for the current Phase-4 synchronous model.
                time.sleep(0.5)

        # If we get here, the request succeeded (status_code may be non-200)
        status_code = response.get("status_code")
        # Defensive: ensure data is a dict even if mediator returns None
        data = response.get("data") or {}

        if status_code != 200:
            if status_code == 202:
                return ActionResult(
                    success=False,
                    message=f"{boundary_notice} Search is temporarily unavailable. Please try again later.",
                    request_id=request.request_id,
                    data=self._empty_widget(),
                )
            return ActionResult(
                success=False,
                message=f"{boundary_notice} I received an unexpected response from the search service.",
                request_id=request.request_id,
                data=self._empty_widget(),
            )

        # ----- Parse DuckDuckGo response (only when status_code == 200) -----
        results = []

        abstract = data.get("Abstract", "")
        abstract_url = data.get("AbstractURL", "")
        if abstract and abstract_url:
            results.append(
                {
                    "title": (abstract[:97] + "…") if len(abstract) > 100 else abstract,
                    "url": abstract_url,
                    "snippet": "",
                }
            )

        related = data.get("RelatedTopics", [])
        for item in related:
            if isinstance(item, dict):
                if "Topics" in item:
                    for sub in item["Topics"]:
                        if isinstance(sub, dict) and sub.get("FirstURL"):
                            text = sub.get("Text", "")
                            results.append(
                                {
                                    "title": (text[:97] + "…") if len(text) > 100 else text,
                                    "url": sub.get("FirstURL", ""),
                                    "snippet": "",
                                }
                            )
                elif item.get("FirstURL"):
                    text = item.get("Text", "")
                    results.append(
                        {
                            "title": (text[:97] + "…") if len(text) > 100 else text,
                            "url": item.get("FirstURL", ""),
                            "snippet": "",
                        }
                    )

        results = results[:5]

        if not results:
            answer = data.get("Answer") or data.get("Abstract")
            if answer:
                results.append(
                    {
                        "title": (answer[:97] + "…") if len(answer) > 100 else answer,
                        "url": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
                        "snippet": "Instant Answer",
                    }
                )

        if not results:
            return ActionResult.ok(
                message=f"{boundary_notice} No results found.",
                data=self._empty_widget(),
                request_id=request.request_id,
            )

        summary_lines = [f"- {result['title']}" for result in results[:3]]
        user_message = f"{boundary_notice} I found {len(results)} results.\n" + "\n".join(summary_lines)

        widget_payload = {
            "type": "search",
            "data": {"results": results},
        }

        return ActionResult.ok(
            message=user_message,
            data={"widget": widget_payload},
            request_id=request.request_id,
        )
