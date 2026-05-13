# Shopify Setup TODO

Status: active setup checklist for Cap 65 live signoff
Scope: read-only Shopify intelligence reporting only
Authority boundary: no write scopes, no mutations, no live-store operator behavior until separately designed, tested, and approved

---

## Current truth

Nova already has the Shopify read-only reporting surface implemented as capability 65: `shopify_intelligence_report`.

Cap 65 is an active runtime capability, not a future concept. It is implemented as a Tier 1 read-only Shopify intelligence report that fetches governed order metrics, product catalog summary, and inventory status through the Shopify GraphQL Admin API.

Certification truth:

- P1 unit tests: passed.
- P2 routing tests: passed.
- P3 integration tests: passed.
- P4 API tests: passed.
- P5 live signoff: blocked because Shopify credentials are not present in the local environment.
- Lock state: not locked until P5 live signoff passes.

Current blocker: the connector is not live-signed because Shopify credentials are not present in the local environment.

Required environment variables:

```text
NOVA_SHOPIFY_SHOP_DOMAIN=<store>.myshopify.com
NOVA_SHOPIFY_ACCESS_TOKEN=shpat_...
NOVA_SHOPIFY_API_VERSION=2026-04
```

The current implementation reads Shopify through the Shopify Admin GraphQL API. It does not scrape the public storefront and it does not search the domain.

Cap 65 is not a Shopify operator. It does not write products, update inventory, create discounts, message customers, publish content, or run the store.

---

## Safety rule

Start with a Shopify development store.

Do not connect a live production store first.
Do not request write scopes for Cap 65.
Do not add write/mutation behavior to Cap 65.
Do not lock Cap 65 until the live checklist passes end-to-end.

Future Shopify operator language is boundary language only. It is not the next action in this TODO and it is not implemented runtime authority.

---

## Phase 1 — Create Shopify developer setup

- [ ] Create or log into a Shopify Partner account.
- [ ] Create a Shopify development store.
- [ ] Record the development store domain in the form `<store>.myshopify.com`.
- [ ] Add a few test products.
- [ ] Add enough test order/product data for a useful read-only report.

Acceptance gate:

- [ ] Development store exists.
- [ ] Store has at least one product.
- [ ] Store domain is available.

---

## Phase 2 — Create read-only Shopify custom app

Inside the Shopify development store:

- [ ] Create a custom app for Nova.
- [ ] Enable Admin API access.
- [ ] Grant read-only scopes only.

Minimum scopes for current Cap 65 testing:

- [ ] `read_orders`
- [ ] `read_products`

Recommended read-only scopes for future Tier 1 reporting expansion, if available and needed:

- [ ] `read_inventory`
- [ ] `read_analytics`
- [ ] `read_price_rules`
- [ ] `read_shipping`

Do not grant write scopes:

- [ ] No `write_products`
- [ ] No `write_inventory`
- [ ] No `write_discounts`
- [ ] No `write_price_rules`
- [ ] No `write_shipping`

Acceptance gate:

- [ ] Custom app exists.
- [ ] Admin API token exists.
- [ ] Token has read-only scopes only.

---

## Phase 3 — Configure Nova locally

Set the environment variables in the same shell session used to start Nova.

PowerShell:

```powershell
$env:NOVA_SHOPIFY_SHOP_DOMAIN = "<store>.myshopify.com"
$env:NOVA_SHOPIFY_ACCESS_TOKEN = "shpat_..."
$env:NOVA_SHOPIFY_API_VERSION = "2026-04"
nova-start
```

cmd.exe:

```cmd
set NOVA_SHOPIFY_SHOP_DOMAIN=<store>.myshopify.com
set NOVA_SHOPIFY_ACCESS_TOKEN=shpat_...
set NOVA_SHOPIFY_API_VERSION=2026-04
nova-start
```

Acceptance gate:

- [ ] Nova starts from the same shell where the variables were set.
- [ ] `system status` shows Shopify connected.
- [ ] No token is committed to the repo.
- [ ] No token is pasted into docs, logs, screenshots, or commits.

---

## Phase 4 — Run Cap 65 live tests

Follow the canonical checklist:

`docs/capability_verification/live_checklists/cap_65_shopify_intelligence_report.md`

Required tests:

- [ ] Basic report: `shopify report`
- [ ] Period report: `shopify report for the last 30 days`
- [ ] Connector-not-configured safe refusal
- [ ] Ledger / Trust receipt verification
- [ ] Read-only confirmation: no writes, no mutations, no confirmation prompt

Acceptance gate:

- [ ] Report returns a structured Shopify intelligence card.
- [ ] Card shows order count, revenue, and active product count.
- [ ] Numbers are plausible for the dev store.
- [ ] Trust receipts show the completed action.
- [ ] No write behavior is observed.

---

## Phase 5 — Sign off and lock Cap 65

Only after all live checklist items pass:

```powershell
python scripts/certify_capability.py live-signoff 65 --notes "all tests pass, read-only confirmed on <store domain>"
python scripts/certify_capability.py lock 65
```

Acceptance gate:

- [ ] Cap 65 live signoff recorded.
- [ ] Cap 65 locked.
- [ ] Current status docs updated if required.

---

## Future Shopify boundary

This section records boundaries only. It is not a next-action list for this TODO.

Future Shopify work, if later approved, must remain separated by authority tier:

- Tier 2: recommendations only, no execution.
- Tier 3: scenario simulation only, no execution.
- Tier 4: governed write execution, dev-store only first.
- Tier 5: marketing/content drafting and explicit publishing approval.
- Tier 6: strategic goal refinement.

Before any write-capable capability exists:

- A separate capability ID must be created.
- Exact Shopify scopes must be defined.
- Explicit user approval must be required.
- Development-store validation must pass first.
- NetworkMediator routing must be proven.
- Ledger and Trust receipt coverage must be proven.
- Rollback or safe-failure behavior must be defined where applicable.

No future Shopify write/operator capability is created, authorized, or implied by this setup TODO.

---

## Done definition

This TODO is complete when:

- [ ] A Shopify development store is connected to Nova.
- [ ] Cap 65 returns a real read-only Shopify report.
- [ ] The report is logged in Trust receipts.
- [ ] No write scope or mutation exists in Cap 65.
- [ ] Cap 65 is live-signed and locked.
