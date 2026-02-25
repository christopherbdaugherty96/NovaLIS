# tests/test_governor_event_symmetry.py

import types
import sys

import pytest

from src.governor.governor import Governor
from src.governor.exceptions import NetworkMediatorError
from src.actions.action_result import ActionResult


class DummyLedger:
    """Captures ledger events for testing."""
    def __init__(self):
        self.events = []

    def log_event(self, event_type, payload):
        self.events.append((event_type, payload))


def _install_dummy_executor(behavior: str):
    """
    Install a fake module at src.executors.web_search_executor with a WebSearchExecutor
    that simulates timeout, exception, or success when execute() is called.
    """
    mod = types.ModuleType("src.executors.web_search_executor")

    class WebSearchExecutor:
        def __init__(self, network):
            self.network = network

        def execute(self, request_id, params):
            if behavior == "timeout":
                raise TimeoutError()
            elif behavior == "exception":
                raise RuntimeError("simulated executor failure")
            else:
                # Success path – return a dummy success result
                return ActionResult.ok("success", data={}, request_id=request_id)

    mod.WebSearchExecutor = WebSearchExecutor
    sys.modules["src.executors.web_search_executor"] = mod


def test_action_attempted_always_gets_action_completed_on_timeout(monkeypatch):
    g = Governor()
    dummy = DummyLedger()

    # Force governor to use our dummy ledger
    monkeypatch.setattr(g, "_ledger", dummy, raising=False)

    # Ensure capability 16 path uses a timeout‑raising executor
    _install_dummy_executor("timeout")

    res = g.handle_governed_invocation(16, {"query": "test"})
    assert res is not None
    assert res.success is False

    event_types = [e[0] for e in dummy.events]
    assert "ACTION_ATTEMPTED" in event_types
    assert "ACTION_COMPLETED" in event_types

    # Find the completion event and verify error_type field
    completions = [e for e in dummy.events if e[0] == "ACTION_COMPLETED"]
    assert len(completions) == 1
    payload = completions[0][1]
    assert payload["error_type"] == "timeout"
    assert payload["success"] is False


def test_action_attempted_always_gets_action_completed_on_exception(monkeypatch):
    g = Governor()
    dummy = DummyLedger()
    monkeypatch.setattr(g, "_ledger", dummy, raising=False)

    _install_dummy_executor("exception")

    res = g.handle_governed_invocation(16, {"query": "test"})
    assert res is not None
    assert res.success is False

    event_types = [e[0] for e in dummy.events]
    assert "ACTION_ATTEMPTED" in event_types
    assert "ACTION_COMPLETED" in event_types

    completions = [e for e in dummy.events if e[0] == "ACTION_COMPLETED"]
    assert len(completions) == 1
    payload = completions[0][1]
    assert payload["error_type"] == "exception"
    assert payload["success"] is False


def test_action_attempted_always_gets_action_completed_on_success(monkeypatch):
    g = Governor()
    dummy = DummyLedger()
    monkeypatch.setattr(g, "_ledger", dummy, raising=False)

    _install_dummy_executor("success")

    res = g.handle_governed_invocation(16, {"query": "test"})
    assert res is not None
    assert res.success is True

    event_types = [e[0] for e in dummy.events]
    assert "ACTION_ATTEMPTED" in event_types
    assert "ACTION_COMPLETED" in event_types

    completions = [e for e in dummy.events if e[0] == "ACTION_COMPLETED"]
    assert len(completions) == 1
    payload = completions[0][1]
    assert "error_type" not in payload  # success path should not have error_type
    assert payload["success"] is True


def test_action_attempted_not_logged_if_queue_blocks(monkeypatch):
    """If queue has pending, ACTION_ATTEMPTED should never be written."""
    g = Governor()
    dummy = DummyLedger()
    monkeypatch.setattr(g, "_ledger", dummy, raising=False)

    # Manually set a pending request
    g._queue.set_pending("fake-id")

    res = g.handle_governed_invocation(16, {"query": "test"})
    assert res is not None
    assert res.success is False

    # No ledger events at all
    assert dummy.events == []