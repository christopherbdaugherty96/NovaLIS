# src/executors/web_search_executor.py

import logging
import time
import os

from src.actions.action_result import ActionResult
from src.conversation.response_style_router import ResponseTemplates

logger = logging.getLogger(__name__)

SEARCH_HARD_TIMEOUT_SECONDS = 7.0


class WebSearchExecutor:
    _avg_latency_seconds = 0.0
    _latency_samples = 0
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

    @classmethod
    def _record_latency(cls, elapsed_seconds: float) -> float:
        cls._latency_samples += 1
        if cls._latency_samples == 1:
            cls._avg_latency_seconds = elapsed_seconds
        else:
            cls._avg_latency_seconds = ((cls._avg_latency_seconds * (cls._latency_samples - 1)) + elapsed_seconds) / cls._latency_samples
        return cls._avg_latency_seconds

    @staticmethod
    def _extract_domain(url: str) -> str:
        clean = (url or "").split("//")[-1].split("/")[0].strip().lower()
        return clean

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
        started_at = time.monotonic()

        max_retries = 1
        for attempt in range(max_retries + 1):
            if time.monotonic() - started_at > SEARCH_HARD_TIMEOUT_SECONDS:
                return ActionResult(
                    success=False,
                    message=f"{boundary_notice} Search timed out. Please try again.",
                    request_id=request.request_id,
                    data=self._empty_widget(),
                )
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

        top_domains = []
        for result in results[:3]:
            domain = self._extract_domain(result.get("url", ""))
            if domain and domain not in top_domains:
                top_domains.append(domain)

        elapsed_seconds = time.monotonic() - started_at
        avg_latency = self._record_latency(elapsed_seconds)
        logger.info("web_search latency=%.2fs avg=%.2fs query=%s", elapsed_seconds, avg_latency, query[:80])

        brief_query = query[:80]
        intro = ResponseTemplates.bounded_research_intro(brief_query)
        findings_block = ResponseTemplates.top_findings_block([result["title"] for result in results[:3]])
        sources_block = ResponseTemplates.sources_block(top_domains)

        report_sections = [
            f"{boundary_notice} {intro}",
            "",
            findings_block,
            "",
            sources_block,
            "",
            f"Search latency: {elapsed_seconds:.1f}s (avg {avg_latency:.1f}s).",
            "Open any dashboard result for full article detail.",
        ]
        user_message = "\n".join(report_sections)

        widget_payload = {
            "type": "search",
            "data": {"results": results},
        }

        return ActionResult.ok(
            message=user_message,
            data={"widget": widget_payload},
            request_id=request.request_id,
        )