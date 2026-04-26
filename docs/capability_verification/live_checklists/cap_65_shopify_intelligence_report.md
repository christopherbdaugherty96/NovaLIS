# Live Test Checklist — Cap 65: shopify_intelligence_report
Phase 5 of 6 · Priority: after cap 64 lock

## Prerequisites
- [ ] Nova is running at `http://localhost:8000`
- [ ] `NOVA_SHOPIFY_SHOP_DOMAIN` is set to a real or dev store domain (e.g. `mystore.myshopify.com`)
- [ ] `NOVA_SHOPIFY_ACCESS_TOKEN` is set to a read-only Admin API token for that store
- [ ] Run `system status` and confirm "Shopify: connected" appears

If you do not have a live Shopify store, create a free Shopify Developer store and generate a custom app with `read_orders` and `read_products` scopes.

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

When all 5 tests pass, run:
```
python scripts/certify_capability.py live-signoff 65 --notes "all tests pass, read-only confirmed on <store domain>"
```

Then lock it:
```
python scripts/certify_capability.py lock 65
```
