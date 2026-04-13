from __future__ import annotations

from pathlib import Path

from tests._dashboard_bundle import load_dashboard_runtime_js


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_renders_policy_center_page_and_widget_flow():
    source = load_dashboard_runtime_js()

    assert "function requestPolicyOverviewRefresh(force = false)" in source
    assert "function requestPolicyDetail(policyId)" in source
    assert "function getPolicyReadinessBuckets(snapshot = {})" in source
    assert "function renderPolicyCenterPage()" in source
    assert 'case "policy_overview":' in source
    assert 'case "policy_item":' in source
    assert 'case "policy_simulation":' in source
    assert 'case "policy_run":' in source
    assert 'safeWSSend({ text: "policy overview", silent_widget_refresh: true });' in source
    assert 'safeWSSend({ text: "what can policies run", silent_widget_refresh: true });' in source
    assert 'page: "policy"' in source
    assert 'setActivePage("settings")' in source
    assert 'btn-policy-create-status' in source
    assert 'btn-policy-capability-map' in source


def test_policy_page_includes_review_surfaces_and_actions():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="page-policy"' in source
    assert 'id="policy-center-summary"' in source
    assert 'id="policy-center-stats"' in source
    assert 'id="policy-center-readiness-summary"' in source
    assert 'id="policy-center-readiness-limit"' in source
    assert 'id="policy-center-readiness"' in source
    assert 'id="policy-center-list"' in source
    assert 'id="policy-center-detail"' in source
    assert 'id="policy-center-simulation"' in source
    assert 'id="policy-center-run"' in source
    assert 'id="btn-policy-refresh"' in source
    assert 'id="btn-policy-create-calendar"' in source
    assert 'id="btn-policy-create-weather"' in source
    assert 'id="btn-policy-create-status"' in source
    assert 'id="btn-policy-capability-map"' in source
    assert 'id="btn-policy-open-trust"' in source
    assert 'id="btn-policy-open-settings"' in source
