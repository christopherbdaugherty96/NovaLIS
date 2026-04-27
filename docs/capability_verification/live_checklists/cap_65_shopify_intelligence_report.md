# Live Test Checklist — Cap 65: shopify_intelligence_report
Phase 5 of 6 · Priority: after cap 64 lock

---

## Current Status — 2026-04-27

**P5: BLOCKED — Shopify credentials not present in environment.**

Automated verification completed 2026-04-27:
- P1 unit tests: 9/9 pass (`tests/executors/test_shopify_intelligence_report_executor.py`, `tests/connectors/test_shopify_connector.py`)
- P2 routing tests: 49/49 pass (`tests/test_shopify_intelligence_report_routing.py`)
- P3 integration tests: 16/16 pass (`tests/certification/cap_65_shopify_intelligence_report/test_p3_integration.py`)
- P4 API tests: 10/10 pass (`tests/certification/cap_65_shopify_intelligence_report/test_p4_api.py`)
- Total: 84 automated tests green

Safety confirmation:
- Read-only: CONFIRMED — all GraphQL calls use `query {}` not `mutation {}`; no write/update/delete endpoints
- NetworkMediator: CONFIRMED — `_gql()` instantiates `NetworkMediator()` and routes every Shopify call through `mediator.request()`
- Credential guard: CONFIRMED — `is_shopify_connected()` check in executor returns clean refusal if env vars absent

Missing to unblock P5:
- `NOVA_SHOPIFY_SHOP_DOMAIN` — not set
- `NOVA_SHOPIFY_ACCESS_TOKEN` — not set

When both are set, start at "Prerequisites" below and run the 5 live tests.

---

## Prerequisites

**Recommended: use a Shopify Developer store for first P5 sign-off.** Create one free at partners.shopify.com, generate a custom app with `read_orders` and `read_products` scopes.

Set env vars in the shell you will start Nova from, then start Nova from that same shell session:

**PowerShell:**
```powershell
$env:NOVA_SHOPIFY_SHOP_DOMAIN = "mystore.myshopify.com"
$env:NOVA_SHOPIFY_ACCESS_TOKEN = "shpat_..."
nova-start
```

**cmd.exe:**
```cmd
set NOVA_SHOPIFY_SHOP_DOMAIN=mystore.myshopify.com
set NOVA_SHOPIFY_ACCESS_TOKEN=shpat_...
nova-start
```

> Nova must be started from the same shell session after setting env vars — the connector bootstraps at startup and reads env vars once.

- [ ] Nova is running at `http://localhost:8000`
- [ ] `NOVA_SHOPIFY_SHOP_DOMAIN` is set to a real or dev store domain (e.g. `mystore.myshopify.com`)
- [ ] `NOVA_SHOPIFY_ACCESS_TOKEN` is set to a read-only Admin API token for that store
- [ ] Run `system status` and confirm "Shopify: connected" appears

---

## Test 1 — Basic report

1. Type in Nova chat:
   ```
   shopify report
   ```
2. ✅ Nova returns a structured store intelligence card (not an error)
3. ✅ Card shows order count, revenue, and active product count
4. ✅ Numbers are plausible for your store

---

## Test 2 — Period selection

1. Type:
   ```
   shopify report for the last 30 days
   ```
2. ✅ Report covers `last_30_days` period (visible in the card or Nova's response)

---

## Test 3 — Connector not configured (safe refusal)

1. Temporarily unset `NOVA_SHOPIFY_SHOP_DOMAIN` (or set it to an empty string)
2. Restart Nova
3. Type: `shopify report`
4. ✅ Nova returns a clear "connector not configured" message — does NOT crash
5. ✅ No Python traceback in the Nova console
6. Restore the env var and restart Nova

---

## Test 4 — Ledger verification

1. Go to the Trust receipts API: `http://localhost:8000/api/trust/receipts`
2. ✅ Response is a JSON object with a `receipts` array
3. ✅ At least one `ACTION_COMPLETED` entry is present from your test above

---

## Test 5 — Read-only confirmation

1. Look at the Nova console output during a Shopify report run
2. ✅ No write operations appear in the logs
3. ✅ No confirmation prompt appears (cap 65 is a read-only network call — no confirmation required)

---

## Sign-off

> **Safety rule:** Cap 65 must not perform any Shopify writes or mutations. If any write behavior is observed during testing, stop — do not sign off or lock.

> **Do not run `lock 65` until all 5 live checklist items above have passed.**

When all 5 tests pass, run from the repo root:
```
python scripts/certify_capability.py live-signoff 65 --notes "all tests pass, read-only confirmed on <store domain>"
```

Then lock:
```
python scripts/certify_capability.py lock 65
```

---

## Troubleshooting

**`system status` does not show "Shopify: connected"**
- Verify `NOVA_SHOPIFY_SHOP_DOMAIN` is set to the full `.myshopify.com` domain (e.g. `mystore.myshopify.com`, not just `mystore`).
- Verify `NOVA_SHOPIFY_ACCESS_TOKEN` starts with `shpat_` (custom app token) or `shpca_` (collaborator token).
- Restart Nova after setting env vars — the connector bootstraps at startup.

**Token scope errors in the Nova console**
- The executor calls `read_orders` and `read_products` via GraphQL Admin API.
- Your custom app token must have at least these two scopes. Re-generate the token in the Shopify admin if scopes are missing: Apps → Develop apps → [your app] → Configuration → Admin API access scopes.

**NetworkMediator refuses the outbound call**
- The connector uses `HttpShopifyConnector` which routes through NetworkMediator. If the call is blocked, check that `cap_65` has `external_effect=True` in the registry (it does) and that no policy is blocking outbound reads.
- NetworkMediator errors appear in the Nova console with the prefix `NetworkMediator:`.

**GraphQL errors / empty data**
- Empty orders or products is valid for a new dev store. Populate a few test orders/products before running Test 1.
- GraphQL errors appear in `ACTION_ATTEMPTED` ledger events. Check `http://localhost:8000/api/trust/receipts` for the raw event detail.

**Test 3 — Connector not configured**
- Unsetting `NOVA_SHOPIFY_SHOP_DOMAIN` alone may not be enough if Nova cached the connector at startup. Restart Nova after unsetting the variable.
- The expected response is a clean `ActionResult` with `success=False` and a message like "Shopify connector not configured". No traceback should appear in the console.

**Report period does not match**
- Valid period values: `last_7_days`, `last_30_days`, `last_90_days`. An unrecognised period defaults to `last_7_days` — this is expected behavior confirmed in Test 2.

**certify_capability.py errors**
- Run from `C:\Nova-Project` (the repo root).
- The `--notes` flag is optional; include the store domain for traceability.
