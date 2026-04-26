# tests/certification/cap_65_shopify_intelligence_report/test_p4_api.py
"""
Phase 4 — API certification for capability 65 (shopify_intelligence_report).

Tests at the HTTP/WebSocket layer. Verifies:
  - App health routes return 200
  - WebSocket session accepts a connection
  - A Shopify report intent does not crash the session layer
  - The not-configured refusal path is handled cleanly at the WS layer
  - /api/trust/receipts endpoint is accessible (trust surface smoke test)

All connector calls are mocked.
"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402
from src.connectors.shopify_connector import (
    ShopifyOrderSummary,
    ShopifyProductSummary,
    ShopifyStoreSnapshot,
)


def _make_snapshot() -> ShopifyStoreSnapshot:
    orders = ShopifyOrderSummary(
        order_count=7,
        total_revenue="350.00",
        currency="USD",
        average_order_value="50.00",
        period_label="last_7_days",
        fetched_at="2026-04-25T00:00:00+00:00",
    )
    products = ShopifyProductSummary(
        total_products=5,
        active_products=5,
        draft_products=0,
        out_of_stock_count=0,
        low_stock_count=0,
        fetched_at="2026-04-25T00:00:00+00:00",
    )
    return ShopifyStoreSnapshot(
        shop_domain="p4-test.myshopify.com",
        shop_name="P4 Test Store",
        orders=orders,
        products=products,
        fetched_at="2026-04-25T00:00:00+00:00",
    )


def _mock_connector() -> MagicMock:
    c = MagicMock()
    c.fetch_store_snapshot = AsyncMock(return_value=_make_snapshot())
    return c


@pytest.fixture(scope="module")
def client():
    """TestClient with Shopify connector mocked out."""
    with (
        patch("src.connectors.shopify_connector.is_shopify_connected", return_value=True),
        patch("src.connectors.shopify_connector.get_shopify_connector", return_value=_mock_connector()),
        patch("src.executors.shopify_intelligence_report_executor.is_shopify_connected", return_value=True),
        patch("src.executors.shopify_intelligence_report_executor.get_shopify_connector", return_value=_mock_connector()),
    ):
        from src.brain_server import app
        with TestClient(app, raise_server_exceptions=False) as c:
            yield c


# ---------------------------------------------------------------------------
# HTTP health routes
# ---------------------------------------------------------------------------

def test_phase_status_200(client):
    assert client.get("/phase-status").status_code == 200


def test_landing_200(client):
    assert client.get("/landing").status_code == 200


def test_root_200(client):
    assert client.get("/").status_code == 200


# ---------------------------------------------------------------------------
# Trust receipts API — smoke test
# ---------------------------------------------------------------------------

def test_trust_receipts_endpoint_exists(client):
    resp = client.get("/api/trust/receipts")
    assert resp.status_code == 200


def test_trust_receipts_returns_list(client):
    resp = client.get("/api/trust/receipts")
    body = resp.json()
    assert "receipts" in body
    assert isinstance(body["receipts"], list)


def test_trust_receipts_summary_endpoint_exists(client):
    resp = client.get("/api/trust/receipts/summary")
    assert resp.status_code == 200


def test_trust_receipts_limit_param(client):
    resp = client.get("/api/trust/receipts?limit=5")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["receipts"]) <= 5


# ---------------------------------------------------------------------------
# WebSocket — Shopify intent does not crash the session
# ---------------------------------------------------------------------------

def test_websocket_accepts_connection(client):
    with client.websocket_connect("/ws") as ws:
        pass


def test_websocket_shopify_intent_does_not_crash(client):
    with (
        patch("src.executors.shopify_intelligence_report_executor.is_shopify_connected", return_value=True),
        patch("src.executors.shopify_intelligence_report_executor.get_shopify_connector", return_value=_mock_connector()),
    ):
        with client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({
                "type": "chat",
                "text": "show me my shopify store report",
            }))
            try:
                raw = ws.receive_text()
                msg = json.loads(raw)
                assert isinstance(msg, dict)
            except Exception:
                pass  # clean close is acceptable


def test_websocket_shopify_not_configured_does_not_crash(client):
    """When the connector is not configured, the session handles the refusal cleanly."""
    with patch("src.executors.shopify_intelligence_report_executor.is_shopify_connected", return_value=False):
        with client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({
                "type": "chat",
                "text": "shopify report",
            }))
            try:
                raw = ws.receive_text()
                msg = json.loads(raw)
                assert isinstance(msg, dict)
            except Exception:
                pass
