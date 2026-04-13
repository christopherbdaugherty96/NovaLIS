from __future__ import annotations

from pathlib import Path

from tests._dashboard_bundle import load_dashboard_runtime_js


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_handles_structured_intelligence_brief_widget_messages():
    source = load_dashboard_runtime_js()

    assert "let latestBriefWidgetState" in source
    assert "function renderIntelligenceBriefWidget(data = {})" in source
    assert 'case "intelligence_brief":' in source
    assert "renderIntelligenceBriefWidget(msg.data || {});" in source
    assert '"placeholder_cluster_count"' in source or "placeholderClusterCount" in source
    assert '"omitted_cluster_count"' in source or "omittedClusterCount" in source
    assert "updateNewsSummary(summaryText);" in source


def test_news_page_includes_dedicated_brief_surface():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="brief-widget"' in source
    assert 'id="brief-grounding-badge"' in source
    assert 'id="brief-summary"' in source
    assert 'id="brief-stats"' in source
    assert 'id="brief-grounding-note"' in source
    assert 'id="brief-sidebar-empty"' in source
    assert 'id="brief-sidebar-cards"' in source
