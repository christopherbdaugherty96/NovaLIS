"""Tests for PR #247 — DeepSeek Log-Only Budget Check.

Proves:
1. from_dict preserves valid falsy values (0, 0.0, "")
2. compute_budget_state supports monthly-only metered policies
3. _log_budget_event computes policy-based state and logs events
4. DeepSeek calls proceed even at warning/limit (no blocking)
5. Ledger events are emitted with purpose tags
6. Existing usage recording still works
7. Morning Brief remains unaffected
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from src.usage.provider_budget_policy import (
    DEFAULT_POLICIES,
    ProviderBudgetPolicy,
    ProviderUsageTotals,
    compute_budget_state,
)
from src.usage.provider_usage_store import provider_usage_store


# ── Fix 1: from_dict falsy-value handling ─────────────────────

class TestFromDictFalsyValues:
    def test_warn_ratio_zero_preserved(self):
        d = DEFAULT_POLICIES["deepseek"].to_dict()
        d["warn_ratio"] = 0.0
        p = ProviderBudgetPolicy.from_dict(d)
        assert p.warn_ratio == 0.0

    def test_max_output_tokens_zero_preserved(self):
        d = DEFAULT_POLICIES["deepseek"].to_dict()
        d["max_output_tokens"] = 0
        p = ProviderBudgetPolicy.from_dict(d)
        assert p.max_output_tokens == 0

    def test_daily_token_limit_zero_preserved(self):
        d = DEFAULT_POLICIES["deepseek"].to_dict()
        d["daily_token_limit"] = 0
        p = ProviderBudgetPolicy.from_dict(d)
        assert p.daily_token_limit == 0

    def test_fallback_empty_string_preserved(self):
        d = DEFAULT_POLICIES["deepseek"].to_dict()
        d["fallback"] = ""
        p = ProviderBudgetPolicy.from_dict(d)
        assert p.fallback == ""

    def test_cost_limit_zero_preserved(self):
        d = DEFAULT_POLICIES["deepseek"].to_dict()
        d["daily_cost_limit_usd"] = 0.0
        d["monthly_cost_limit_usd"] = 0.0
        p = ProviderBudgetPolicy.from_dict(d)
        assert p.daily_cost_limit_usd == 0.0
        assert p.monthly_cost_limit_usd == 0.0

    def test_missing_keys_use_defaults(self):
        p = ProviderBudgetPolicy.from_dict({})
        assert p.warn_ratio == 0.8
        assert p.max_output_tokens == 500
        assert p.fallback == "local"

    def test_none_values_use_defaults(self):
        p = ProviderBudgetPolicy.from_dict({
            "warn_ratio": None,
            "max_output_tokens": None,
            "fallback": None,
        })
        assert p.warn_ratio == 0.8
        assert p.max_output_tokens == 500
        assert p.fallback == "local"

    def test_roundtrip_with_zero_values(self):
        original = ProviderBudgetPolicy(
            provider_id="test",
            display_name="Test",
            warn_ratio=0.0,
            max_output_tokens=0,
            daily_token_limit=0,
            fallback="",
        )
        restored = ProviderBudgetPolicy.from_dict(original.to_dict())
        assert restored == original


# ── Fix 2: monthly-only metered policy support ────────────────

class TestMonthlyOnlyPolicy:
    def test_monthly_only_warning(self):
        policy = ProviderBudgetPolicy(
            provider_id="test",
            display_name="Test",
            metered=True,
            daily_token_limit=0,
            monthly_token_limit=10000,
            warn_ratio=0.8,
        )
        usage = ProviderUsageTotals(monthly_tokens=8500)
        assert compute_budget_state(usage, policy) == "warning"

    def test_monthly_only_limit(self):
        policy = ProviderBudgetPolicy(
            provider_id="test",
            display_name="Test",
            metered=True,
            daily_token_limit=0,
            monthly_token_limit=10000,
            warn_ratio=0.8,
        )
        usage = ProviderUsageTotals(monthly_tokens=10000)
        assert compute_budget_state(usage, policy) == "limit"

    def test_monthly_only_normal(self):
        policy = ProviderBudgetPolicy(
            provider_id="test",
            display_name="Test",
            metered=True,
            daily_token_limit=0,
            monthly_token_limit=10000,
            warn_ratio=0.8,
        )
        usage = ProviderUsageTotals(monthly_tokens=5000)
        assert compute_budget_state(usage, policy) == "normal"

    def test_monthly_cost_only_limit(self):
        policy = ProviderBudgetPolicy(
            provider_id="test",
            display_name="Test",
            metered=True,
            daily_token_limit=0,
            monthly_cost_limit_usd=1.00,
            warn_ratio=0.8,
        )
        usage = ProviderUsageTotals(monthly_cost_usd=1.00)
        assert compute_budget_state(usage, policy) == "limit"

    def test_no_limits_at_all_is_normal(self):
        policy = ProviderBudgetPolicy(
            provider_id="test",
            display_name="Test",
            metered=True,
            daily_token_limit=0,
            monthly_token_limit=0,
        )
        usage = ProviderUsageTotals(
            daily_tokens=999999, monthly_tokens=999999,
        )
        assert compute_budget_state(usage, policy) == "normal"

    def test_existing_daily_tests_still_pass(self):
        """Confirm the fix didn't break daily-limit behavior."""
        policy = ProviderBudgetPolicy(
            provider_id="test",
            display_name="Test",
            metered=True,
            daily_token_limit=10000,
            warn_ratio=0.8,
        )
        assert compute_budget_state(
            ProviderUsageTotals(daily_tokens=5000), policy,
        ) == "normal"
        assert compute_budget_state(
            ProviderUsageTotals(daily_tokens=8000), policy,
        ) == "warning"
        assert compute_budget_state(
            ProviderUsageTotals(daily_tokens=10000), policy,
        ) == "limit"


# ── DeepSeek log-only budget event ────────────────────────────

class TestLogBudgetEvent:
    def test_returns_budget_state_normal(self):
        from src.providers.deepseek_reasoning_provider import (
            _log_budget_event,
        )
        with patch(
            "src.ledger.writer.LedgerWriter",
        ) as MockWriter:
            mock_ledger = MagicMock()
            MockWriter.return_value = mock_ledger

            state = _log_budget_event(
                usage_snapshot={
                    "estimated_total_tokens": 1000,
                    "estimated_cost_usd": 0.001,
                    "event_count": 1,
                },
                analysis_profile="task_scoped",
                request_id="test-123",
                model="deepseek-v4-flash",
            )
            assert state == "normal"
            mock_ledger.log_event.assert_called_once_with(
                "PROVIDER_USAGE_RECORDED",
                pytest.approx(
                    {
                        "provider_id": "deepseek",
                        "model": "deepseek-v4-flash",
                        "analysis_profile": "task_scoped",
                        "request_id": "test-123",
                        "daily_tokens": 1000,
                        "daily_cost_usd": 0.001,
                        "daily_call_count": 1,
                        "budget_state": "normal",
                        "policy_daily_token_limit": 50000,
                        "policy_daily_cost_limit_usd": 0.05,
                        "enforcement": "log_only",
                    },
                    abs=1e-6,
                ),
            )

    def test_returns_warning_and_logs_two_events(self):
        from src.providers.deepseek_reasoning_provider import (
            _log_budget_event,
        )
        with patch(
            "src.ledger.writer.LedgerWriter",
        ) as MockWriter:
            mock_ledger = MagicMock()
            MockWriter.return_value = mock_ledger

            state = _log_budget_event(
                usage_snapshot={
                    "estimated_total_tokens": 42000,
                    "estimated_cost_usd": 0.0,
                    "event_count": 5,
                },
                analysis_profile="deep_reason",
                request_id="test-456",
                model="deepseek-v4-pro",
            )
            assert state == "warning"
            assert mock_ledger.log_event.call_count == 2
            calls = mock_ledger.log_event.call_args_list
            assert calls[0][0][0] == "PROVIDER_USAGE_RECORDED"
            assert calls[1][0][0] == "PROVIDER_BUDGET_WARNING"

    def test_returns_limit_and_logs_would_block(self):
        from src.providers.deepseek_reasoning_provider import (
            _log_budget_event,
        )
        with patch(
            "src.ledger.writer.LedgerWriter",
        ) as MockWriter:
            mock_ledger = MagicMock()
            MockWriter.return_value = mock_ledger

            state = _log_budget_event(
                usage_snapshot={
                    "estimated_total_tokens": 55000,
                    "estimated_cost_usd": 0.0,
                    "event_count": 10,
                },
                analysis_profile="task_scoped",
                request_id="test-789",
                model="deepseek-v4-flash",
            )
            assert state == "limit"
            assert mock_ledger.log_event.call_count == 2
            calls = mock_ledger.log_event.call_args_list
            assert calls[0][0][0] == "PROVIDER_USAGE_RECORDED"
            assert calls[1][0][0] == "PROVIDER_BUDGET_WARNING"
            warning_meta = calls[1][0][1]
            assert warning_meta["would_block"] is True
            assert warning_meta["enforcement"] == "log_only"

    def test_includes_purpose_tag(self):
        from src.providers.deepseek_reasoning_provider import (
            _log_budget_event,
        )
        with patch(
            "src.ledger.writer.LedgerWriter",
        ) as MockWriter:
            mock_ledger = MagicMock()
            MockWriter.return_value = mock_ledger

            _log_budget_event(
                usage_snapshot={
                    "estimated_total_tokens": 100,
                    "event_count": 1,
                },
                analysis_profile="deep_reason",
                request_id="test-purpose",
                model="deepseek-v4-flash",
            )
            meta = mock_ledger.log_event.call_args_list[0][0][1]
            assert meta["analysis_profile"] == "deep_reason"
            assert meta["request_id"] == "test-purpose"

    def test_ledger_failure_does_not_raise(self):
        from src.providers.deepseek_reasoning_provider import (
            _log_budget_event,
        )
        with patch(
            "src.ledger.writer.LedgerWriter",
            side_effect=RuntimeError("ledger broken"),
        ):
            state = _log_budget_event(
                usage_snapshot={"estimated_total_tokens": 100},
                analysis_profile="analysis",
                request_id="test",
                model="deepseek-v4-flash",
            )
            assert state == "normal"

    def test_missing_policy_returns_normal(self):
        from src.providers.deepseek_reasoning_provider import (
            _log_budget_event,
        )
        with patch(
            "src.usage.provider_budget_policy."
            "DEFAULT_POLICIES",
            {},
        ):
            state = _log_budget_event(
                usage_snapshot={"estimated_total_tokens": 999999},
                analysis_profile="analysis",
                request_id="test",
                model="deepseek-v4-flash",
            )
            assert state == "normal"


# ── Proof: DeepSeek never blocked ─────────────────────────────

class TestDeepSeekNeverBlocked:
    """Prove that _log_budget_event is log-only — no blocking,
    no exception, no early return, regardless of budget state."""

    def test_normal_state_returns_string(self):
        from src.providers.deepseek_reasoning_provider import (
            _log_budget_event,
        )
        with patch(
            "src.ledger.writer.LedgerWriter",
        ):
            result = _log_budget_event(
                usage_snapshot={"estimated_total_tokens": 0},
                analysis_profile="analysis",
                request_id="test",
                model="deepseek-v4-flash",
            )
            assert isinstance(result, str)

    def test_warning_state_returns_string(self):
        from src.providers.deepseek_reasoning_provider import (
            _log_budget_event,
        )
        with patch(
            "src.ledger.writer.LedgerWriter",
        ):
            result = _log_budget_event(
                usage_snapshot={"estimated_total_tokens": 42000},
                analysis_profile="analysis",
                request_id="test",
                model="deepseek-v4-flash",
            )
            assert isinstance(result, str)
            assert result == "warning"

    def test_limit_state_returns_string_not_exception(self):
        from src.providers.deepseek_reasoning_provider import (
            _log_budget_event,
        )
        with patch(
            "src.ledger.writer.LedgerWriter",
        ):
            result = _log_budget_event(
                usage_snapshot={"estimated_total_tokens": 999999},
                analysis_profile="analysis",
                request_id="test",
                model="deepseek-v4-flash",
            )
            assert isinstance(result, str)
            assert result == "limit"

    def test_analyze_method_does_not_raise_on_budget_limit(self):
        """The full analyze() call path must not block even when
        the policy budget state is 'limit'."""
        from src.providers.deepseek_reasoning_provider import (
            DeepSeekReasoningProvider,
        )

        fake_response = {
            "data": {
                "choices": [
                    {"message": {"content": "Test advisory response"}}
                ],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "total_tokens": 150,
                },
            }
        }

        mock_network = MagicMock()
        mock_network.request.return_value = fake_response

        provider = DeepSeekReasoningProvider(network=mock_network)

        with (
            patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"}),
            patch.object(
                provider_usage_store,
                "record_reasoning_event",
                return_value={
                    "estimated_total_tokens": 999999,
                    "estimated_cost_usd": 99.0,
                    "event_count": 500,
                    "budget_state": "limit",
                    "budget_state_label": "Budget reached",
                },
            ),
            patch(
                "src.ledger.writer.LedgerWriter",
            ),
        ):
            result = provider.analyze(
                prompt="Test prompt",
                analysis_profile="task_scoped",
                request_id="no-block-test",
            )
            assert result.text == "Test advisory response"
            assert result.usage_meta["policy_budget_state"] == "limit"
            assert result.usage_meta["analysis_profile"] == "task_scoped"

    def test_analyze_source_has_no_raise_on_budget(self):
        """Static proof: _log_budget_event never raises or returns
        a refusal — it only returns a string."""
        import inspect
        from src.providers.deepseek_reasoning_provider import (
            _log_budget_event,
        )
        source = inspect.getsource(_log_budget_event)
        assert "raise" not in source.lower().split("exc_info")[0]
        assert "refusal" not in source.lower()
        assert "block(" not in source.lower()


# ── Existing usage recording still works ──────────────────────

class TestExistingUsageRecordingUnchanged:
    def test_provider_usage_store_api_intact(self):
        from src.usage.provider_usage_store import ProviderUsageStore
        store = ProviderUsageStore.__new__(ProviderUsageStore)
        assert hasattr(store, "record_reasoning_event")
        assert hasattr(store, "snapshot")
        assert hasattr(store, "configure_budget")
        assert hasattr(store, "_build_snapshot")

    def test_usage_store_not_modified_by_this_pr(self):
        """ProviderUsageStore source must not reference
        provider_budget_policy — that wiring is for #248."""
        import importlib
        mod = importlib.import_module("src.usage.provider_usage_store")
        source = open(mod.__loader__.get_filename()).read()
        assert "provider_budget_policy" not in source
        assert "compute_budget_state" not in source
        assert "ProviderBudgetPolicy" not in source


# ── Morning Brief unaffected ──────────────────────────────────

class TestMorningBriefStillUnaffected:
    def test_morning_brief_handler_no_budget_refs(self):
        import src.conversation.morning_brief_handler as mod
        source = open(mod.__file__).read()
        assert "_log_budget_event" not in source
        assert "PROVIDER_USAGE_RECORDED" not in source

    def test_daily_brief_no_budget_refs(self):
        import src.brief.daily_brief as mod
        source = open(mod.__file__).read()
        assert "_log_budget_event" not in source
        assert "PROVIDER_USAGE_RECORDED" not in source

    def test_routine_graph_no_budget_refs(self):
        import src.routine.routine_graph as mod
        source = open(mod.__file__).read()
        assert "_log_budget_event" not in source
        assert "PROVIDER_USAGE_RECORDED" not in source


# ── No other providers changed ────────────────────────────────

class TestNoOtherProviderChanges:
    def test_network_mediator_unchanged(self):
        import src.governor.network_mediator as mod
        source = open(mod.__file__).read()
        assert "_log_budget_event" not in source
        assert "PROVIDER_USAGE_RECORDED" not in source

    def test_governor_budget_check_unchanged(self):
        """The existing _check_network_budget in governor.py must
        not reference the new policy-based budget logic."""
        import src.governor.governor as mod
        source = open(mod.__file__).read()
        assert "compute_budget_state" not in source
        assert "ProviderBudgetPolicy" not in source
        assert "_log_budget_event" not in source


# ── Ledger event types still registered ───────────────────────

class TestLedgerEventsRegistered:
    def test_usage_recorded_exists(self):
        from src.ledger.event_types import EVENT_TYPES
        assert "PROVIDER_USAGE_RECORDED" in EVENT_TYPES

    def test_budget_warning_exists(self):
        from src.ledger.event_types import EVENT_TYPES
        assert "PROVIDER_BUDGET_WARNING" in EVENT_TYPES

    def test_usage_blocked_exists_for_future(self):
        from src.ledger.event_types import EVENT_TYPES
        assert "PROVIDER_USAGE_BLOCKED" in EVENT_TYPES
