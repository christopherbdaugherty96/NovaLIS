from src.rendering.intelligence_brief_renderer import IntelligenceBriefRenderer


def test_render_brief_contains_structured_sections():
    renderer = IntelligenceBriefRenderer()
    out = renderer.render_brief(
        [
            {"title": "AI regulation bill advances", "source": "Reuters", "summary": "Policy update on AI systems."},
            {"title": "Chip export rules tightened", "source": "AP", "summary": "Semiconductor policy changes."},
        ],
        analysis_text="Key Developments\n- Regulatory pressure increasing.",
    )
    assert "NOVA INTELLIGENCE BRIEF" in out
    assert "Daily Situation Overview" in out
    assert "Strategic Snapshot" in out
    assert "Cross-Story Insights" in out
    assert "Topic Clusters" in out
    assert "AI REGULATION" in out


def test_render_single_has_signal_line():
    renderer = IntelligenceBriefRenderer()
    out = renderer.render_single(
        {"title": "Inflation cools", "source": "NPR", "summary": "Economy shows easing pressure."},
        analysis_text="Context text.",
    )
    assert "DETAILED STORY ANALYSIS" in out
    assert "Signal" in out
    assert "Implication" in out
    assert "Watch" in out


def test_render_multi_source_report_sections():
    renderer = IntelligenceBriefRenderer()
    out = renderer.render_multi_source_report(
        query="ai regulation updates",
        findings=["AI regulation bill advances", "Senate hearing on AI policy"],
        sources=["abcnews.go.com", "reuters.com"],
        analysis_text="Regulatory cadence is increasing.",
    )
    assert "NOVA MULTI-SOURCE REPORT" in out
    assert "Strategic Snapshot" in out
    assert "Top Findings" in out
    assert "Cross-Story Insight" in out
    assert "Sources" in out


def test_render_structured_intelligence_brief_sections():
    renderer = IntelligenceBriefRenderer()
    out = renderer.render_structured_intelligence_brief(
        topic="Global AI Regulation Trends",
        summary="Governments are increasing regulatory oversight of AI systems.",
        key_findings=["EU AI Act uses risk tiers.", "US policy emphasizes voluntary frameworks."],
        supporting_sources=["ec.europa.eu", "whitehouse.gov"],
        contradictions=["Industry groups warn about innovation drag."],
        confidence=0.82,
    )
    assert "INTELLIGENCE BRIEF" in out
    assert "Topic: Global AI Regulation Trends" in out
    assert "Key Findings" in out
    assert "Supporting Sources" in out
    assert "Contradictions" in out
    assert "0.82" in out
