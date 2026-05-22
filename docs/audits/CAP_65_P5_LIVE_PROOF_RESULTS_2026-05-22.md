# Cap 65 P5 Live Proof Results — 2026-05-22

## Summary

```text
Cap 65: shopify_intelligence_report
Store: auralis-design.myshopify.com
P5 live proof: 5/5 PASS
Full P1-P5 suite: 89/89 PASS (60.77s)
Token exposed in chat: NO (rotated token, never printed)
```

## Test Results

### Test 1 — Basic report (PASS)

```text
shop_domain: auralis-design.myshopify.com
shop_name: Auralis Design
period: last_7_days
order_count: 0
total_revenue: 0.00
active_products: 21
total_products: 25
fetched_at: 2026-05-22T23:24:37+00:00
error: none
```

Result: structured store intelligence card returned successfully.
Numbers are plausible (25 products, 0 orders on a new Printify-connected store).

### Test 2 — Period selection (PASS)

```text
period: last_30_days
order_count: 0
active_products: 21
```

Result: period parameter correctly forwarded and reflected in response.

### Test 3 — Missing-credential refusal (PASS)

```text
refusal_message: Shopify connector is not configured. Set
  NOVA_SHOPIFY_SHOP_DOMAIN and NOVA_SHOPIFY_ACCESS_TOKEN to
  enable store intelligence reports.
success: False
```

Result: clean refusal, no crash, no traceback.

### Test 4 — Ledger / ActionResult fields (PASS)

```text
capability_id: 65
authority_class: read_only_network
external_effect: True
reversible: True
request_id: p5-ledger-check
```

Result: all governed metadata fields present and correct.

### Test 5 — Read-only confirmation (PASS)

```text
mutation_blocks_found: 0
query_blocks_found: 2 (Inventory, Orders)
non_gql_write_endpoints: 0
requires_confirmation: False
authority_class: read_only_network
token_format_valid: True (starts with shpat_)
token_printed: False
```

Result: no mutations in connector source, no write endpoints,
no confirmation gate (read-only capability), token never printed.

## Scopes Verification

```text
Shopify Admin API scopes: read_orders, read_products
Shopify app: NovaLIS (novalis-2, Active)
Shopify Dev Dashboard org: 217960397
App installed on: auralis-design.myshopify.com
```

## Token Security

```text
Initial token was exposed in chat during OAuth exchange.
Compromised token: revoked via API (DELETE /admin/api_permissions/current.json).
Confirmed dead: 401 Unauthorized on re-test.
Fresh token: generated via reinstall + OAuth exchange.
Fresh token: written directly to .env, never displayed.
.env: gitignored, never committed.
```

## Full Test Suite

```text
89 passed in 60.77s

Breakdown:
  P3 integration: 16/16
  P4 API: 10/10
  P5 live proof: 5/5
  P1 unit (executor): 15/15 (includes 6 connector tests)
  P2 routing: 25/25
  P1 unit (connector): 6/6 (overlaps with above)
  Total unique: 89 pass, 0 fail
```

## Evidence Files

```text
P5 test file:
  tests/certification/cap_65_shopify_intelligence_report/test_p5_live_proof.py

P1-P4 test files:
  tests/executors/test_shopify_intelligence_report_executor.py
  tests/connectors/test_shopify_connector.py
  tests/test_shopify_intelligence_report_routing.py
  tests/certification/cap_65_shopify_intelligence_report/test_p3_integration.py
  tests/certification/cap_65_shopify_intelligence_report/test_p4_api.py

P5 live checklist:
  docs/capability_verification/live_checklists/cap_65_shopify_intelligence_report.md

This results doc:
  docs/audits/CAP_65_P5_LIVE_PROOF_RESULTS_2026-05-22.md
```

## Safety Boundary

```text
No Shopify writes or mutations.
No capability expansion.
No authority expansion.
No capability_locks.json changes (pending separate lock decision).
No token in any committed file, doc, or chat output.
```
