# Trust Review Card Plan

Last reviewed: 2026-04-28

## Current Truth

Nova already has initial proof surfaces:

- `/api/trust/receipts` exposes recent receipt-worthy governed-action ledger events.
- `/api/trust/receipts/summary` exposes a compact receipt summary.
- Dashboard Action Receipts are the visible UI surface when available, but the API remains the direct proof source.
- This document now describes the fuller Trust Review Card / Trust Panel direction, not a from-scratch proof surface.

The remaining gap is richer user-facing review: clearer blocked reasons, confirmation-state preview, proof browsing, and a stronger demo flow.

---

## Purpose

Users should not need to inspect source code or backend logs to understand what the system did.

The fuller Trust Review Card should make governed actions legible before, during, and after execution.

It should explain:

1. What the user asked for
2. What Nova understood
3. Whether a real action is involved
4. Which capability is allowed to act
5. Whether confirmation is required
6. What happened
7. Where the receipt/proof can be inspected

---

## Current Receipt Surfaces

Current surfaces to build from:

- Trust Receipts API: `/api/trust/receipts`
- Trust Receipts summary API: `/api/trust/receipts/summary`
- Dashboard Action Receipts when available
- Ledger-backed governed-action events
- Capability live checklists for proof capture

These are real proof surfaces. The fuller Trust Review Card should extend them rather than replace them with mock UI.

---

## What The Fuller Card Should Show

For any governed action, a Trust Review Card can display:

1. User request
2. Detected intent
3. Capability selected
4. Why it was allowed or blocked
5. Whether confirmation was required
6. Current state: pending, confirmed, completed, blocked, failed
7. Result summary
8. Ledger event / receipt event
9. Timestamp / receipt link
10. Next safe user action

---

## Example — Cap 64 Email Draft

```text
Request: Draft an email to John about tomorrow
Intent: create local email draft
Capability: send_email_draft
Status: Allowed with confirmation
Receipt event: EMAIL_DRAFT_CREATED
Result: Draft opened in local mail client
Boundary: Nova did not send email; user must review and send manually
```

This distinction matters. Cap 64 is a draft/manual-send flow, not autonomous email sending.

---

## Why It Matters

- Converts invisible governance into visible value
- Builds user trust faster
- Makes demos clearer
- Helps debugging
- Distinguishes Nova from generic agent wrappers
- Shows that memory/context do not authorize action
- Makes capability proof easier to capture

---

## Scope Guidance

Build on what exists:

- improve latest action card clarity
- improve recent receipts list
- add blocked-action explanation
- add confirmation-state preview
- add direct receipt/proof links
- show safe next step after completion/failure

Do not wait for a perfect dashboard redesign.

---

## Truth Constraint

The UI should reflect real ledgered events and runtime decisions, not mock data or marketing claims.

Do not claim:

- Action Receipts equal a complete Trust Panel
- Cap 64 sends email
- Cap 65 writes to Shopify
- memory authorizes execution
- scheduler/background loops are broad autonomy
- P5 signoff is complete without live proof

The Trust Review Card exists to make authority boundaries visible, not to widen them.
