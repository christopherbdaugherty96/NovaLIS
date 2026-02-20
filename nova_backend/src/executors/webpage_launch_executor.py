# src/executors/webpage_launch_executor.py

import webbrowser
from src.actions.action_request import ActionRequest
from src.actions.action_result import ActionResult
from src.ledger.writer import LedgerWriter

# Static preset mapping (Phase‑2 only)
PRESETS = {
    "google": "https://www.google.com",
    "facebook": "https://www.facebook.com",
    "pandora": "https://www.pandora.com",
    "github": "https://www.github.com",
    "twitter": "https://www.twitter.com",
    "youtube": "https://www.youtube.com",
}

class WebpageLaunchExecutor:
    """
    Executes a governed webpage launch for preset domains.
    No dynamic lookup, no confirmation – pure static mapping.
    """

    def __init__(self, ledger: LedgerWriter):
        self.ledger = ledger

    def execute(self, request: ActionRequest) -> ActionResult:
        target = request.params.get("target", "").lower()
        print(f"[DEBUG] WebpageLaunchExecutor executing for target '{target}'")

        url = PRESETS.get(target)

        if not url:
            print(f"[DEBUG] Target '{target}' not in presets")
            return ActionResult.failure(
                f"I don't have a preset for '{target}'.",
                request_id=request.request_id
            )

        try:
            webbrowser.open(url)
            # Log success
            self.ledger.log_event("WEBPAGE_LAUNCH", {
                "requested_name": target,
                "resolved_url": url,
                "preset": True,
                "success": True,
                "request_id": request.request_id
            })
            print(f"[DEBUG] Browser opened for {url}")
            return ActionResult.ok(
                f"Opening {url}.",
                request_id=request.request_id
            )
        except Exception as e:
            print(f"[DEBUG] Exception in webbrowser.open: {e}")
            # Log failure
            self.ledger.log_event("WEBPAGE_LAUNCH", {
                "requested_name": target,
                "resolved_url": url,
                "preset": True,
                "success": False,
                "error": str(e),
                "request_id": request.request_id
            })
            return ActionResult.failure(
                "Could not open the browser.",
                request_id=request.request_id
            )