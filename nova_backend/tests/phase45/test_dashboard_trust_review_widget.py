from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_renders_trust_review_sections_from_system_status():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert "let trustReviewState" in source
    assert "function renderTrustPanel(data = {})" in source
    assert '"trust_review_summary"' in source or "trustReviewState.summary" in source
    assert '"recent_runtime_activity"' in source or "trustReviewState.activity" in source
    assert '"blocked_conditions"' in source or "trustReviewState.blocked" in source


def test_home_page_includes_trust_review_sections():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="trust-summary"' in source
    assert 'id="trust-recent-activity"' in source
    assert 'id="trust-blocked"' in source
    assert 'id="trust-note"' in source
