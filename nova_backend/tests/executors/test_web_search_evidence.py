from src.actions.action_request import ActionRequest
from src.actions.action_result import ActionResult
from src.executors.web_search_executor import WebSearchExecutor
from src.governor.execute_boundary.execute_boundary import ExecuteBoundary


class _NoopNetwork:
    def request(self, *args, **kwargs):  # pragma: no cover
        raise AssertionError("network should not be called by this unit test")


def _request() -> ActionRequest:
    return ActionRequest(
        capability_id=16,
        params={"query": "latest AI model releases", "session_id": "test-session"},
        request_id="search-test",
    )


def test_web_search_widget_includes_structured_evidence(monkeypatch):
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)
    executor = WebSearchExecutor(_NoopNetwork(), ExecuteBoundary())
    results = [
        {
            "title": "AI model release roundup",
            "url": "https://example.com/models",
            "snippet": "Several model releases were announced.",
        }
    ]
    source_packets = [
        {
            "title": "AI model release roundup",
            "url": "https://example.com/models",
            "domain": "example.com",
            "text": "A new AI model was announced this week with stronger coding performance.",
        }
    ]

    monkeypatch.setattr(executor, "_parse_results", lambda data: results)
    monkeypatch.setattr(executor, "_search_duckduckgo", lambda request, query, session_id: {"status_code": 200, "data": {}})
    monkeypatch.setattr(executor, "_collect_source_packets", lambda **kwargs: source_packets)
    monkeypatch.setattr(
        executor,
        "_synthesize_researched_summary",
        lambda **kwargs: "A source-backed model release summary.",
    )

    action_result = executor.execute(_request())

    assert isinstance(action_result, ActionResult)
    assert action_result.success is True
    evidence = action_result.data["widget"]["data"].get("evidence")
    assert evidence is not None
    assert evidence["query"] == "latest AI model releases"
    assert evidence["evidence_status"] in {"source_backed", "snippet_backed"}
