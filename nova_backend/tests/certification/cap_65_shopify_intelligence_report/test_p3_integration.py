# tests/certification/cap_65_shopify_intelligence_report/test_p3_integration.py
"""
Phase 3 — Integration certification for capability 65 (shopify_intelligence_report).

Tests the FULL Governor spine:
  GovernorMediator → CapabilityRegistry → ExecuteBoundary
  → LedgerWriter → ShopifyIntelligenceReportExecutor → ActionResult

The connector's outbound Shopify API calls are mocked. Two execution paths
are tested: connector not configured (safe refusal) and connector configured
with a mocked store snapshot.
"""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.governor.governor import Governor
from src.connectors.shopify_connector import (
    ShopifyOrderSummary,
    ShopifyProductSummary,
    ShopifyStoreSnapshot,
)


_CAPABILITY_ID = 65
_CAPABILITY_NAME = "shopify_intelligence_report"

_BASE_PARAMS: dict[str, Any] = {
    "period": "last_7_days",
    "market_context": "integration test",
    "low_stock_threshold": 5,
}


def _make_snapshot() -> ShopifyStoreSnapshot:
    orders = ShopifyOrderSummary(
        order_count=42,
        total_revenue="1,234.56",
        currency="USD",
        average_order_value="29.39",
        period_label="last_7_days",
        fetched_at="2026-04-25T00:00:00+00:00",
    )
    products = ShopifyProductSummary(
        total_products=10,
        active_products=8,
        draft_products=2,
        out_of_stock_count=0,
        low_stock_count=1,
        fetched_at="2026-04-25T00:00:00+00:00",
    )
    return ShopifyStoreSnapshot(
        shop_domain="test.myshopify.com",
        shop_name="Test Store",
        orders=orders,
        products=products,
        fetched_at="2026-04-25T00:00:00+00:00",
    )


def _make_governor() -> Governor:
    return Governor()


def _make_mock_connector() -> MagicMock:
    connector = MagicMock()
    connector.fetch_store_snapshot = AsyncMock(return_value=_make_snapshot())
    return connector


# ---------------------------------------------------------------------------
# Registry / capability checks
# ---------------------------------------------------------------------------

def test_cap_65_is_registered():
    gov = _make_governor()
    cap = gov.registry.get(_CAPABILITY_ID)
    assert cap is not None
    assert cap.name == _CAPABILITY_NAME


def test_cap_65_is_enabled():
    gov = _make_governor()
    assert gov.registry.is_enabled(_CAPABILITY_ID) is True


def test_cap_65_authority_class():
    gov = _make_governor()
    cap = gov.registry.get(_CAPABILITY_ID)
    assert str(cap.authority_class) == "read_only_network"


def test_cap_65_has_external_effect():
    gov = _make_governor()
    cap = gov.registry.get(_CAPABILITY_ID)
    assert cap.external_effect is True


def test_cap_65_does_not_require_confirmation():
    gov = _make_governor()
    cap = gov.registry.get(_CAPABILITY_ID)
    assert cap.requires_confirmation is False


# ---------------------------------------------------------------------------
# Connector not configured — safe refusal path
# ---------------------------------------------------------------------------

def test_not_configured_returns_refusal():
    """When the Shopify connector is not set up, governor returns a clean refusal."""
    gov = _make_governor()
    with patch("src.executors.shopify_intelligence_report_executor.is_shopify_connected", return_value=False):
        result = gov.handle_governed_invocation(_CAPABILITY_ID, _BASE_PARAMS)
    assert result.success is False
    assert "shopify" in result.message.lower() or "connector" in result.message.lower()


def test_not_configured_refusal_is_not_exception():
    """Refusal must be a structured ActionResult, not an unhandled exception."""
    gov = _make_governor()
    with patch("src.executors.shopify_intelligence_report_executor.is_shopify_connected", return_value=False):
        result = gov.handle_governed_invocation(_CAPABILITY_ID, _BASE_PARAMS)
    assert hasattr(result, "success")
    assert hasattr(result, "message")


# ---------------------------------------------------------------------------
# Connector configured — happy path through full spine
# ---------------------------------------------------------------------------

def test_configured_connector_passes_through_spine():
    gov = _make_governor()
    connector = _make_mock_connector()
    with (
        patch("src.executors.shopify_intelligence_report_executor.is_shopify_connected", return_value=True),
        patch("src.executors.shopify_intelligence_report_executor.get_shopify_connector", return_value=connector),
    ):
        result = gov.handle_governed_invocation(_CAPABILITY_ID, _BASE_PARAMS)
    assert result.success is True


def test_result_authority_class_is_read_only_network():
    gov = _make_governor()
    connector = _make_mock_connector()
    with (
        patch("src.executors.shopify_intelligence_report_executor.is_shopify_connected", return_value=True),
        patch("src.executors.shopify_intelligence_report_executor.get_shopify_connector", return_value=connector),
    ):
        result = gov.handle_governed_invocation(_CAPABILITY_ID, _BASE_PARAMS)
    assert result.authority_class == "read_only_network"


def test_result_external_effect_is_true():
    gov = _make_governor()
    connector = _make_mock_connector()
    with (
        patch("src.executors.shopify_intelligence_report_executor.is_shopify_connected", return_value=True),
        patch("src.executors.shopify_intelligence_report_executor.get_shopify_connector", return_value=connector),
    ):
        result = gov.handle_governed_invocation(_CAPABILITY_ID, _BASE_PARAMS)
    assert result.external_effect is True


def test_result_reversible_is_true():
    gov = _make_governor()
    connector = _make_mock_connector()
    with (
        patch("src.executors.shopify_intelligence_report_executor.is_shopify_connected", return_value=True),
        patch("src.executors.shopify_intelligence_report_executor.get_shopify_connector", return_value=connector),
    ):
        result = gov.handle_governed_invocation(_CAPABILITY_ID, _BASE_PARAMS)
    assert result.reversible is True


def test_result_has_request_id():
    gov = _make_governor()
    connector = _make_mock_connector()
    with (
        patch("src.executors.shopify_intelligence_report_executor.is_shopify_connected", return_value=True),
        patch("src.executors.shopify_intelligence_report_executor.get_shopify_connector", return_value=connector),
    ):
        result = gov.handle_governed_invocation(_CAPABILITY_ID, _BASE_PARAMS)
    assert result.request_id is not None and len(result.request_id) > 0


# ---------------------------------------------------------------------------
# Ledger events
# ---------------------------------------------------------------------------

def test_spine_logs_action_attempted():
    gov = _make_governor()
    logged: list[str] = []
    original = gov.ledger.log_event

    def _capture(event_type, payload):
        logged.append(event_type)
        return original(event_type, payload)

    gov.ledger.log_event = _capture
    connector = _make_mock_connector()
    with (
        patch("src.executors.shopify_intelligence_report_executor.is_shopify_connected", return_value=True),
        patch("src.executors.shopify_intelligence_report_executor.get_shopify_connector", return_value=connector),
    ):
        gov.handle_governed_invocation(_CAPABILITY_ID, _BASE_PARAMS)
    assert "ACTION_ATTEMPTED" in logged


def test_spine_logs_action_completed():
    gov = _make_governor()
    logged: list[str] = []
    original = gov.ledger.log_event

    def _capture(event_type, payload):
        logged.append(event_type)
        return original(event_type, payload)

    gov.ledger.log_event = _capture
    connector = _make_mock_connector()
    with (
        patch("src.executors.shopify_intelligence_report_executor.is_shopify_connected", return_value=True),
        patch("src.executors.shopify_intelligence_report_executor.get_shopify_connector", return_value=connector),
    ):
        gov.handle_governed_invocation(_CAPABILITY_ID, _BASE_PARAMS)
    assert "ACTION_COMPLETED" in logged


# ---------------------------------------------------------------------------
# Period normalization
# ---------------------------------------------------------------------------

def test_invalid_period_is_normalized_to_default():
    """An unrecognized period must not crash — executor normalizes to last_7_days."""
    gov = _make_governor()
    connector = _make_mock_connector()
    with (
        patch("src.executors.shopify_intelligence_report_executor.is_shopify_connected", return_value=True),
        patch("src.executors.shopify_intelligence_report_executor.get_shopify_connector", return_value=connector),
    ):
        result = gov.handle_governed_invocation(_CAPABILITY_ID, {**_BASE_PARAMS, "period": "not_a_valid_period"})
    assert result.success is True


# ---------------------------------------------------------------------------
# Governance fence — unrelated capabilities unaffected
# ---------------------------------------------------------------------------

def test_unknown_capability_still_refused():
    gov = _make_governor()
    result = gov.handle_governed_invocation(9999, {})
    assert result.success is False
