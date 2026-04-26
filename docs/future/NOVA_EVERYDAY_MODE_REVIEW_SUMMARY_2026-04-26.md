# Nova Everyday Mode — Review Summary

Date: 2026-04-26

Related docs:

- [`NOVA_EVERYDAY_MODE_PRODUCT_VISION.md`](NOVA_EVERYDAY_MODE_PRODUCT_VISION.md)
- [`NOVA_EVERYDAY_MODE_IMPLEMENTATION_NOTES.md`](NOVA_EVERYDAY_MODE_IMPLEMENTATION_NOTES.md)
- [`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md)
- [`../../4-15-26 NEW ROADMAP/HANDOFF_2026-04-26_TRUST_RECEIPT_RECOVERY.md`](../../4-15-26%20NEW%20ROADMAP/HANDOFF_2026-04-26_TRUST_RECEIPT_RECOVERY.md)

---

## Executive Summary

Nova’s long-term product direction is **Everyday Mode**: a safe, plain-language assistant for everyday people with normal jobs, homes, side businesses, and small businesses.

The goal is not to make users understand Nova’s internal governance system. The goal is to let them benefit from it without needing to know terms like capability, mediator, ledger, OpenClaw, branch, runtime hash, or certification lock.

The core product translation is:

> **simple outside, governed inside.**

Nova should feel like:

> “I have a reliable assistant who helps me write, organize, remember, and prepare — but does not secretly act behind my back.”

---

## What Nova Should Become For Everyday Users

Nova should become a **personal helper appliance** for life, work, and small business.

The everyday user should see surfaces like:

```text
Today
Messages
Business
Money
Customers
Website
Appointments
Files
Reminders
What changed?
```

They should not be forced to understand:

```text
Capabilities
Governor
Ledger
NetworkMediator
OpenClaw
Runtime state
Branches
Commits
Certification locks
```

Those systems still matter, but they should sit underneath the product surface.

---

## Core Everyday Modes

Everyday Mode should eventually organize Nova around real-life modes:

### Personal Mode

For everyday life:

```text
Plan my day
Make a grocery list
Summarize a document
Help me write a message
Remind me later
Explain this bill
Organize my files
```

### Work Mode

For someone with a basic job or office/job responsibilities:

```text
Help me write this email
Summarize meeting notes
Prepare for an interview
Make a schedule
Turn notes into a checklist
Explain a policy
```

### Small Business Mode

For a side hustle or local small business:

```text
Reply to a customer
Create a quote
Draft an invoice
Make a service list
Update website copy
Check appointments
Prepare a social post
Review a lead
Track follow-ups
```

### Owner Mode

For the builder or advanced users:

```text
Repo status
Runtime truth
Capability locks
OpenClaw recovery
Installer validation
Branch work
```

Owner Mode should exist, but it should not dominate the everyday-user surface.

---

## Highest-Value First Features

The strongest first Everyday Mode features are:

1. **Message and email helper**
   - Draft replies.
   - Ask for tone only when useful.
   - Never send without approval.

2. **Appointment and reminder helper**
   - Create reminders.
   - Prepare calendar entries.
   - Ask before adding or changing anything.

3. **Customer follow-up tracker**
   - Show who needs a reply.
   - Prioritize leads and quote follow-ups.
   - Draft messages, but do not send automatically.

4. **Quote and invoice helper**
   - Create quote drafts.
   - Offer text, email draft, PDF, or save-only output.
   - Never charge, send, or publish without approval.

5. **Website helper**
   - Rewrite homepage copy.
   - Save as draft.
   - Preview changes.
   - Hide Git terminology from non-technical users.

6. **Explain what I’m looking at**
   - Explain bills, pages, forms, documents, or screenshots.
   - Offer next actions such as summarize, set reminder, compare, or draft a question.

---

## The First Shippable Slice

The first real Everyday Mode milestone should be small, not broad.

A five-button interface is enough:

```text
Plan my day
Reply to someone
Help my business
Make a document
Explain what I’m looking at
```

Each button should open a guided flow.

The first flows should be read-only or draft-only wherever possible.

That gives normal users immediate value without widening Nova’s authority too quickly.

---

## Governance Translation Rule

Nova should not weaken governance to feel easier.

Instead, Nova should translate governance into ordinary language.

Do not show everyday users:

```text
Capability 64 requires P5 lock
NetworkMediator pass
Ledger event written
Runtime fingerprint
Branch restore/trust-receipts-cap65
```

Show:

```text
This will open an email draft.
You review it before sending.
This checks data only and will not change anything.
This action will be logged so you can review it later.
Approve?
```

The governance model should remain intact under the surface.

---

## Current Runtime Boundary

This vision is future product direction, not a claim that every feature exists today.

Current runtime truth still matters:

- Nova is a governance-first local AI system.
- Runtime truth is generated from the codebase and should outrank roadmap claims.
- Current generated runtime state lists 27 enabled capabilities.
- Phase 8 and Phase 9 are active.
- Trust Panel system is still not fully implemented in runtime truth.
- Full Phase-8 governed envelope execution remains deferred.
- Trust receipt backend/API is not currently on `main`; it exists in stranded commit `e9c0187` with follow-up `92baccd` and must be recovered before trust receipt UI is treated as live.

Do not present Everyday Mode as already complete.

---

## Correct Implementation Order

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

Do not skip directly to broad UI, dashboard cards, or autonomous flows before backend truth and certification are reconciled.

---

## Non-Technical Setup Principle

A normal person should install Nova and answer questions like:

```text
What is your name?
What do you want Nova to help with?
Do you run a business?
What type?
Do you want reminders?
Do you want email drafting?
Do you want calendar help?
```

They should not start with:

```text
Enter model path
Configure connector package
Set environment variable
Choose provider lane
Review runtime hash
```

Those belong in advanced settings or Owner Mode.

---

## Small Business Command Center Direction

For a small business owner, Nova should become a simple command center:

```text
Business Command Center

Today:
- New leads: 2
- Quotes waiting: 1
- Appointments: 3
- Follow-ups needed: 4
- Website status: live
- Social post drafts: 1
```

Actions:

```text
[Reply to lead]
[Create quote]
[Schedule appointment]
[Draft invoice]
[Update website]
[Make Facebook post]
[Show follow-ups]
```

This is the path where Nova becomes useful and sellable for everyday people.

---

## Acceptance Criteria

Everyday Mode is useful only when a non-technical user can say:

- I know what Nova can help me with today.
- I can draft a message without worrying it was sent automatically.
- I can see what Nova did recently in plain English.
- I can handle a customer follow-up without understanding the underlying system.
- I can use it for my job or small business without seeing code terms.
- I understand when Nova is asking permission and why.
- I feel helped, not managed by a policy engine.

---

## Strategic Recommendation

After the trust receipt recovery and Cap 64/65 close-out work, the next product milestone should be:

> **Nova Everyday Mode**

This should not be treated as a separate product from Nova’s governance architecture. It should be the human-facing layer on top of that architecture.

The strongest market direction is not:

> “AI agent for developers.”

It is:

> **A safe everyday assistant for people who need help managing life, work, and small business without giving an AI uncontrolled authority.**

---

## Final Product Rule

The product layer should make Nova feel easy.

The governance layer should make Nova stay safe.

Everyday Mode succeeds only when both are true:

> **simple outside, governed inside.**
