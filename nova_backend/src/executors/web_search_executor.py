# src/executors/web_search_executor.py

import logging
import time
import os

from src.actions.action_result import ActionResult

logger = logging.getLogger(__name__)


class WebSearchExecutor:
    """
    Executes a governed web search using the Brave Search API.
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

        # Early check for API key to avoid silent misconfiguration
        brave_key = os.getenv("BRAVE_API_KEY")
        if not brave_key:
            return ActionResult(
                success=False,
                message="Search service is not configured.",
                request_id=request.request_id,
                data=self._empty_widget(),
            )

        boundary_notice = "I'm checking online."

        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                # Perform the search via NetworkMediator using Brave API
                response = self.network.request(
                    capability_id=request.capability_id,
                    method="GET",
                    url="https://api.search.brave.com/res/v1/web/search",
                    params={
                        "q": query,
                        "count": 5,
                    },
                    headers={
                        "Accept": "application/json",
                        "X-Subscription-Token": brave_key,
                    },
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

        # Handle specific HTTP error codes deterministically
        if status_code == 401:
            return ActionResult(
                success=False,
                message=f"{boundary_notice} Search authentication failed.",
                request_id=request.request_id,
                data=self._empty_widget(),
            )

        if status_code == 429:
            return ActionResult(
                success=False,
                message=f"{boundary_notice} Search rate limit reached. Please try again later.",
                request_id=request.request_id,
                data=self._empty_widget(),
            )

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

        # ----- Parse Brave response -----
        results = []

        web_data = data.get("web", {})
        brave_results = web_data.get("results", [])

        for item in brave_results:
            results.append(
                {
                    "title": item.get("title", "")[:100],
                    "url": item.get("url", ""),
                    "snippet": item.get("description", "")[:200],
                }
            )

        results = results[:5]

        if not results:
            return ActionResult.ok(
                message=f"{boundary_notice} No reliable results were found.",
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