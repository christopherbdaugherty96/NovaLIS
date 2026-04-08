"""Web search skill for OpenClaw — wraps Governor capability 16.

Adapts the existing WebSearchExecutor (Brave + DuckDuckGo fallback) into
the BaseSkill/SkillResult contract so the OpenClaw agent system can use
web search as a composable tool.

Design constraints:
  - All network traffic goes through NetworkMediator (capability 16)
  - WebSearchExecutor is synchronous — wrapped in asyncio.to_thread()
  - Results are structured as SkillResult with widget_data for dashboard
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from src.base_skill import BaseSkill, SkillResult
from src.governor.network_mediator import NetworkMediator

logger = logging.getLogger(__name__)

SEARCH_CAPABILITY_ID = 16


class WebSearchSkill(BaseSkill):
    name = "web_search"
    description = "Search the web for information using Brave Search or DuckDuckGo"

    def __init__(self, network: NetworkMediator | None = None) -> None:
        self._network = network or NetworkMediator()

    def can_handle(self, query: str) -> bool:
        q = (query or "").strip().lower()
        if not q:
            return False
        if any(term in q for term in ("search for", "look up", "find online", "web search", "google")):
            return True
        if q.startswith("search "):
            return True
        return False

    async def handle(self, query: str) -> SkillResult:
        """Execute a web search and return structured results."""
        search_query = self._extract_query(query)
        if not search_query:
            return SkillResult(
                success=False,
                message="Please tell me what you'd like to search for.",
                skill=self.name,
            )

        try:
            result = await asyncio.to_thread(
                self._execute_search, search_query,
            )
            return result
        except Exception as exc:
            logger.warning("Web search failed: %s", exc)
            return SkillResult(
                success=False,
                message="Web search is unavailable right now.",
                data={"error": str(exc)[:200]},
                skill=self.name,
            )

    def _execute_search(self, query: str) -> SkillResult:
        """Run the search synchronously through WebSearchExecutor."""
        from src.executors.web_search_executor import WebSearchExecutor
        from src.governor.execute_boundary import ExecuteBoundary

        boundary = ExecuteBoundary()
        executor = WebSearchExecutor(self._network, boundary)

        # Build a minimal ActionRequest-compatible object
        request = _SearchRequest(
            capability_id=SEARCH_CAPABILITY_ID,
            params={"query": query},
            request_id=f"openclaw_search_{id(self)}",
        )

        action_result = executor.execute(request)

        # Convert ActionResult → SkillResult
        widget = {}
        if action_result.data and isinstance(action_result.data, dict):
            widget = action_result.data.get("widget", {})

        widget_data_inner = widget.get("data", {}) if isinstance(widget, dict) else {}
        results_list = widget_data_inner.get("results", []) if isinstance(widget_data_inner, dict) else []
        researched_summary = str(widget_data_inner.get("researched_summary", "")).strip()

        return SkillResult(
            success=action_result.success,
            message=action_result.message,
            data={
                "query": query,
                "result_count": len(results_list),
                "results": results_list[:5],
                "researched_summary": researched_summary,
                "provider": str(widget_data_inner.get("provider", "")).strip(),
            },
            widget_data={
                "type": "search",
                "data": widget_data_inner,
            },
            skill=self.name,
        )

    @staticmethod
    def _extract_query(raw: str) -> str:
        """Strip common prefixes to get the actual search query."""
        q = (raw or "").strip()
        for prefix in ("search for ", "search ", "look up ", "find online ", "web search "):
            if q.lower().startswith(prefix):
                q = q[len(prefix):].strip()
                break
        return q


class _SearchRequest:
    """Minimal duck-typed ActionRequest for WebSearchExecutor."""

    def __init__(self, capability_id: int, params: dict[str, Any], request_id: str) -> None:
        self.capability_id = capability_id
        self.params = params
        self.request_id = request_id
