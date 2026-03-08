# src/executors/web_search_executor.py

import logging
import os
import time

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
        return (url or "").split("//")[-1].split("/")[0].strip().lower()

    def _parse_results(self, data: dict) -> list[dict]:
        # Brave format
        web_results = ((data.get("web") or {}).get("results") or []) if isinstance(data, dict) else []
        if web_results:
            out = []
            for item in web_results:
                out.append(
                    {
                        "title": (item.get("title") or "")[:100],
                        "url": item.get("url", ""),
                        "snippet": (item.get("description") or "")[:200],
                    }
                )
            return out

        # Legacy Duck style used by tests
        out = []
        abstract = (data.get("Abstract") or "").strip() if isinstance(data, dict) else ""
        abstract_url = (data.get("AbstractURL") or "").strip() if isinstance(data, dict) else ""
        if abstract and abstract_url:
            title = (abstract[:99] + "…") if len(abstract) > 100 else abstract
            out.append({"title": title, "url": abstract_url, "snippet": abstract[:200]})

        for topic in (data.get("RelatedTopics") or []) if isinstance(data, dict) else []:
            if isinstance(topic, dict) and topic.get("FirstURL") and topic.get("Text"):
                out.append({"title": topic["Text"][:100], "url": topic["FirstURL"], "snippet": topic["Text"][:200]})
            for sub in topic.get("Topics", []) if isinstance(topic, dict) else []:
                if isinstance(sub, dict) and sub.get("FirstURL") and sub.get("Text"):
                    out.append({"title": sub["Text"][:100], "url": sub["FirstURL"], "snippet": sub["Text"][:200]})

        return out

    def execute(self, request) -> ActionResult:
        query = request.params.get("query", "").strip()
        session_id = str(request.params.get("session_id") or "").strip() or None
        if not query:
            return ActionResult.failure("No search query provided.", data=self._empty_widget(), request_id=request.request_id)

        boundary_notice = "I'm checking online."
        started_at = time.monotonic()

        brave_key = os.getenv("BRAVE_API_KEY", "").strip()
        if not brave_key:
            return ActionResult.failure("Web search is not configured.", data=self._empty_widget(), request_id=request.request_id)

        max_retries = 1
        for attempt in range(max_retries + 1):
            if time.monotonic() - started_at > SEARCH_HARD_TIMEOUT_SECONDS:
                return ActionResult.failure(f"{boundary_notice} Search timed out. Please try again.", data=self._empty_widget(), request_id=request.request_id)
            try:
                response = self.network.request(
                    capability_id=request.capability_id,
                    method="GET",
                    url="https://api.search.brave.com/res/v1/web/search",
                    params={"q": query, "count": 5},
                    headers={"Accept": "application/json", "X-Subscription-Token": brave_key},
                    as_json=True,
                    timeout=5,
                    request_id=request.request_id,
                    session_id=session_id,
                )
                break
            except Exception as error:
                if error.__class__.__name__ != "NetworkMediatorError":
                    raise
                logger.debug("Attempt %s failed: %s", attempt + 1, error)
                if attempt == max_retries:
                    return ActionResult.failure(
                        f"{boundary_notice} I couldn't complete the search due to a network issue.",
                        data=self._empty_widget(),
                        request_id=request.request_id,
                    )
                time.sleep(0.5)

        status_code = response.get("status_code")
        data = response.get("data") or {}

        if status_code == 401:
            return ActionResult.failure(f"{boundary_notice} Search authentication failed.", data=self._empty_widget(), request_id=request.request_id)
        if status_code == 429:
            return ActionResult.failure(f"{boundary_notice} Search rate limit reached. Please try again later.", data=self._empty_widget(), request_id=request.request_id)
        if status_code != 200:
            if status_code == 202:
                return ActionResult.failure(f"{boundary_notice} Search is temporarily unavailable. Please try again later.", data=self._empty_widget(), request_id=request.request_id)
            return ActionResult.failure(f"{boundary_notice} I received an unexpected response from the search service.", data=self._empty_widget(), request_id=request.request_id)

        results = self._parse_results(data)[:5]
        if not results:
            return ActionResult.ok(message=f"{boundary_notice} No results found.", data=self._empty_widget(), request_id=request.request_id)

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

        return ActionResult.ok(
            message=user_message,
            data={"widget": {"type": "search", "data": {"results": results}}},
            request_id=request.request_id,
        )
