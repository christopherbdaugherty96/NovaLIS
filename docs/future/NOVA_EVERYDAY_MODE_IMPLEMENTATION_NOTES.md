# Nova Everyday Mode Implementation Notes

Date: 2026-04-26

Companion to: [`NOVA_EVERYDAY_MODE_PRODUCT_VISION.md`](NOVA_EVERYDAY_MODE_PRODUCT_VISION.md)

Status: implementation guidance / grounding notes

---

## Why This Exists

The Everyday Mode product vision captures Nova’s future user-facing direction: a safe everyday assistant for life, work, and small business.

This implementation note prevents the vision from being mistaken for current runtime truth.

The vision should guide product direction, UX design, and feature prioritization, but it does **not** mean every feature described there exists today.

---

## Current Truth Boundary

As of this note:

- Nova remains a governance-first local AI system.
- Everyday Mode is a future product layer, not a fully implemented user mode.
- Non-technical users should eventually see plain-language flows, not capability IDs, runtime hashes, branch names, or certification details.
- Governance must stay underneath the product surface.
- Everyday Mode must not bypass GovernorMediator, CapabilityRegistry, ExecuteBoundary, NetworkMediator, or LedgerWriter.
- Trust receipt UI should not be treated as implemented until the backend is recovered onto `main`, tested, and hardened.

---

## Implementation Order

The correct near-term order is:

1. Recover stranded trust receipt / Cap 65 work from commit `e9c0187`.
2. Apply follow-up correction commit `92baccd`.
3. Verify files, certification status, and tests.
4. Harden the trust receipt store for missing/corrupt ledger cases.
5. Add targeted receipt-store tests.
6. Complete Cap 64 P5 live signoff and lock.
7. Complete Cap 65 P5 live Shopify checklist and lock.
8. Validate the clean Windows installer path and inspect `C:\Program Files\Nova\bootstrap.log`.
9. Start the Everyday Mode UX layer with the smallest useful non-technical flows.

Do not skip directly to a dashboard card or broad Everyday Mode UI before the backend truth is restored and verified.

---

## First Everyday Mode Slice

The first shippable Everyday Mode slice should be intentionally small:

```text
Plan my day
Reply to someone
Help my business
Make a document
Explain what I’m looking at
```

Each button should open a guided flow.

The first flows should be draft-only or read-only wherever possible.

---

## Highest-Value First Flows

### 1. Draft Customer Reply

User-facing wording:

```text
Help me reply to this customer.
```

Nova should:

- ask for tone only when helpful
- draft the reply
- offer edit/copy/open draft/save options
- clearly state that it will not send without approval

### 2. Quote / Invoice Draft

User-facing wording:

```text
Make a quote for lawn mowing, weed whacking, and debris removal for $150.
```

Nova should:

- produce a clean quote
- offer output options such as text, email draft, PDF, or save only
- avoid charging, sending, or publishing without approval

### 3. Follow-Up List

User-facing wording:

```text
Who do I need to follow up with today?
```

Nova should:

- list leads/customers needing action
- prioritize the most urgent follow-up
- draft messages but not send them automatically

### 4. Plain-English Recent Actions

User-facing wording:

```text
What did Nova do today?
```

Nova should eventually show:

```text
- Drafted email — not sent
- Opened folder
- Checked Shopify data — read only
- Created reminder
```

This depends on trust receipt backend recovery and hardening.

---

## UX Translation Rule

Internal truth should be translated before it reaches non-technical users.

Do not show ordinary users:

```text
Capability 64
P5 lock
NetworkMediator
Ledger event type
Runtime fingerprint
Branch restore/trust-receipts-cap65
```

Show:

```text
This opens an email draft.
You review it before sending.
This checks data only and will not change anything.
This action will be logged so you can review it later.
```

Owner Mode can expose technical truth, but Everyday Mode should default to human language.

---

## Everyday Mode Non-Goals

Everyday Mode should **not** become:

- a replacement for the governance spine
- an unrestricted autonomous agent
- a developer dashboard with friendlier labels
- a branch/commit workflow for normal users
- a place where Nova sends, buys, posts, publishes, or changes things silently
- a feature that hides meaningful risk from the user

---

## Acceptance Criteria For Everyday Mode

A first Everyday Mode version is useful only if a non-technical user can answer “yes” to these:

- I know what Nova can help me with today.
- I can draft a message without worrying it was sent automatically.
- I can see what Nova did recently in plain English.
- I can handle a customer follow-up without understanding the underlying system.
- I can use it for my job or small business without seeing code terms.
- I understand when Nova is asking permission and why.
- I feel helped, not managed by a policy engine.

---

## Product Principle

The product layer should make Nova feel easy.

The governance layer should make Nova stay safe.

Everyday Mode succeeds only when both are true:

> simple outside, governed inside.
