from __future__ import annotations

from types import SimpleNamespace


def _request(capability_id: int, params: dict):
    return SimpleNamespace(capability_id=capability_id, params=params, request_id="req-1")


def test_summary_requires_cached_headlines():
    from src.executors.news_intelligence_executor import NewsIntelligenceExecutor

    executor = NewsIntelligenceExecutor()
    result = executor.execute_summary(_request(49, {"selection": "all", "headlines": []}))
    assert result.success is False
    assert "Say 'news' first" in result.message


def test_summary_enforces_max_three(monkeypatch):
    from src.executors import news_intelligence_executor as mod

    monkeypatch.setattr(mod, "generate_chat", lambda *args, **kwargs: "Summary\nKey Points\nContext\nImplications")

    headlines = [
        {"title": "A", "source": "S1", "url": "u1"},
        {"title": "B", "source": "S2", "url": "u2"},
        {"title": "C", "source": "S3", "url": "u3"},
        {"title": "D", "source": "S4", "url": "u4"},
    ]
    executor = mod.NewsIntelligenceExecutor()
    result = executor.execute_summary(_request(49, {"indices": [1, 2, 3, 4], "headlines": headlines}))
    assert result.success is False
    assert "up to three headlines" in result.message


def test_intelligence_brief_updates_topic_map(monkeypatch):
    from src.executors import news_intelligence_executor as mod

    monkeypatch.setattr(
        mod,
        "generate_chat",
        lambda *args, **kwargs: "Top Headlines\n1. A\n\nKey Developments\n- X\n\nSignals to Watch\n- Y",
    )
    headlines = [
        {"title": "NASA delays Artemis mission", "source": "Example", "url": "https://example.com/1"},
        {"title": "AI regulation bill advances", "source": "Example", "url": "https://example.com/2"},
    ]
    executor = mod.NewsIntelligenceExecutor()
    result = executor.execute_brief(_request(50, {"headlines": headlines, "topic_history": {"ai": 1}}))
    assert result.success is True
    assert "DAILY INTELLIGENCE BRIEF" in result.message
    assert isinstance(result.data, dict)
    assert isinstance(result.data.get("topic_map"), dict)
    assert "ai" in result.data["topic_map"]
