from pathlib import Path
import re

from tests._dashboard_bundle import load_dashboard_runtime_css


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_dashboard_uses_document_level_scrolling():
    source = load_dashboard_runtime_css()
    assert "html," in source
    assert "overflow-y: auto;" in source
    assert ".dashboard {" in source
    assert "min-height: 100vh;" in source
    assert ".page-view {" in source
    assert "overflow: visible;" in source


def test_news_surfaces_do_not_force_inner_scroll_regions():
    source = load_dashboard_runtime_css()
    news_list_blocks = re.findall(r"#news-list\s*\{([^}]*)\}", source, re.S)
    nav_blocks = re.findall(r"\.news-category-nav\s*\{([^}]*)\}", source, re.S)
    page_blocks = re.findall(r"\.news-category-page-card\s*\{([^}]*)\}", source, re.S)
    assert any("overflow: visible;" in block for block in news_list_blocks)
    assert any("overflow: visible;" in block for block in nav_blocks)
    assert any("overflow: visible;" in block for block in page_blocks)


def test_home_page_uses_responsive_document_level_grid():
    source = load_dashboard_runtime_css()
    assert ".page-home {" in source
    assert "grid-template-columns: repeat(12, minmax(0, 1fr));" in source
