"""Tests for model-health check caching introduced in the
STARTUP_HYDRATION_STABILITY lane.

Verifies that concurrent callers of _model_status_details() share a
single Ollama health check within the cache TTL window, preventing
the startup stampede that caused CPU/memory spikes when Chrome
connected.
"""
from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock, patch

import pytest

import src.executors.os_diagnostics_executor as diag_mod
from src.executors.os_diagnostics_executor import OSDiagnosticsExecutor


@pytest.fixture(autouse=True)
def _clear_cache():
    """Reset the module-level model status cache before each test."""
    diag_mod._model_status_cache.clear()
    diag_mod._model_status_cache_ts = 0.0
    yield
    diag_mod._model_status_cache.clear()
    diag_mod._model_status_cache_ts = 0.0


def _mock_llm_manager(*, health=True, blocked=False, fallback=False, model="test-model"):
    mgr = MagicMock()
    mgr.model = model
    mgr.active_model = model
    mgr.inference_blocked = blocked
    mgr._using_fallback = fallback
    mgr.health_check.return_value = health
    return mgr


class TestModelStatusCache:
    def test_cache_prevents_repeated_health_checks(self):
        mgr = _mock_llm_manager(health=True)
        with patch("src.llm.llm_manager.llm_manager", mgr):
            r1 = OSDiagnosticsExecutor._model_status_details()
            r2 = OSDiagnosticsExecutor._model_status_details()

        assert r1 == r2
        assert r1[0] == "available"
        assert mgr.health_check.call_count == 1

    def test_cache_expires_after_ttl(self):
        mgr = _mock_llm_manager(health=True)
        with patch("src.llm.llm_manager.llm_manager", mgr):
            OSDiagnosticsExecutor._model_status_details()
            assert mgr.health_check.call_count == 1

            diag_mod._model_status_cache_ts = time.monotonic() - 20.0

            OSDiagnosticsExecutor._model_status_details()
            assert mgr.health_check.call_count == 2

    def test_concurrent_callers_share_single_check(self):
        call_count = 0
        call_event = threading.Event()

        def slow_health_check():
            nonlocal call_count
            call_count += 1
            call_event.wait(timeout=2)
            return True

        mgr = _mock_llm_manager(health=True)
        mgr.health_check.side_effect = slow_health_check

        results = [None, None, None, None]

        def caller(idx):
            with patch("src.llm.llm_manager.llm_manager", mgr):
                results[idx] = OSDiagnosticsExecutor._model_status_details()

        threads = [threading.Thread(target=caller, args=(i,)) for i in range(4)]
        for t in threads:
            t.start()

        time.sleep(0.1)
        call_event.set()

        for t in threads:
            t.join(timeout=5)

        non_none = [r for r in results if r is not None]
        assert len(non_none) >= 1
        for r in non_none:
            assert r[0] in ("available", "unavailable", "unknown")

    def test_blocked_model_status_cached(self):
        mgr = _mock_llm_manager(health=True, blocked=True)
        with patch("src.llm.llm_manager.llm_manager", mgr):
            r1 = OSDiagnosticsExecutor._model_status_details()
            r2 = OSDiagnosticsExecutor._model_status_details()

        assert r1[0] == "blocked"
        assert r1 == r2
        assert mgr.health_check.call_count == 1

    def test_unavailable_model_status_cached(self):
        mgr = _mock_llm_manager(health=False)
        with patch("src.llm.llm_manager.llm_manager", mgr):
            r1 = OSDiagnosticsExecutor._model_status_details()
            r2 = OSDiagnosticsExecutor._model_status_details()

        assert r1[0] == "unavailable"
        assert r1 == r2
        assert mgr.health_check.call_count == 1

    def test_uncached_still_works_directly(self):
        mgr = _mock_llm_manager(health=True)
        with patch("src.llm.llm_manager.llm_manager", mgr):
            r = OSDiagnosticsExecutor._model_status_details_uncached()
        assert r[0] == "available"
        assert mgr.health_check.call_count == 1
