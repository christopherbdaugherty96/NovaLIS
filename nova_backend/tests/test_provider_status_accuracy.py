"""Tests for PR #249 -- Provider Budget Status Accuracy.

Proves:
1. provider_status() reads real usage from provider_usage_store
2. Provider status shows warning/limit budget states accurately
3. DeepSeek bridge falls through to local fallback on budget block
4. Blocked text does not promise fallback it cannot deliver
5. Normal/warning DeepSeek behavior unchanged through bridge
6. Boundary files untouched
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.usage.provider_usage_store import provider_usage_store

# -- Provider status uses real usage totals --

class TestProviderStatusAccuracy:
    def test_status_reads_real_usage(self):
        from src.usage.provider_status import provider_status

        with patch.object(
            provider_usage_store,
            "snapshot",
            return_value={
                "estimated_total_tokens": 42000,
                "estimated_cost_usd": 0.04,
                "event_count": 5,
            },
        ):
            snap = provider_status()
            ds = next(
                p for p in snap["providers"]
                if p["provider_id"] == "deepseek"
            )
            assert ds["budget_state"] == "warning"

    def test_status_shows_limit(self):
        from src.usage.provider_status import provider_status

        with patch.object(
            provider_usage_store,
            "snapshot",
            return_value={
                "estimated_total_tokens": 55000,
                "estimated_cost_usd": 0.06,
                "event_count": 10,
            },
        ):
            snap = provider_status()
            ds = next(
                p for p in snap["providers"]
                if p["provider_id"] == "deepseek"
            )
            assert ds["budget_state"] == "limit"

    def test_status_shows_normal_when_low_usage(self):
        from src.usage.provider_status import provider_status

        with patch.object(
            provider_usage_store,
            "snapshot",
            return_value={
                "estimated_total_tokens": 1000,
                "estimated_cost_usd": 0.001,
                "event_count": 1,
            },
        ):
            snap = provider_status()
            ds = next(
                p for p in snap["providers"]
                if p["provider_id"] == "deepseek"
            )
            assert ds["budget_state"] == "normal"

    def test_non_metered_always_normal(self):
        from src.usage.provider_status import provider_status

        with patch.object(
            provider_usage_store,
            "snapshot",
            return_value={
                "estimated_total_tokens": 55000,
                "estimated_cost_usd": 0.06,
                "event_count": 10,
            },
        ):
            snap = provider_status()
            brave = next(
                p for p in snap["providers"]
                if p["provider_id"] == "brave_search"
            )
            assert brave["budget_state"] == "normal"
            assert brave["metered"] is False

    def test_snapshot_failure_returns_normal(self):
        from src.usage.provider_status import provider_status

        with patch.object(
            provider_usage_store,
            "snapshot",
            side_effect=RuntimeError("store broken"),
        ):
            snap = provider_status()
            ds = next(
                p for p in snap["providers"]
                if p["provider_id"] == "deepseek"
            )
            assert ds["budget_state"] == "normal"


# -- Provider status rendering --

class TestProviderStatusRendering:
    def test_warning_renders_budget_label(self):
        from src.brain_server import (
            _render_provider_status_message,
        )
        from src.usage.provider_status import provider_status

        with patch.object(
            provider_usage_store,
            "snapshot",
            return_value={
                "estimated_total_tokens": 42000,
                "estimated_cost_usd": 0.04,
                "event_count": 5,
            },
        ):
            snap = provider_status()
            msg, _ = _render_provider_status_message(snap)
            assert "budget warning" in msg.lower()

    def test_limit_renders_budget_label(self):
        from src.brain_server import (
            _render_provider_status_message,
        )
        from src.usage.provider_status import provider_status

        with patch.object(
            provider_usage_store,
            "snapshot",
            return_value={
                "estimated_total_tokens": 55000,
                "estimated_cost_usd": 0.06,
                "event_count": 10,
            },
        ):
            snap = provider_status()
            msg, _ = _render_provider_status_message(snap)
            assert "budget limit" in msg.lower()

    def test_normal_does_not_render_budget_label(self):
        from src.brain_server import (
            _render_provider_status_message,
        )
        from src.usage.provider_status import provider_status

        with patch.object(
            provider_usage_store,
            "snapshot",
            return_value={
                "estimated_total_tokens": 1000,
                "estimated_cost_usd": 0.001,
                "event_count": 1,
            },
        ):
            snap = provider_status()
            msg, _ = _render_provider_status_message(snap)
            assert "budget" not in msg.lower()


# -- DeepSeek bridge blocked fallback --

class TestBridgeBlockedFallback:
    def _make_bridge(self, mock_network):
        from src.conversation.deepseek_bridge import DeepSeekBridge
        from src.providers.deepseek_reasoning_provider import (
            DeepSeekReasoningProvider,
        )

        bridge = DeepSeekBridge.__new__(DeepSeekBridge)
        bridge._provider = DeepSeekReasoningProvider(
            network=mock_network,
        )
        bridge._cognitive_log = MagicMock()
        bridge._cognitive_log.started.return_value = MagicMock()
        bridge._registry = MagicMock()
        bridge._registry.is_enabled.return_value = True
        return bridge

    def test_blocked_falls_through_to_local(self):
        """When DeepSeek is budget-blocked and local fallback
        is enabled, the bridge must call llm_gateway."""
        mock_net = MagicMock()
        bridge = self._make_bridge(mock_net)

        with (
            patch.dict("os.environ", {
                "DEEPSEEK_API_KEY": "test-key",
                "NOVA_ALLOW_LOCAL_REASONING_FALLBACK": "true",
            }),
            patch.object(
                provider_usage_store,
                "snapshot",
                return_value={
                    "estimated_total_tokens": 55000,
                    "estimated_cost_usd": 0.06,
                    "event_count": 10,
                },
            ),
            patch(
                "src.ledger.writer.LedgerWriter",
            ),
            patch(
                "src.conversation.deepseek_bridge.llm_gateway"
            ) as mock_gw,
            patch.object(
                provider_usage_store,
                "record_reasoning_event",
                return_value={},
            ),
        ):
            mock_gw.generate_chat.return_value = (
                "Local fallback analysis result"
            )
            result = bridge.analyze(
                "What should I prioritize?",
                [],
                analysis_profile="task_scoped",
            )
            mock_net.request.assert_not_called()
            mock_gw.generate_chat.assert_called_once()
            assert result == "Local fallback analysis result"

    def test_blocked_without_fallback_returns_clear_message(self):
        """When local fallback is disabled, blocked DeepSeek
        returns a clear denial without promising fallback."""
        mock_net = MagicMock()
        bridge = self._make_bridge(mock_net)

        with (
            patch.dict("os.environ", {
                "DEEPSEEK_API_KEY": "test-key",
                "NOVA_ALLOW_LOCAL_REASONING_FALLBACK": "",
            }),
            patch.object(
                provider_usage_store,
                "snapshot",
                return_value={
                    "estimated_total_tokens": 55000,
                    "estimated_cost_usd": 0.06,
                    "event_count": 10,
                },
            ),
            patch("src.ledger.writer.LedgerWriter"),
        ):
            result = bridge.analyze(
                "Test blocked no fallback",
                [],
                analysis_profile="task_scoped",
            )
            mock_net.request.assert_not_called()
            assert "budget limit" in result.lower()
            assert "fallback" not in result.lower()

    def test_blocked_text_no_false_promise(self):
        """The provider-level blocked text must not promise
        a local fallback that the provider cannot deliver."""
        from src.providers.deepseek_reasoning_provider import (
            DeepSeekReasoningProvider,
        )

        mock_net = MagicMock()
        provider = DeepSeekReasoningProvider(network=mock_net)

        with (
            patch.dict(
                "os.environ", {"DEEPSEEK_API_KEY": "test-key"},
            ),
            patch.object(
                provider_usage_store,
                "snapshot",
                return_value={
                    "estimated_total_tokens": 55000,
                    "estimated_cost_usd": 0.06,
                    "event_count": 10,
                },
            ),
            patch("src.ledger.writer.LedgerWriter"),
        ):
            result = provider.analyze(
                prompt="Test",
                analysis_profile="task_scoped",
                request_id="text-test",
            )
            assert "fallback" not in result.text.lower()
            assert "—" not in result.text

    def test_normal_proceeds_through_bridge(self):
        """Normal budget state: bridge returns real DeepSeek
        analysis, not fallback."""
        mock_net = MagicMock()
        mock_net.request.return_value = {
            "data": {
                "choices": [
                    {"message": {"content": "Real analysis"}}
                ],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "total_tokens": 150,
                },
            }
        }
        bridge = self._make_bridge(mock_net)

        with (
            patch.dict("os.environ", {
                "DEEPSEEK_API_KEY": "test-key",
            }),
            patch.object(
                provider_usage_store,
                "snapshot",
                return_value={
                    "estimated_total_tokens": 1000,
                    "estimated_cost_usd": 0.001,
                    "event_count": 1,
                },
            ),
            patch.object(
                provider_usage_store,
                "record_reasoning_event",
                return_value={
                    "estimated_total_tokens": 1150,
                    "estimated_cost_usd": 0.002,
                    "event_count": 2,
                    "budget_state": "normal",
                    "budget_state_label": "Normal",
                },
            ),
            patch("src.ledger.writer.LedgerWriter"),
        ):
            result = bridge.analyze(
                "Test normal",
                [],
                analysis_profile="task_scoped",
            )
            mock_net.request.assert_called_once()
            assert result == "Real analysis"


# -- Boundary files untouched --

class TestBoundaryFilesStillUntouched:
    def test_morning_brief_no_status_refs(self):
        import src.conversation.morning_brief_handler as mod
        source = open(mod.__file__).read()
        assert "_metered_usage_snapshot" not in source
        assert "budget_blocked" not in source

    def test_daily_brief_no_status_refs(self):
        import src.brief.daily_brief as mod
        source = open(mod.__file__).read()
        assert "_metered_usage_snapshot" not in source
        assert "budget_blocked" not in source

    def test_network_mediator_unchanged(self):
        import src.governor.network_mediator as mod
        source = open(mod.__file__).read()
        assert "_metered_usage_snapshot" not in source

    def test_governor_unchanged(self):
        import src.governor.governor as mod
        source = open(mod.__file__).read()
        assert "_metered_usage_snapshot" not in source

    def test_openai_lane_unchanged(self):
        import src.providers.openai_responses_lane as mod
        source = open(mod.__file__).read()
        assert "_metered_usage_snapshot" not in source
        assert "budget_blocked" not in source
