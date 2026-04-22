# src/executors/shopify_intelligence_report_executor.py
"""
Shopify Intelligence Report Executor — cap 65 (shopify_intelligence_report)

Fetches a read-only snapshot of Shopify store metrics via the registered
ShopifyConnector and returns a structured widget for the Trust UI.

Authority class: read_only_network
Risk: low
External effect: true (outbound read to Shopify Admin API)
Reversible: true (read only — no store state changed)

Tier 1 read-only. No write operations in this executor. Tier 4 (write) paths
are gated behind separate capabilities (66+) pending P5 live sign-off against
a Shopify dev store.
"""
from __future__ import annotations

import asyncio
from typing import Any

from src.actions.action_result import ActionResult
from src.connectors.shopify_connector import (
    ShopifyConnectorError,
    get_shopify_connector,
    is_shopify_connected,
)


_CAPABILITY_ID = 65
_AUTHORITY_CLASS = "read_only_network"

_VALID_PERIODS = frozenset({"today", "last_7_days", "last_30_days", "last_90_days"})


class ShopifyIntelligenceReportExecutor:
    """
    Governed executor for Shopify store intelligence reads.

    Delegates to the registered ShopifyConnector. If no connector is configured
    or if the connector reports not-configured, returns a safe refusal that
    surfaces connector setup guidance in the UI.
    """

    def execute(self, req) -> ActionResult:
        params: dict[str, Any] = dict(req.params or {})
        period = str(params.get("period") or "last_7_days").strip()
        if period not in _VALID_PERIODS:
            period = "last_7_days"
        market_context = str(params.get("market_context") or "").strip()
        try:
            low_stock_threshold = max(1, int(params.get("low_stock_threshold") or 5))
        except (TypeError, ValueError):
            low_stock_threshold = 5

        if not is_shopify_connected():
            return ActionResult.refusal(
                "Shopify connector is not configured. "
                "Set NOVA_SHOPIFY_SHOP_DOMAIN and NOVA_SHOPIFY_ACCESS_TOKEN "
                "to enable store intelligence reports.",
                request_id=req.request_id,
                authority_class=_AUTHORITY_CLASS,
                external_effect=True,
                reversible=True,
                capability_id=_CAPABILITY_ID,
            )

        connector = get_shopify_connector()
        try:
            snapshot = asyncio.run(
                connector.fetch_store_snapshot(
                    period=period,
                    market_context=market_context,
                    low_stock_threshold=low_stock_threshold,
                )
            )
        except ShopifyConnectorError as exc:
            return ActionResult.refusal(
                f"Shopify connector error: {exc}",
                request_id=req.request_id,
                authority_class=_AUTHORITY_CLASS,
                external_effect=True,
                reversible=True,
                capability_id=_CAPABILITY_ID,
            )
        except Exception as exc:
            return ActionResult.refusal(
                f"Unexpected error fetching Shopify data: {exc}",
                request_id=req.request_id,
                authority_class=_AUTHORITY_CLASS,
                external_effect=True,
                reversible=True,
                capability_id=_CAPABILITY_ID,
            )

        snapshot_dict = snapshot.as_dict()
        orders = snapshot_dict.get("orders", {})
        products = snapshot_dict.get("products", {})

        message = (
            f"Shopify store '{snapshot.shop_name}' - {period.replace('_', ' ')}: "
            f"{orders.get('order_count', 0)} orders, "
            f"{orders.get('currency', '')} {orders.get('total_revenue', '0')} revenue, "
            f"{products.get('active_products', 0)} active products."
        )
        if snapshot.error:
            message += f" (Partial data: {snapshot.error})"

        widget = {
            "type": "shopify_intelligence_report",
            "shop_domain": snapshot.shop_domain,
            "shop_name": snapshot.shop_name,
            "period": period,
            "market_context": market_context,
            "orders": orders,
            "products": products,
            "fetched_at": snapshot.fetched_at,
            "error": snapshot.error,
        }

        return ActionResult(
            success=True,
            message=message,
            data={
                "speakable_text": message,
                "structured_data": widget,
                "widget": widget,
            },
            request_id=req.request_id,
            authority_class=_AUTHORITY_CLASS,
            external_effect=True,
            reversible=True,
            capability_id=_CAPABILITY_ID,
        )
