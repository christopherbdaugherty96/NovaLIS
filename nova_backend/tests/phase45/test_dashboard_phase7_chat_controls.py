from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"


def test_chat_input_exposes_deepseek_second_opinion_button():
    index_source = INDEX_PATH.read_text(encoding="utf-8")
    dashboard_source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert 'id="deepseek-btn"' in index_source
    assert "Second opinion" in index_source
    assert "function requestDeepSeekSecondOpinion()" in dashboard_source
    assert 'appendChatMessage("user", "Second opinion")' in dashboard_source
    assert 'safeWSSend({ text: "second opinion", invocation_source: "deepseek_button" }' in dashboard_source
