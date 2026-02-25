# tests/test_network_mediation_enforced.py

import sys

def test_web_search_executor_handles_network_mediator_error(monkeypatch):
    # Ensure we get the real executor, not a cached dummy
    if "src.executors.web_search_executor" in sys.modules:
        del sys.modules["src.executors.web_search_executor"]

    from src.executors.web_search_executor import WebSearchExecutor
    from src.governor.exceptions import NetworkMediatorError
    from src.governor.network_mediator import NetworkMediator

    executor = WebSearchExecutor(NetworkMediator())

    def fail_request(**_kwargs):
        raise NetworkMediatorError("blocked")

    monkeypatch.setattr(executor.network, "request", fail_request)

    request_id = "test-123"
    params = {"query": "nova", "capability_id": 16}
    result = executor.execute(request_id, params)

    assert result.success is False