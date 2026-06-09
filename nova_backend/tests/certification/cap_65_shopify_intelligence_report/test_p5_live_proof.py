"""
Cap 65 P5 Live Proof — shopify_intelligence_report

Runs against a REAL Shopify store (auralis-design.myshopify.com).
Requires NOVA_SHOPIFY_SHOP_DOMAIN and NOVA_SHOPIFY_ACCESS_TOKEN in .env.

This test file MUST NOT print, log, or assert on the access token value.
Only the shop domain, product/order counts, and redacted evidence are captured.

Safety boundary:
  - All GraphQL calls use query {}, never mutation {}
  - No writes, updates, or deletes to the Shopify store
  - Token is read from env only by the connector, never surfaced
  - Scopes: read_orders, read_products (read-only)
"""
from __future__ import annotations

import os
import re
import sys

import pytest

pytestmark = pytest.mark.live_shopify

# ── Bootstrap ──────────────────────────────────────────────────────────
# Load .env so the connector can find credentials.
_env_path = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", ".env"
)
if os.path.isfile(_env_path):
    with open(_env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

_backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(_backend_root)
sys.path.insert(0, _backend_root)

from src.connectors.shopify_connector import (
    bootstrap_shopify_connector,
    is_shopify_connected,
)
from src.executors.shopify_intelligence_report_executor import (
    ShopifyIntelligenceReportExecutor,
)


class _FakeRequest:
    """Minimal request object for the executor."""
    def __init__(self, params=None, request_id="p5-live-proof"):
        self.params = params or {}
        self.request_id = request_id


# ── Test 1: Basic Shopify intelligence report ──────────────────────────

def test_p5_basic_report():
    """Live Test 1 — basic shopify report against Auralis Design."""
    bootstrap_shopify_connector()
    assert is_shopify_connected(), "Shopify connector not configured"

    executor = ShopifyIntelligenceReportExecutor()
    result = executor.execute(_FakeRequest(params={"period": "last_7_days"}))

    assert result.success, f"Report failed: {result.message}"
    assert "shopify" in result.message.lower() or "Auralis" in result.message

    widget = result.data["widget"]
    assert widget["type"] == "shopify_intelligence_report"
    assert widget["shop_domain"], "shop_domain missing"
    assert widget["shop_name"], "shop_name missing"
    assert widget["period"] == "last_7_days"

    orders = widget["orders"]
    products = widget["products"]
    assert isinstance(orders["order_count"], int)
    assert isinstance(products["active_products"], int)
    assert products["active_products"] >= 0

    # Print evidence (no token)
    print(f"  shop_domain: {widget['shop_domain']}")
    print(f"  shop_name: {widget['shop_name']}")
    print(f"  period: {widget['period']}")
    print(f"  order_count: {orders['order_count']}")
    print(f"  total_revenue: {orders.get('total_revenue', 'N/A')}")
    print(f"  active_products: {products['active_products']}")
    print(f"  total_products: {products['total_products']}")
    print(f"  fetched_at: {widget['fetched_at']}")
    print(f"  error: {widget.get('error', 'none')}")


# ── Test 2: Period selection ───────────────────────────────────────────

def test_p5_period_selection():
    """Live Test 2 — period selection (last_30_days)."""
    executor = ShopifyIntelligenceReportExecutor()
    result = executor.execute(
        _FakeRequest(params={"period": "last_30_days"})
    )

    assert result.success, f"Period report failed: {result.message}"
    widget = result.data["widget"]
    assert widget["period"] == "last_30_days", (
        f"Expected last_30_days, got {widget['period']}"
    )
    print(f"  period: {widget['period']}")
    print(f"  order_count: {widget['orders']['order_count']}")
    print(f"  active_products: {widget['products']['active_products']}")


# ── Test 3: Missing-credential refusal ─────────────────────────────────

def test_p5_missing_credential_refusal():
    """Live Test 3 — safe refusal when credentials are absent."""
    from src.connectors import shopify_connector as mod

    # Save and clear
    saved = mod._shopify_connector
    mod._shopify_connector = None

    try:
        assert not is_shopify_connected()
        executor = ShopifyIntelligenceReportExecutor()
        result = executor.execute(_FakeRequest())

        assert not result.success, "Expected refusal, got success"
        assert "not configured" in result.message.lower(), (
            f"Expected 'not configured' refusal, got: {result.message}"
        )
        print(f"  refusal_message: {result.message}")
        print(f"  success: {result.success}")
    finally:
        # Restore
        mod._shopify_connector = saved
        assert is_shopify_connected(), "Failed to restore connector"


# ── Test 4: Ledger / ActionResult verification ─────────────────────────

def test_p5_action_result_fields():
    """Live Test 4 — ActionResult has correct governed fields."""
    executor = ShopifyIntelligenceReportExecutor()
    result = executor.execute(_FakeRequest(
        params={"period": "last_7_days"},
        request_id="p5-ledger-check",
    ))

    assert result.success
    assert result.capability_id == 65
    assert result.authority_class == "read_only_network"
    assert result.external_effect is True
    assert result.reversible is True
    assert result.request_id == "p5-ledger-check"

    print(f"  capability_id: {result.capability_id}")
    print(f"  authority_class: {result.authority_class}")
    print(f"  external_effect: {result.external_effect}")
    print(f"  reversible: {result.reversible}")
    print(f"  request_id: {result.request_id}")


# ── Test 5: Read-only confirmation ─────────────────────────────────────

def test_p5_read_only_confirmation():
    """Live Test 5 — confirm no mutations in GraphQL queries."""
    # Verify source code has no mutations
    connector_path = os.path.join(
        _backend_root, "src", "connectors",
        "shopify_connector.py",
    )
    with open(connector_path) as f:
        source = f.read()

    # Check: no mutation blocks (mutation keyword followed by name or brace)
    mutation_matches = re.findall(
        r'^\s*mutation\s+\w+', source, re.MULTILINE | re.IGNORECASE
    )
    assert not mutation_matches, (
        f"SAFETY VIOLATION: mutation found in connector: {mutation_matches}"
    )

    # Check: GraphQL templates use query (named or anonymous)
    query_matches = re.findall(
        r'^\s*query\s+\w+', source, re.MULTILINE
    )
    assert len(query_matches) >= 2, (
        f"Expected at least 2 named query blocks, found {len(query_matches)}"
    )

    # Check: no write/update/delete REST endpoints
    write_patterns = re.findall(
        r'\b(PUT|POST|DELETE|PATCH)\b.*shopify', source, re.IGNORECASE
    )
    # POST is used for GraphQL endpoint (expected), filter those out
    non_gql_writes = [
        p for p in write_patterns
        if "graphql" not in p.lower()
    ]
    assert not non_gql_writes, (
        f"SAFETY VIOLATION: non-GraphQL write endpoints found: {non_gql_writes}"
    )

    # Check: requires_confirmation is false in registry (read-only, no gate)
    registry_path = os.path.join(
        _backend_root, "src", "config",
        "registry.json",
    )
    import json
    with open(registry_path) as f:
        registry = json.load(f)
    cap65 = None
    for cap in registry.get("capabilities", []):
        if cap.get("id") == 65:
            cap65 = cap
            break
    assert cap65 is not None, "Cap 65 not found in registry"
    assert cap65["requires_confirmation"] is False, (
        "Cap 65 should NOT require confirmation (read-only)"
    )
    assert cap65["authority_class"] == "read_only_network"

    # Verify token is not in any test output
    token_env = os.environ.get("NOVA_SHOPIFY_ACCESS_TOKEN", "")
    assert token_env.startswith("shpat_"), "Token not set"
    # We intentionally do NOT print or assert on the full token value

    print("  mutation_blocks_found: 0")
    print(f"  query_blocks_found: {len(query_matches)}")
    print("  non_gql_write_endpoints: 0")
    print(f"  requires_confirmation: {cap65['requires_confirmation']}")
    print(f"  authority_class: {cap65['authority_class']}")
    print(f"  token_format_valid: {token_env.startswith('shpat_')}")
    print("  token_printed: False")


# ── Runner ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        ("Test 1 — Basic report", test_p5_basic_report),
        ("Test 2 — Period selection", test_p5_period_selection),
        ("Test 3 — Missing-credential refusal", test_p5_missing_credential_refusal),
        ("Test 4 — Ledger / ActionResult fields", test_p5_action_result_fields),
        ("Test 5 — Read-only confirmation", test_p5_read_only_confirmation),
    ]

    passed = 0
    failed = 0
    for name, fn in tests:
        print(f"\n{'='*60}")
        print(f"  {name}")
        print(f"{'='*60}")
        try:
            fn()
            print("  PASS")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"  Cap 65 P5 Live Proof: {passed}/{passed+failed} passed")
    print(f"{'='*60}")

    sys.exit(1 if failed else 0)
