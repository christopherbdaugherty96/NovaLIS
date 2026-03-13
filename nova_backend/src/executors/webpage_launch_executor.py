from __future__ import annotations

import webbrowser

from src.actions.action_result import ActionResult
from src.ledger.writer import LedgerWriter
from src.utils.web_target_planner import domain_from_url, plan_web_open

class WebpageLaunchExecutor:
    """Executes governed webpage launch with normalization, preview, and guarded confirmation."""

    def __init__(self, ledger: LedgerWriter):
        self.ledger = ledger

    @classmethod
    def plan_open(cls, params: dict) -> dict:
        """Resolve a target into an actionable plan used by brain_server and executor."""
        return plan_web_open(params)

    def execute(self, request) -> ActionResult:
        plan = self.plan_open(request.params or {})
        if not plan.get("ok"):
            return ActionResult.failure(str(plan.get("message") or "Unable to resolve website target."), request_id=request.request_id)

        url = str(plan["url"])
        domain = str(plan.get("domain") or domain_from_url(url))

        if plan.get("preview"):
            self.ledger.log_event(
                "WEBPAGE_PREVIEW",
                {
                    "resolved_url": url,
                    "domain": domain,
                    "request_id": request.request_id,
                    "reason": plan.get("reason"),
                },
            )
            preview_text = (
                f"Preview ready: {domain or url}\n"
                f"URL: {url}\n"
                "Risk: low\n"
                "Reply 'yes' to open it now or 'no' to cancel."
            )
            return ActionResult.ok(
                message=preview_text,
                request_id=request.request_id,
                data={"widget": {"type": "website_preview", "data": {"url": url, "domain": domain, "risk": "low"}}},
            )

        try:
            opened = bool(webbrowser.open(url))
            if not opened:
                self.ledger.log_event(
                    "WEBPAGE_LAUNCH",
                    {
                        "resolved_url": url,
                        "domain": domain,
                        "success": False,
                        "error": "webbrowser.open returned False",
                        "request_id": request.request_id,
                        "reason": plan.get("reason"),
                    },
                )
                return ActionResult.failure(
                    "I couldn't open your default browser for that website.",
                    data={"url": url, "domain": domain},
                    request_id=request.request_id,
                )
            self.ledger.log_event(
                "WEBPAGE_LAUNCH",
                {
                    "resolved_url": url,
                    "domain": domain,
                    "success": True,
                    "request_id": request.request_id,
                    "reason": plan.get("reason"),
                },
            )
            return ActionResult.ok(
                message=(
                    f"Opened {domain or url} in your default browser.\n"
                    "Reason: user-invoked.\n"
                    "Risk: low.\n"
                    f"URL: {url}"
                ),
                request_id=request.request_id,
                data={"opened_domain": domain or url, "url": url},
            )
        except Exception as error:
            self.ledger.log_event(
                "WEBPAGE_LAUNCH",
                {
                    "resolved_url": url,
                    "domain": domain,
                    "success": False,
                    "error": str(error),
                    "request_id": request.request_id,
                    "reason": plan.get("reason"),
                },
            )
            return ActionResult.failure(
                "I couldn't open your default browser for that website.",
                data={"url": url, "domain": domain},
                request_id=request.request_id,
            )
