from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from tests._dashboard_bundle import (
    load_dashboard_runtime_css,
    load_dashboard_runtime_js,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def _extract_js_function(source: str, name: str) -> str:
    start = source.index(f"function {name}")
    brace_start = source.index("{", start)
    depth = 0
    for idx in range(brace_start, len(source)):
        char = source[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start : idx + 1]
    raise AssertionError(f"Could not extract function {name}")


def _extract_js_object_const(source: str, name: str) -> str:
    start = source.index(f"const {name} = ")
    end = source.index("\n};", start) + 3
    return source[start:end]


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


def test_trust_center_receipts_surface_includes_read_only_detail_fields():
    source = INDEX_PATH.read_text(encoding="utf-8")
    dashboard = load_dashboard_runtime_js()

    assert 'id="trust-center-receipts"' in source
    assert 'id="trust-center-receipt-detail"' in source
    assert "trustReviewState.receipts" in dashboard
    assert "selectedReceiptKey" in dashboard
    assert "Capability" in dashboard
    assert "Execution status" in dashboard
    assert "Approval required" in dashboard
    assert "Source path" in dashboard
    assert "Select a receipt to see how a governed request moved from user intent to capability execution and into the ledger." in dashboard
    assert "No governed actions recorded yet. Governed actions appear here after they run." in dashboard


def test_trust_center_receipts_renderer_stays_display_only():
    source = load_dashboard_runtime_js()
    match = re.search(
        r"function _renderReceiptRows\(host\) \{(?P<body>.*?)\n\}\n\nfunction _renderReceiptDetail",
        source,
        flags=re.DOTALL,
    )
    assert match is not None
    body = match.group("body")

    assert 'textContent = `Path: ${sourcePath}`;' in body
    assert "safeWSSend" not in body
    assert "injectUserText" not in body
    assert "setActivePage" not in body
    assert "GovernorMediator" not in body
    assert "OpenClaw" not in body
    assert "approve" not in body.lower()


def test_trust_center_receipts_preserve_action_outcome_truth_matrix():
    source = load_dashboard_runtime_js()
    styles = load_dashboard_runtime_css()
    node = os.environ.get("NODE_EXE") or shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for the Trust Center receipt outcome regression")

    blocks = [
        _extract_js_object_const(source, "_RECEIPT_LABELS"),
        _extract_js_object_const(source, "_RECEIPT_OUTCOME"),
        _extract_js_object_const(source, "_OUTCOME_LABEL"),
        _extract_js_object_const(source, "_RECEIPT_BOUNDARY"),
        _extract_js_function(source, "_receiptOutcomeState"),
        _extract_js_function(source, "_receiptActionFailureState"),
        _extract_js_function(source, "_receiptLabel"),
        _extract_js_function(source, "_receiptOutcomeKey"),
        _extract_js_function(source, "_receiptBoundary"),
        _extract_js_function(source, "_receiptExecutionStatus"),
        _extract_js_function(source, "_receiptOutcomeLabel"),
    ]
    script = "\n".join(blocks) + """
const cases = [
  {
    name: "visible verified",
    receipt: { event_type: "ACTION_COMPLETED", status: "completed", success: true, outcome_state: "visible_verified" },
    label: "Action completed",
    outcomeKey: "done",
    outcomeLabel: "Done",
    status: "completed",
    boundary: "",
  },
  {
    name: "accepted unverified",
    receipt: { event_type: "ACTION_COMPLETED", status: "completed", success: true, outcome_state: "accepted_unverified" },
    label: "Action accepted; outcome unverified",
    outcomeKey: "unverified",
    outcomeLabel: "Outcome unverified",
    status: "accepted_unverified",
    boundary: "Request accepted; visible outcome not verified",
  },
  {
    name: "unknown unverified",
    receipt: { event_type: "ACTION_COMPLETED", status: "failed", success: false, outcome_state: "unknown_unverified" },
    label: "Action outcome unknown; not verified",
    outcomeKey: "unverified",
    outcomeLabel: "Outcome unverified",
    status: "unknown_unverified",
    boundary: "Dispatch may have begun; visible outcome not verified",
  },
  {
    name: "rejected",
    receipt: { event_type: "ACTION_COMPLETED", status: "failed", success: false, outcome_state: "rejected" },
    label: "Action rejected",
    outcomeKey: "failed",
    outcomeLabel: "Failed",
    status: "rejected",
    boundary: "Request rejected; intended effect did not occur",
  },
  {
    name: "rejected overrides generic success",
    receipt: { event_type: "ACTION_COMPLETED", status: "completed", success: true, outcome_state: "rejected" },
    label: "Action rejected",
    outcomeKey: "failed",
    outcomeLabel: "Failed",
    status: "rejected",
    boundary: "Request rejected; intended effect did not occur",
  },
  {
    name: "failed overrides generic success",
    receipt: { event_type: "ACTION_COMPLETED", status: "completed", success: true, outcome_state: "failed" },
    label: "Action failed",
    outcomeKey: "failed",
    outcomeLabel: "Failed",
    status: "failed",
    boundary: "Action reported failure; visible outcome not verified",
  },
  {
    name: "failed status overrides accepted unverified",
    receipt: { event_type: "ACTION_COMPLETED", status: "failed", success: true, outcome_state: "accepted_unverified" },
    label: "Action failed",
    outcomeKey: "failed",
    outcomeLabel: "Failed",
    status: "failed",
    boundary: "Action reported failure; visible outcome not verified",
  },
  {
    name: "failed success flag overrides visible verified",
    receipt: { event_type: "ACTION_COMPLETED", status: "completed", success: false, outcome_state: "visible_verified" },
    label: "Action failed",
    outcomeKey: "failed",
    outcomeLabel: "Failed",
    status: "failed",
    boundary: "Action reported failure; visible outcome not verified",
  },
  {
    name: "missing outcome state with failed status",
    receipt: { event_type: "ACTION_COMPLETED", status: "failed", success: false },
    label: "Action failed",
    outcomeKey: "failed",
    outcomeLabel: "Failed",
    status: "failed",
    boundary: "Action reported failure; visible outcome not verified",
  },
  {
    name: "legacy successful action completed",
    receipt: { event_type: "ACTION_COMPLETED", status: "completed", success: true },
    label: "Action completed",
    outcomeKey: "done",
    outcomeLabel: "Done",
    status: "completed",
    boundary: "",
  },
];
for (const testCase of cases) {
  const actual = {
    label: _receiptLabel(testCase.receipt),
    outcomeKey: _receiptOutcomeKey(testCase.receipt),
    outcomeLabel: _receiptOutcomeLabel(testCase.receipt),
    status: _receiptExecutionStatus(testCase.receipt),
    boundary: _receiptBoundary(testCase.receipt),
  };
  for (const field of ["label", "outcomeKey", "outcomeLabel", "status", "boundary"]) {
    if (actual[field] !== testCase[field]) {
      throw new Error(`${testCase.name} ${field}: expected ${testCase[field]}, got ${actual[field]}`);
    }
  }
}
"""
    subprocess.run([node, "-e", script], check=True)

    rows = _extract_js_function(source, "_renderReceiptRows")
    detail = _extract_js_function(source, "_renderReceiptDetail")
    assert "const label = _receiptLabel(r);" in rows
    assert "const outcome = _receiptOutcomeKey(r);" in rows
    assert "const boundary = _receiptBoundary(r);" in rows
    assert '["Receipt", _receiptLabel(selected) || "Unknown"]' in detail
    assert '["Boundary", _receiptBoundary(selected)' in detail
    assert ".trust-activity-outcome-unverified" in styles
    assert '.trust-activity-item[data-outcome="unverified"]' in styles


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
