# Nova Solo Business Assistant Implementation Notes

Date: 2026-04-26

Companion to: [`NOVA_SOLO_BUSINESS_ASSISTANT_PRODUCT_VISION.md`](NOVA_SOLO_BUSINESS_ASSISTANT_PRODUCT_VISION.md)

Status: implementation guidance / grounding notes

---

## Purpose

The Solo Business Assistant vision is Nova’s first focused future product direction for independents and small local businesses.

This note explains how to build toward that direction without overstating what currently exists, weakening Nova’s governance model, or jumping too quickly into broad SaaS infrastructure.

---

## Current Truth Boundary

The Solo Business Assistant is a future product layer, not a fully shipped product.

Future work should keep these truths separate:

- Runtime truth comes from generated runtime docs and live code.
- Product vision describes where Nova should go.
- SaaS packaging should come after the core workflow is useful.
- Business-facing language should not erase internal governance requirements.
- Trust receipt backend/API is not currently on `main`; it exists in stranded commit `e9c0187` with follow-up `92baccd` and must be recovered, verified, and hardened before any “What did Nova do?” user surface is treated as real.

---

## Build Order

The correct near-term order remains:

1. Recover stranded trust receipt / Cap 65 work from commit `e9c0187`.
2. Apply follow-up correction commit `92baccd`.
3. Verify files, certification status, and tests.
4. Harden the trust receipt store for missing/corrupt ledger cases.
5. Add targeted receipt-store tests.
6. Complete Cap 64 P5 live signoff and lock.
7. Complete Cap 65 P5 live Shopify checklist and lock.
8. Validate the clean Windows installer path and inspect `C:\Program Files\Nova\bootstrap.log`.
9. Build the first Solo Business Assistant shell.
10. Add core business workflows.
11. Add governed automations.
12. Add SaaS/account/billing layer only after the workflow proves useful.

---

## First Build Slice

The first implementation slice should be intentionally small and demoable.

Suggested shell:

```text
Today in your business

New leads: 0
Follow-ups needed: 0
Quotes waiting: 0
Appointments today: 0
Draft messages ready: 0
Actions sent automatically: 0

[Reply to lead]
[Create quote]
[Show follow-ups]
[What did Nova do?]
```

If real integrations are not ready, this can start with local/manual sample data and explicit draft-only flows.

---

## First Workflow Priority

Build these in order:

### 1. Draft Customer Reply

Lowest risk, highest daily value.

- User enters or pastes a customer message.
- Nova drafts a reply.
- Nova offers edit/copy/open draft/save.
- Nova clearly states it will not send automatically.

### 2. Quote Draft

- User enters customer name, service list, and price.
- Nova creates a clean quote.
- Nova offers copy, email draft, PDF, or save-only.
- Nova does not charge or send.

### 3. Follow-Up Reminder

- User enters a customer/lead and follow-up date.
- Nova creates or suggests a reminder.
- Nova can draft the follow-up text.
- Nova does not send automatically.

### 4. Appointment Confirmation Draft

- User enters appointment details.
- Nova drafts a confirmation message.
- Nova does not send automatically.

### 5. Plain-English Action History

- Depends on trust receipt backend recovery and hardening.
- Should show what Nova did and did not do in user language.

---

## Data Model To Start With

Do not start with a full CRM.

Start with minimal local records:

```text
Lead
- name
- contact method
- request
- status
- last contact date
- next follow-up date
- notes

Quote
- customer name
- services
- price
- status
- created date
- follow-up date

Appointment
- customer name
- date/time
- service
- location
- status

Draft
- type
- customer
- content
- created date
- status
```

This is enough for the first Solo Business Assistant workflows.

---

## Business Rules Implementation

Business Rules should be plain-language wrappers over Nova’s existing governance model.

User-facing examples:

```text
Never send customer messages without approval.
Never post to social media without approval.
Never change prices without approval.
Never delete customer records.
Never charge a customer.
Always show what changed.
Always let me pause automations.
```

Internal mapping can later connect these to:

```text
capability permissions
confirmation requirements
ledger events
network access controls
automation policies
risk levels
```

Do not build a separate unsafe rules system that bypasses the Governor.

---

## SaaS Layer Timing

Do not begin with billing, teams, or broad cloud infrastructure.

SaaS comes after three things are true:

1. A solo operator can complete a useful workflow.
2. The workflow repeats often enough to justify monthly payment.
3. Nova can explain what it did and what it did not do.

Only then add:

```text
accounts
billing
business profiles
template library
optional sync
cloud dashboard
support/onboarding
privacy/export controls
```

---

## What Not To Build First

Do not build these first:

```text
full CRM
team enterprise platform
general automation marketplace
autonomous sales bot
full accounting system
automatic social posting
automatic customer charging
unrestricted agent actions
```

These either add too much complexity or increase risk before the core value is proven.

---

## First Demo Acceptance Criteria

The first demo is successful if a local small-business owner can:

- paste a customer inquiry
- get a useful reply draft
- create a simple quote draft
- set or draft a follow-up reminder
- see that nothing was sent automatically
- understand the approval boundary
- understand what Nova did in plain English

The first demo does not need cloud billing, a full CRM, or autonomous posting.

---

## Product / Governance Balance

The Solo Business Assistant should make Nova feel commercially useful without weakening the system’s reason for existing.

Product layer:

```text
Reply to lead
Create quote
Show follow-ups
What happened today?
```

Governance layer underneath:

```text
approval gates
capability checks
network mediation
ledger events
risk labels
pause/stop controls
```

The user does not need to see the internals unless they choose Owner Mode.

---

## Near-Term Recommendation

After recovering the stranded trust receipt / Cap 65 work and completing Cap 64 close-out, the next real product milestone should be:

> **Solo Business Assistant MVP**

Scope:

```text
one dashboard shell
one lead reply draft flow
one quote draft flow
one follow-up reminder flow
plain-English action history placeholder
Business Rules display
```

Keep it local-first and draft-first.

Do not add SaaS billing until this core flow feels useful.

---

## Final Rule

The first real future of Nova is not “do everything.”

It is:

> help independents and small businesses stop missing customers, quotes, and follow-ups — while keeping every real-world action governed and approved.
