"""Read-only provider status snapshot.

Returns current state of all known providers and connectors
without modifying any call paths or runtime behavior.
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any

from src.usage.provider_budget_policy import (
    DEFAULT_POLICIES,
    ProviderBudgetPolicy,
    ProviderStatusEntry,
    ProviderUsageTotals,
    compute_budget_state,
)
from src.usage.provider_usage_store import provider_usage_store


def _metered_usage_snapshot() -> ProviderUsageTotals:
    """Read current daily usage from the provider usage store."""
    try:
        snap = provider_usage_store.snapshot()
        return ProviderUsageTotals(
            daily_tokens=int(
                snap.get("estimated_total_tokens") or 0
            ),
            daily_cost_usd=float(
                snap.get("estimated_cost_usd") or 0.0
            ),
            daily_call_count=int(
                snap.get("event_count") or 0
            ),
        )
    except Exception:
        return ProviderUsageTotals()


def _env_key_present(key: str) -> bool:
    return bool(os.environ.get(key, "").strip())


def _ollama_status(*, session_id: str = "") -> dict[str, Any]:
    """Check Ollama only through the verified local-model boundary."""
    try:
        from src.llm.local_ollama_bootstrap import verified_local_ollama_status
        from src.nova_config import OLLAMA_MODEL, OLLAMA_URL

        connected = verified_local_ollama_status(
            base_url=str(OLLAMA_URL or "http://localhost:11434").strip(),
            model=str(OLLAMA_MODEL or "gemma4:e4b").strip(),
            request_id=f"provider-status-{uuid.uuid4()}",
            session_id=session_id,
        )
        if connected:
            return {"connected": True, "error": ""}
        return {"connected": False, "error": "Local Ollama identity unavailable"}
    except Exception as exc:
        return {"connected": False, "error": str(exc)[:120]}


def _calendar_status() -> dict[str, Any]:
    """Check Calendar connector — env var and ICS file only."""
    ics_raw = (os.getenv("NOVA_CALENDAR_ICS_PATH") or "").strip()
    if not ics_raw:
        return {"connected": False, "note": "No ICS path configured"}
    ics_path = Path(ics_raw)
    if ics_path.is_file():
        return {"connected": True, "note": ics_path.name}
    return {"connected": False, "note": f"ICS not found: {ics_path.name}"}


def _email_status() -> dict[str, Any]:
    """Check Email connector config without importing connector."""
    has_config = any(
        _env_key_present(k)
        for k in ("NOVA_EMAIL_PROVIDER", "GMAIL_CREDENTIALS_PATH")
    )
    if has_config:
        return {"connected": True, "note": "Configured"}
    return {"connected": False, "note": "Not configured"}


def provider_status(
    *,
    policies: dict[str, ProviderBudgetPolicy] | None = None,
    session_id: str = "",
) -> dict[str, Any]:
    """Build a read-only snapshot of all provider states.

    The local Ollama availability check uses Nova's verified, evidenced
    loopback boundary. Other entries inspect configuration and local state.
    """
    pol = policies or DEFAULT_POLICIES

    entries: list[dict[str, Any]] = []

    ollama = _ollama_status(session_id=session_id)
    entries.append(
        ProviderStatusEntry(
            provider_id="ollama",
            display_name="Ollama (local model)",
            connected=ollama["connected"],
            enabled=True,
            metered=False,
            budget_state="normal",
            last_error=ollama.get("error", ""),
        ).to_dict()
    )

    provider_env_keys = {
        "deepseek": "DEEPSEEK_API_KEY",
        "deepseek_reasoner": "DEEPSEEK_API_KEY",
        "openai": "OPENAI_API_KEY",
        "brave_search": "BRAVE_API_KEY",
        "weather": "WEATHER_API_KEY",
        "news": "NEWS_API_KEY",
        "shopify": "NOVA_SHOPIFY_ACCESS_TOKEN",
    }

    usage_snapshot = _metered_usage_snapshot()

    for provider_id, policy in pol.items():
        env_key = provider_env_keys.get(provider_id, "")
        connected = _env_key_present(env_key) if env_key else False

        usage = usage_snapshot if policy.metered else ProviderUsageTotals()
        budget_state = compute_budget_state(usage, policy)

        entries.append(
            ProviderStatusEntry(
                provider_id=provider_id,
                display_name=policy.display_name,
                connected=connected,
                enabled=policy.enabled,
                metered=policy.metered,
                budget_state=budget_state,
                usage=usage,
                policy=policy,
            ).to_dict()
        )

    cal = _calendar_status()
    entries.append(
        ProviderStatusEntry(
            provider_id="calendar",
            display_name="Calendar (local ICS)",
            connected=cal["connected"],
            enabled=True,
            metered=False,
            budget_state="normal",
            last_error=cal.get("note", ""),
        ).to_dict()
    )

    email = _email_status()
    entries.append(
        ProviderStatusEntry(
            provider_id="email",
            display_name="Email",
            connected=email["connected"],
            enabled=True,
            metered=False,
            budget_state="normal",
            last_error=email.get("note", ""),
        ).to_dict()
    )

    return {
        "type": "provider_status_snapshot",
        "providers": entries,
        "provider_count": len(entries),
        "metered_count": sum(
            1 for e in entries if e.get("metered")
        ),
        "connected_count": sum(
            1 for e in entries if e.get("connected")
        ),
    }
