# Nova Everyday Mode Product Vision

Date: 2026-04-26

Status: Future product direction / durable vision note

Purpose: preserve the intended everyday-user direction for Nova so future work does not stay trapped in developer-only dashboards, repo audits, or internal governance language.

---

## Core Direction

To make Nova useful for an everyday non-tech person, stop thinking of it first as an “AI system” and start shaping it as a **personal helper appliance**.

The user should not need to know what a capability, mediator, ledger, branch, local model, token, or OpenClaw is.

They should experience Nova like:

> “This helps me run my day, my home, and my small business — safely — without me needing to understand tech.”

---

## The Everyday-User Version Of Nova

For a normal person with a basic job or small business, Nova should be built around **life situations**, not technical features.

Instead of presenting:

```text
Capabilities
Governor
Ledger
NetworkMediator
OpenClaw
Runtime state
```

Present:

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

Nova’s governance still matters, but it should live underneath the surface.

The user should only see governance when it matters:

```text
Nova can draft this message, but you send it.
Nova can open this page, but not buy anything.
Nova can prepare this customer reply, but not contact them without approval.
Nova can look at your store data, but not change products or prices.
```

That is the balance: **simple outside, governed inside.**

---

## Product Version To Aim For

### 1. The Home Screen Should Be “What Do You Need Help With?”

Not a developer dashboard.

The first screen should look like:

```text
Good morning, Chris.

What do you want to work on?

[Plan my day]
[Reply to messages]
[Work on my business]
[Check appointments]
[Make a website update]
[Create a quote/invoice]
[Research something]
[Explain what I’m looking at]
```

Below that:

```text
Recent activity:
- Drafted client email — not sent
- Checked website leads — read only
- Opened project folder
- No background actions running
```

That gives trust without overwhelming them.

---

## Give Nova Modes Based On Real Life

For a non-tech user, modes should not be “Phase 8” or “governed connector runtime.”

They should be:

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

For someone with a job:

```text
Help me write this email
Summarize meeting notes
Prepare for an interview
Make a schedule
Turn notes into a checklist
Explain a policy
```

### Small Business Mode

For someone running a side business:

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

Most people should never see Owner Mode unless they choose it.

---

# Most Valuable Everyday Features

## 1. Message And Email Helper

This is probably the most useful everyday feature.

The user says:

```text
Help me reply to this customer.
```

Nova asks:

```text
What tone do you want?

[Friendly]
[Professional]
[Short]
[Apologetic]
[Sales focused]
```

Nova drafts the reply.

Then:

```text
I drafted it. I will not send it unless you approve.
```

For normal people, this is huge.

Use cases:

- customer inquiries
- appointment confirmations
- late replies
- refund responses
- estimate follow-ups
- thank-you messages
- job emails
- landlord/tenant messages
- school messages
- business outreach

This should be one of Nova’s core “daily value” paths.

---

## 2. Appointment And Reminder Helper

A normal person should be able to say:

```text
Remind me to call Rob tomorrow at 10.
```

Or:

```text
Book a lawn care estimate for Friday at 3.
```

Nova should show:

```text
I can add this to your calendar:

Lawn care estimate
Friday, May 1
3:00 PM
Reminder: 1 hour before

Approve?
```

For a small business, this becomes powerful:

```text
New inquiry from Sarah:
- wants lawn mowing
- available Saturday
- address in Ypsilanti

Suggested next step:
Send appointment confirmation.
```

---

## 3. Customer Follow-Up Tracker

For a small business, the money is in follow-up.

Nova should have a simple customer board:

```text
Leads
- Sarah — asked about lawn mowing — needs reply
- Mike — quote sent — follow up tomorrow
- Angela — appointment booked — confirm address
- Rob’s Lawn Care — website draft pending photos
```

The user should be able to say:

```text
Who do I need to follow up with today?
```

Nova answers:

```text
You have 3 follow-ups:
1. Mike — quote sent 2 days ago
2. Sarah — no reply sent yet
3. Angela — appointment tomorrow, confirm address
```

This is practical, not flashy.

---

## 4. Quote And Invoice Helper

For everyday small business users, this is big.

Example:

```text
Make a quote for lawn mowing, weed whacking, and debris removal for $150.
```

Nova creates:

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

Then:

```text
Would you like this as:
[Text message]
[Email]
[PDF]
[Save only]
```

Nova should not send or charge anything without approval.

---

## 5. Website Helper

For a small business user, Nova can become:

> “My website person in a box.”

The user says:

```text
Make my homepage sound more professional.
```

Nova responds:

```text
Here is a better version:

Rob’s Lawn Care provides reliable lawn mowing, weed whacking, and debris removal for homeowners in Ypsilanti and nearby areas.

Would you like me to save this as a draft website update?
```

For non-tech users, never say:

```text
Commit to repo?
Push branch?
Open PR?
```

Say:

```text
Save as draft
Preview change
Ask before publishing
```

Under the hood, Nova can still use Git. But the user sees plain language.

---

## 6. “Explain What I’m Looking At”

This is one of Nova’s strongest everyday possibilities.

User says:

```text
What am I looking at?
```

Nova analyzes the screen and says:

```text
This looks like a utility bill.
The amount due is $184.22.
The due date is May 5.
There may be a late fee after that date.

I can help you:
[Summarize it]
[Set reminder]
[Compare to last bill]
[Draft a question to the company]
```

For everyday people, this is magic — but useful magic.

---

# Key Design Rule

## Hide System Complexity Until It Matters

Do not show:

```text
Capability 64 requires P5 lock
NetworkMediator pass
Ledger event written
```

Show:

```text
This will open an email draft.
You review it before sending.
Action will be logged.
Approve?
```

That is the same governance, translated into human language.

---

# What Nova Should Not Do For Everyday Users

Nova should not feel like:

- a coding assistant
- a policy engine
- a terminal wrapper
- a dashboard full of system internals
- a sci-fi autonomous agent
- something that asks too many questions
- something that says “I can’t” constantly
- something that requires setup knowledge

It should feel like:

> “I have a reliable assistant who helps me write, organize, remember, and prepare — but does not secretly act behind my back.”

---

# Best Everyday Nova Flow

## Morning

```text
Nova:
Good morning.

Today:
- 2 appointments
- 3 customer follow-ups
- 1 unpaid invoice draft
- Website inquiry from last night
- No background actions running

What do you want to handle first?
```

User clicks:

```text
Customer follow-ups
```

Nova:

```text
Here are the follow-ups:

1. Sarah — asked about lawn care pricing
2. Mike — quote sent two days ago
3. Angela — appointment tomorrow

Recommended:
Reply to Sarah first.
```

User:

```text
Draft reply.
```

Nova:

```text
Draft:

Hi Sarah, thanks for reaching out. I’d be happy to help with lawn mowing, weed whacking, and debris removal. If you send your address and a few photos of the yard, I can give you a more accurate estimate.

I will not send this unless you approve.

[Edit]
[Open email draft]
[Copy text]
[Save for later]
```

That is the product.

---

# What To Build First

Do not try to make Nova do everything.

Build the **Everyday Assistant Layer** in stages.

## Stage 1 — Plain-Language Home Screen

Create a user-facing dashboard with:

```text
Today
Messages
Business
Appointments
Files
Reminders
Recent actions
```

Not technical panels first.

## Stage 2 — Draft-Only Communication

Build:

```text
Draft email
Draft text message
Draft customer reply
Draft quote follow-up
```

All draft-only. No autonomous sending.

This gives value while staying safe.

## Stage 3 — Small Business Assistant

Add templates for:

```text
New customer inquiry
Quote
Invoice
Follow-up
Appointment confirmation
Website update draft
Social post draft
```

## Stage 4 — Trust Receipts In Plain English

Once the backend is recovered and hardened, show:

```text
What Nova did:
- Drafted email — not sent
- Opened folder
- Checked Shopify data — read only
- Created reminder
```

That is more useful than a raw ledger.

Important: under current repo truth, the trust receipt backend must be recovered from stranded commit `e9c0187` and hardened before this stage is treated as implemented.

## Stage 5 — Guided Setup

Make first-run setup dead simple:

```text
What do you want Nova to help with?

[Personal life]
[Job/work]
[Small business]
[Website]
[Customers]
[Appointments]
```

Then Nova configures the interface around that.

---

# The Small Business Version

For someone like a lawn care owner, bartender, barber, cleaner, mobile detailer, handyman, or restaurant owner, Nova should have a business command center:

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

This is where Nova becomes sellable.

---

# The Non-Tech Setup

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

Not:

```text
Enter model path
Configure connector package
Set environment variable
Choose provider lane
Review runtime hash
```

Those can exist in advanced settings.

---

# Honest Product Positioning

For everyday users, Nova should be described like this:

> Nova is a private local assistant that helps you write, organize, plan, and run small daily tasks. It can draft messages, help with customers, organize follow-ups, explain documents, and prepare actions — but it does not secretly send, buy, post, or change things without your approval.

For small business:

> Nova helps small business owners handle customer messages, quotes, appointments, website updates, reminders, and follow-ups from one simple local assistant.

That is understandable and sellable without hype.

---

# Recommended Product Direction

After recovering the stranded trust receipt work, the next product milestone should be:

## Nova Everyday Mode

A simple mode for non-tech users with five buttons:

```text
Plan my day
Reply to someone
Help my business
Make a document
Explain what I’m looking at
```

Each button opens a guided flow.

That is the bridge between Nova’s deep governance architecture and a real person saying:

> “This actually helps me.”

Nova’s strongest market is not “AI agent for developers.”

It is:

> **A safe everyday assistant for people who need help managing life, work, and small business without giving an AI uncontrolled authority.**

---

# Guardrails For Future Work

- Do not weaken the governance spine to make the product feel easier.
- Translate governance into plain language instead of exposing raw system internals.
- Keep draft-only communication as the safest first high-value feature.
- Do not treat trust receipt UI as implemented until the backend is recovered, tested, and hardened.
- Do not let Owner Mode dominate the everyday-user surface.
- Keep non-tech users away from branches, commits, environment variables, capability IDs, runtime hashes, and certification details unless they explicitly choose an advanced view.
- Everyday Mode should sit on top of Nova’s governance model; it should not replace or bypass it.
