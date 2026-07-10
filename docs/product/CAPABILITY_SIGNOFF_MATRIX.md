# Capability Signoff Matrix

Last reviewed: 2026-07-09 (synced to `python scripts/certify_capability.py status`: 4/27 locked — Cap 16, 22, 64, 65)

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
| Cap 64 — `send_email_draft` | Locked (P1–P5 passed, 2026-05-20) | Opens a local `mailto:` draft after confirmation. Nova does not use SMTP, access an inbox, or send email autonomously. Human must review and send manually. Locked = bounded, not expandable. |
| Cap 65 — `shopify_intelligence_report` | Locked (P1–P5 passed, 2026-05-22) | Read-only Shopify reporting/intelligence, live credential-backed proof recorded. No product/order/customer writes, fulfillment, refunds, or customer messaging. Locked = bounded, not expandable. |
| Action Receipts / trust receipts | Implemented, maturing UX | Visible receipt surface and `/api/trust/receipts` exist. Fuller Trust Panel remains future work. |
| Memory / continuity | Implemented, evolving UX | Supports continuity and reasoning context. Memory is not authority and cannot bypass governance. |
| Scheduler / background loop | Gated / bounded where present | Must remain settings-controlled, permissioned, capped, and unable to bypass governance. Not broad hidden autonomy. |

---

## Current Human Signoff Queue

The queue is empty. Cap 64 and Cap 65 both completed P5 live signoff and locked
(2026-05-20 and 2026-05-22; closeout: `docs/status/APPROVAL_GATE_CERTIFICATION_CLOSEOUT_2026-05-19.md`
and Cap 65 evidence recorded in `docs/status/CURRENT_WORK_STATUS.md`).

The historical checklists remain at
`docs/capability_verification/live_checklists/` as the procedure record. Re-running
them requires a new P1-P5 lock decision — locks are not reopened casually.

---

## Do Not Overclaim

Do not say:
- Cap 64 sends email.
- Cap 65 writes to Shopify.
- A lock authorizes scope expansion (locked = bounded, not expandable).
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
