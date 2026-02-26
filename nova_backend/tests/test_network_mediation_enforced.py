def test_web_search_executor_handles_network_mediator_error(monkeypatch):
    from src.actions.action_request import ActionRequest
    from src.executors.web_search_executor import WebSearchExecutor
    from src.governor.exceptions import NetworkMediatorError
    from src.governor.network_mediator import NetworkMediator
    from src.governor.execute_boundary import ExecuteBoundary

    executor = WebSearchExecutor(NetworkMediator(), ExecuteBoundary())

    def fail_request(**_kwargs):
        raise NetworkMediatorError("blocked")

    monkeypatch.setattr(executor.network, "request", fail_request)

    request = ActionRequest(
        request_id="test",
        capability_id=16,
        params={"query": "nova"},
    )

    result = executor.execute(request)

    assert result.success is False
    assert result.data["widget"]["data"]["results"] == []
