from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"


def test_search_widget_buttons_use_supported_topic_followups():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert 'summarizeBtn.textContent = "Quick take";' in source
    assert 'compareBtn.textContent = "See wider coverage";' in source
    assert 'injectUserText(`research latest coverage of ${topic}`, "text")' in source
    assert "summarize this result:" not in source
    assert 'injectUserText("compare the top 3 search results", "text")' not in source
