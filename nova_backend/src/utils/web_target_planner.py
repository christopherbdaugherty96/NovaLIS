from __future__ import annotations

import re
from typing import Any, Mapping

# Presets and aliases that can open directly without confirmation.
WEB_PRESETS = {
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


def normalize_web_target_text(target: str) -> str:
    cleaned = (target or "").strip().lower()
    cleaned = re.sub(r"\b(?:website|webpage|site|homepage)\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(
        r"\b(?:[a-z]\s+){1,}[a-z]\b",
        lambda m: re.sub(r"\s+", "", m.group(0)),
        cleaned,
    )
    return cleaned


def domain_from_url(url: str) -> str:
    cleaned = (url or "").strip()
    host = cleaned
    if "://" in host:
        host = host.split("://", 1)[1]
    host = host.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0].lower().strip()
    if host.startswith("www."):
        host = host[4:]
    return host


def normalize_web_url(raw: str) -> str:
    candidate = (raw or "").strip()
    if not candidate:
        return ""
    if not re.match(r"^https?://", candidate, re.IGNORECASE):
        candidate = f"https://{candidate}"
    if not re.match(r"^https?://", candidate, re.IGNORECASE):
        return ""
    domain = domain_from_url(candidate)
    if not domain:
        return ""
    return candidate


def plan_web_open(params: Mapping[str, Any]) -> dict[str, Any]:
    preview = bool(params.get("preview"))
    confirmed = bool(params.get("confirmed"))

    resolved_url = normalize_web_url(str(params.get("resolved_url") or ""))
    if resolved_url:
        domain = domain_from_url(resolved_url)
        return {
            "ok": True,
            "url": resolved_url,
            "domain": domain or "unknown-domain",
            "display": domain or resolved_url,
            "requires_confirmation": True,
            "preview": preview,
            "confirmed": confirmed,
            "reason": "resolved_from_source",
        }

    target = normalize_web_target_text(str(params.get("target") or ""))
    if not target:
        return {"ok": False, "message": "Tell me which site to open."}

    if target in WEB_PRESETS:
        url = WEB_PRESETS[target]
        return {
            "ok": True,
            "url": url,
            "domain": domain_from_url(url),
            "display": target,
            "requires_confirmation": False,
            "preview": preview,
            "confirmed": confirmed,
            "reason": "preset_alias",
        }

    guessed_url = normalize_web_url(target)
    if guessed_url:
        domain = domain_from_url(guessed_url)
        return {
            "ok": True,
            "url": guessed_url,
            "domain": domain or "unknown-domain",
            "display": target,
            "requires_confirmation": True,
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
