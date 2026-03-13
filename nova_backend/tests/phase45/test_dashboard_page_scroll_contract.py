from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
STYLE_PATH = PROJECT_ROOT / "nova_backend" / "static" / "style.phase1.css"


def test_page_views_are_scrollable_within_main_shell():
    source = STYLE_PATH.read_text(encoding="utf-8")
    assert ".main {" in source
    assert "overflow: hidden;" in source
    assert ".page-view {" in source
    assert "overflow-y: auto;" in source
    assert "overflow-x: hidden;" in source


def test_home_page_uses_item_alignment_for_scrollable_stack():
    source = STYLE_PATH.read_text(encoding="utf-8")
    assert ".page-home {" in source
    assert "justify-items: end;" in source
