# Nova Solo Business Assistant — Product Decision Record

Date: 2026-04-26

Status: Accepted as first focused future product direction

Related docs:

- [`NOVA_SOLO_BUSINESS_ASSISTANT_PRODUCT_VISION.md`](NOVA_SOLO_BUSINESS_ASSISTANT_PRODUCT_VISION.md)
- [`NOVA_SOLO_BUSINESS_ASSISTANT_IMPLEMENTATION_NOTES.md`](NOVA_SOLO_BUSINESS_ASSISTANT_IMPLEMENTATION_NOTES.md)
- [`NOVA_EVERYDAY_MODE_PRODUCT_VISION.md`](NOVA_EVERYDAY_MODE_PRODUCT_VISION.md)

---

## Decision

Nova’s first focused future product direction is:

> **Nova Solo Business Assistant** — a governed workflow assistant for independent workers and small local businesses.

This direction is more specific than broad Everyday Mode and should be treated as the first practical market wedge for Nova.

The target user is not primarily a developer, enterprise team, or general AI hobbyist.

The target user is an independent operator or small local business owner who needs help with:

```text
customer replies
follow-ups
quotes
appointments
website/social drafts
simple business organization
plain-English action history
safe automations
```

---

## Why This Decision Was Made

Broad “AI productivity SaaS” is too vague and crowded.

Nova’s stronger fit is a specific pain:

> small businesses lose money when owners miss messages, forget follow-ups, delay quotes, or lose track of customer admin.

Nova’s governance model becomes a real differentiator here because small-business users need help, but they also need to trust that AI will not secretly:

```text
send a message
post online
change a price
charge a customer
delete records
publish a website change
modify business data
```

So the product advantage is not just automation.

The advantage is:

> **useful automation under visible user authority.**

---

## Product Thesis

Nova should help independent workers and small businesses:

```text
reply faster
quote faster
follow up consistently
stay organized
know what happened
approve every real action
```

Nova should not start as:

```text
an enterprise platform
a full CRM
a full accounting system
a general agent marketplace
a broad autonomous employee replacement
```

The first product should be small, useful, and trustworthy.

---

## First Product Shape

The first product surface should be a small business command center:

```text
Today in your business

New leads: 2
Follow-ups needed: 3
Quotes waiting: 1
Appointments today: 2
Draft messages ready: 4
Actions sent automatically: 0

[Reply to leads]
[Create quote]
[Show follow-ups]
[What did Nova do?]
```

The first flows should be:

1. Draft customer reply.
2. Create quote draft.
3. Create follow-up reminder.
4. Draft appointment confirmation.
5. Show plain-English action history.

---

## Governance Product Translation

For this market, do not lead with words like:

```text
GovernorMediator
CapabilityRegistry
ExecuteBoundary
NetworkMediator
LedgerWriter
```

Translate them into:

```text
Business Rules
approval before sending
read-only checks
draft first
action history
pause automations
```

Example Business Rules:

```text
Never send customer messages without approval.
Never post to social media without approval.
Never change prices without approval.
Never charge a customer.
Always show what changed.
Always let me pause automations.
```

---

## Implementation Constraint

This is a product direction, not a claim that all features exist today.

The near-term technical sequence still applies:

1. Recover trust receipt work from `e9c0187`.
2. Apply `92baccd`.
3. Verify files, tests, and certification state.
4. Harden trust receipt behavior.
5. Complete Cap 64 and Cap 65 live close-out.
6. Then build the first Solo Business Assistant shell.

Do not skip backend truth reconciliation to build broad UI first.

---

## SaaS Constraint

Do not build the SaaS layer first.

Accounts, billing, cloud dashboard, sync, and plan tiers should wait until the core workflow is useful.

A SaaS product needs:

```text
clear user
painful problem
repeatable workflow
reason to pay monthly
simple onboarding
trustworthy product experience
```

Solo Business Assistant is the likely path to that.

---

## Non-Goals For The First Version

The first version should not include:

```text
team enterprise administration
full CRM replacement
full accounting
unrestricted autonomous sales bot
automatic social posting
automatic customer charging
broad marketplace of agents
```

Those may be future directions only after the first workflow proves useful and trusted.

---

## Accepted Product Statement

Use this as the stable one-sentence direction:

> **Nova is a governed everyday workflow assistant that helps independent workers and small businesses draft, organize, automate, and act safely — while keeping the user in control of real-world actions.**

---

## Practical Next Product Milestone

After the current trust receipt / Cap 64 / Cap 65 recovery and close-out work, build:

> **Solo Business Assistant MVP**

Scope:

```text
one dashboard shell
one customer reply draft flow
one quote draft flow
one follow-up reminder flow
plain-English action history placeholder
Business Rules display
```

Success means a small-business owner can use Nova for a real customer inquiry without understanding the technical system and without worrying that Nova acted behind their back.
