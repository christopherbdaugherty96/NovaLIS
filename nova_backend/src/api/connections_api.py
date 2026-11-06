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

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from fastapi import APIRouter, HTTPException

from src.connections.connections_store import PROVIDER_REGISTRY, connections_store
from src.governor.exceptions import (
    DisclosureDeniedError,
    NetworkMediatorError,
    ProviderConnectionNetworkError,
)
from src.governor.network_mediator import NetworkMediator


@dataclass(frozen=True)
class ConnectionHealthOperation:
    url: str
    params: Callable[[str], dict[str, str] | None]
    headers: Callable[[str], dict[str, str] | None]


CONNECTION_HEALTH_OPERATIONS = {
    "openai": ConnectionHealthOperation(
        url="https://api.openai.com/v1/models",
        params=lambda _key: None,
        headers=lambda key: {"Authorization": f"Bearer {key}"},
    ),
    "brave": ConnectionHealthOperation(
        url="https://api.search.brave.com/res/v1/web/search",
        params=lambda _key: {"q": "test", "count": "1"},
        headers=lambda key: {
            "X-Subscription-Token": key,
            "Accept": "application/json",
        },
    ),
    "news": ConnectionHealthOperation(
        url="https://newsapi.org/v2/top-headlines",
        params=lambda key: {"country": "us", "pageSize": "1", "apiKey": key},
        headers=lambda _key: None,
    ),
    "weather": ConnectionHealthOperation(
        url=(
            "https://weather.visualcrossing.com/VisualCrossingWebServices/"
            "rest/services/timeline/london"
        ),
        params=lambda key: {
            "key": key,
            "include": "current",
            "contentType": "json",
            "unitGroup": "metric",
        },
        headers=lambda _key: None,
    ),
}


def _reject_trial_provider_operation() -> None:
    if str(os.getenv("NOVA_RUNTIME_PROFILE") or "").strip().lower() == "trial":
        raise HTTPException(
            status_code=403,
            detail="Provider connection isn't available in this trial version.",
        )


def build_connections_router(
    *, network_mediator: NetworkMediator | None = None
) -> APIRouter:
    router = APIRouter()
    mediator = network_mediator or NetworkMediator()

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
        _reject_trial_provider_operation()
        if provider not in PROVIDER_REGISTRY:
            raise HTTPException(status_code=404, detail=f"Unknown provider: {provider}")

        key = str(payload.get("key") or "").strip()
        if not key:
            raise HTTPException(status_code=400, detail="key must be a non-empty string")

        # Persist key and update env var
        _saved, generation = connections_store.save_key_with_generation(provider, key)

        # Run health check
        ok, detail = await asyncio.to_thread(_health_check, provider, key, mediator)
        applied, snap = _record_health_outcome(
            provider,
            expected_generation=generation,
            ok=ok,
            detail=detail,
        )
        if not applied:
            ok = None
            detail = "Connection configuration changed before verification completed."

        return {"ok": ok, "detail": detail, "provider": snap}

    # ------------------------------------------------------------------
    # POST /api/settings/connections/{provider}/test
    # ------------------------------------------------------------------

    @router.post("/api/settings/connections/{provider}/test")
    async def test_existing_key(provider: str):
        """Re-run health check against the already-stored key."""
        _reject_trial_provider_operation()
        if provider not in PROVIDER_REGISTRY:
            raise HTTPException(status_code=404, detail=f"Unknown provider: {provider}")

        key, generation = connections_store.get_key_with_generation(provider)
        if not key:
            raise HTTPException(status_code=400, detail="No key stored for this provider")

        ok, detail = await asyncio.to_thread(_health_check, provider, key, mediator)
        applied, snap = _record_health_outcome(
            provider,
            expected_generation=generation,
            ok=ok,
            detail=detail,
        )
        if not applied:
            ok = None
            detail = "Connection configuration changed before verification completed."

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

def _record_health_outcome(
    provider_id: str,
    *,
    expected_generation: int,
    ok: bool | None,
    detail: str,
) -> tuple[bool, dict[str, Any]]:
    return connections_store.record_health_if_current(
        provider_id,
        expected_generation=expected_generation,
        ok=ok,
        detail=detail,
    )


def _health_check(
    provider_id: str, key: str, mediator: NetworkMediator
) -> tuple[bool | None, str]:
    """Run a lightweight connectivity check for the given provider.

    Returns (ok: bool, detail: str).  Never raises — all errors are caught
    and returned as (False, error_message).
    """
    try:
        checker = _HEALTH_CHECKERS.get(provider_id, _check_token)
        if provider_id in CONNECTION_HEALTH_OPERATIONS:
            return checker(key, mediator)
        return checker(key)
    except DisclosureDeniedError:
        return None, "Connection verification unavailable under the current Data-Out policy."
    except ProviderConnectionNetworkError as exc:
        if exc.status_code == 429 and provider_id in {"openai", "brave", "weather"}:
            return True, "Key valid but rate-limited (429). Treating as connected."
        if exc.status_code == 401:
            return False, "Invalid API key (401)."
        if exc.status_code == 426 and provider_id == "news":
            return False, "Plan upgrade required (426)."
        return False, f"Unexpected status {exc.status_code}."
    except NetworkMediatorError:
        return False, "Provider connection request failed."
    except Exception:
        return False, "Unexpected internal error."


def _governed_health_request(
    provider: str, key: str, mediator: NetworkMediator
) -> dict[str, Any]:
    operation = CONNECTION_HEALTH_OPERATIONS[provider]
    return mediator.connection_request(
        provider,
        "health",
        "GET",
        operation.url,
        params=operation.params(key),
        headers=operation.headers(key),
        as_json=False,
        timeout=8,
    )


def _check_openai(key: str, mediator: NetworkMediator) -> tuple[bool, str]:
    _governed_health_request("openai", key, mediator)
    return True, "Connected — models endpoint responded."


def _check_brave(key: str, mediator: NetworkMediator) -> tuple[bool, str]:
    _governed_health_request("brave", key, mediator)
    return True, "Connected — search endpoint responded."


def _check_news(key: str, mediator: NetworkMediator) -> tuple[bool, str]:
    _governed_health_request("news", key, mediator)
    return True, "Connected — headlines endpoint responded."


def _check_weather(key: str, mediator: NetworkMediator) -> tuple[bool, str]:
    _governed_health_request("weather", key, mediator)
    return True, "Connected — forecast endpoint responded."


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
