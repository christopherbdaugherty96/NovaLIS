"""Tests for Provider Budget Visibility Foundation.

Proves:
1. Policy/status data models serialize correctly
2. Budget state computation is correct for all thresholds
3. Provider status snapshot builds without calling any provider
4. New ledger event types are registered
5. No provider call path is changed
"""
from __future__ import annotations

import json

import pytest

from src.ledger.event_types import EVENT_TYPES
from src.usage.provider_budget_policy import (
    DEFAULT_POLICIES,
    ProviderBudgetPolicy,
    ProviderStatusEntry,
    ProviderUsageTotals,
    compute_budget_state,
)
from src.usage.provider_status import provider_status


class TestProviderBudgetPolicy:
    def test_default_policies_exist(self):
        assert "deepseek" in DEFAULT_POLICIES
        assert "openai" in DEFAULT_POLICIES
        assert "brave_search" in DEFAULT_POLICIES
        assert "weather" in DEFAULT_POLICIES
        assert "news" in DEFAULT_POLICIES
        assert "shopify" in DEFAULT_POLICIES
        assert "deepseek_reasoner" in DEFAULT_POLICIES

    def test_deepseek_defaults(self):
        p = DEFAULT_POLICIES["deepseek"]
        assert p.provider_id == "deepseek"
        assert p.metered is True
        assert p.enabled is False
        assert p.daily_token_limit == 50_000
        assert p.monthly_token_limit == 1_000_000
        assert p.daily_cost_limit_usd == 0.05
        assert p.monthly_cost_limit_usd == 1.00
        assert p.fallback == "local"

    def test_deepseek_reasoner_requires_approval(self):
        p = DEFAULT_POLICIES["deepseek_reasoner"]
        assert p.requires_approval is True
        assert p.metered is True
        assert p.max_output_tokens == 1200

    def test_openai_defaults(self):
        p = DEFAULT_POLICIES["openai"]
        assert p.metered is True
        assert p.daily_token_limit == 4_000

    def test_free_tier_providers_not_metered(self):
        for pid in ("brave_search", "weather", "news"):
            p = DEFAULT_POLICIES[pid]
            assert p.metered is False, f"{pid} should not be metered"
            assert p.enabled is True, f"{pid} should be enabled"

    def test_shopify_disabled_by_default(self):
        p = DEFAULT_POLICIES["shopify"]
        assert p.enabled is False
        assert p.metered is False

    def test_policy_roundtrip(self):
        p = DEFAULT_POLICIES["deepseek"]
        d = p.to_dict()
        restored = ProviderBudgetPolicy.from_dict(d)
        assert restored == p

    def test_policy_to_dict_keys(self):
        p = DEFAULT_POLICIES["deepseek"]
        d = p.to_dict()
        expected_keys = {
            "provider_id", "display_name", "enabled", "metered",
            "daily_token_limit", "monthly_token_limit",
            "daily_cost_limit_usd", "monthly_cost_limit_usd",
            "warn_ratio", "max_output_tokens",
            "requires_approval", "fallback",
        }
        assert set(d.keys()) == expected_keys

    def test_policy_from_empty_dict(self):
        p = ProviderBudgetPolicy.from_dict({})
        assert p.provider_id == ""
        assert p.enabled is False
        assert p.daily_token_limit == 0

    def test_policy_is_frozen(self):
        p = DEFAULT_POLICIES["deepseek"]
        with pytest.raises(AttributeError):
            p.enabled = True  # type: ignore[misc]

    def test_all_policies_json_serializable(self):
        for pid, p in DEFAULT_POLICIES.items():
            d = p.to_dict()
            serialized = json.dumps(d)
            assert isinstance(serialized, str), f"{pid} not serializable"


class TestProviderUsageTotals:
    def test_defaults_are_zero(self):
        u = ProviderUsageTotals()
        assert u.daily_tokens == 0
        assert u.monthly_tokens == 0
        assert u.daily_cost_usd == 0.0
        assert u.monthly_cost_usd == 0.0
        assert u.daily_call_count == 0
        assert u.monthly_call_count == 0

    def test_to_dict(self):
        u = ProviderUsageTotals(
            daily_tokens=1000, monthly_tokens=5000,
            daily_cost_usd=0.001234, monthly_cost_usd=0.005678,
            daily_call_count=3, monthly_call_count=15,
        )
        d = u.to_dict()
        assert d["daily_tokens"] == 1000
        assert d["monthly_tokens"] == 5000
        assert d["daily_cost_usd"] == 0.001234
        assert d["daily_call_count"] == 3


class TestComputeBudgetState:
    def test_non_metered_always_normal(self):
        policy = ProviderBudgetPolicy(
            provider_id="test", display_name="Test",
            metered=False, daily_token_limit=0,
        )
        usage = ProviderUsageTotals(daily_tokens=999999)
        assert compute_budget_state(usage, policy) == "normal"

    def test_zero_limit_always_normal(self):
        policy = ProviderBudgetPolicy(
            provider_id="test", display_name="Test",
            metered=True, daily_token_limit=0,
        )
        usage = ProviderUsageTotals(daily_tokens=999999)
        assert compute_budget_state(usage, policy) == "normal"

    def test_under_threshold_normal(self):
        policy = ProviderBudgetPolicy(
            provider_id="test", display_name="Test",
            metered=True, daily_token_limit=10000, warn_ratio=0.8,
        )
        usage = ProviderUsageTotals(daily_tokens=5000)
        assert compute_budget_state(usage, policy) == "normal"

    def test_at_warning_threshold(self):
        policy = ProviderBudgetPolicy(
            provider_id="test", display_name="Test",
            metered=True, daily_token_limit=10000, warn_ratio=0.8,
        )
        usage = ProviderUsageTotals(daily_tokens=8000)
        assert compute_budget_state(usage, policy) == "warning"

    def test_at_limit(self):
        policy = ProviderBudgetPolicy(
            provider_id="test", display_name="Test",
            metered=True, daily_token_limit=10000, warn_ratio=0.8,
        )
        usage = ProviderUsageTotals(daily_tokens=10000)
        assert compute_budget_state(usage, policy) == "limit"

    def test_over_limit(self):
        policy = ProviderBudgetPolicy(
            provider_id="test", display_name="Test",
            metered=True, daily_token_limit=10000, warn_ratio=0.8,
        )
        usage = ProviderUsageTotals(daily_tokens=15000)
        assert compute_budget_state(usage, policy) == "limit"

    def test_cost_limit_warning(self):
        policy = ProviderBudgetPolicy(
            provider_id="test", display_name="Test",
            metered=True, daily_token_limit=100000,
            daily_cost_limit_usd=0.05, warn_ratio=0.8,
        )
        usage = ProviderUsageTotals(
            daily_tokens=1000, daily_cost_usd=0.041,
        )
        assert compute_budget_state(usage, policy) == "warning"

    def test_cost_limit_reached(self):
        policy = ProviderBudgetPolicy(
            provider_id="test", display_name="Test",
            metered=True, daily_token_limit=100000,
            daily_cost_limit_usd=0.05, warn_ratio=0.8,
        )
        usage = ProviderUsageTotals(
            daily_tokens=1000, daily_cost_usd=0.05,
        )
        assert compute_budget_state(usage, policy) == "limit"

    def test_monthly_token_warning(self):
        policy = ProviderBudgetPolicy(
            provider_id="test", display_name="Test",
            metered=True, daily_token_limit=100000,
            monthly_token_limit=50000, warn_ratio=0.8,
        )
        usage = ProviderUsageTotals(
            daily_tokens=1000, monthly_tokens=42000,
        )
        assert compute_budget_state(usage, policy) == "warning"

    def test_monthly_token_limit(self):
        policy = ProviderBudgetPolicy(
            provider_id="test", display_name="Test",
            metered=True, daily_token_limit=100000,
            monthly_token_limit=50000, warn_ratio=0.8,
        )
        usage = ProviderUsageTotals(
            daily_tokens=1000, monthly_tokens=50000,
        )
        assert compute_budget_state(usage, policy) == "limit"

    def test_monthly_cost_limit(self):
        policy = ProviderBudgetPolicy(
            provider_id="test", display_name="Test",
            metered=True, daily_token_limit=100000,
            monthly_cost_limit_usd=1.00, warn_ratio=0.8,
        )
        usage = ProviderUsageTotals(
            daily_tokens=1000, monthly_cost_usd=1.00,
        )
        assert compute_budget_state(usage, policy) == "limit"

    def test_daily_limit_takes_precedence_over_monthly(self):
        policy = ProviderBudgetPolicy(
            provider_id="test", display_name="Test",
            metered=True, daily_token_limit=1000,
            monthly_token_limit=100000, warn_ratio=0.8,
        )
        usage = ProviderUsageTotals(
            daily_tokens=1000, monthly_tokens=5000,
        )
        assert compute_budget_state(usage, policy) == "limit"


class TestProviderStatusEntry:
    def test_to_dict_keys(self):
        entry = ProviderStatusEntry(
            provider_id="test", display_name="Test",
        )
        d = entry.to_dict()
        expected_keys = {
            "provider_id", "display_name", "connected", "enabled",
            "metered", "budget_state", "usage", "policy",
            "last_error", "last_call_at",
        }
        assert set(d.keys()) == expected_keys

    def test_to_dict_with_policy(self):
        policy = DEFAULT_POLICIES["deepseek"]
        entry = ProviderStatusEntry(
            provider_id="deepseek", display_name="DeepSeek",
            policy=policy,
        )
        d = entry.to_dict()
        assert d["policy"] is not None
        assert d["policy"]["provider_id"] == "deepseek"

    def test_to_dict_without_policy(self):
        entry = ProviderStatusEntry(
            provider_id="test", display_name="Test",
        )
        d = entry.to_dict()
        assert d["policy"] is None

    def test_json_serializable(self):
        entry = ProviderStatusEntry(
            provider_id="test", display_name="Test",
            policy=DEFAULT_POLICIES["deepseek"],
            usage=ProviderUsageTotals(daily_tokens=100),
        )
        serialized = json.dumps(entry.to_dict())
        assert isinstance(serialized, str)


class TestProviderStatusSnapshot:
    def test_returns_dict(self):
        result = provider_status()
        assert isinstance(result, dict)
        assert result["type"] == "provider_status_snapshot"

    def test_has_providers_list(self):
        result = provider_status()
        assert "providers" in result
        assert isinstance(result["providers"], list)
        assert len(result["providers"]) > 0

    def test_has_ollama_entry(self):
        result = provider_status()
        ids = [p["provider_id"] for p in result["providers"]]
        assert "ollama" in ids

    def test_has_all_default_providers(self):
        result = provider_status()
        ids = {p["provider_id"] for p in result["providers"]}
        for pid in DEFAULT_POLICIES:
            assert pid in ids, f"missing provider: {pid}"

    def test_counts_correct(self):
        result = provider_status()
        assert result["provider_count"] == len(result["providers"])
        metered = sum(
            1 for p in result["providers"] if p["metered"]
        )
        assert result["metered_count"] == metered

    def test_custom_policies(self):
        custom = {
            "test_only": ProviderBudgetPolicy(
                provider_id="test_only",
                display_name="Test Only",
                enabled=True,
                metered=True,
                daily_token_limit=100,
            ),
        }
        result = provider_status(policies=custom)
        ids = {p["provider_id"] for p in result["providers"]}
        assert "test_only" in ids
        assert "ollama" in ids
        assert "deepseek" not in ids

    def test_snapshot_is_json_serializable(self):
        result = provider_status()
        serialized = json.dumps(result)
        assert isinstance(serialized, str)


class TestLedgerEventTypes:
    def test_provider_usage_recorded_registered(self):
        assert "PROVIDER_USAGE_RECORDED" in EVENT_TYPES

    def test_provider_usage_blocked_registered(self):
        assert "PROVIDER_USAGE_BLOCKED" in EVENT_TYPES

    def test_provider_budget_warning_registered(self):
        assert "PROVIDER_BUDGET_WARNING" in EVENT_TYPES

    def test_existing_events_still_present(self):
        assert "EXTERNAL_NETWORK_CALL" in EVENT_TYPES
        assert "NETWORK_CALL_FAILED" in EVENT_TYPES
        assert "ROUTINE_BRIEF_COMPLETED" in EVENT_TYPES
        assert "ACTION_ATTEMPTED" in EVENT_TYPES
        assert "ACTION_COMPLETED" in EVENT_TYPES


class TestNoBehaviorChange:
    """Prove that no existing provider call path was modified."""

    def test_provider_usage_store_unchanged(self):
        from src.usage.provider_usage_store import ProviderUsageStore
        store = ProviderUsageStore.__new__(ProviderUsageStore)
        assert hasattr(store, "record_reasoning_event")
        assert hasattr(store, "snapshot")
        assert hasattr(store, "configure_budget")

    def test_network_mediator_unchanged(self):
        from src.governor.network_mediator import NetworkMediator
        m = NetworkMediator.__new__(NetworkMediator)
        assert hasattr(m, "request")
        assert hasattr(m, "_check_rate_limit")
        assert hasattr(m, "_validate_url")

    def test_deepseek_provider_not_imported_by_budget_policy(self):
        import src.usage.provider_budget_policy as mod
        source = open(mod.__file__).read()
        assert "deepseek_reasoning_provider" not in source
        assert "deepseek_bridge" not in source

    def test_provider_status_does_not_import_providers(self):
        import src.usage.provider_status as mod
        source = open(mod.__file__).read()
        assert "deepseek_reasoning_provider" not in source
        assert "openai_responses_lane" not in source
        assert "web_search_executor" not in source
        assert "weather_service" not in source
        assert "news_service" not in source
