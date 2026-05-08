from __future__ import annotations

import re
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


def test_chat_trust_review_card_renders_deterministic_non_action_fields():
    source = load_dashboard_runtime_js()
    styles = load_dashboard_runtime_css()

    assert "function renderTrustReviewCard(parent, card = null)" in source
    assert 'panel.setAttribute("aria-label", "Trust Review Card");' in source
    assert '["Understood", goal || requestText]' in source
    assert '["Status", status]' in source
    assert '["Authorized", authorizationGranted ? "Yes" : "No"]' in source
    assert '["Needs confirmation", "Not granted by this card"]' in source
    assert '["Why no action happened", whyNoAction]' in source
    assert "This card is display-only; no execution was performed or authorized." in source
    assert ".trust-review-card" in styles
    assert ".trust-review-card-row" in styles


def test_chat_trust_review_card_has_no_dispatch_or_action_controls():
    source = load_dashboard_runtime_js()
    match = re.search(
        r"function renderTrustReviewCard\(parent, card = null\) \{(?P<body>.*?)\n\}\n\nfunction appendUsageStrip",
        source,
        flags=re.DOTALL,
    )
    assert match is not None
    body = match.group("body")

    assert 'createElement("button")' not in body
    assert "addEventListener" not in body
    assert "safeWSSend" not in body
    assert "injectUserText" not in body
    assert "setActivePage" not in body
    assert "appendAssistantActions" not in body


def test_chat_payload_passes_trust_review_card_to_display_renderer():
    source = load_dashboard_runtime_js()

    assert "trustReviewCard = null" in source
    assert "renderTrustReviewCard(div, trustReviewCard);" in source
    assert "msg.trust_review_card || null" in source
