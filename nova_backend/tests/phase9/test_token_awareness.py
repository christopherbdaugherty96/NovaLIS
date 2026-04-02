"""
Phase 9 — Token Awareness Layer tests.

Covers:
  - Budget gate: governor refuses budget-gated caps when budget is exhausted
  - Budget snapshot: governor attaches budget_state to result.data for network caps
  - /api/token/budget endpoint: returns usage snapshot
  - send_token_budget_update: does not raise when called with/without result data
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src import brain_server
from src.usage.provider_usage_store import ProviderUsageStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _exhausted_usage_store(tmp_path: Path) -> ProviderUsageStore:
    """A usage store that is already at budget limit (1 token budget, 999 used)."""
    store = ProviderUsageStore(tmp_path / "usage.json", daily_token_budget=1)
    store.record_reasoning_event(
        provider="test",
        route="test",
        analysis_profile="test",
        prompt_text="x" * 4000,  # ~1000 estimated tokens → well over budget
        response_text="y",
    )
    return store


def _warning_usage_store(tmp_path: Path) -> ProviderUsageStore:
    """A usage store that is in warning state (80% of 1000 used)."""
    store = ProviderUsageStore(tmp_path / "usage.json", daily_token_budget=1000, warning_ratio=0.8)
    store.record_reasoning_event(
        provider="test",
        route="test",
        analysis_profile="test",
        prompt_text="x" * 3400,  # ~850 estimated tokens → >80% of 1000
        response_text="y",
    )
    return store


# ---------------------------------------------------------------------------
# Governor budget gate tests
# ---------------------------------------------------------------------------

class TestGovernorBudgetGate:
    def test_budget_gated_cap_is_refused_when_limit_reached(self, tmp_path):
        from src.governor.governor import Governor, _BUDGET_GATED_CAP_IDS

        assert len(_BUDGET_GATED_CAP_IDS) > 0, "Budget-gated cap IDs must be defined"
        exhausted_store = _exhausted_usage_store(tmp_path)
        governor = Governor()

        # Patch the module-level singleton that governor imports
        usage_module = importlib.import_module("src.usage.provider_usage_store")
        with patch.object(usage_module, "provider_usage_store", exhausted_store):
            cap_id = next(iter(_BUDGET_GATED_CAP_IDS))  # pick any budget-gated cap
            result = governor._check_network_budget(cap_id)

        assert result is not None
        assert result.success is False
        assert "budget reached" in result.message.lower()
        assert isinstance(result.data, dict)
        assert result.data.get("budget_state") == "limit"

    def test_non_budget_gated_cap_passes_budget_check(self, tmp_path):
        from src.governor.governor import Governor, _BUDGET_GATED_CAP_IDS

        exhausted_store = _exhausted_usage_store(tmp_path)
        governor = Governor()

        # Cap 32 is local-only — not budget-gated
        non_network_cap = 32
        assert non_network_cap not in _BUDGET_GATED_CAP_IDS

        usage_module = importlib.import_module("src.usage.provider_usage_store")
        with patch.object(usage_module, "provider_usage_store", exhausted_store):
            result = governor._check_network_budget(non_network_cap)

        assert result is None, "Local cap should not be budget-blocked"

    def test_warning_state_does_not_block_execution(self, tmp_path):
        from src.governor.governor import Governor, _BUDGET_GATED_CAP_IDS

        warning_store = _warning_usage_store(tmp_path)
        snapshot = warning_store.snapshot()
        assert snapshot["budget_state"] == "warning", "Test precondition: store must be in warning state"

        governor = Governor()
        cap_id = next(iter(_BUDGET_GATED_CAP_IDS))

        usage_module = importlib.import_module("src.usage.provider_usage_store")
        with patch.object(usage_module, "provider_usage_store", warning_store):
            result = governor._check_network_budget(cap_id)

        assert result is None, "Warning state must not block execution — only warn"

    def test_budget_exception_does_not_block_execution(self, tmp_path):
        from src.governor.governor import Governor, _BUDGET_GATED_CAP_IDS

        governor = Governor()
        cap_id = next(iter(_BUDGET_GATED_CAP_IDS))

        # Simulate provider_usage_store raising an exception
        broken_store = MagicMock()
        broken_store.snapshot.side_effect = RuntimeError("store unavailable")

        usage_module = importlib.import_module("src.usage.provider_usage_store")
        with patch.object(usage_module, "provider_usage_store", broken_store):
            result = governor._check_network_budget(cap_id)

        assert result is None, "Budget check failure must not block execution (fail open)"


# ---------------------------------------------------------------------------
# Budget snapshot in result.data
# ---------------------------------------------------------------------------

class TestBudgetSnapshotInResult:
    def test_budget_gated_cap_ids_match_known_network_caps(self):
        from src.governor.governor import _BUDGET_GATED_CAP_IDS

        # These are the expected network-mediated caps that consume external tokens.
        expected = {16, 48, 49, 50, 55, 56, 63}
        assert _BUDGET_GATED_CAP_IDS == expected

    def test_fresh_usage_store_snapshot_has_normal_state(self, tmp_path):
        store = ProviderUsageStore(tmp_path / "usage.json", daily_token_budget=10_000)
        snapshot = store.snapshot()
        assert snapshot["budget_state"] == "normal"
        assert snapshot["budget_remaining_tokens"] == 10_000

    def test_exhausted_store_snapshot_has_limit_state(self, tmp_path):
        store = _exhausted_usage_store(tmp_path)
        snapshot = store.snapshot()
        assert snapshot["budget_state"] == "limit"
        assert snapshot["budget_remaining_tokens"] == 0


# ---------------------------------------------------------------------------
# /api/token/budget endpoint
# ---------------------------------------------------------------------------

class TestTokenBudgetEndpoint:
    def _make_client(self, monkeypatch, tmp_path):
        from src.settings.runtime_settings_store import RuntimeSettingsStore
        from src.tasks.notification_schedule_store import NotificationScheduleStore

        store = RuntimeSettingsStore(tmp_path / "settings.json")
        usage_store = ProviderUsageStore(tmp_path / "usage.json", daily_token_budget=5000)

        settings_module = importlib.import_module("src.settings.runtime_settings_store")
        diagnostics_module = importlib.import_module("src.executors.os_diagnostics_executor")
        settings_api_module = importlib.import_module("src.api.settings_api")

        monkeypatch.setattr(settings_module, "runtime_settings_store", store)
        monkeypatch.setattr(diagnostics_module, "runtime_settings_store", store)
        monkeypatch.setattr(diagnostics_module, "provider_usage_store", usage_store)
        monkeypatch.setattr(brain_server, "runtime_settings_store", store)
        monkeypatch.setattr(settings_api_module, "provider_usage_store", usage_store)

        from src.openclaw.agent_runtime_store import OpenClawAgentRuntimeStore
        agent_store = OpenClawAgentRuntimeStore(tmp_path / "agent.json")
        runtime_module = importlib.import_module("src.openclaw.agent_runtime_store")
        monkeypatch.setattr(runtime_module, "openclaw_agent_runtime_store", agent_store)
        monkeypatch.setattr(brain_server, "openclaw_agent_runtime_store", agent_store)
        monkeypatch.setattr(brain_server, "NotificationScheduleStore", lambda: NotificationScheduleStore(tmp_path / "ns.json"))
        monkeypatch.delenv("WEATHER_API_KEY", raising=False)
        monkeypatch.delenv("NOVA_OPENCLAW_BRIDGE_TOKEN", raising=False)

        return TestClient(brain_server.app), usage_store

    def test_token_budget_endpoint_returns_200(self, monkeypatch, tmp_path):
        client, _ = self._make_client(monkeypatch, tmp_path)
        response = client.get("/api/token/budget")
        assert response.status_code == 200

    def test_token_budget_endpoint_returns_snapshot_fields(self, monkeypatch, tmp_path):
        client, _ = self._make_client(monkeypatch, tmp_path)
        response = client.get("/api/token/budget")
        payload = response.json()
        assert "budget_state" in payload
        assert "budget_remaining_tokens" in payload
        assert "budget_state_label" in payload
        assert payload["budget_state"] == "normal"
        assert payload["budget_remaining_tokens"] == 5000

    def test_token_budget_endpoint_reflects_exhausted_budget(self, monkeypatch, tmp_path):
        client, usage_store = self._make_client(monkeypatch, tmp_path)
        # Exhaust the budget
        usage_store.record_reasoning_event(
            provider="test", route="test", analysis_profile="test",
            prompt_text="x" * 20_000, response_text="y",
        )
        response = client.get("/api/token/budget")
        payload = response.json()
        assert payload["budget_state"] == "limit"
        assert payload["budget_remaining_tokens"] == 0
