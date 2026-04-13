from __future__ import annotations

from pathlib import Path

from tests._dashboard_bundle import load_dashboard_runtime_css, load_dashboard_runtime_js


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_header_uses_dropdown_menu_strip():
    index_source = INDEX_PATH.read_text(encoding="utf-8")
    dashboard_source = load_dashboard_runtime_js()
    style_source = load_dashboard_runtime_css()

    assert 'id="header-menu-strip"' in index_source
    assert "function injectHeaderMenus()" in dashboard_source
    assert "header-menu-page-btn" in dashboard_source
    assert ".header-menu-strip" in style_source
    assert ".header-menu-panel" in style_source


def test_news_page_exposes_search_and_source_grounded_article_actions():
    index_source = INDEX_PATH.read_text(encoding="utf-8")
    dashboard_source = load_dashboard_runtime_js()

    assert 'id="news-search-input"' in index_source
    assert 'id="btn-news-search"' in index_source
    assert 'id="btn-news-refresh"' in index_source
    assert "function runNewsSearch()" in dashboard_source
    assert 'injectUserText("today\'s news", "text")' in dashboard_source
    assert 'summary of article ${storyIndex}' in dashboard_source
    assert "requestInlineAssistantAction(`summary of article ${storyIndex}`" in dashboard_source
    assert "requestInlineAssistantAction(`summarize ${categoryKey} news`" in dashboard_source
    assert 'case "news_summary":' in dashboard_source
    assert 'latestNewsSummaryState = {' in dashboard_source


def test_news_page_uses_cleaner_category_language_and_inline_summary_surface():
    dashboard_source = load_dashboard_runtime_js()
    style_source = load_dashboard_runtime_css()

    assert '"global", "local", "politics", "tech", "crypto"' in dashboard_source
    assert 'requestInlineAssistantAction(`summarize ${categoryKey} news`' in dashboard_source
    assert ".news-inline-summary" in style_source
    assert ".news-inline-summary-body" in style_source
