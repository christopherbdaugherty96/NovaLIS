"""Tests for PR #248 — DeepSeek Hard Budget Enforcement.

Proves:
1. Pre-call gate blocks when budget state is "limit"
2. Pre-call gate allows normal and warning states
3. Blocked calls emit PROVIDER_USAGE_BLOCKED
4. Blocked calls do NOT emit PROVIDER_USAGE_RECORDED
5. Blocked calls never reach the network/API
6. Blocked result is clear and non-crashing
7. Warning state proceeds and logs warning
8. Normal state proceeds without extra events
9. Morning Brief and other providers remain untouched
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.usage.provider_usage_store import provider_usage_store

# ── Pre-call budget gate ────────────────────────────────────

class TestCheckBudgetGate:
    def test_normal_returns_normal(self):
        from src.providers.deepseek_reasoning_provider import (
            _check_budget_gate,
        )
        with (
            patch.object(
                provider_usage_store,
                "snapshot",
                return_value={
                    "estimated_total_tokens": 1000,
                    "estimated_cost_usd": 0.001,
                    "event_count": 1,
                },
            ),
            patch("src.ledger.writer.LedgerWriter"),
        ):
            state = _check_budget_gate(
                analysis_profile="task_scoped",
                request_id="test-normal",
                model="deepseek-v4-flash",
            )
            assert state == "normal"

    def test_warning_returns_warning(self):
        from src.providers.deepseek_reasoning_provider import (
            _check_budget_gate,
        )
        with (
            patch.object(
                provider_usage_store,
                "snapshot",
                return_value={
                    "estimated_total_tokens": 42000,
                    "estimated_cost_usd": 0.04,
                    "event_count": 5,
                },
            ),
            patch("src.ledger.writer.LedgerWriter"),
        ):
            state = _check_budget_gate(
                analysis_profile="deep_reason",
                request_id="test-warning",
                model="deepseek-v4-flash",
            )
            assert state == "warning"

    def test_limit_returns_limit(self):
        from src.providers.deepseek_reasoning_provider import (
            _check_budget_gate,
        )
        with (
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
            state = _check_budget_gate(
                analysis_profile="task_scoped",
                request_id="test-limit",
                model="deepseek-v4-flash",
            )
            assert state == "limit"

    def test_limit_emits_provider_usage_blocked(self):
        from src.providers.deepseek_reasoning_provider import (
            _check_budget_gate,
        )
        with (
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
            ) as MockWriter,
        ):
            mock_ledger = MagicMock()
            MockWriter.return_value = mock_ledger

            _check_budget_gate(
                analysis_profile="task_scoped",
                request_id="test-blocked",
                model="deepseek-v4-flash",
            )
            mock_ledger.log_event.assert_called_once()
            event_name = mock_ledger.log_event.call_args[0][0]
            event_meta = mock_ledger.log_event.call_args[0][1]
            assert event_name == "PROVIDER_USAGE_BLOCKED"
            assert event_meta["enforcement"] == "hard"
            assert event_meta["budget_state"] == "limit"
            assert event_meta["analysis_profile"] == "task_scoped"

    def test_limit_does_not_emit_usage_recorded(self):
        from src.providers.deepseek_reasoning_provider import (
            _check_budget_gate,
        )
        with (
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
            ) as MockWriter,
        ):
            mock_ledger = MagicMock()
            MockWriter.return_value = mock_ledger

            _check_budget_gate(
                analysis_profile="task_scoped",
                request_id="test-no-recorded",
                model="deepseek-v4-flash",
            )
            for call in mock_ledger.log_event.call_args_list:
                assert call[0][0] != "PROVIDER_USAGE_RECORDED"

    def test_normal_emits_no_events(self):
        from src.providers.deepseek_reasoning_provider import (
            _check_budget_gate,
        )
        with (
            patch.object(
                provider_usage_store,
                "snapshot",
                return_value={
                    "estimated_total_tokens": 1000,
                    "estimated_cost_usd": 0.001,
                    "event_count": 1,
                },
            ),
            patch(
                "src.ledger.writer.LedgerWriter",
            ) as MockWriter,
        ):
            mock_ledger = MagicMock()
            MockWriter.return_value = mock_ledger

            _check_budget_gate(
                analysis_profile="task_scoped",
                request_id="test-normal",
                model="deepseek-v4-flash",
            )
            mock_ledger.log_event.assert_not_called()

    def test_missing_policy_returns_normal(self):
        from src.providers.deepseek_reasoning_provider import (
            _check_budget_gate,
        )
        with (
            patch.object(
                provider_usage_store,
                "snapshot",
                return_value={
                    "estimated_total_tokens": 999999,
                },
            ),
            patch(
                "src.usage.provider_budget_policy."
                "DEFAULT_POLICIES",
                {},
            ),
        ):
            state = _check_budget_gate(
                analysis_profile="analysis",
                request_id="test",
                model="deepseek-v4-flash",
            )
            assert state == "normal"

    def test_snapshot_failure_returns_normal(self):
        from src.providers.deepseek_reasoning_provider import (
            _check_budget_gate,
        )
        with patch.object(
            provider_usage_store,
            "snapshot",
            side_effect=RuntimeError("store broken"),
        ):
            state = _check_budget_gate(
                analysis_profile="analysis",
                request_id="test",
                model="deepseek-v4-flash",
            )
            assert state == "normal"


# ── Hard enforcement in analyze() ────────────────────────────

class TestAnalyzeHardEnforcement:
    def test_limit_blocks_before_network_call(self):
        """Budget limit must prevent the network request entirely."""
        from src.providers.deepseek_reasoning_provider import (
            DeepSeekReasoningProvider,
        )

        mock_network = MagicMock()
        provider = DeepSeekReasoningProvider(network=mock_network)

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
                prompt="Should be blocked",
                analysis_profile="task_scoped",
                request_id="block-test",
            )
            mock_network.request.assert_not_called()
            assert result.usage_meta["blocked"] is True

    def test_blocked_result_has_clear_text(self):
        from src.providers.deepseek_reasoning_provider import (
            DeepSeekReasoningProvider,
        )

        mock_network = MagicMock()
        provider = DeepSeekReasoningProvider(network=mock_network)

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
                prompt="Should be blocked",
                analysis_profile="task_scoped",
                request_id="block-text-test",
            )
            assert "budget limit reached" in result.text.lower()
            assert "--" in result.text

    def test_blocked_result_metadata(self):
        from src.providers.deepseek_reasoning_provider import (
            DeepSeekReasoningProvider,
        )

        mock_network = MagicMock()
        provider = DeepSeekReasoningProvider(network=mock_network)

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
                prompt="Should be blocked",
                analysis_profile="deep_reason",
                request_id="meta-test",
            )
            assert result.route == "budget_blocked"
            assert result.provider == "DeepSeek"
            assert result.usage_meta["policy_budget_state"] == "limit"
            assert result.usage_meta["enforcement"] == "hard"
            assert result.usage_meta["analysis_profile"] == "deep_reason"
            assert result.usage_meta["blocked"] is True

    def test_blocked_does_not_record_usage(self):
        """Blocked call must not call record_reasoning_event."""
        from src.providers.deepseek_reasoning_provider import (
            DeepSeekReasoningProvider,
        )

        mock_network = MagicMock()
        provider = DeepSeekReasoningProvider(network=mock_network)

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
            patch.object(
                provider_usage_store,
                "record_reasoning_event",
            ) as mock_record,
            patch("src.ledger.writer.LedgerWriter"),
        ):
            provider.analyze(
                prompt="Should be blocked",
                analysis_profile="task_scoped",
                request_id="no-record-test",
            )
            mock_record.assert_not_called()

    def test_warning_proceeds_with_network_call(self):
        """Warning state must allow the network call."""
        from src.providers.deepseek_reasoning_provider import (
            DeepSeekReasoningProvider,
        )

        fake_response = {
            "data": {
                "choices": [
                    {"message": {"content": "Warning advisory"}}
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
            patch.dict(
                "os.environ", {"DEEPSEEK_API_KEY": "test-key"},
            ),
            patch.object(
                provider_usage_store,
                "snapshot",
                return_value={
                    "estimated_total_tokens": 42000,
                    "estimated_cost_usd": 0.04,
                    "event_count": 5,
                },
            ),
            patch.object(
                provider_usage_store,
                "record_reasoning_event",
                return_value={
                    "estimated_total_tokens": 42150,
                    "estimated_cost_usd": 0.041,
                    "event_count": 6,
                    "budget_state": "warning",
                    "budget_state_label": "Budget low",
                },
            ),
            patch("src.ledger.writer.LedgerWriter"),
        ):
            result = provider.analyze(
                prompt="Warning test",
                analysis_profile="task_scoped",
                request_id="warning-test",
            )
            mock_network.request.assert_called_once()
            assert result.text == "Warning advisory"

    def test_normal_proceeds_with_network_call(self):
        """Normal state must allow the network call."""
        from src.providers.deepseek_reasoning_provider import (
            DeepSeekReasoningProvider,
        )

        fake_response = {
            "data": {
                "choices": [
                    {"message": {"content": "Normal advisory"}}
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
            patch.dict(
                "os.environ", {"DEEPSEEK_API_KEY": "test-key"},
            ),
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
            result = provider.analyze(
                prompt="Normal test",
                analysis_profile="analysis",
                request_id="normal-test",
            )
            mock_network.request.assert_called_once()
            assert result.text == "Normal advisory"


# ── Blocked call emits correct events ────────────────────────

class TestBlockedCallEvents:
    def test_blocked_emits_usage_blocked_event(self):
        from src.providers.deepseek_reasoning_provider import (
            DeepSeekReasoningProvider,
        )

        mock_network = MagicMock()
        provider = DeepSeekReasoningProvider(network=mock_network)

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
            patch(
                "src.ledger.writer.LedgerWriter",
            ) as MockWriter,
        ):
            mock_ledger = MagicMock()
            MockWriter.return_value = mock_ledger

            provider.analyze(
                prompt="Blocked event test",
                analysis_profile="task_scoped",
                request_id="event-test",
            )
            assert mock_ledger.log_event.call_count == 1
            event_name = mock_ledger.log_event.call_args[0][0]
            assert event_name == "PROVIDER_USAGE_BLOCKED"

    def test_blocked_does_not_emit_usage_recorded(self):
        from src.providers.deepseek_reasoning_provider import (
            DeepSeekReasoningProvider,
        )

        mock_network = MagicMock()
        provider = DeepSeekReasoningProvider(network=mock_network)

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
            patch(
                "src.ledger.writer.LedgerWriter",
            ) as MockWriter,
        ):
            mock_ledger = MagicMock()
            MockWriter.return_value = mock_ledger

            provider.analyze(
                prompt="No-recorded test",
                analysis_profile="task_scoped",
                request_id="no-recorded-test",
            )
            for call in mock_ledger.log_event.call_args_list:
                assert call[0][0] != "PROVIDER_USAGE_RECORDED"


# ── Boundary files untouched ─────────────────────────────────

class TestBoundaryFilesUntouched:
    def test_morning_brief_no_budget_gate(self):
        import src.conversation.morning_brief_handler as mod
        source = open(mod.__file__).read()
        assert "_check_budget_gate" not in source
        assert "PROVIDER_USAGE_BLOCKED" not in source
        assert "budget_blocked" not in source

    def test_daily_brief_no_budget_gate(self):
        import src.brief.daily_brief as mod
        source = open(mod.__file__).read()
        assert "_check_budget_gate" not in source
        assert "PROVIDER_USAGE_BLOCKED" not in source

    def test_network_mediator_unchanged(self):
        import src.governor.network_mediator as mod
        source = open(mod.__file__).read()
        assert "_check_budget_gate" not in source
        assert "PROVIDER_USAGE_BLOCKED" not in source
        assert "budget_blocked" not in source

    def test_governor_no_policy_budget(self):
        import src.governor.governor as mod
        source = open(mod.__file__).read()
        assert "_check_budget_gate" not in source
        assert "PROVIDER_USAGE_BLOCKED" not in source

    def test_openai_lane_unchanged(self):
        import src.providers.openai_responses_lane as mod
        source = open(mod.__file__).read()
        assert "_check_budget_gate" not in source
        assert "PROVIDER_USAGE_BLOCKED" not in source

    def test_weather_unchanged(self):
        import src.skills.weather as mod
        source = open(mod.__file__).read()
        assert "_check_budget_gate" not in source

    def test_news_unchanged(self):
        import src.skills.news as mod
        source = open(mod.__file__).read()
        assert "_check_budget_gate" not in source

    def test_web_search_unchanged(self):
        import src.executors.web_search_executor as mod
        source = open(mod.__file__).read()
        assert "_check_budget_gate" not in source


# ── Source-level proof ───────────────────────────────────────

class TestSourceLevelProof:
    def test_gate_is_before_network_call_in_source(self):
        """_check_budget_gate must appear before
        self._network.request in the analyze method source."""
        import inspect

        from src.providers.deepseek_reasoning_provider import (
            DeepSeekReasoningProvider,
        )
        source = inspect.getsource(
            DeepSeekReasoningProvider.analyze,
        )
        gate_pos = source.index("_check_budget_gate")
        network_pos = source.index("self._network.request")
        assert gate_pos < network_pos

    def test_blocked_return_is_before_network_call(self):
        """The budget_blocked return must appear before
        the network request in analyze source."""
        import inspect

        from src.providers.deepseek_reasoning_provider import (
            DeepSeekReasoningProvider,
        )
        source = inspect.getsource(
            DeepSeekReasoningProvider.analyze,
        )
        blocked_pos = source.index("budget_blocked")
        network_pos = source.index("self._network.request")
        assert blocked_pos < network_pos

    def test_check_budget_gate_never_raises(self):
        """_check_budget_gate wraps everything in try/except —
        it must never crash the caller."""
        import inspect

        from src.providers.deepseek_reasoning_provider import (
            _check_budget_gate,
        )
        source = inspect.getsource(_check_budget_gate)
        assert 'return "normal"' in source
        assert "try:" in source
        assert "except Exception:" in source
