from __future__ import annotations

import inspect

from src.llm.model_network_mediator import ModelNetworkMediator


def test_model_network_mediator_has_explicit_locks_for_shared_state():
    mediator = ModelNetworkMediator()
    assert hasattr(mediator, "_rate_lock")
    assert hasattr(mediator, "_session_lock")
    assert hasattr(mediator._rate_lock, "acquire")
    assert hasattr(mediator._session_lock, "acquire")


def test_model_network_mediator_uses_locks_in_rate_limit_and_request_paths():
    source = inspect.getsource(ModelNetworkMediator)
    assert "with self._rate_lock" in source
    assert "with self._session_lock" in source
