from __future__ import annotations

import time
from types import SimpleNamespace


def _request(capability_id: int, params: dict):
    return SimpleNamespace(capability_id=capability_id, params=params, request_id="req-1")


def test_summary_requires_cached_headlines():
    from src.executors.news_intelligence_executor import NewsIntelligenceExecutor

    executor = NewsIntelligenceExecutor()
    result = executor.execute_summary(_request(49, {"selection": "all", "headlines": []}))
    assert result.success is False
    assert "Say 'news' first" in result.message


def test_daily_brief_missing_headlines_reports_current_state():
    from src.executors.news_intelligence_executor import NewsIntelligenceExecutor

    executor = NewsIntelligenceExecutor()
    result = executor.execute_brief(_request(50, {"headlines": []}))
    assert result.success is False
    assert "headline data isn't available right now" in result.message


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
    assert "NOVA INTELLIGENCE BRIEF" in result.message
    assert isinstance(result.data, dict)
    assert result.speakable_text.startswith("Daily intelligence brief ready.")
    assert isinstance(result.structured_data, dict)
    assert isinstance(result.data.get("topic_map"), dict)
    assert "ai" in result.data["topic_map"]
    assert "ai" in result.structured_data["topic_map"]


def test_summary_falls_back_when_llm_is_slow(monkeypatch):
    from src.executors import news_intelligence_executor as mod

    def _slow_generate(*args, **kwargs):
        time.sleep(0.05)
        return "this should timeout in test"

    monkeypatch.setattr(mod, "generate_chat", _slow_generate)
    monkeypatch.setattr(mod, "LLM_TIMEOUT_SECONDS", 0.01)

    headlines = [{"title": "A", "source": "S1", "url": "u1"}]
    executor = mod.NewsIntelligenceExecutor()
    result = executor.execute_summary(_request(49, {"indices": [1], "headlines": headlines}))
    assert result.success is True
    assert "Limited detail is available from the headline alone." in result.message


def test_llm_timeout_waits_for_worker_completion(monkeypatch):
    from src.executors import news_intelligence_executor as mod

    state = {"done": False}

    def _slow_generate(*args, **kwargs):
        time.sleep(0.05)
        state["done"] = True
        return "slow output"

    monkeypatch.setattr(mod, "generate_chat", _slow_generate)

    executor = mod.NewsIntelligenceExecutor()
    _ = executor._llm_or_fallback("prompt", "fallback", "req-timeout-test", timeout_seconds=0.01)

    assert state["done"] is True


def test_summary_filters_by_source(monkeypatch):
    from src.executors import news_intelligence_executor as mod

    monkeypatch.setattr(mod, "generate_chat", lambda *args, **kwargs: "Summary\nKey Points\nContext\nImplications")
    headlines = [
        {"title": "A", "source": "ABC News", "url": "u1"},
        {"title": "B", "source": "FOX News", "url": "u2"},
    ]
    executor = mod.NewsIntelligenceExecutor()
    result = executor.execute_summary(
        _request(49, {"selection": "source", "source_query": "abc", "headlines": headlines})
    )
    assert result.success is True
    assert "Source: ABC News" in result.message


def test_summary_filters_by_topic(monkeypatch):
    from src.executors import news_intelligence_executor as mod

    monkeypatch.setattr(mod, "generate_chat", lambda *args, **kwargs: "Summary\nKey Points\nContext\nImplications")
    headlines = [
        {"title": "Updates on war in the region", "source": "Reuters", "url": "u1"},
        {"title": "Sports roundup", "source": "AP", "url": "u2"},
    ]
    executor = mod.NewsIntelligenceExecutor()
    result = executor.execute_summary(
        _request(49, {"selection": "topic", "topic_query": "war", "headlines": headlines})
    )
    assert result.success is True
    assert "war in the region" in result.message.lower()


def test_summary_filters_by_category(monkeypatch):
    from src.executors import news_intelligence_executor as mod

    monkeypatch.setattr(
        mod,
        "generate_chat",
        lambda *args, **kwargs: "The article explains a policy update and why it matters right now.",
    )
    headlines = [{"title": "General headline", "source": "Reuters", "url": "u1"}]
    categories = {
        "tech": {
            "title": "Tech News",
            "items": [
                {
                    "title": "Chip roadmap expands",
                    "source": "The Verge",
                    "url": "https://example.com/tech-1",
                    "summary": "Vendors expanded long-term AI chip roadmaps.",
                    "video_url": "https://video.example.com/tech-1.mp4",
                }
            ],
        }
    }
    executor = mod.NewsIntelligenceExecutor()
    result = executor.execute_summary(
        _request(
            49,
            {
                "selection": "category",
                "category_key": "tech",
                "headlines": headlines,
                "categories": categories,
            },
        )
    )
    assert result.success is True
    assert "CATEGORY SUMMARY - Tech News" in result.message
    assert "Video: https://video.example.com/tech-1.mp4" in result.message


def test_summary_uses_source_page_excerpt_when_network_available(monkeypatch):
    from src.executors import news_intelligence_executor as mod

    prompts: list[str] = []

    def _fake_generate(prompt, **kwargs):
        prompts.append(prompt)
        return "The article says exports tightened after new policy guidance."

    monkeypatch.setattr(mod, "generate_chat", _fake_generate)

    class _FakeNetwork:
        def request(self, capability_id, method, url, **kwargs):
            del capability_id, method, url, kwargs
            return {
                "status_code": 200,
                "text": "<html><body><p>Exports tightened after policy guidance from regulators.</p></body></html>",
            }

    headlines = [
        {
            "title": "Export policy shifts",
            "source": "Reuters",
            "url": "https://example.com/policy",
            "summary": "Initial headline synopsis.",
        }
    ]
    executor = mod.NewsIntelligenceExecutor(network=_FakeNetwork())
    result = executor.execute_summary(_request(49, {"indices": [1], "headlines": headlines}))
    assert result.success is True
    assert prompts
    assert "Article excerpt (source-page read):" in prompts[0]


def test_summary_all_includes_related_story_comparison(monkeypatch):
    from src.executors import news_intelligence_executor as mod

    monkeypatch.setattr(
        mod,
        "generate_chat",
        lambda *args, **kwargs: "The headline describes a major geopolitical development with limited confirmed detail.",
    )
    headlines = [
        {"title": "Oil prices surge over Iran war fears", "source": "BBC News", "url": "u1"},
        {"title": "U.S. strike video in Iran triggers global response", "source": "NPR", "url": "u2"},
        {"title": "Local sports roundup", "source": "AP", "url": "u3"},
    ]
    executor = mod.NewsIntelligenceExecutor()
    result = executor.execute_summary(_request(49, {"selection": "all", "headlines": headlines}))
    assert result.success is True
    assert "HEADLINE-BY-HEADLINE SUMMARY" in result.message
    assert "Story 1" in result.message
    assert "RELATED STORY COMPARISON" in result.message
    assert isinstance(result.data, dict)
    assert isinstance(result.data.get("related_pairs"), list)


def test_summary_compare_indices_action():
    from src.executors.news_intelligence_executor import NewsIntelligenceExecutor

    headlines = [
        {"title": "Oil prices surge over Iran war fears", "source": "BBC News", "url": "u1"},
        {"title": "U.S. strike video in Iran triggers global response", "source": "NPR", "url": "u2"},
    ]
    executor = NewsIntelligenceExecutor()
    result = executor.execute_summary(
        _request(49, {"action": "compare_indices", "left_index": 1, "right_index": 2, "headlines": headlines})
    )
    assert result.success is True
    assert "HEADLINE COMPARISON - Story 1 vs Story 2" in result.message
    assert "Shared terms" in result.message


def test_story_page_summary_reads_article_page(monkeypatch):
    from src.executors import news_intelligence_executor as mod

    monkeypatch.setattr(
        mod,
        "generate_chat",
        lambda *args, **kwargs: (
            "Article Summary\nExports tightened after policy guidance.\n\n"
            "Key Facts\n- Regulators expanded controls.\n\n"
            "Why It Matters\nSupply risk increased."
        ),
    )

    class _FakeNetwork:
        def request(self, capability_id, method, url, **kwargs):
            del capability_id, method, kwargs
            return {
                "status_code": 200,
                "text": f"<html><body><h1>{url}</h1><p>Regulators expanded export controls overnight.</p></body></html>",
            }

    headlines = [
        {"title": "Export controls tightened", "source": "Reuters", "url": "https://example.com/a"},
        {"title": "Secondary story", "source": "BBC", "url": "https://example.com/b"},
    ]
    executor = mod.NewsIntelligenceExecutor(network=_FakeNetwork())
    result = executor.execute_summary(
        _request(49, {"action": "story_page_summary", "story_index": 1, "headlines": headlines})
    )
    assert result.success is True
    assert "STORY PAGE SUMMARY - Story 1" in result.message
    assert "Reference: https://example.com/a" in result.message
    assert isinstance(result.data, dict)
    assert result.speakable_text.startswith("Story page summary ready for story 1.")
    assert result.structured_data["widget"]["type"] == "news_summary"
    assert int(result.data.get("story_index") or 0) == 1


def test_story_page_summary_fails_when_source_page_unavailable():
    from src.executors.news_intelligence_executor import NewsIntelligenceExecutor

    headlines = [
        {"title": "Export controls tightened", "source": "Reuters", "url": "https://example.com/a"},
    ]
    executor = NewsIntelligenceExecutor(network=None)
    result = executor.execute_summary(
        _request(49, {"action": "story_page_summary", "story_index": 1, "headlines": headlines})
    )
    assert result.success is False
    assert "couldn't read the article page" in result.message.lower()


def test_summary_includes_published_timestamp(monkeypatch):
    from src.executors import news_intelligence_executor as mod

    monkeypatch.setattr(
        mod,
        "generate_chat",
        lambda *args, **kwargs: "The report says exports tightened after a policy update.",
    )
    headlines = [
        {
            "title": "Export policy shifts",
            "source": "Reuters",
            "url": "https://example.com/policy",
            "published": "Mon, 09 Mar 2026 01:00:00 GMT",
        }
    ]
    executor = mod.NewsIntelligenceExecutor()
    result = executor.execute_summary(_request(49, {"indices": [1], "headlines": headlines}))
    assert result.success is True
    assert "Published: 2026-03-09 01:00 UTC" in result.message


def test_headline_normalization_dedupes_sentences():
    from src.executors.news_intelligence_executor import NewsIntelligenceExecutor

    executor = NewsIntelligenceExecutor()
    item = {"title": "Policy update", "source": "Reuters", "published": ""}
    normalized = executor._normalize_headline_summary(
        "Summary\nPolicy shifted overnight. Policy shifted overnight. Limited detail is available from the headline alone.",
        item,
    )
    assert normalized.count("Policy shifted overnight") == 1
    assert "Limited detail is available from the headline alone." in normalized


def test_brief_reads_source_pages_when_enabled(monkeypatch):
    from src.executors import news_intelligence_executor as mod

    monkeypatch.setattr(
        mod,
        "generate_chat",
        lambda *args, **kwargs: "Summary\nMerged from source pages.\n\nImplication\nCross-source alignment indicates elevated monitoring needs.",
    )

    class _FakeNetwork:
        def request(self, capability_id, method, url, **kwargs):
            return {
                "status_code": 200,
                "text": f"<html><body><h1>{url}</h1><p>Detail from source page for {url}.</p></body></html>",
            }

    headlines = [
        {"title": "A", "source": "ABC News", "url": "https://abc.example/a"},
        {"title": "B", "source": "BBC News", "url": "https://bbc.example/b"},
    ]
    executor = mod.NewsIntelligenceExecutor(network=_FakeNetwork())
    result = executor.execute_brief(_request(50, {"headlines": headlines, "read_sources": True}))
    assert result.success is True
    assert "NOVA DAILY INTELLIGENCE BRIEF" in result.message
    assert "Major Themes Today" in result.message
    assert "Story 1:" in result.message
    assert isinstance(result.data, dict)
    assert isinstance(result.data.get("sources"), list)
    assert len(result.data.get("sources")) == 2
    assert isinstance(result.data.get("brief_clusters"), list)
    assert len(result.data.get("brief_clusters")) >= 1


def test_brief_uses_cluster_fallback_when_source_synthesis_is_unavailable(monkeypatch):
    from src.executors import news_intelligence_executor as mod

    monkeypatch.setattr(mod, "generate_chat", lambda *args, **kwargs: "")

    class _FakeNetwork:
        def request(self, capability_id, method, url, **kwargs):
            return {
                "status_code": 200,
                "text": f"<html><body><h1>{url}</h1><p>Detail from source page for {url}.</p></body></html>",
            }

    headlines = [
        {"title": "AI chip roadmap", "source": "ABC News", "url": "https://abc.example/a"},
        {"title": "AI export policy", "source": "BBC News", "url": "https://bbc.example/b"},
    ]
    executor = mod.NewsIntelligenceExecutor(network=_FakeNetwork())
    result = executor.execute_brief(_request(50, {"headlines": headlines, "read_sources": True}))
    assert result.success is True
    assert "NOVA DAILY INTELLIGENCE BRIEF" in result.message
    assert "[Fallback]" in result.message
    assert "placeholder source-grounded summaries" in result.message
    assert isinstance(result.data, dict)
    assert isinstance(result.data.get("brief_clusters"), list)
    assert len(result.data.get("brief_clusters")) >= 1
    assert result.data["brief_clusters"][0]["summary"].startswith("[Fallback]")
    assert result.data["brief_clusters"][0]["implication"] == (
        "Treat this as a placeholder and review the linked source pages directly."
    )
    assert result.data["widget"]["data"]["placeholder_cluster_count"] >= 1
    assert result.data["widget"]["data"]["omitted_cluster_count"] == 0


def test_brief_followup_actions_expand_compare_track():
    from src.executors import news_intelligence_executor as mod

    executor = mod.NewsIntelligenceExecutor()
    clusters = [
        {
            "id": 1,
            "title": "Technology",
            "summary": "AI infrastructure competition is intensifying.",
            "implication": "Capacity planning may shift.",
            "sources": ["ABC News", "BBC News"],
            "items": [{"title": "AI chip roadmap", "source": "ABC News"}],
        },
        {
            "id": 2,
            "title": "Global Security",
            "summary": "Regional tensions remain elevated.",
            "implication": "Risk posture may tighten.",
            "sources": ["Reuters"],
            "items": [{"title": "Regional escalation warning", "source": "Reuters"}],
        },
    ]

    expanded = executor.execute_brief(_request(50, {"action": "expand_cluster", "story_id": 1, "brief_clusters": clusters}))
    assert expanded.success is True
    assert "Story 1: Technology" in expanded.message

    compared = executor.execute_brief(
        _request(50, {"action": "compare_clusters", "left_story_id": 1, "right_story_id": 2, "brief_clusters": clusters})
    )
    assert compared.success is True
    assert "Comparison: Story 1 vs Story 2" in compared.message

    tracked = executor.execute_brief(_request(50, {"action": "track_cluster", "story_id": 2, "brief_clusters": clusters}))
    assert tracked.success is True
    assert tracked.data["track_topic"] == "Global Security"
