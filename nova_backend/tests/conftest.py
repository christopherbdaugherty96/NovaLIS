"""Suite-wide test isolation fixtures.

The OS diagnostics executor keeps a module-level model-status cache with a
10-second TTL (added with the startup health checks). Tests that monkeypatch
`llm_manager` state expect `_model_status_details()` to recompute, but a cache
warmed by an earlier test within the TTL returns stale status instead. That
makes assertions order- and timing-dependent (observed: Linux CI failing
`test_os_diagnostics_executor_reports_blocked_model_as_not_ready` with
'unavailable' while Windows passed).

Resetting the cache around every test keeps runtime behavior untouched while
making model-status assertions deterministic.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _reset_model_status_cache():
    from src.executors import os_diagnostics_executor as mod

    with mod._model_status_cache_lock:
        mod._model_status_cache = {}
        mod._model_status_cache_ts = 0.0
    yield
    with mod._model_status_cache_lock:
        mod._model_status_cache = {}
        mod._model_status_cache_ts = 0.0


@pytest.fixture(autouse=True)
def _reset_news_result_cache():
    """The news skill keeps a module-level short-lived result cache (added to stop
    the dashboard refresh from exhausting the network rate limit). Tests that
    monkeypatch the RSS fetch expect ``handle()`` to actually fetch, so a cache
    warmed by an earlier test would return stale results. Reset around every test."""
    from src.skills import news as news_mod

    news_mod.reset_news_result_cache()
    yield
    news_mod.reset_news_result_cache()
