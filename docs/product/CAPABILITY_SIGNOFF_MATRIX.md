# Capability Signoff Matrix

Last reviewed: 2026-04-28

This is a human-facing snapshot of capability proof status.

Use the certification script for exact live pass/fail state:

```text
python scripts/certify_capability.py status
```

Generated runtime docs remain the authority for exact active capability surface. This matrix explains readiness in plain language.

---

## Status Labels

| Label | Meaning |
|---|---|
| P1–P4 passed | Automated unit/routing/integration/API checks are reported passing. |
| Ready for human P5 | Automated proof is strong, but a human still needs to run live local proof. |
| Blocked on credentials | Live proof requires external credentials or account setup. |
| Locked | Do not use this label unless the certification script and committed evidence prove lock succeeded. |
| Future / not started | Planned or active capability without full proof path yet. |

---

## Highlighted Capabilities

| Capability | Current Status | Human Truth |
|---|---|---|
| Cap 64 — `send_email_draft` | P1–P4 passed; P5 ready for human | Opens a local `mailto:` draft after confirmation. Nova does not use SMTP, access an inbox, or send email autonomously. Human must review and send manually. |
| Cap 65 — `shopify_intelligence_report` | P1–P4 passed; P5 blocked on credentials | Read-only Shopify reporting/intelligence. Requires `NOVA_SHOPIFY_SHOP_DOMAIN` and `NOVA_SHOPIFY_ACCESS_TOKEN`. No product/order/customer writes, fulfillment, refunds, or customer messaging. |
| Action Receipts / trust receipts | Implemented, maturing UX | Visible receipt surface and `/api/trust/receipts` exist. Fuller Trust Panel remains future work. |
| Memory / continuity | Implemented, evolving UX | Supports continuity and reasoning context. Memory is not authority and cannot bypass governance. |
| Scheduler / background loop | Gated / bounded where present | Must remain settings-controlled, permissioned, capped, and unable to bypass governance. Not broad hidden autonomy. |

---

## Current Human Signoff Queue

1. **Cap 64 P5 live signoff**
   - Run Nova locally with a configured mail client.
   - Follow `docs/capability_verification/live_checklists/cap_64_send_email_draft.md`.
   - Confirm the local draft opens.
   - Confirm no email is sent automatically.
   - Confirm `EMAIL_DRAFT_CREATED` appears in trust receipts.
   - Only then run live-signoff and lock commands.

2. **Cap 65 P5 live signoff**
   - Use a Shopify developer or test store first.
   - Set `NOVA_SHOPIFY_SHOP_DOMAIN` and `NOVA_SHOPIFY_ACCESS_TOKEN` in the same shell that starts Nova.
   - Follow `docs/capability_verification/live_checklists/cap_65_shopify_intelligence_report.md`.
   - Confirm read-only behavior.
   - Only then run live-signoff and lock commands.

---

## Do Not Overclaim

Do not say:
- Cap 64 sends email.
- Cap 64 is P5 complete before human local proof.
- Cap 64 is locked before certification proves it.
- Cap 65 writes to Shopify.
- Cap 65 is P5 complete without real credentials and live proof.
- Action Receipts equal a complete Trust Panel.
- Memory can authorize actions.
- Scheduler equals broad autonomy.

---

## Why This Matrix Exists

Capability status can become misleading if automated tests, local proof, live credentials, and user-facing docs are mixed together.

This matrix keeps those layers separate:

- tests show implementation confidence
- live signoff shows real local proof
- lock means the capability passed the defined certification process
- docs explain the current human-facing truth
