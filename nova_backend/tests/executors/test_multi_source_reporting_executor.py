from __future__ import annotations

from types import SimpleNamespace


def _request(params: dict):
    return SimpleNamespace(capability_id=48, params=params, request_id="req-msr")


def test_multi_source_report_structured_output(monkeypatch):
    from src.executors import multi_source_reporting_executor as mod

    class FakeNetwork:
        def request(self, **kwargs):
            del kwargs
            return {
                "status_code": 200,
                "data": {
                    "web": {
                        "results": [
                            {"title": "AI regulation bill advances", "url": "https://abcnews.go.com/a"},
                            {"title": "Chip export controls updated", "url": "https://foxnews.com/b"},
                            {"title": "Senate hearing on AI policy", "url": "https://reuters.com/c"},
                        ]
                    }
                },
            }

    monkeypatch.setattr(mod, "generate_chat", lambda *args, **kwargs: "Regulatory movement remains active.")
    executor = mod.MultiSourceReportingExecutor(FakeNetwork())
    result = executor.execute(_request({"query": "ai regulation updates"}))

    assert result.success is True
    assert "INTELLIGENCE BRIEF" in result.message
    assert "Key Findings" in result.message
    assert "Supporting Sources" in result.message
    assert "Confidence" in result.message
    assert "abcnews.go.com" in result.message
    assert isinstance(result.data, dict)
    assert result.data.get("widget", {}).get("type") == "search"
    assert isinstance(result.data.get("structured_brief"), dict)


def test_multi_source_report_handles_missing_query():
    from src.executors.multi_source_reporting_executor import MultiSourceReportingExecutor

    class FakeNetwork:
        def request(self, **kwargs):
            del kwargs
            return {"status_code": 500, "data": {}}

    executor = MultiSourceReportingExecutor(FakeNetwork())
    result = executor.execute(_request({"query": ""}))
    assert result.success is False
    assert "No report query provided." in result.message
