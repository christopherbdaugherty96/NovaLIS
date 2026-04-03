from __future__ import annotations

"""Connection cards API.

Endpoints
---------
GET  /api/settings/connections                     — all provider statuses (safe, no key values)
POST /api/settings/connections/{provider}/key      — save key + run health check
POST /api/settings/connections/{provider}/test     — re-run health check on existing key
DELETE /api/settings/connections/{provider}        — clear single provider key
DELETE /api/settings/connections/all               — clear all provider keys (with confirmed=true guard)
"""

import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from src.connections.connections_store import connections_store, PROVIDER_REGISTRY


def build_connections_router() -> APIRouter:
    router = APIRouter()

    # ------------------------------------------------------------------
    # GET /api/settings/connections
    # ------------------------------------------------------------------

    @router.get("/api/settings/connections")
    async def get_connections():
        """Return safe status for every registered provider."""
        return connections_store.snapshot()

    # ------------------------------------------------------------------
    # POST /api/settings/connections/{provider}/key
    # ------------------------------------------------------------------

    @router.post("/api/settings/connections/{provider}/key")
    async def save_and_test_key(provider: str, payload: dict[str, Any]):
        """Save a provider key and run a health check. Returns pass/fail."""
        if provider not in PROVIDER_REGISTRY:
            raise HTTPException(status_code=404, detail=f"Unknown provider: {provider}")

        key = str(payload.get("key") or "").strip()
        if not key:
            raise HTTPException(status_code=400, detail="key must be a non-empty string")

        # Persist key and update env var
        connections_store.save_key(provider, key)

        # Run health check
        ok, detail = _health_check(provider, key)
        snap = connections_store.record_health(provider, ok=ok, detail=detail)

        return {"ok": ok, "detail": detail, "provider": snap}

    # ------------------------------------------------------------------
    # POST /api/settings/connections/{provider}/test
    # ------------------------------------------------------------------

    @router.post("/api/settings/connections/{provider}/test")
    async def test_existing_key(provider: str):
        """Re-run health check against the already-stored key."""
        if provider not in PROVIDER_REGISTRY:
            raise HTTPException(status_code=404, detail=f"Unknown provider: {provider}")

        key = connections_store.get_key(provider)
        if not key:
            raise HTTPException(status_code=400, detail="No key stored for this provider")

        ok, detail = _health_check(provider, key)
        snap = connections_store.record_health(provider, ok=ok, detail=detail)

        return {"ok": ok, "detail": detail, "provider": snap}

    # ------------------------------------------------------------------
    # DELETE /api/settings/connections/all  (must be before /{provider})
    # ------------------------------------------------------------------

    @router.delete("/api/settings/connections/all")
    async def clear_all_keys(payload: dict[str, Any] | None = None):
        """Clear all provider keys. Requires confirmed=true in body."""
        confirmed = bool((payload or {}).get("confirmed"))
        if not confirmed:
            raise HTTPException(
                status_code=400,
                detail="Pass {\"confirmed\": true} to reset all connections.",
            )
        providers = connections_store.clear_all()
        return {"ok": True, "providers": providers}

    # ------------------------------------------------------------------
    # DELETE /api/settings/connections/{provider}
    # ------------------------------------------------------------------

    @router.delete("/api/settings/connections/{provider}")
    async def clear_provider_key(provider: str):
        """Clear a single provider key and remove the env var."""
        if provider not in PROVIDER_REGISTRY:
            raise HTTPException(status_code=404, detail=f"Unknown provider: {provider}")

        snap = connections_store.clear_key(provider)
        return {"ok": True, "provider": snap}

    return router


# ---------------------------------------------------------------------------
# Health-check implementations (one per provider kind)
# ---------------------------------------------------------------------------

def _health_check(provider_id: str, key: str) -> tuple[bool, str]:
    """Run a lightweight connectivity check for the given provider.

    Returns (ok: bool, detail: str).  Never raises — all errors are caught
    and returned as (False, error_message).
    """
    try:
        checker = _HEALTH_CHECKERS.get(provider_id, _check_token)
        return checker(key)
    except Exception as exc:
        return False, f"Unexpected error: {exc}"


def _check_openai(key: str) -> tuple[bool, str]:
    import requests
    try:
        r = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=8,
        )
        if r.status_code == 200:
            return True, "Connected — models endpoint responded."
        if r.status_code == 401:
            return False, "Invalid API key (401)."
        if r.status_code == 429:
            return True, "Key valid but rate-limited (429). Treating as connected."
        return False, f"Unexpected status {r.status_code}."
    except requests.exceptions.Timeout:
        return False, "Request timed out."
    except requests.exceptions.ConnectionError:
        return False, "Could not reach api.openai.com. Check your network."


def _check_brave(key: str) -> tuple[bool, str]:
    import requests
    try:
        r = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": "test", "count": "1"},
            headers={"X-Subscription-Token": key, "Accept": "application/json"},
            timeout=8,
        )
        if r.status_code == 200:
            return True, "Connected — search endpoint responded."
        if r.status_code == 401:
            return False, "Invalid subscription token (401)."
        if r.status_code == 429:
            return True, "Key valid but rate-limited (429). Treating as connected."
        return False, f"Unexpected status {r.status_code}."
    except requests.exceptions.Timeout:
        return False, "Request timed out."
    except requests.exceptions.ConnectionError:
        return False, "Could not reach api.search.brave.com."


def _check_news(key: str) -> tuple[bool, str]:
    import requests
    try:
        r = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={"country": "us", "pageSize": "1", "apiKey": key},
            timeout=8,
        )
        if r.status_code == 200:
            return True, "Connected — headlines endpoint responded."
        if r.status_code == 401:
            return False, "Invalid API key (401)."
        if r.status_code == 426:
            return False, "Plan upgrade required (426)."
        return False, f"Unexpected status {r.status_code}."
    except requests.exceptions.Timeout:
        return False, "Request timed out."
    except requests.exceptions.ConnectionError:
        return False, "Could not reach newsapi.org."


def _check_weather(key: str) -> tuple[bool, str]:
    import requests
    try:
        r = requests.get(
            "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/london",
            params={"key": key, "include": "current", "contentType": "json", "unitGroup": "metric"},
            timeout=8,
        )
        if r.status_code == 200:
            return True, "Connected — forecast endpoint responded."
        if r.status_code == 401:
            return False, "Invalid API key (401)."
        if r.status_code == 429:
            return True, "Key valid but rate-limited (429). Treating as connected."
        return False, f"Unexpected status {r.status_code}."
    except requests.exceptions.Timeout:
        return False, "Request timed out."
    except requests.exceptions.ConnectionError:
        return False, "Could not reach weather.visualcrossing.com."


def _check_calendar(path: str) -> tuple[bool, str]:
    """Calendar provider uses a file path, not an API key."""
    p = Path(path)
    if not path.strip():
        return False, "No file path provided."
    if not p.exists():
        return False, f"File not found: {path}"
    if not p.suffix.lower() == ".ics":
        return False, "File must be an .ics calendar file."
    return True, f"File found: {p.name}"


def _check_token(key: str) -> tuple[bool, str]:
    """Generic token check — just validates the key is non-empty."""
    if len(key) < 8:
        return False, "Token too short (minimum 8 characters)."
    return True, "Token saved."


_HEALTH_CHECKERS: dict[str, Any] = {
    "openai": _check_openai,
    "brave": _check_brave,
    "news": _check_news,
    "weather": _check_weather,
    "calendar": _check_calendar,
    "bridge": _check_token,
}
