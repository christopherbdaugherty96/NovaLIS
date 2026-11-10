from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest
from src.connectors import shopify_connector as shopify_module
from src.connectors.shopify_connector import HttpShopifyConnector, ShopifyConnectorError
from src.governor.disclosure_policy import (
    CredentialCategory,
    DataCategory,
    InitiationClass,
    ProviderClass,
    TransportClass,
)
from src.governor.disclosure_transport import disclosure_facts


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


@pytest.mark.parametrize(
    "configured_domain",
    [
        "http://example.myshopify.com",
        "https://user@example.myshopify.com",
        "https://example.myshopify.com:443",
        "https://example.myshopify.com/admin",
        "https://example.myshopify.com/?preview=1",
        "https://example.myshopify.com/#fragment",
        "example.myshopify.com.evil.test",
        "evilmyshopify.com",
        "two.labels.myshopify.com",
        "-leading.myshopify.com",
        "trailing-.myshopify.com",
        "ex%61mple.myshopify.com",
        "examplе.myshopify.com",
        "example.myshopify.com\\@evil.test",
    ],
)
def test_http_shopify_connector_rejects_noncanonical_admin_destination(
    configured_domain,
):
    with pytest.raises(ShopifyConnectorError, match="canonical Shopify shop domain"):
        HttpShopifyConnector(configured_domain, "synthetic-token")


def test_shopify_disclosure_classifier_binds_exact_request(monkeypatch):
    captured = {}

    class _CapturingMediator:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def request(self, **kwargs):
            captured["request"] = kwargs
            raise RuntimeError("stop before transport")

    monkeypatch.setattr(
        "src.governor.network_mediator.NetworkMediator",
        _CapturingMediator,
    )
    connector = HttpShopifyConnector("example.myshopify.com", "synthetic-token")

    with pytest.raises(RuntimeError, match="stop before transport"):
        asyncio.run(connector._gql("{ shop { name } }", {"limit": 1}))

    classifier = captured["disclosure_classifier"]
    request = captured["request"]
    facts = disclosure_facts(
        transport=TransportClass.HTTP,
        method=request["method"],
        url=request["url"],
        headers=request["headers"],
        json_payload=request["json_payload"],
        capability_id=request["capability_id"],
    )
    context = classifier(facts)

    assert context is not None
    assert context.caller == "shopify_connector.capability_65"
    assert context.purpose == "shopify_read_only_admin_graphql"
    assert context.provider == "shopify"
    assert context.provider_class is ProviderClass.COMMERCE
    assert context.data_categories == frozenset({DataCategory.SHOP_DATA})
    assert context.initiation is InitiationClass.USER_INITIATED
    assert facts.credential_categories == frozenset(
        {CredentialCategory.ORIGIN_CREDENTIAL}
    )

    assert classifier(
        disclosure_facts(
            transport=TransportClass.HTTP,
            method="GET",
            url=request["url"],
            headers=request["headers"],
            json_payload=request["json_payload"],
            capability_id=request["capability_id"],
        )
    ) is None
    assert classifier(
        disclosure_facts(
            transport=TransportClass.HTTP,
            method=request["method"],
            url=request["url"],
            headers={**request["headers"], "X-Unexpected": "value"},
            json_payload=request["json_payload"],
            capability_id=request["capability_id"],
        )
    ) is None
    assert classifier(
        disclosure_facts(
            transport=TransportClass.HTTP,
            method=request["method"],
            url="https://other.myshopify.com/admin/api/2026-04/graphql.json",
            headers=request["headers"],
            json_payload=request["json_payload"],
            capability_id=request["capability_id"],
        )
    ) is None
    assert classifier(
        disclosure_facts(
            transport=TransportClass.HTTP,
            method=request["method"],
            url=request["url"],
            headers=request["headers"],
            json_payload={"unexpected": "shape"},
            capability_id=request["capability_id"],
        )
    ) is None


def test_default_shopify_denial_precedes_dns_and_client(monkeypatch):
    attempts = {"dns": 0, "client": 0}

    def forbidden_dns(*_args, **_kwargs):
        attempts["dns"] += 1
        raise AssertionError("denial must precede DNS")

    def forbidden_client(*_args, **_kwargs):
        attempts["client"] += 1
        raise AssertionError("denial must precede client construction")

    monkeypatch.setattr(
        "src.governor.network_mediator.socket.getaddrinfo",
        forbidden_dns,
    )
    monkeypatch.setattr(
        "src.governor.network_mediator.requests.Session",
        forbidden_client,
    )
    connector = HttpShopifyConnector("example.myshopify.com", "synthetic-token")

    with pytest.raises(ShopifyConnectorError, match="Network error reaching Shopify"):
        asyncio.run(connector._gql("{ shop { name } }"))

    assert attempts == {"dns": 0, "client": 0}


def test_invalid_shopify_environment_is_truthfully_unavailable(monkeypatch):
    monkeypatch.setenv("NOVA_SHOPIFY_SHOP_DOMAIN", "attacker.example")
    monkeypatch.setenv("NOVA_SHOPIFY_ACCESS_TOKEN", "synthetic-token")
    monkeypatch.delenv("NOVA_RUNTIME_PROFILE", raising=False)
    monkeypatch.setattr(shopify_module, "_shopify_connector", None)

    shopify_module.bootstrap_shopify_connector()

    assert shopify_module.get_shopify_connector() is None
    assert shopify_module.is_shopify_connected() is False


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
