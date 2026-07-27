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
def _block_external_browser_launches(monkeypatch: pytest.MonkeyPatch):
    """Prevent automated tests from opening the user's real browser.

    The webpage-launch executor performs a real OS browser launch via
    ``webbrowser.open`` (src/executors/webpage_launch_executor.py). Executor
    unit tests fake it, but a higher-level simulation path was feeding a
    synthetic search result (``https://abcnews.go.com/story-a``, from
    tests/simulation/conftest.py) into the real executor without mocking the
    launch, so running the full suite opened a browser window (and a 404) on the
    desktop — a leaked external desktop effect confirmed in the ledger.

    Block it suite-wide by default. Tests that specifically prove browser-launch
    behavior override this with their own ``monkeypatch`` in the test body, which
    applies after this autouse fixture.
    """
    monkeypatch.setattr("webbrowser.open", lambda *_args, **_kwargs: True)


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
