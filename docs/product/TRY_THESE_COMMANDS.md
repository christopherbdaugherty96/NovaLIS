# Try These Commands

## Everyday Utility
- What works today?
- Summarize today's news
- Explain what Nova can do

## Governance and Proof
- What capabilities are active?
- Explain how actions are controlled.
- Why was that action blocked?
- Show me where governed action receipts are recorded.

After a governed action, inspect:
- `http://localhost:8000/api/trust/receipts`
- `http://localhost:8000/api/trust/receipts/summary`

## Memory and Context
- What do you remember in this session?
- Explain the difference between memory, receipts, and runtime truth.
- Can memory authorize actions?

## Productivity
- Draft an email to `test@example.com` about tomorrow.
  - Confirm only if you want to test local draft opening.
  - Close the draft without sending.
- Turn this into a checklist.
- Search the web and cite sources.

## Connector-Dependent
- Shopify report
  - Requires `NOVA_SHOPIFY_SHOP_DOMAIN` and `NOVA_SHOPIFY_ACCESS_TOKEN`.
  - Current Shopify support is read-only reporting.
