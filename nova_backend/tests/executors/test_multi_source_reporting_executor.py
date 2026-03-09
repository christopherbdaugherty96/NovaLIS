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
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    executor = mod.MultiSourceReportingExecutor(FakeNetwork())
    result = executor.execute(_request({"query": "ai regulation updates"}))

    assert result.success is True
    assert "INTELLIGENCE BRIEF" in result.message
    assert "Key Findings" in result.message
    assert "Supporting Sources" in result.message
    assert "Confidence" in result.message
    assert "Source Credibility" in result.message
    assert "Confidence Factors" in result.message
    assert "Counter Analysis" in result.message
    assert "abcnews.go.com" in result.message
    assert isinstance(result.data, dict)
    assert result.data.get("widget", {}).get("type") == "search"
    assert isinstance(result.data.get("structured_brief"), dict)
    assert result.data["structured_brief"].get("contract_status") == "pass"
    assert result.data["structured_brief"].get("validation_status") == "pass"
    brief = result.data["structured_brief"]
    assert isinstance(brief.get("source_credibility"), list)
    assert isinstance(brief.get("confidence_factors"), dict)
    assert 0.0 <= float(brief.get("confidence", 0.0)) <= 1.0
    assert brief.get("counter_analysis")
    classes = {str(row.get("classification")) for row in brief.get("source_credibility", [])}
    assert "primary" in classes


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


def test_multi_source_report_falls_back_on_validation_failure(monkeypatch):
    from src.executors import multi_source_reporting_executor as mod

    class FakeNetwork:
        def request(self, **kwargs):
            del kwargs
            return {
                "status_code": 200,
                "data": {
                    "web": {
                        "results": [
                            {"title": "AI regulation bill advances", "url": "https://reuters.com/a"},
                        ]
                    }
                },
            }

    class BadValidationPipeline:
        def validate(self, raw_text: str, presented_text: str):
            del raw_text, presented_text
            return SimpleNamespace(ok=False, stage="AuthorityLanguageDetector", reason="blocked")

    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    monkeypatch.setattr(mod, "generate_chat", lambda *args, **kwargs: "Short analysis text.")
    executor = mod.MultiSourceReportingExecutor(FakeNetwork())
    executor.validation_pipeline = BadValidationPipeline()

    result = executor.execute(_request({"query": "ai regulation updates"}))
    assert result.success is True
    assert "INTELLIGENCE BRIEF" in result.message
    brief = result.data.get("structured_brief", {})
    assert brief.get("contract_status") == "fail"
    assert brief.get("fallback_reason")
    assert isinstance(brief.get("source_credibility"), list)
    assert isinstance(brief.get("confidence_factors"), dict)
