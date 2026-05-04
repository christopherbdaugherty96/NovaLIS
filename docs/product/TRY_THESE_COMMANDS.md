# Try These Commands

## Everyday Utility
- What works today?
- Summarize today's news
- Explain what Nova can do

## Memory
- remember: My preferred tone is concise
- review memories
- why-used

Notes:
- Memory is explicit and receipted
- Memory provides context only and does not authorize actions

## Planning
- Plan my week

Notes:
- Produces a structured plan
- Records approval decisions
- Does not execute actions

## Governance and Proof
- What capabilities are active?
- Explain how actions are controlled
- Why was that action blocked?

After a governed action, inspect:
- `http://localhost:8000/api/trust/receipts`
- `http://localhost:8000/api/trust/receipts/summary`

## Productivity
- Draft an email to `test@example.com` about tomorrow

Notes:
- Opens a local mail client draft
- Nova does not send email

## Search
- Search for [topic]

Notes:
- Results include sources and confidence
- This is read-only and does not trigger actions

## Connector-Dependent
- Shopify report

Notes:
- Requires `NOVA_SHOPIFY_SHOP_DOMAIN` and `NOVA_SHOPIFY_ACCESS_TOKEN`
- Current Shopify support is read-only reporting
