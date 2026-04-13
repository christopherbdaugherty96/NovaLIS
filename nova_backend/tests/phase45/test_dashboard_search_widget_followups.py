from __future__ import annotations

from tests._dashboard_bundle import load_dashboard_runtime_js


def test_search_widget_buttons_use_supported_topic_followups():
    source = load_dashboard_runtime_js()

    assert 'summarizeBtn.textContent = "Quick take";' in source
    assert 'compareBtn.textContent = "See wider coverage";' in source
    assert 'injectUserText(`research latest coverage of ${topic}`, "text")' in source
    assert "summarize this result:" not in source
    assert 'injectUserText("compare the top 3 search results", "text")' not in source
