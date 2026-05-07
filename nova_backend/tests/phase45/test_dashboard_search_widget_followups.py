from __future__ import annotations

from tests._dashboard_bundle import load_dashboard_runtime_css, load_dashboard_runtime_js


def test_search_widget_buttons_use_supported_topic_followups():
    source = load_dashboard_runtime_js()

    assert 'summarizeBtn.textContent = "Quick take";' in source
    assert 'compareBtn.textContent = "See wider coverage";' in source
    assert 'injectUserText(`research latest coverage of ${topic}`, "text")' in source
    assert "summarize this result:" not in source
    assert 'injectUserText("compare the top 3 search results", "text")' not in source


def test_search_widget_renders_evidence_status_metadata():
    source = load_dashboard_runtime_js()

    assert "function appendSearchEvidencePanel(container, evidence)" in source
    assert 'title.textContent = "Evidence state";' in source
    assert "`Provider: ${formatEvidenceLabel(evidence.provider_status)}`" in source
    assert "`Freshness: ${formatEvidenceLabel(evidence.freshness_status)}`" in source
    assert "`Source signals: ${sourceCredibility.length}`" in source
    assert "search-credibility-row" in source


def test_search_widget_keeps_degraded_empty_search_visible():
    source = load_dashboard_runtime_js()

    assert "if (!results.length && !structuredReport && !hasVisibleSearchEvidence(evidence))" in source
    assert 'quickAnswerTitle.textContent = results.length ? "Quick answer" : "Search state";' in source
    assert "No reliable results are currently available for this search." in source


def test_search_evidence_panel_has_visible_degraded_state_styles():
    css = load_dashboard_runtime_css()

    assert ".search-evidence-panel" in css
    assert ".search-evidence-title" in css
    assert ".search-credibility-row" in css
