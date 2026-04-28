# Proof Capture Checklist

Last reviewed: 2026-04-28

This checklist explains how to capture human-reviewable proof for governed Nova actions.

It exists to prevent a common documentation failure: automated tests pass, but the repo starts talking like a live human signoff happened when it did not.

## Ground Rules

- Do not fake screenshots, logs, receipts, or certification output.
- Do not mark P5 complete until the live checklist actually passed.
- Do not run lock commands until live signoff passed.
- Redact private email addresses, tokens, store domains, customer names, order numbers, and secrets before committing proof.
- Prefer proof that shows both the user-facing outcome and the backend receipt/ledger evidence.
- If proof is missing, say `ready for human`, `blocked`, or `not yet signed off` instead of complete.

---

## Proof Record Template

Use this table in signoff notes, PR bodies, audit reports, or proof folders.

| Field | Value |
|---|---|
| Capability |  |
| Date |  |
| Operator |  |
| Environment |  |
| Checklist used |  |
| Evidence path / screenshot path |  |
| Receipt event observed |  |
| Result | pass / fail / blocked |
| Notes |  |

---

## Cap 64 — `send_email_draft`

Current expected truth:
- Requires confirmation.
- Opens a local OS mail client draft through `mailto:`.
- Does not use SMTP.
- Does not access an inbox.
- Does not send email autonomously.
- Logs `EMAIL_DRAFT_CREATED` on success.
- Logs `EMAIL_DRAFT_FAILED` on failure.

Live proof should show:

- [ ] Nova prompted for confirmation.
- [ ] The operator typed an accepted confirmation word such as `yes`.
- [ ] A local mail client draft opened.
- [ ] The draft was not sent.
- [ ] `/api/trust/receipts` contains a recent `EMAIL_DRAFT_CREATED` event.
- [ ] The receipt evidence matches the test request.
- [ ] Any screenshot or copied JSON redacts private information.

Required checklist:

```text
docs/capability_verification/live_checklists/cap_64_send_email_draft.md
```

Only after all Cap 64 live checklist items pass:

```text
python scripts/certify_capability.py live-signoff 64
python scripts/certify_capability.py lock 64
```

Do not claim Cap 64 is P5-complete or locked unless those commands succeed and the evidence is committed or referenced.

---

## Cap 65 — `shopify_intelligence_report`

Current expected truth:
- Read-only Shopify intelligence/reporting.
- Requires `NOVA_SHOPIFY_SHOP_DOMAIN`.
- Requires `NOVA_SHOPIFY_ACCESS_TOKEN`.
- Uses read/query behavior only.
- Does not write products.
- Does not write orders.
- Does not write customers.
- Does not perform fulfillment or refunds.
- Does not message customers.

Live proof should show:

- [ ] Nova was started from a shell with the Shopify environment variables set.
- [ ] A Shopify report command returned a structured read-only report.
- [ ] The report used a test/dev store or otherwise safe store context.
- [ ] `/api/trust/receipts` contains the expected governed-action receipt.
- [ ] No Shopify mutation/write behavior was observed.
- [ ] No tokens, store secrets, customer data, or private order details are committed.

Required checklist:

```text
docs/capability_verification/live_checklists/cap_65_shopify_intelligence_report.md
```

Only after all Cap 65 live checklist items pass:

```text
python scripts/certify_capability.py live-signoff 65 --notes "all tests pass, read-only confirmed on <redacted store>"
python scripts/certify_capability.py lock 65
```

Do not claim Cap 65 is P5-complete or locked without credential-backed live proof.

---

## Trust Receipts / Action Receipts

The current proof path should prefer real receipt evidence.

Useful surfaces:

```text
http://localhost:8000/api/trust/receipts
http://localhost:8000/api/trust/receipts/summary
```

Action Receipts and the Trust Receipts API are current proof surfaces. A fuller Trust Review Card / Trust Panel remains future work.

---

## What Not To Commit

Do not commit:
- raw access tokens
- full Shopify customer/order data
- private inbox content
- unredacted personal email addresses unless they are test addresses
- local machine secrets
- screenshots containing unrelated private desktop content

---

## Final Rule

Proof is stronger than claims.

If the proof is not there yet, the correct status is not complete.
It is ready, blocked, or pending human signoff.
