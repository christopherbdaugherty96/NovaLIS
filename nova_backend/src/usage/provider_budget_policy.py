"""Provider budget policy and status models.

Read-only vocabulary for unified metered-provider visibility.
No enforcement logic — that belongs in a future ProviderBudgetGuard.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProviderBudgetPolicy:
    """Per-provider budget configuration. Immutable after creation."""

    provider_id: str
    display_name: str
    enabled: bool = False
    metered: bool = False
    daily_token_limit: int = 0
    monthly_token_limit: int = 0
    daily_cost_limit_usd: float = 0.0
    monthly_cost_limit_usd: float = 0.0
    warn_ratio: float = 0.8
    max_output_tokens: int = 500
    requires_approval: bool = False
    fallback: str = "local"

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "display_name": self.display_name,
            "enabled": self.enabled,
            "metered": self.metered,
            "daily_token_limit": self.daily_token_limit,
            "monthly_token_limit": self.monthly_token_limit,
            "daily_cost_limit_usd": self.daily_cost_limit_usd,
            "monthly_cost_limit_usd": self.monthly_cost_limit_usd,
            "warn_ratio": self.warn_ratio,
            "max_output_tokens": self.max_output_tokens,
            "requires_approval": self.requires_approval,
            "fallback": self.fallback,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProviderBudgetPolicy:
        def _int(key: str, default: int) -> int:
            v = data.get(key)
            return int(v) if v is not None else default

        def _float(key: str, default: float) -> float:
            v = data.get(key)
            return float(v) if v is not None else default

        def _str(key: str, default: str) -> str:
            v = data.get(key)
            return str(v) if v is not None else default

        return cls(
            provider_id=_str("provider_id", ""),
            display_name=_str("display_name", ""),
            enabled=bool(data.get("enabled")),
            metered=bool(data.get("metered")),
            daily_token_limit=_int("daily_token_limit", 0),
            monthly_token_limit=_int("monthly_token_limit", 0),
            daily_cost_limit_usd=_float("daily_cost_limit_usd", 0.0),
            monthly_cost_limit_usd=_float(
                "monthly_cost_limit_usd", 0.0
            ),
            warn_ratio=_float("warn_ratio", 0.8),
            max_output_tokens=_int("max_output_tokens", 500),
            requires_approval=bool(data.get("requires_approval")),
            fallback=_str("fallback", "local"),
        )


@dataclass
class ProviderUsageTotals:
    """Running usage totals for a single provider."""

    daily_tokens: int = 0
    monthly_tokens: int = 0
    daily_cost_usd: float = 0.0
    monthly_cost_usd: float = 0.0
    daily_call_count: int = 0
    monthly_call_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "daily_tokens": self.daily_tokens,
            "monthly_tokens": self.monthly_tokens,
            "daily_cost_usd": round(self.daily_cost_usd, 6),
            "monthly_cost_usd": round(self.monthly_cost_usd, 6),
            "daily_call_count": self.daily_call_count,
            "monthly_call_count": self.monthly_call_count,
        }


@dataclass
class ProviderStatusEntry:
    """Read-only status for a single provider."""

    provider_id: str
    display_name: str
    connected: bool = False
    enabled: bool = False
    metered: bool = False
    budget_state: str = "normal"
    usage: ProviderUsageTotals = field(
        default_factory=ProviderUsageTotals
    )
    policy: ProviderBudgetPolicy | None = None
    last_error: str = ""
    last_call_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "display_name": self.display_name,
            "connected": self.connected,
            "enabled": self.enabled,
            "metered": self.metered,
            "budget_state": self.budget_state,
            "usage": self.usage.to_dict(),
            "policy": self.policy.to_dict() if self.policy else None,
            "last_error": self.last_error,
            "last_call_at": self.last_call_at,
        }


DEFAULT_POLICIES: dict[str, ProviderBudgetPolicy] = {
    "deepseek": ProviderBudgetPolicy(
        provider_id="deepseek",
        display_name="DeepSeek",
        enabled=False,
        metered=True,
        daily_token_limit=50_000,
        monthly_token_limit=1_000_000,
        daily_cost_limit_usd=0.05,
        monthly_cost_limit_usd=1.00,
        warn_ratio=0.8,
        max_output_tokens=500,
        requires_approval=False,
        fallback="local",
    ),
    "deepseek_reasoner": ProviderBudgetPolicy(
        provider_id="deepseek_reasoner",
        display_name="DeepSeek Reasoner",
        enabled=False,
        metered=True,
        daily_token_limit=25_000,
        monthly_token_limit=500_000,
        daily_cost_limit_usd=0.10,
        monthly_cost_limit_usd=2.00,
        warn_ratio=0.8,
        max_output_tokens=1200,
        requires_approval=True,
        fallback="local",
    ),
    "openai": ProviderBudgetPolicy(
        provider_id="openai",
        display_name="OpenAI",
        enabled=False,
        metered=True,
        daily_token_limit=4_000,
        monthly_token_limit=100_000,
        daily_cost_limit_usd=0.05,
        monthly_cost_limit_usd=1.00,
        warn_ratio=0.8,
        max_output_tokens=500,
        requires_approval=False,
        fallback="local",
    ),
    "brave_search": ProviderBudgetPolicy(
        provider_id="brave_search",
        display_name="Brave Search",
        enabled=True,
        metered=False,
        daily_token_limit=0,
        monthly_token_limit=0,
        fallback="unavailable",
    ),
    "weather": ProviderBudgetPolicy(
        provider_id="weather",
        display_name="Weather (Visual Crossing)",
        enabled=True,
        metered=False,
        daily_token_limit=0,
        monthly_token_limit=0,
        fallback="unavailable",
    ),
    "news": ProviderBudgetPolicy(
        provider_id="news",
        display_name="News (RSS + NewsAPI)",
        enabled=True,
        metered=False,
        daily_token_limit=0,
        monthly_token_limit=0,
        fallback="unavailable",
    ),
    "shopify": ProviderBudgetPolicy(
        provider_id="shopify",
        display_name="Shopify (read-only)",
        enabled=False,
        metered=False,
        daily_token_limit=0,
        monthly_token_limit=0,
        fallback="unavailable",
    ),
}


def compute_budget_state(
    usage: ProviderUsageTotals,
    policy: ProviderBudgetPolicy,
) -> str:
    """Determine budget state from usage and policy. Pure function."""
    if not policy.metered:
        return "normal"

    worst = "normal"

    if policy.daily_token_limit > 0:
        daily_ratio = usage.daily_tokens / policy.daily_token_limit
        if daily_ratio >= 1.0:
            return "limit"
        if daily_ratio >= policy.warn_ratio:
            worst = "warning"

    if policy.daily_cost_limit_usd > 0:
        cost_ratio = usage.daily_cost_usd / policy.daily_cost_limit_usd
        if cost_ratio >= 1.0:
            return "limit"
        if cost_ratio >= policy.warn_ratio:
            worst = "warning"

    if policy.monthly_token_limit > 0:
        monthly_ratio = (
            usage.monthly_tokens / policy.monthly_token_limit
        )
        if monthly_ratio >= 1.0:
            return "limit"
        if monthly_ratio >= policy.warn_ratio:
            worst = "warning"

    if policy.monthly_cost_limit_usd > 0:
        monthly_cost_ratio = (
            usage.monthly_cost_usd / policy.monthly_cost_limit_usd
        )
        if monthly_cost_ratio >= 1.0:
            return "limit"
        if monthly_cost_ratio >= policy.warn_ratio:
            worst = "warning"

    return worst
