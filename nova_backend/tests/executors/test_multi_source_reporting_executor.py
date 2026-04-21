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
    assert "Bottom line:" in result.message
    assert "Key Findings" in result.message
    assert "Supporting Sources" in result.message
    assert "Confidence" in result.message
    assert "Source Credibility" in result.message
    assert "Confidence Factors" in result.message
    assert "Counter Analysis" in result.message
    assert "abcnews.go.com" in result.message
    assert isinstance(result.data, dict)
    assert result.speakable_text.startswith("Research report ready")
    assert isinstance(result.structured_data, dict)
    assert result.structured_data.get("widget", {}).get("type") == "search"
    assert result.data.get("widget", {}).get("type") == "search"
    widget_data = result.data.get("widget", {}).get("data", {})
    assert widget_data.get("query") == "ai regulation updates"
    assert widget_data.get("provider") == "Brave Search"
    assert widget_data.get("result_count") == 3
    assert widget_data.get("summary")
    assert isinstance(widget_data.get("results"), list)
    assert isinstance(widget_data.get("structured_brief"), dict)
    assert "snippet" in widget_data["results"][0]
    assert isinstance(result.data.get("structured_brief"), dict)
    assert result.data["structured_brief"].get("contract_status") == "pass"
    assert result.data["structured_brief"].get("validation_status") == "pass"
    brief = result.data["structured_brief"]
    assert widget_data["structured_brief"] == brief
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
    assert result.structured_data["failure_kind"] == "missing_query"


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


def test_multi_source_report_uses_duck_fallback_when_brave_missing(monkeypatch):
    from src.executors import multi_source_reporting_executor as mod

    class FakeNetwork:
        def request(self, **kwargs):
            del kwargs
            return {
                "status_code": 200,
                "data": {
                    "Abstract": "AI regulation outlook",
                    "AbstractURL": "https://duck.example/ai-regulation",
                    "RelatedTopics": [
                        {"Text": "Policy hearing summary", "FirstURL": "https://duck.example/hearing"}
                    ],
                },
            }

    monkeypatch.delenv("BRAVE_API_KEY", raising=False)
    monkeypatch.setattr(mod, "generate_chat", lambda *args, **kwargs: "Analyst note.")

    executor = mod.MultiSourceReportingExecutor(FakeNetwork())
    result = executor.execute(_request({"query": "ai regulation updates"}))
    assert result.success is True
    brief = result.data.get("structured_brief", {})
    assert brief.get("search_provider") == "duckduckgo"
    assert "INTELLIGENCE BRIEF" in result.message
    assert "Bottom line:" in result.message


def test_multi_source_report_source_reliability_focus_preserves_topic_query(monkeypatch):
    from src.executors import multi_source_reporting_executor as mod

    class FakeNetwork:
        def request(self, **kwargs):
            del kwargs
            return {
                "status_code": 200,
                "data": {
                    "web": {
                        "results": [
                            {"title": "Policy update from agency", "url": "https://www.commerce.gov/a"},
                            {"title": "Industry reaction summary", "url": "https://www.semiconductors.org/b"},
                        ]
                    }
                },
            }

    monkeypatch.setattr(mod, "generate_chat", lambda *args, **kwargs: "Reliability remains mixed across source types.")
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    executor = mod.MultiSourceReportingExecutor(FakeNetwork())

    result = executor.execute(_request({"query": "semiconductor policy updates", "analysis_focus": "source_reliability"}))

    assert result.success is True
    assert "Topic: source reliability for semiconductor policy updates" in result.message
    widget_data = result.data.get("widget", {}).get("data", {})
    assert widget_data.get("query") == "semiconductor policy updates"
    assert widget_data.get("analysis_focus") == "source_reliability"
    assert widget_data.get("summary") == (
        "Source reliability scan for 'semiconductor policy updates' reviewed 2 finding(s) across 2 source domain(s)."
    )
    brief = result.data.get("structured_brief", {})
    assert brief.get("topic") == "source reliability for semiconductor policy updates"
    assert brief.get("analysis_focus") == "source_reliability"


def test_multi_source_report_skips_counter_model_when_analyst_note_unavailable(monkeypatch):
    from src.executors import multi_source_reporting_executor as mod

    class FakeNetwork:
        def request(self, **kwargs):
            del kwargs
            return {
                "status_code": 200,
                "data": {
                    "web": {
                        "results": [
                            {"title": "Policy update from agency", "url": "https://www.commerce.gov/a"},
                            {"title": "Industry reaction summary", "url": "https://www.semiconductors.org/b"},
                        ]
                    }
                },
            }

    captured: dict[str, float | bool] = {}

    def _fake_generate_chat(*args, **kwargs):
        del args
        captured["analyst_timeout"] = float(kwargs.get("timeout") or 0.0)
        return None

    monkeypatch.setattr(mod, "generate_chat", _fake_generate_chat)
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    executor = mod.MultiSourceReportingExecutor(FakeNetwork())

    def _unexpected_counter_analysis(*args, **kwargs):
        del args, kwargs
        captured["counter_called"] = True
        raise AssertionError("counter analysis should not run when analyst note is unavailable")

    executor.deepseek_bridge.analyze = _unexpected_counter_analysis

    result = executor.execute(_request({"query": "semiconductor policy updates"}))

    assert result.success is True
    assert captured["analyst_timeout"] == mod.ANALYST_NOTE_TIMEOUT_SECONDS
    assert captured.get("counter_called") is not True
    brief = result.data.get("structured_brief", {})
    assert str(brief.get("counter_analysis") or "").startswith("Counter-view:")


def test_multi_source_report_counter_analysis_uses_bounded_timeout(monkeypatch):
    from src.executors import multi_source_reporting_executor as mod

    class FakeNetwork:
        def request(self, **kwargs):
            del kwargs
            return {
                "status_code": 200,
                "data": {
                    "web": {
                        "results": [
                            {"title": "Policy update from agency", "url": "https://www.commerce.gov/a"},
                            {"title": "Industry reaction summary", "url": "https://www.semiconductors.org/b"},
                        ]
                    }
                },
            }

    captured: dict[str, float] = {}

    monkeypatch.setattr(mod, "generate_chat", lambda *args, **kwargs: "Analyst note available.")
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    executor = mod.MultiSourceReportingExecutor(FakeNetwork())

    def _fake_counter_analysis(*args, **kwargs):
        del args
        captured["counter_timeout"] = float(kwargs.get("timeout_seconds") or 0.0)
        return "Counter-view: there is still uncertainty in the available coverage."

    executor.deepseek_bridge.analyze = _fake_counter_analysis

    result = executor.execute(_request({"query": "semiconductor policy updates"}))

    assert result.success is True
    assert captured["counter_timeout"] == mod.COUNTER_ANALYSIS_TIMEOUT_SECONDS
