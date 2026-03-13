from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[3]
STYLE_PATH = PROJECT_ROOT / "nova_backend" / "static" / "style.phase1.css"


def test_dashboard_uses_document_level_scrolling():
    source = STYLE_PATH.read_text(encoding="utf-8")
    assert "html," in source
    assert "overflow-y: auto;" in source
    assert ".dashboard {" in source
    assert "min-height: 100vh;" in source
    assert ".page-view {" in source
    assert "overflow: visible;" in source


def test_news_surfaces_do_not_force_inner_scroll_regions():
    source = STYLE_PATH.read_text(encoding="utf-8")
    news_list_block = re.search(r"#news-list\s*\{([^}]*)\}", source, re.S)
    nav_block = re.search(r"\.news-category-nav\s*\{([^}]*)\}", source, re.S)
    page_block = re.search(r"\.news-category-page-card\s*\{([^}]*)\}", source, re.S)
    assert news_list_block and "overflow: visible;" in news_list_block.group(1)
    assert nav_block and "overflow: visible;" in nav_block.group(1)
    assert page_block and "overflow: visible;" in page_block.group(1)


def test_home_page_uses_item_alignment_for_scrollable_stack():
    source = STYLE_PATH.read_text(encoding="utf-8")
    assert ".page-home {" in source
    assert "justify-items: end;" in source
