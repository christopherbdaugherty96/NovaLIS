# Nova Solo Business Assistant Product Vision

Date: 2026-04-26

Status: First real future product direction for Nova / durable vision note

Related docs:

- [`NOVA_EVERYDAY_MODE_PRODUCT_VISION.md`](NOVA_EVERYDAY_MODE_PRODUCT_VISION.md)
- [`NOVA_EVERYDAY_MODE_IMPLEMENTATION_NOTES.md`](NOVA_EVERYDAY_MODE_IMPLEMENTATION_NOTES.md)
- [`NOVA_EVERYDAY_MODE_REVIEW_SUMMARY_2026-04-26.md`](NOVA_EVERYDAY_MODE_REVIEW_SUMMARY_2026-04-26.md)

---

## Executive Summary

Nova’s first real future should be focused on **independents and very small businesses**.

The sharper product direction is not a broad “AI productivity assistant.” It is:

> **A governed workflow assistant for independent workers and small local businesses that helps them handle customers, quotes, follow-ups, appointments, documents, website updates, and safe automations without giving AI uncontrolled authority.**

This is more specific, easier to explain, easier to sell, and better aligned with Nova’s core philosophy:

> **AI can help with work, but real-world actions must stay governed, visible, logged, and user-approved.**

The product promise for independents is:

> **Nova helps you run the admin side of your small business without hiring an assistant — and without letting AI secretly send, post, charge, or change things without your approval.**

Even simpler:

> **Nova helps small business owners stop missing messages, quotes, and follow-ups.**

---

## Who This Is For

Nova Solo Business Assistant is for independent workers, side hustlers, solo operators, and small local businesses.

Examples:

```text
lawn care owners
mobile bartenders
barbers
cleaners
handymen
mobile detailers
small restaurants
food trucks
photographers
solo web designers
local consultants
salon owners
fitness trainers
home service providers
side hustlers
```

These users usually do not need an enterprise AI platform.

They need help with everyday business admin:

```text
Answer customers faster
Stop missing follow-ups
Create quotes
Book appointments
Send reminders
Make basic website/social updates
Keep track of who needs what
Know what happened today
```

---

## The Pain Nova Should Solve

Small businesses and independent workers lose money from simple workflow gaps:

```text
forgot to reply
forgot to follow up
quote never sent
customer details scattered in texts
appointment not confirmed
website out of date
no reminder system
no simple CRM
social posts inconsistent
business owner overwhelmed
```

Nova should be the assistant that says:

```text
You have 3 people to follow up with today.
Sarah asked for lawn mowing pricing.
Mike got a quote 2 days ago and has not replied.
Angela has an appointment tomorrow and needs confirmation.
Would you like me to draft those replies?
```

That is immediately useful.

---

## Product Identity

Nova should be positioned for this market as:

> **A safe AI admin assistant for independent workers and small businesses. It helps manage leads, customer replies, quotes, appointments, reminders, website copy, and follow-ups — while keeping you in control of every real action.**

A shorter sales hook:

> **Nova helps small business owners stop missing messages, quotes, and follow-ups.**

A more technical version for advanced users:

> **Nova is a governed workflow assistant that separates AI reasoning from execution authority.**

But the everyday small-business user should mostly hear:

> **Nova helps you reply faster, quote faster, follow up consistently, stay organized, and approve every real action.**

---

## Small-Business Command Center

The product should center around a small-business command center, not a developer dashboard.

Example home screen:

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
[Schedule appointment]
[Draft invoice]
[Update website]
[Make social post]
[Show follow-ups]
[What did Nova do?]
```

The line `Actions sent automatically: 0` is important. It turns Nova’s governance into a visible trust advantage.

---

## Core Product Promise

For independents and small businesses, Nova should promise:

```text
Reply faster.
Quote faster.
Follow up consistently.
Stay organized.
Know what happened.
Approve every real action.
```

Nova should not promise to “replace an employee” or “run your whole business automatically.”

The promise is simpler and stronger:

> **Nova handles the messy admin work around customers and follow-ups while keeping the owner in control.**

---

## Best First Workflows

Do not start with everything.

Start with the work every independent hates and the work that directly affects revenue.

---

### 1. Lead Reply

Customer asks:

```text
“How much for lawn mowing?”
```

Nova responds:

```text
I drafted a reply asking for address, yard size, and photos.

[Edit]
[Copy]
[Open text/email draft]
[Save]
```

Example draft:

```text
Hi Sarah, thanks for reaching out. I’d be happy to help with lawn mowing, weed whacking, and debris removal. Could you send your address and a few photos of the yard? I can give you a more accurate estimate from there.
```

Trust line:

```text
Nova will not send this automatically.
```

---

### 2. Quote Draft

User says:

```text
Create a quote for Sarah:
- lawn mowing
- weed whacking
- debris removal
- total $150
```

Nova creates a clean quote:

```text
Quote for Sarah

Services:
- Lawn mowing
- Weed whacking
- Debris removal

Total: $150

Terms:
Payment due at completion.
Quote valid for 7 days.
```

Options:

```text
[Edit]
[Copy]
[Open email draft]
[Save as PDF]
[Save only]
```

Nova should not send, charge, or publish anything without approval.

---

### 3. Follow-Up Reminder

Nova notices:

```text
Mike got a quote 2 days ago.
```

Suggested follow-up:

```text
Hi Mike, just checking in to see if you had any questions about the quote.
```

Options:

```text
[Edit]
[Copy]
[Open draft]
[Remind me tomorrow]
[Mark done]
```

---

### 4. Appointment Confirmation

Nova sees:

```text
Angela is scheduled tomorrow at 3 PM.
```

Nova asks:

```text
Draft confirmation?
```

Example:

```text
Hi Angela, just confirming your appointment for tomorrow at 3 PM. Please let me know if anything changes. Thank you!
```

Options:

```text
[Edit]
[Copy]
[Open message draft]
[Save]
```

---

### 5. Website / Social Update

User says:

```text
Turn this into a Facebook post:
“Spring cleanup openings this weekend.”
```

Nova drafts:

```text
Spring cleanup openings are available this weekend. If your yard needs mowing, weed whacking, or debris removal, send a message to get on the schedule.
```

Options:

```text
[Edit]
[Copy]
[Save draft]
[Ask before posting]
```

Do not post automatically by default.

---

### 6. What Happened Today?

User asks:

```text
What happened today?
```

Nova should eventually show:

```text
Today Nova:
- drafted 3 customer replies
- created 1 quote draft
- reminded you about 2 follow-ups
- checked website copy
- sent nothing automatically
```

That last line is the trust differentiator.

This flow depends on trust receipt recovery and hardening before it should be treated as real product functionality.

---

## Business Rules, Not Technical Governance

For independents, call them **Business Rules**, not governance.

Example:

```text
Nova Business Rules

- Never send customer messages without approval.
- Never post to social media without approval.
- Never change prices without approval.
- Never delete customer records.
- Never charge a customer.
- Always show what changed.
- Always let me pause automations.
```

This is the small-business version of Nova’s governance philosophy.

Advanced mode can map those rules to:

```text
capability permissions
execution gates
network rules
approval requirements
ledger events
automation policies
```

But small-business users should see plain-language rules.

---

## Governed Automation Levels

Nova should support automation levels that are easy to understand.

### Level 1 — Suggest

```text
Nova notices Sarah needs a follow-up.
Nova suggests a reply.
Nothing happens automatically.
```

### Level 2 — Draft

```text
Nova drafts the reply and saves it.
User reviews later.
```

### Level 3 — Prepare

```text
Nova prepares a quote, calendar event, or website update.
User approves before final action.
```

### Level 4 — Approved Automation

```text
Every Friday at 5 PM, Nova creates a weekly report and shows me a draft.
```

### Level 5 — Limited Delegated Action

Only for low-risk, user-approved tasks:

```text
Move completed notes to an archive folder.
Create a reminder.
Generate a weekly PDF.
Update an internal dashboard.
```

### Level 6 — High-Risk Actions

Always require approval:

```text
send email
post online
charge customer
change website live
delete files
make purchases
change prices
modify business records
```

This should be built into Nova’s product language.

---

## What Nova Should Not Be At First

Do not start with:

```text
team enterprise platform
general agent marketplace
full accounting system
full CRM
autonomous sales bot
AI employee replacement
```

Start with:

```text
reply faster
quote faster
follow up consistently
stay organized
know what happened
approve every real action
```

---

## First Paid Product

The first paid SaaS-style product should be:

# Nova Solo Business Assistant

For one-person and small local businesses.

Included:

```text
Lead tracker
Customer follow-up board
Quote drafts
Invoice drafts
Appointment reminders
Message drafting
Website copy drafts
Social post drafts
Plain-English action history
Business Rules / approval controls
```

Avoid calling it a CRM at first.

Say:

> “A simple AI assistant for your business follow-ups and customer admin.”

---

## Why This Is Better Than Broad SaaS

Broad SaaS is too vague.

“AI productivity assistant” competes with everyone.

But:

> “AI assistant for local small businesses that drafts replies, quotes, and follow-ups safely”

is specific.

It fits existing Nova-adjacent projects and interests:

```text
Pour Social
Auralis Digital
Rob’s Lawn Care
local businesses without websites
lead generation
customer communication
quotes
appointments
safe automation
```

This connects the projects together.

---

## Possible Product Tiers

Pricing should not be finalized until the workflow is real, but possible tiers are:

### Starter

```text
Draft replies
Follow-up reminders
Quote templates
Basic business dashboard
Manual approval required
```

### Solo Pro

```text
Lead tracker
Appointment helper
Website/social drafts
Plain-English action history
Recurring follow-up reminders
```

### Local Business

```text
Multiple service templates
Customer pipeline
Calendar integration
Website update drafts
Monthly business reports
More automation rules
```

### Operator / Advanced

```text
Shopify reporting
Website management
OpenClaw/local worker
Custom workflows
Advanced governance rules
```

---

## First Demo Scenario

A lawn care owner opens Nova.

```text
Nova:
You have 4 business items today.

1. Sarah asked for mowing pricing.
2. Mike needs a quote follow-up.
3. Angela has an appointment tomorrow.
4. Your spring cleanup post is drafted but not posted.

Recommended:
Reply to Sarah first.

[Draft reply]
[Create quote]
[Show all follow-ups]
```

Owner clicks **Draft reply**.

```text
Nova:
Draft:

Hi Sarah, thanks for reaching out. I’d be happy to help with lawn mowing, weed whacking, and debris removal. Could you send your address and a few photos of the yard? I can give you a more accurate estimate from there.

Nova will not send this automatically.

[Edit]
[Copy]
[Open email/text draft]
[Save]
```

That is the product.

---

## SaaS Direction

Nova can become SaaS, but not by becoming a vague cloud chatbot.

The SaaS should form around useful, repeatable independent-business workflows:

```text
lead capture
customer replies
quote drafts
follow-up reminders
appointment confirmations
website/social drafts
plain-English action history
business rules
approved automations
```

A future SaaS architecture may include:

```text
accounts
billing
business profile
workflow templates
cloud dashboard
optional sync
connector setup
support/onboarding
privacy/export controls
```

But the core workflow must be useful before billing and cloud layers matter.

---

## Product Roadmap Order

Given Nova’s current state, the order should be:

### Step 1 — Recover Trust Receipt Work

Recover:

```text
e9c0187
92baccd
```

Verify and merge.

### Step 2 — Finish Cap 64

Get email draft live signoff and lock.

This matters because draft communication is core to Solo Business Assistant.

### Step 3 — Harden Trust Receipts

People need to see:

```text
What did Nova do?
What did Nova not do?
What is waiting for approval?
```

### Step 4 — Build Solo Business Shell

Simple dashboard and a few guided flows.

### Step 5 — Build Core Business Workflows

```text
lead reply
quote draft
follow-up reminder
appointment confirmation
website/social draft
what happened today
```

### Step 6 — Add Governed Automations

Start with safe automations:

```text
reminders
draft reports
draft replies
follow-up suggestions
weekly summaries
```

### Step 7 — SaaS Layer

Only after the workflow is useful:

```text
accounts
billing
cloud dashboard
sync
templates
business profiles
```

---

## Key Warning

Do not try to become SaaS before the core workflow feels useful.

A SaaS product is not just cloud hosting plus billing.

A SaaS product means:

```text
A clear user
A painful problem
A repeatable workflow
A reason to pay monthly
A simple onboarding path
A trustworthy product experience
```

For Nova, the first paying user is probably not a developer.

It is someone like:

```text
I run a lawn care business and I forget to follow up.
I do mobile bartending and need help with quotes/messages.
I do web design and need help managing leads.
I run a barbershop and want appointment/message help.
I work a normal job and need help staying organized.
```

Build for that person.

---

## Final One-Sentence Version

> **Nova is a governed everyday workflow assistant that helps independent workers and small businesses draft, organize, automate, and act safely — while keeping the user in control of real-world actions.**

---

## Guardrails

- Focus on independents and small local businesses first.
- Do not make Nova a broad generic AI productivity SaaS.
- Keep first workflows close to revenue and admin pain: replies, quotes, follow-ups, appointments.
- Keep communication draft-first.
- Require approval for sending, posting, charging, publishing, deleting, changing prices, or modifying business records.
- Turn governance into plain-language Business Rules.
- Build the SaaS layer after the workflow is useful, not before.
- Keep the owner in control of every real-world action.
