"""
NovaLIS — Phase-2 Handler: open_view
"""

import webbrowser
from typing import Dict, Any
from urllib.parse import urlparse

from ...actions.action_request import ActionRequest
from ...actions.action_result import ActionResult
from ...actions.action_types import ActionType

def _allowed_views() -> Dict[str, Dict[str, Any]]:
    return {
        "dashboard": {
            "name": "Nova Dashboard",
            "url": "http://localhost:8080",
        },
        "news": {
            "name": "News View",
            "url": "https://www.reuters.com",
        },
        # ✅ FIX 1: Added "weather" entry
        "weather": {
            "name": "Weather View",
            "url": "https://www.weather.com",
        },
    }

def open_view(action: ActionRequest) -> ActionResult:
    if not isinstance(action, ActionRequest):
        return ActionResult(False, "Invalid action request.")

    if action.action_type is not ActionType.OPEN_VIEW:
        return ActionResult(False, "Invalid action type.")

    payload = action.payload or {}
    view_id = (payload.get("view_id") or "").strip().lower()

    if not view_id:
        return ActionResult(False, "No view specified.")

    spec = _allowed_views().get(view_id)
    if not spec:
        return ActionResult(
            success=False,
            message="That view is not approved to open.",
            data={"view_id": view_id},
        )

    url = spec.get("url")
    name = spec.get("name", view_id)

    # URL safety
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return ActionResult(False, "That view URL is not allowed.")

    try:
        opened = bool(webbrowser.open(url))
        if not opened:
            return ActionResult(False, f"{name} could not be opened.")
        return ActionResult(True, f"Opened {name}.", {"url": url})
    except Exception:
        return ActionResult(False, f"{name} could not be opened.")