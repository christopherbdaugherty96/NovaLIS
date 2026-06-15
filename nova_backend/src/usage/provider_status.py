"""Read-only provider status snapshot.

Returns current state of all known providers without modifying
any call paths or runtime behavior.
"""
from __future__ import annotations

import os
from typing import Any

from src.usage.provider_budget_policy import (
    DEFAULT_POLICIES,
    ProviderBudgetPolicy,
    ProviderStatusEntry,
    ProviderUsageTotals,
    compute_budget_state,
)


def _env_key_present(key: str) -> bool:
    return bool(os.environ.get(key, "").strip())


def _ollama_status() -> dict[str, Any]:
    """Check Ollama availability without importing heavy modules."""
    try:
        import urllib.request
        with urllib.request.urlopen(
            "http://localhost:11434/api/tags", timeout=2
        ) as resp:
            if resp.status == 200:
                return {"connected": True, "error": ""}
    except Exception as exc:
        return {"connected": False, "error": str(exc)[:120]}
    return {"connected": False, "error": "unexpected"}


def provider_status(
    *,
    policies: dict[str, ProviderBudgetPolicy] | None = None,
) -> dict[str, Any]:
    """Build a read-only snapshot of all provider states.

    Does NOT call any provider API. Only checks env vars and
    local state to determine connected/enabled status.
    """
    pol = policies or DEFAULT_POLICIES

    entries: list[dict[str, Any]] = []

    ollama = _ollama_status()
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

    for provider_id, policy in pol.items():
        env_key = provider_env_keys.get(provider_id, "")
        connected = _env_key_present(env_key) if env_key else False

        usage = ProviderUsageTotals()
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
