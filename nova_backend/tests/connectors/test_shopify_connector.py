from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.connectors.shopify_connector import HttpShopifyConnector, ShopifyConnectorError


def test_http_shopify_connector_uses_configured_api_version():
    connector = HttpShopifyConnector(
        "https://Example.myshopify.com/",
        "token",
        api_version="2026-04",
    )

    assert connector._url() == "https://example.myshopify.com/admin/api/2026-04/graphql.json"


def test_http_shopify_connector_defaults_to_supported_api_version(monkeypatch):
    monkeypatch.delenv("NOVA_SHOPIFY_API_VERSION", raising=False)

    connector = HttpShopifyConnector("example.myshopify.com", "token")

    assert "/admin/api/2026-04/graphql.json" in connector._url()


def test_http_shopify_connector_rejects_invalid_api_version():
    with pytest.raises(ShopifyConnectorError, match="Invalid Shopify API version"):
        HttpShopifyConnector(
            "example.myshopify.com",
            "token",
            api_version="../2026-04",
        )


@pytest.mark.asyncio
async def test_fetch_store_snapshot_raises_when_primary_store_info_fails():
    connector = HttpShopifyConnector("example.myshopify.com", "token")
    connector._gql = AsyncMock(side_effect=ShopifyConnectorError("invalid token"))

    with pytest.raises(ShopifyConnectorError, match="store info"):
        await connector.fetch_store_snapshot()


@pytest.mark.asyncio
async def test_fetch_store_snapshot_keeps_partial_inventory_failure():
    connector = HttpShopifyConnector("example.myshopify.com", "token")
    connector._gql = AsyncMock(
        side_effect=[
            {
                "shop": {"name": "Example"},
                "allProducts": {"count": 3},
                "activeProducts": {"count": 2},
                "draftProducts": {"count": 1},
            },
            ShopifyConnectorError("inventory filter unsupported"),
            {"orders": {"edges": [], "pageInfo": {"hasNextPage": False}}},
        ]
    )

    snapshot = await connector.fetch_store_snapshot()

    assert snapshot.shop_name == "Example"
    assert snapshot.products.total_products == 3
    assert "inventory filter unsupported" in snapshot.error


@pytest.mark.asyncio
async def test_fetch_store_snapshot_raises_when_secondary_reads_all_fail():
    connector = HttpShopifyConnector("example.myshopify.com", "token")
    connector._gql = AsyncMock(
        side_effect=[
            {
                "shop": {"name": "Example"},
                "allProducts": {"count": 3},
                "activeProducts": {"count": 2},
                "draftProducts": {"count": 1},
            },
            ShopifyConnectorError("inventory timeout"),
            ShopifyConnectorError("orders timeout"),
        ]
    )

    with pytest.raises(ShopifyConnectorError, match="inventory timeout"):
        await connector.fetch_store_snapshot()
