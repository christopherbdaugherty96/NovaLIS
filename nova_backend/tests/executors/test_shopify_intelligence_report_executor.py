"""Unit tests for ShopifyIntelligenceReportExecutor (capability 65 — P1)."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.actions.action_result import ActionResult
from src.connectors.shopify_connector import (
    ShopifyConnectorError,
    ShopifyOrderSummary,
    ShopifyProductSummary,
    ShopifyStoreSnapshot,
)
from src.executors.shopify_intelligence_report_executor import ShopifyIntelligenceReportExecutor


def _req(params: dict | None = None, request_id: str = "req-shopify-1"):
    return SimpleNamespace(params=params or {}, request_id=request_id)


def _make_snapshot(
    period: str = "last_7_days",
    order_count: int = 42,
    total_revenue: str = "12,450.00",
    currency: str = "USD",
    active_products: int = 10,
    error: str = "",
) -> ShopifyStoreSnapshot:
    return ShopifyStoreSnapshot(
        shop_domain="mystore.myshopify.com",
        shop_name="My Store",
        orders=ShopifyOrderSummary(
            order_count=order_count,
            total_revenue=total_revenue,
            currency=currency,
            average_order_value="296.43",
            period_label=period,
            fetched_at="2026-04-21T00:00:00+00:00",
        ),
        products=ShopifyProductSummary(
            total_products=12,
            active_products=active_products,
            draft_products=2,
            out_of_stock_count=1,
            low_stock_count=3,
            fetched_at="2026-04-21T00:00:00+00:00",
        ),
        fetched_at="2026-04-21T00:00:00+00:00",
        error=error,
    )


class TestShopifyNotConfigured:
    def test_returns_refusal_when_not_connected(self):
        with patch("src.executors.shopify_intelligence_report_executor.is_shopify_connected", return_value=False):
            result = ShopifyIntelligenceReportExecutor().execute(_req())
        assert result.success is False
        assert "not configured" in result.message.lower()

    def test_refusal_has_correct_capability_id(self):
        with patch("src.executors.shopify_intelligence_report_executor.is_shopify_connected", return_value=False):
            result = ShopifyIntelligenceReportExecutor().execute(_req())
        assert result.capability_id == 65

    def test_refusal_mentions_env_vars(self):
        with patch("src.executors.shopify_intelligence_report_executor.is_shopify_connected", return_value=False):
            result = ShopifyIntelligenceReportExecutor().execute(_req())
        assert "NOVA_SHOPIFY" in result.message


class TestShopifyConnectorError:
    def _patch_connected(self, mock_connector):
        return patch.multiple(
            "src.executors.shopify_intelligence_report_executor",
            is_shopify_connected=MagicMock(return_value=True),
            get_shopify_connector=MagicMock(return_value=mock_connector),
        )

    def test_connector_error_returns_refusal(self):
        connector = MagicMock()
        connector.fetch_store_snapshot = AsyncMock(side_effect=ShopifyConnectorError("rate limited"))
        with self._patch_connected(connector):
            result = ShopifyIntelligenceReportExecutor().execute(_req())
        assert result.success is False
        assert "rate limited" in result.message

    def test_unexpected_error_returns_refusal(self):
        connector = MagicMock()
        connector.fetch_store_snapshot = AsyncMock(side_effect=RuntimeError("unexpected"))
        with self._patch_connected(connector):
            result = ShopifyIntelligenceReportExecutor().execute(_req())
        assert result.success is False
        assert "unexpected" in result.message.lower()


class TestShopifySuccessPath:
    def _patch_with_snapshot(self, snapshot: ShopifyStoreSnapshot):
        connector = MagicMock()
        connector.fetch_store_snapshot = AsyncMock(return_value=snapshot)
        return patch.multiple(
            "src.executors.shopify_intelligence_report_executor",
            is_shopify_connected=MagicMock(return_value=True),
            get_shopify_connector=MagicMock(return_value=connector),
        )

    def test_success_result_is_true(self):
        with self._patch_with_snapshot(_make_snapshot()):
            result = ShopifyIntelligenceReportExecutor().execute(_req())
        assert result.success is True

    def test_capability_id_is_65(self):
        with self._patch_with_snapshot(_make_snapshot()):
            result = ShopifyIntelligenceReportExecutor().execute(_req())
        assert result.capability_id == 65

    def test_authority_class_is_read_only_network(self):
        with self._patch_with_snapshot(_make_snapshot()):
            result = ShopifyIntelligenceReportExecutor().execute(_req())
        assert result.authority_class == "read_only_network"

    def test_external_effect_is_true(self):
        with self._patch_with_snapshot(_make_snapshot()):
            result = ShopifyIntelligenceReportExecutor().execute(_req())
        assert result.external_effect is True

    def test_reversible_is_true(self):
        with self._patch_with_snapshot(_make_snapshot()):
            result = ShopifyIntelligenceReportExecutor().execute(_req())
        assert result.reversible is True

    def test_message_includes_shop_name(self):
        with self._patch_with_snapshot(_make_snapshot()):
            result = ShopifyIntelligenceReportExecutor().execute(_req())
        assert "My Store" in result.message

    def test_message_includes_order_count(self):
        with self._patch_with_snapshot(_make_snapshot(order_count=42)):
            result = ShopifyIntelligenceReportExecutor().execute(_req())
        assert "42" in result.message

    def test_widget_type_correct(self):
        with self._patch_with_snapshot(_make_snapshot()):
            result = ShopifyIntelligenceReportExecutor().execute(_req())
        widget = result.data.get("widget", {})
        assert widget.get("type") == "shopify_intelligence_report"

    def test_widget_has_orders_and_products(self):
        with self._patch_with_snapshot(_make_snapshot()):
            result = ShopifyIntelligenceReportExecutor().execute(_req())
        widget = result.data.get("widget", {})
        assert "orders" in widget
        assert "products" in widget

    def test_partial_error_included_in_message(self):
        with self._patch_with_snapshot(_make_snapshot(error="partial timeout")):
            result = ShopifyIntelligenceReportExecutor().execute(_req())
        assert "partial" in result.message.lower()

    def test_default_period_is_last_7_days(self):
        connector = MagicMock()
        connector.fetch_store_snapshot = AsyncMock(return_value=_make_snapshot())
        with patch.multiple(
            "src.executors.shopify_intelligence_report_executor",
            is_shopify_connected=MagicMock(return_value=True),
            get_shopify_connector=MagicMock(return_value=connector),
        ):
            ShopifyIntelligenceReportExecutor().execute(_req({}))
        connector.fetch_store_snapshot.assert_awaited_once()
        _, kwargs = connector.fetch_store_snapshot.call_args
        assert kwargs.get("period") == "last_7_days"

    def test_custom_period_forwarded(self):
        connector = MagicMock()
        connector.fetch_store_snapshot = AsyncMock(return_value=_make_snapshot())
        with patch.multiple(
            "src.executors.shopify_intelligence_report_executor",
            is_shopify_connected=MagicMock(return_value=True),
            get_shopify_connector=MagicMock(return_value=connector),
        ):
            ShopifyIntelligenceReportExecutor().execute(_req({"period": "last_30_days"}))
        _, kwargs = connector.fetch_store_snapshot.call_args
        assert kwargs.get("period") == "last_30_days"

    def test_invalid_period_falls_back_to_default(self):
        connector = MagicMock()
        connector.fetch_store_snapshot = AsyncMock(return_value=_make_snapshot())
        with patch.multiple(
            "src.executors.shopify_intelligence_report_executor",
            is_shopify_connected=MagicMock(return_value=True),
            get_shopify_connector=MagicMock(return_value=connector),
        ):
            ShopifyIntelligenceReportExecutor().execute(_req({"period": "unknown_period"}))
        _, kwargs = connector.fetch_store_snapshot.call_args
        assert kwargs.get("period") == "last_7_days"
