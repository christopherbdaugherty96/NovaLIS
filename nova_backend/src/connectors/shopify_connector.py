# src/connectors/shopify_connector.py
"""
Shopify Connector — interface stub for Shopify Admin API integration.

This module defines the protocol that a Shopify store integration must implement
to enable governed reporting (capability 65: shopify_intelligence_report) and
future Shopify operator capabilities (66-76).

Status: STUB — not yet connected.
The interface is defined here so the governed connector layer, capability registry,
and future executor can be wired correctly. Actual HTTP calls to the Shopify
GraphQL Admin API are not yet implemented.

Implementation requirements for a real connector:
  1. Subclass or duck-type `ShopifyConnector`.
  2. Register the instance via `set_shopify_connector(instance)` at startup.
  3. Never store credentials in plain text in the repo.
     Use environment variables or the governed identity layer (src/identity/).
  4. All network I/O must go through the governor's NetworkMediator when
     invoked from a governed capability path.
  5. Use the Shopify GraphQL Admin API as primary. REST is legacy-only.
  6. All returned dataclasses must be serialisable to JSON via .as_dict().

Environment variables expected by a real implementation:
  NOVA_SHOPIFY_SHOP_DOMAIN   — e.g. "mystore.myshopify.com"
  NOVA_SHOPIFY_ACCESS_TOKEN  — OAuth access token from Shopify Admin API
                               (stored via governed identity layer, not plain env
                               in production — env var is the dev/bootstrap path)

Authentication note:
  This connector uses OAuth 2.0 through the Shopify Admin API authorization flow.
  Read-only scopes (Tier 1) are requested at initial connection.
  Write scopes (Tier 4) must not be present until explicitly activated by the user.
  Token validity must be checked before every API call.
  Expired or revoked tokens must surface as a visible connection error — never fail
  silently.

Dev store requirement:
  Tier 4 (write) paths must be validated against a Shopify development store before
  any live store activation. The P5 live sign-off for write capabilities is gated on
  this validation passing end-to-end.

GraphQL conventions:
  All queries use #graphql tagged literals, `as const`, and @inContext(country:,
  language:) for market-aware queries where applicable. Fragment reuse is preferred
  over copy-pasted field selections. See also:
  docs/future/HYDROGEN_OXYGEN_STOREFRONT_BUILD_RULESET_2026-04-12.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Data contracts
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ShopifyOrderSummary:
    """Aggregated order metrics for a reporting period."""

    order_count: int
    total_revenue: str          # Currency-formatted string, e.g. "12,450.00"
    currency: str               # ISO 4217 code, e.g. "USD"
    average_order_value: str    # Currency-formatted string
    period_label: str           # e.g. "last_7_days", "last_30_days"
    fetched_at: str             # ISO 8601 UTC

    def as_dict(self) -> dict[str, Any]:
        return {
            "order_count": self.order_count,
            "total_revenue": self.total_revenue,
            "currency": self.currency,
            "average_order_value": self.average_order_value,
            "period_label": self.period_label,
            "fetched_at": self.fetched_at,
        }


@dataclass(frozen=True)
class ShopifyProductSummary:
    """Aggregated product catalog metrics."""

    total_products: int
    active_products: int
    draft_products: int
    out_of_stock_count: int     # Variants with zero inventory
    low_stock_count: int        # Variants at or below the configured restock threshold
    fetched_at: str             # ISO 8601 UTC

    def as_dict(self) -> dict[str, Any]:
        return {
            "total_products": self.total_products,
            "active_products": self.active_products,
            "draft_products": self.draft_products,
            "out_of_stock_count": self.out_of_stock_count,
            "low_stock_count": self.low_stock_count,
            "fetched_at": self.fetched_at,
        }


@dataclass(frozen=True)
class ShopifyStoreSnapshot:
    """
    Top-level store snapshot returned by `fetch_store_snapshot`.

    This is the primary data contract for capability 65
    (shopify_intelligence_report) and the KPI Command Center brief.
    """

    shop_domain: str
    shop_name: str
    orders: ShopifyOrderSummary
    products: ShopifyProductSummary
    fetched_at: str             # ISO 8601 UTC
    market_context: str = ""    # e.g. "US/en" if @inContext was applied
    error: str = ""             # Non-empty if partial failure

    def as_dict(self) -> dict[str, Any]:
        return {
            "shop_domain": self.shop_domain,
            "shop_name": self.shop_name,
            "orders": self.orders.as_dict(),
            "products": self.products.as_dict(),
            "fetched_at": self.fetched_at,
            "market_context": self.market_context,
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------

class ShopifyConnector:
    """
    Abstract base for Shopify Admin API integrations.

    Implementations must be async-safe. All network I/O should be awaitable
    and routed through the governor's NetworkMediator when invoked from a
    governed capability path. Raise `ShopifyConnectorError` for recoverable
    failures (auth, rate limit, timeout, revoked token).
    """

    @property
    def shop_domain(self) -> str:
        """The Shopify store domain, e.g. 'mystore.myshopify.com'."""
        raise NotImplementedError

    @property
    def is_configured(self) -> bool:
        """Return True if all required credentials are present and valid."""
        raise NotImplementedError

    async def fetch_store_snapshot(
        self,
        *,
        period: str = "last_7_days",
        market_context: str = "",
        low_stock_threshold: int = 5,
    ) -> ShopifyStoreSnapshot:
        """
        Fetch a governed snapshot of core store metrics.

        This is the primary read path for capability 65. All data is sourced
        from the Shopify GraphQL Admin API. The fetch is logged by the caller
        via the governed network path.

        Args:
            period: Reporting window. One of: "today", "last_7_days",
                    "last_30_days", "last_90_days".
            market_context: If set, applies @inContext(country:, language:)
                            to market-sensitive queries. Format: "US/en".
            low_stock_threshold: Variants at or below this quantity are
                                 counted as low stock.

        Returns:
            ShopifyStoreSnapshot with order and product metrics.

        Raises:
            ShopifyConnectorError: On recoverable failure.
        """
        raise NotImplementedError(
            f"{type(self).__name__} does not implement fetch_store_snapshot. "
            "Provide a concrete ShopifyConnector implementation."
        )

    async def health_check(self) -> dict[str, Any]:
        """
        Return a dict with at minimum: {'ok': bool, 'label': str, 'shop': str}.

        Used by the Trust and Settings pages to show connector readiness.
        Must check token validity as part of the health check — a token that
        has been revoked since last session must surface ok=False here.
        """
        raise NotImplementedError


class ShopifyConnectorError(Exception):
    """Raised by ShopifyConnector on recoverable failures (auth, rate limit, etc.)."""


# ---------------------------------------------------------------------------
# Singleton registry
# ---------------------------------------------------------------------------

_shopify_connector: ShopifyConnector | None = None


def get_shopify_connector() -> ShopifyConnector | None:
    """Return the registered Shopify connector, or None if not yet configured."""
    return _shopify_connector


def set_shopify_connector(connector: ShopifyConnector) -> None:
    """Register the active Shopify connector at startup."""
    global _shopify_connector
    if not isinstance(connector, ShopifyConnector):
        raise TypeError(
            f"set_shopify_connector requires a ShopifyConnector instance, "
            f"got {type(connector)}"
        )
    _shopify_connector = connector


def is_shopify_connected() -> bool:
    """True if a Shopify connector is registered and reports itself as configured."""
    connector = _shopify_connector
    if connector is None:
        return False
    try:
        return bool(connector.is_configured)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# HTTP implementation
# ---------------------------------------------------------------------------

import asyncio
import os
from datetime import datetime, timedelta, timezone


_API_VERSION = "2024-04"

_SHOP_QUERY = """
{
  shop { name }
  allProducts: productsCount { count }
  activeProducts: productsCount(query: "status:active") { count }
  draftProducts: productsCount(query: "status:draft") { count }
}
"""

# Separate query so an unsupported inventory filter never takes down shop/product counts.
_INVENTORY_QUERY = """
query Inventory($outOfStockQuery: String!, $lowStockQuery: String!) {
  outOfStockVariants: productVariants(first: 250, query: $outOfStockQuery) {
    edges { node { id } }
    pageInfo { hasNextPage }
  }
  lowStockVariants: productVariants(first: 250, query: $lowStockQuery) {
    edges { node { id } }
    pageInfo { hasNextPage }
  }
}
"""

_ORDERS_QUERY = """
query Orders($q: String!) {
  orders(first: 250, query: $q) {
    edges {
      node {
        totalPriceSet {
          shopMoney { amount currencyCode }
        }
      }
    }
    pageInfo { hasNextPage }
  }
}
"""

_HEALTH_QUERY = "{ shop { name } }"


def _period_to_order_query(period: str) -> str:
    now = datetime.now(timezone.utc)
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "last_90_days":
        start = now - timedelta(days=90)
    elif period == "last_30_days":
        start = now - timedelta(days=30)
    else:
        start = now - timedelta(days=7)
    return f"created_at:>={start.strftime('%Y-%m-%dT%H:%M:%SZ')}"


def _fmt_currency(amount: float) -> str:
    return f"{amount:,.2f}"


class HttpShopifyConnector(ShopifyConnector):
    """
    Live Shopify Admin GraphQL API connector.

    Routes all network I/O through NetworkMediator (cap 65). Token is never
    logged. Raise ShopifyConnectorError for any recoverable failure.
    """

    def __init__(self, shop_domain: str, access_token: str) -> None:
        self._shop_domain = shop_domain.strip().lower().rstrip("/")
        self._access_token = access_token.strip()

    @property
    def shop_domain(self) -> str:
        return self._shop_domain

    @property
    def is_configured(self) -> bool:
        return bool(self._shop_domain and self._access_token)

    def _url(self) -> str:
        return f"https://{self._shop_domain}/admin/api/{_API_VERSION}/graphql.json"

    def _headers(self) -> dict[str, str]:
        return {
            "X-Shopify-Access-Token": self._access_token,
            "Content-Type": "application/json",
            "User-Agent": "Nova/1.0 (+https://local.nova)",
        }

    async def _gql(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        from src.governor.network_mediator import NetworkMediator, NetworkMediatorError

        mediator = NetworkMediator()
        try:
            resp = await asyncio.to_thread(
                mediator.request,
                capability_id=65,
                method="POST",
                url=self._url(),
                json_payload={"query": query, "variables": variables or {}},
                headers=self._headers(),
                as_json=True,
            )
        except NetworkMediatorError as exc:
            raise ShopifyConnectorError(f"Network error reaching Shopify: {exc}") from exc

        status = resp.get("status_code", 200)
        if status == 401:
            raise ShopifyConnectorError("Shopify access token is invalid or revoked.")
        if status == 403:
            raise ShopifyConnectorError("Shopify API permission denied — check token scopes.")
        if status == 429:
            raise ShopifyConnectorError("Shopify API rate limit hit. Try again shortly.")
        if status >= 400:
            raise ShopifyConnectorError(f"Shopify API returned HTTP {status}.")

        body = resp.get("data") or {}
        if isinstance(body, dict) and body.get("errors"):
            errs = body["errors"]
            msg = (errs[0].get("message") if isinstance(errs, list) and errs else str(errs))
            raise ShopifyConnectorError(f"GraphQL error: {msg}")

        return (body.get("data") or {}) if isinstance(body, dict) else {}

    async def fetch_store_snapshot(
        self,
        *,
        period: str = "last_7_days",
        market_context: str = "",
        low_stock_threshold: int = 5,
    ) -> ShopifyStoreSnapshot:
        fetched_at = datetime.now(timezone.utc).isoformat()
        order_query = _period_to_order_query(period)
        error_parts: list[str] = []

        # --- shop info + product counts ---
        shop_data: dict[str, Any] = {}
        try:
            shop_data = await self._gql(_SHOP_QUERY)
        except ShopifyConnectorError as exc:
            error_parts.append(f"store info: {exc}")

        shop_name = str((shop_data.get("shop") or {}).get("name") or self._shop_domain)
        total_products = int((shop_data.get("allProducts") or {}).get("count") or 0)
        active_products = int((shop_data.get("activeProducts") or {}).get("count") or 0)
        draft_products = int((shop_data.get("draftProducts") or {}).get("count") or 0)

        # --- inventory counts (separate query so a filter failure is isolated) ---
        inv_data: dict[str, Any] = {}
        try:
            inv_data = await self._gql(
                _INVENTORY_QUERY,
                variables={
                    "outOfStockQuery": "inventory_quantity:<=0",
                    "lowStockQuery": f"inventory_quantity:<={low_stock_threshold}",
                },
            )
        except ShopifyConnectorError as exc:
            error_parts.append(f"inventory: {exc}")

        oos_node = inv_data.get("outOfStockVariants") or {}
        ls_node = inv_data.get("lowStockVariants") or {}
        out_of_stock_count = len(oos_node.get("edges") or [])
        if (oos_node.get("pageInfo") or {}).get("hasNextPage"):
            error_parts.append("out-of-stock count truncated at 250 variants")
        low_stock_count = len(ls_node.get("edges") or [])
        if (ls_node.get("pageInfo") or {}).get("hasNextPage"):
            error_parts.append("low-stock count truncated at 250 variants")

        # --- order aggregation ---
        order_data: dict[str, Any] = {}
        try:
            order_data = await self._gql(_ORDERS_QUERY, variables={"q": order_query})
        except ShopifyConnectorError as exc:
            error_parts.append(f"orders: {exc}")

        orders_node = order_data.get("orders") or {}
        edges = orders_node.get("edges") or []
        if (orders_node.get("pageInfo") or {}).get("hasNextPage"):
            error_parts.append("order count truncated at 250 orders")

        order_count = len(edges)
        currency = "USD"
        total_revenue = 0.0
        for edge in edges:
            money = ((edge.get("node") or {}).get("totalPriceSet") or {}).get("shopMoney") or {}
            try:
                total_revenue += float(money.get("amount") or 0)
            except (TypeError, ValueError):
                pass
            if money.get("currencyCode"):
                currency = str(money["currencyCode"])

        avg_order_value = (total_revenue / order_count) if order_count else 0.0

        products = ShopifyProductSummary(
            total_products=total_products,
            active_products=active_products,
            draft_products=draft_products,
            out_of_stock_count=out_of_stock_count,
            low_stock_count=low_stock_count,
            fetched_at=fetched_at,
        )
        orders = ShopifyOrderSummary(
            order_count=order_count,
            total_revenue=_fmt_currency(total_revenue),
            currency=currency,
            average_order_value=_fmt_currency(avg_order_value),
            period_label=period,
            fetched_at=fetched_at,
        )
        return ShopifyStoreSnapshot(
            shop_domain=self._shop_domain,
            shop_name=shop_name,
            orders=orders,
            products=products,
            fetched_at=fetched_at,
            market_context=market_context,
            error="; ".join(error_parts),
        )

    async def health_check(self) -> dict[str, Any]:
        try:
            data = await self._gql(_HEALTH_QUERY)
            name = str((data.get("shop") or {}).get("name") or self._shop_domain)
            return {"ok": True, "label": "Connected", "shop": name}
        except ShopifyConnectorError as exc:
            return {"ok": False, "label": str(exc), "shop": self._shop_domain}


# ---------------------------------------------------------------------------
# Bootstrap helper — call once at startup
# ---------------------------------------------------------------------------

def bootstrap_shopify_connector() -> None:
    """Register HttpShopifyConnector from env vars if both are set."""
    domain = os.getenv("NOVA_SHOPIFY_SHOP_DOMAIN", "").strip()
    token = os.getenv("NOVA_SHOPIFY_ACCESS_TOKEN", "").strip()
    if domain and token:
        set_shopify_connector(HttpShopifyConnector(domain, token))
