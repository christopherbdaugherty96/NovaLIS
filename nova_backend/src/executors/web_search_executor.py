# src/executors/web_search_executor.py

import os
from typing import Dict, Any, List

from src.actions.action_request import ActionRequest
from src.actions.action_result import ActionResult
from src.governor.network_mediator import NetworkMediator
from src.governor.execute_boundary import ExecuteBoundary
from src.governor.exceptions import NetworkMediatorError


BRAVE_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"
DEFAULT_COUNT = 5


class WebSearchExecutor:
    """
    Read-only governed web search.
    Deterministic. No ranking logic. No query mutation.
    Returns structured results only.
    """

    def __init__(self, network: NetworkMediator, boundary: ExecuteBoundary):
        self.network = network
        self.boundary = boundary

    def execute(self, request: ActionRequest) -> ActionResult:
        query = (request.params.get("query") or "").strip()
        if not query:
            return ActionResult.refusal("Search query cannot be empty.", request_id=request.request_id)

        api_key = os.getenv("BRAVE_API_KEY")
        if not api_key:
            return ActionResult.refusal("Search service is not configured.", request_id=request.request_id)

        headers = {
            "X-Subscription-Token": api_key,
            "Accept": "application/json",
        }

        params = {
            "q": query,
            "count": DEFAULT_COUNT,
        }

        # Check timeout before network call (enter_execution must have been called by Governor)
        self.boundary.check_timeout()

        try:
            result = self.network.request(
                capability_id=16,
                method="GET",
                url=BRAVE_ENDPOINT,
                params=params,
                headers=headers,
            )
        except NetworkMediatorError:
            # Mediator already logged details; return a user-friendly refusal.
            return ActionResult.refusal("Search failed due to a network issue.", request_id=request.request_id)

        self.boundary.check_timeout()

        payload = result.get("data") or {}
        web_results = (payload.get("web") or {}).get("results") or []

        structured: List[Dict[str, Any]] = [
            {
                "title": r.get("title"),
                "url": r.get("url"),
                "description": r.get("description"),
            }
            for r in web_results[:DEFAULT_COUNT]
        ]

        return ActionResult.ok({"results": structured}, request_id=request.request_id)