from __future__ import annotations

import re
import webbrowser

from src.actions.action_result import ActionResult
from src.ledger.writer import LedgerWriter

# Presets and aliases that can open directly without confirmation.
PRESETS = {
    "google": "https://www.google.com",
    "facebook": "https://www.facebook.com",
    "pandora": "https://www.pandora.com",
    "github": "https://www.github.com",
    "twitter": "https://www.twitter.com",
    "youtube": "https://www.youtube.com",
    "abc news": "https://abcnews.go.com",
    "abc": "https://abcnews.go.com",
    "fox news": "https://www.foxnews.com",
    "fox": "https://www.foxnews.com",
    "cnn": "https://www.cnn.com",
    "bbc": "https://www.bbc.com/news",
    "reuters": "https://www.reuters.com",
    "ap": "https://apnews.com",
    "npr": "https://www.npr.org",
}

SAFE_DIRECT_DOMAINS = {
    "google.com",
    "github.com",
    "youtube.com",
    "facebook.com",
    "twitter.com",
    "x.com",
    "cnn.com",
    "bbc.com",
    "reuters.com",
    "apnews.com",
    "npr.org",
    "foxnews.com",
    "abcnews.go.com",
}


class WebpageLaunchExecutor:
    """Executes governed webpage launch with normalization, preview, and guarded confirmation."""

    def __init__(self, ledger: LedgerWriter):
        self.ledger = ledger

    @staticmethod
    def _normalize_target_text(target: str) -> str:
        cleaned = (target or "").strip().lower()
        cleaned = re.sub(r"\b(?:website|webpage|site|homepage)\b", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        cleaned = re.sub(
            r"\b(?:[a-z]\s+){1,}[a-z]\b",
            lambda m: re.sub(r"\s+", "", m.group(0)),
            cleaned,
        )
        return cleaned

    @staticmethod
    def _domain_from_url(url: str) -> str:
        cleaned = (url or "").strip()
        host = cleaned
        if "://" in host:
            host = host.split("://", 1)[1]
        host = host.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0].lower().strip()
        if host.startswith("www."):
            host = host[4:]
        return host

    @classmethod
    def _normalize_url(cls, raw: str) -> str:
        candidate = (raw or "").strip()
        if not candidate:
            return ""
        if not re.match(r"^https?://", candidate, re.IGNORECASE):
            candidate = f"https://{candidate}"
        if not re.match(r"^https?://", candidate, re.IGNORECASE):
            return ""
        domain = cls._domain_from_url(candidate)
        if not domain:
            return ""
        return candidate

    @classmethod
    def plan_open(cls, params: dict) -> dict:
        """Resolve a target into an actionable plan used by brain_server and executor."""
        preview = bool(params.get("preview"))
        confirmed = bool(params.get("confirmed"))

        resolved_url = cls._normalize_url(str(params.get("resolved_url") or ""))
        if resolved_url:
            domain = cls._domain_from_url(resolved_url)
            known = any(domain == safe or domain.endswith(f".{safe}") for safe in SAFE_DIRECT_DOMAINS)
            return {
                "ok": True,
                "url": resolved_url,
                "domain": domain or "unknown-domain",
                "display": domain or resolved_url,
                "requires_confirmation": not known,
                "preview": preview,
                "confirmed": confirmed,
                "reason": "resolved_from_source",
            }

        target = cls._normalize_target_text(str(params.get("target") or ""))
        if not target:
            return {"ok": False, "message": "Tell me which site to open."}

        if target in PRESETS:
            url = PRESETS[target]
            return {
                "ok": True,
                "url": url,
                "domain": cls._domain_from_url(url),
                "display": target,
                "requires_confirmation": False,
                "preview": preview,
                "confirmed": confirmed,
                "reason": "preset_alias",
            }

        guessed_url = cls._normalize_url(target)
        if guessed_url:
            domain = cls._domain_from_url(guessed_url)
            known = any(domain == safe or domain.endswith(f".{safe}") for safe in SAFE_DIRECT_DOMAINS)
            return {
                "ok": True,
                "url": guessed_url,
                "domain": domain or "unknown-domain",
                "display": target,
                "requires_confirmation": not known,
                "preview": preview,
                "confirmed": confirmed,
                "reason": "normalized_domain",
            }

        return {
            "ok": False,
            "message": (
                f"I couldn't normalize '{target}' into a valid website. "
                "Try 'open cnn.com' or 'open github'."
            ),
        }

    def execute(self, request) -> ActionResult:
        plan = self.plan_open(request.params or {})
        if not plan.get("ok"):
            return ActionResult.failure(str(plan.get("message") or "Unable to resolve website target."), request_id=request.request_id)

        url = str(plan["url"])
        domain = str(plan.get("domain") or "")

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
                "Use 'yes' to open now or 'no' to cancel."
            )
            return ActionResult.ok(
                message=preview_text,
                request_id=request.request_id,
                data={"widget": {"type": "website_preview", "data": {"url": url, "domain": domain, "risk": "low"}}},
            )

        try:
            webbrowser.open(url)
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
                    f"Opened {domain or url}.\n"
                    "Reason: user-invoked.\n"
                    "Risk: low."
                ),
                request_id=request.request_id,
                data={"opened_domain": domain or url},
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
            return ActionResult.failure("Could not open the browser.", request_id=request.request_id)
