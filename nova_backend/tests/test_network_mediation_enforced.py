def test_web_search_executor_requires_key(monkeypatch):
    from src.executors.web_search_executor import WebSearchExecutor
    from src.governor.network_mediator import NetworkMediator
    from src.governor.execute_boundary import ExecuteBoundary
    from src.actions.action_request import ActionRequest

    monkeypatch.delenv("BRAVE_API_KEY", raising=False)

    executor = WebSearchExecutor(NetworkMediator(), ExecuteBoundary())

    req = ActionRequest(
        request_id="test",
        capability_id=16,
        params={"query": "nova"}
    )

    result = executor.execute(req)

    assert result.success is False
