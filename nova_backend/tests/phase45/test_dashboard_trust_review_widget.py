from __future__ import annotations

from pathlib import Path

from tests._dashboard_bundle import load_dashboard_runtime_css, load_dashboard_runtime_js


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_renders_trust_review_sections_from_system_status():
    source = load_dashboard_runtime_js()

    assert "let trustReviewState" in source
    assert "function renderTrustPanel(data = {})" in source
    assert '"trust_review_summary"' in source or "trustReviewState.summary" in source
    assert '"recent_runtime_activity"' in source or "trustReviewState.activity" in source
    assert '"blocked_conditions"' in source or "trustReviewState.blocked" in source
    assert '"policy_capability_readiness"' in source or "trustReviewState.policyReadiness" in source
    assert "selectedPolicyCapabilityKey" in source


def test_dashboard_refreshes_trust_review_from_trust_status_messages():
    source = load_dashboard_runtime_js()

    assert 'case "trust_status":' in source
    assert "renderTrustPanel(msg.data || {});" in source


def test_dashboard_trust_review_surface_marks_activity_outcomes():
    source = load_dashboard_runtime_js()
    styles = load_dashboard_runtime_css()

    assert "item.outcome" in source
    assert "trust-activity-outcome" in source
    assert '.trust-activity-item[data-outcome="issue"]' in styles
    assert "item.reason" in source
    assert "item.effect" in source
    assert "item.request_id" in source
    assert "item.ledger_ref" in source
    assert ".trust-activity-correlation" in styles


def test_home_page_includes_trust_review_sections():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="page-trust"' in source
    assert 'id="trust-center-summary"' in source
    assert 'id="trust-center-activity"' in source
    assert 'id="trust-center-blocked"' in source
    assert 'id="trust-center-assistive-list"' in source


def test_trust_center_page_includes_policy_readiness_sections():
    source = INDEX_PATH.read_text(encoding="utf-8")
    dashboard = load_dashboard_runtime_js()

    assert 'id="btn-trust-center-policy-map"' in source
    assert 'id="trust-center-policy-summary"' in source
    assert 'id="trust-center-policy-limit"' in source
    assert 'id="trust-center-policy-groups"' in source
    assert 'id="trust-center-policy-detail"' in source
    assert "selectedBlocked.next_step" in dashboard
    assert "selected.capability_name" in dashboard or "selected.capability_id" in dashboard
