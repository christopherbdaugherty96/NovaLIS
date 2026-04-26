# Nova Role-Based Assistant Core Vision

Date: 2026-04-26

Status: Core future product vision / umbrella direction

Related docs:

- [`NOVA_EVERYDAY_TASK_SERVICE_EXPANSION_2026-04-26.md`](NOVA_EVERYDAY_TASK_SERVICE_EXPANSION_2026-04-26.md)
- [`NOVA_SOLO_BUSINESS_ASSISTANT_PRODUCT_VISION.md`](NOVA_SOLO_BUSINESS_ASSISTANT_PRODUCT_VISION.md)
- [`NOVA_SOLO_BUSINESS_ASSISTANT_DECISION_RECORD_2026-04-26.md`](NOVA_SOLO_BUSINESS_ASSISTANT_DECISION_RECORD_2026-04-26.md)
- [`NOVA_EVERYDAY_MODE_PRODUCT_VISION.md`](NOVA_EVERYDAY_MODE_PRODUCT_VISION.md)

---

## Executive Summary

Nova’s core future is bigger than a small-business assistant and broader than a generic productivity tool.

The core idea is:

> **Nova is a role-based governed assistant for home, work, everyday tasks, and small business.**

The user should be able to direct Nova into the role they need:

```text
Home Assistant
Personal Assistant
Work Helper
Business Assistant
Business Manager
Research Assistant
File Organizer
Owner Mode
```

Each role changes Nova’s priorities, dashboard, suggested workflows, and vocabulary.

But every role shares the same foundation:

```text
real-world actions stay bounded
high-risk actions require approval
actions are logged
users can review what happened
users can pause or stop automations
Nova does not secretly take authority
```

The short brand-level phrase is:

> **Your assistant, under your rules.**

Longer explanation:

> Nova helps with home, work, and business tasks — drafting, organizing, summarizing, filling forms, managing follow-ups, and automating safe workflows — while keeping real-world actions governed and approved.

---

## Core Product Idea

Nova should become a practical local assistant for real home, work, and business tasks, not a fantasy assistant where AI controls everything.

Nova should be:

> **A useful assistant under user-defined rules.**

Nova can help with real tasks, prepare work, automate safe steps, and manage workflows, but the user remains the authority.

Nova is not:

```text
AI controls everything
AI knows everything
AI acts freely for the user
AI sends, posts, buys, deletes, submits, or changes things silently
```

Nova is:

```text
AI helps with real tasks
AI prepares work
AI manages workflow queues
AI automates low-risk steps when allowed
AI asks before important actions
AI logs what happened
AI keeps the user in control
```

---

## Role-Based Nova

Nova should not be locked into one fixed identity.

The user should be able to say:

```text
Nova, be my home assistant.
Nova, be my personal assistant.
Nova, be my work helper.
Nova, be my business assistant.
Nova, be my business manager.
Nova, be my research analyst.
Nova, be my file organizer.
Nova, switch to Owner Mode.
```

Each role should adjust:

```text
what Nova pays attention to
which workflows are surfaced first
which dashboard cards appear
what language Nova uses
which rules are shown
which automations are available
which approval boundaries are most visible
```

The role changes the product surface, not the governance spine.

---

## Main Roles

### 1. Home Assistant Mode

This is the home-life version of Nova.

Nova helps with:

```text
reminders
household tasks
shopping lists
bills
appointments
family schedules
documents
forms
home maintenance
basic device actions
explaining what is on screen
summarizing mail/documents
```

Example experience:

```text
User:
Nova, what do I need to handle around the house today?

Nova:
You have 4 home items:
1. Electric bill due Friday.
2. Oil change reminder next week.
3. Grocery list is missing dog food.
4. Rob’s lawn care estimate needs confirmation.

I can help you:
[Set reminders]
[Draft a message]
[Make a checklist]
[Explain a bill]
```

This is a practical governed home assistant, not uncontrolled sci-fi autonomy.

---

### 2. Personal Assistant Mode

This role helps with personal life admin.

Nova helps with:

```text
emails
forms
calendar
appointments
task lists
notes
documents
phone call scripts
decision summaries
```

Example:

```text
User:
Help me fill out this form.

Nova:
I can help prepare the form.
I will not submit it without approval.

I can fill in:
- name
- address
- phone
- email

I still need:
- employer name
- income field
- signature confirmation
```

This is especially useful for people who are not good with computers or do not want to fight with forms, websites, and digital paperwork.

---

### 3. Work Helper Mode

This role is for someone with a basic job or everyday work tasks.

Nova helps with:

```text
summarizing work emails
drafting replies
turning instructions into steps
making checklists
preparing reports
summarizing policies
organizing documents
planning the day
```

Example:

```text
User:
Summarize what I need to do from these emails.

Nova:
Here are your work tasks:
1. Reply to Amanda about the schedule.
2. Review the policy update.
3. Send the inventory count by 3 PM.
4. Follow up on the customer issue.

I can draft the first reply if you want.
```

This role should feel like:

> “Nova helps me get through my work tasks without needing to be good with software.”

---

### 4. Business Assistant Mode

This role is for independents, side hustlers, and small businesses.

Nova helps with:

```text
customer replies
quotes
invoices
follow-ups
appointments
website/social drafts
lead tracking
simple CRM
business reminders
```

Example:

```text
User:
Act as my business assistant today.

Nova:
Today in your business:
- 2 new leads
- 3 follow-ups needed
- 1 quote waiting
- 2 appointments
- 0 actions sent automatically

Recommended:
Reply to Sarah first. She asked about pricing yesterday.
```

This role connects directly to the Solo Business Assistant product direction.

---

### 5. Business Manager Mode

Business Manager Mode is one level above Business Assistant.

It does not mean Nova becomes the boss or acts freely.

It means Nova helps manage the workflow:

```text
who needs follow-up
what quotes are open
what appointments are coming
what tasks are overdue
what content is drafted
what needs approval
what changed today
```

Example:

```text
Nova:
You are falling behind on follow-ups.

Priority list:
1. Mike — quote sent 3 days ago, no response.
2. Sarah — asked for pricing, no reply drafted.
3. Angela — appointment tomorrow, confirmation not sent.

I recommend handling these in order.
```

Business Manager Mode should say:

```text
I recommend this.
I prepared this.
I need your approval before sending.
```

It should not silently send, post, charge, delete, or change records.

---

### 6. Research / News Assistant Mode

Nova helps with:

```text
summarizing articles
tracking topics
comparing sources
creating briefs
explaining news
watching trends
```

Example:

```text
User:
Summarize the latest news about AI agents.

Nova:
Here are the main points:
1. ...
2. ...
3. ...

What matters for Nova:
- ...

Risks:
- ...

Recommended:
- ...
```

This connects to Nova’s existing intelligence brief, headline summary, multi-source reporting, and story tracking direction.

---

### 7. File / Document Organizer Mode

Nova helps with:

```text
finding documents
summarizing PDFs
renaming files
making folders
organizing notes
turning documents into tasks
```

Example:

```text
User:
Organize these project files.

Nova:
I can suggest a folder structure first.
I will not move files until you approve.

Suggested:
- Contracts
- Invoices
- Client Photos
- Website Drafts
- Notes
```

Prepare first. Act after approval.

---

### 8. Owner Mode

Owner Mode is for the builder, advanced users, operators, and technical review.

Owner Mode can expose:

```text
repo status
runtime truth
capability locks
OpenClaw recovery
installer validation
branch work
certification status
runtime hashes
logs
```

Most users should not start here.

Owner Mode should be available, but it should not dominate Nova’s everyday interface.

---

## Role Rules

Nova’s rules should adapt to the role, but always map back to the same governed authority model.

For home users, call them **Home Rules**:

```text
Never buy anything without approval.
Never submit forms without approval.
Never delete files without approval.
Remind me before deadlines.
Ask before contacting anyone.
```

For business users, call them **Business Rules**:

```text
Never send customer messages without approval.
Never post online without approval.
Never change prices without approval.
Never charge customers.
Always show what changed.
```

For work users, call them **Work Rules**:

```text
Draft replies, but do not send.
Summarize documents clearly.
Do not modify work files without approval.
Keep task lists organized.
```

For technical users, call them **Action Rules** or **Governance Rules**:

```text
capability permissions
execution gates
network rules
approval requirements
ledger events
automation policies
```

The plain-language name changes by role. The safety model does not.

---

## Automation Model

Nova should work independently only inside boundaries.

Think of automation as levels.

### Level 1 — Notice

```text
Nova notices something and tells you.
```

Example:

```text
You have a quote that needs follow-up.
```

### Level 2 — Suggest

```text
Nova suggests what to do.
```

Example:

```text
I recommend following up with Mike today.
```

### Level 3 — Draft

```text
Nova prepares the work.
```

Example:

```text
I drafted the follow-up message.
```

### Level 4 — Queue For Approval

```text
Nova puts actions in an approval queue.
```

Example:

```text
3 drafts are waiting for approval.
```

### Level 5 — Auto-Complete Low-Risk Tasks

Only for safe tasks the user allowed:

```text
create reminders
summarize pages
organize notes
generate reports
archive completed items
```

### Level 6 — Never Without Approval

```text
send
post
buy
delete
submit
charge
publish
change records
```

This is the heart of Nova.

---

## Service / SaaS Packaging

Nova can become a service without losing its local-first and governed identity.

Instead of one vague assistant, package Nova as role packs.

Possible role packs:

```text
Home Assistant Pack
Work Helper Pack
Solo Business Pack
CRM / Customer Follow-Up Pack
Research Briefing Pack
Document Organizer Pack
Owner / Operator Pack
```

Each pack should define:

```text
tasks it helps with
rules it must follow
approval boundaries
templates
dashboard cards
automations
```

This lets Nova be broad without becoming chaotic.

---

## Possible Product Tiers

Do not finalize pricing before the workflow is real, but the structure could become:

### Free / Local

```text
basic assistant
draft messages
summaries
manual reminders
local files
```

### Personal

```text
home tasks
forms
email review
calendar/reminders
document summaries
```

### Solo Business

```text
leads
quotes
follow-ups
appointments
business rules
customer history
```

### Business Manager

```text
light CRM
recurring reports
workflow automations
website/social drafts
approval queue
```

### Operator

```text
advanced local automations
OpenClaw worker
custom rules
integrations
developer/owner mode
```

---

## Interface Direction

The home screen should let the user choose Nova’s role:

```text
Choose Nova’s role today:

[Home Assistant]
[Personal Assistant]
[Work Helper]
[Business Assistant]
[Business Manager]
[Research Assistant]
[File Organizer]
[Owner Mode]
```

Each role should have its own dashboard.

### Home Assistant Dashboard

```text
Home Today
- 2 reminders
- 1 bill to review
- 1 form draft
- 3 household tasks

[Explain a bill]
[Make grocery list]
[Set reminder]
[Help fill form]
[What did Nova do?]
```

### Work Helper Dashboard

```text
Work Today
- 5 emails to review
- 2 tasks due
- 1 document to summarize
- 1 reply draft ready

[Summarize emails]
[Draft reply]
[Make checklist]
[Prepare report]
```

### Business Manager Dashboard

```text
Business Today
- 3 leads
- 2 follow-ups
- 1 quote waiting
- 2 appointments
- 0 actions sent automatically

[Reply to leads]
[Create quote]
[Show CRM]
[Draft social post]
[What changed?]
```

---

## Relationship To Existing Product Docs

This core vision sits above the other future docs.

Hierarchy:

```text
Core Vision:
Role-Based Governed Assistant

Main roles:
- Home Assistant
- Personal Assistant
- Work Helper
- Solo Business Assistant
- Business Manager
- Research Assistant
- File Organizer
- Owner Mode

First market wedge:
Solo Business Assistant

Future expansion:
Everyday Task Service + lightweight CRM
```

The Solo Business Assistant remains the first focused commercial wedge.

The Everyday Task Service expansion preserves the broader non-technical task assistant identity.

Owner Mode preserves the advanced builder/operator surface.

---

## Implementation Guidance

Build reusable primitives that can serve multiple roles:

```text
draft message
summarize content
extract tasks
create checklist
prepare form fields
save draft
ask for approval
record action receipt
create reminder
create follow-up item
create/update customer record
organize files
explain screen/page/document
```

Then compose those primitives into role-specific workflows.

Example:

```text
Draft Message
```

can serve:

```text
customer reply
job email
landlord message
school message
appointment response
support request
```

Example:

```text
Summarize Content
```

can serve:

```text
news article
work policy
insurance page
product page
government form instructions
PDF document
email thread
```

Example:

```text
Approval Queue
```

can serve:

```text
send email
post content
submit form
publish website change
confirm appointment
change record
```

This avoids building disconnected vertical features.

---

## Near-Term Build Order

The product vision should not override current repo/runtime truth.

Near-term order remains:

1. Recover stranded trust receipt / Cap 65 work from commit `e9c0187`.
2. Apply follow-up correction commit `92baccd`.
3. Verify files, certification status, and tests.
4. Harden the trust receipt store for missing/corrupt ledger cases.
5. Add targeted receipt-store tests.
6. Complete Cap 64 P5 live signoff and lock.
7. Complete Cap 65 P5 live Shopify checklist and lock.
8. Validate the clean Windows installer path and inspect `C:\Program Files\Nova\bootstrap.log`.
9. Build the first role-based shell.
10. Start with Solo Business Assistant as the first commercial wedge.
11. Expand into everyday task roles after the first workflows are useful.

---

## What Not To Do

Do not make Nova:

```text
only a CRM
only a small-business assistant
only a browser automation tool
only a coding assistant
only an enterprise platform
an unrestricted fantasy assistant
```

Do not let the SaaS idea erase the local-first governed identity.

Do not let role-specific UX bypass the governance model.

Do not build broad UI before the core workflows and trust/action receipts are real.

---

## Best One-Sentence Options

### Option 1

> **Nova is a governed role-based assistant for home, work, and small business that helps people complete everyday tasks while keeping real-world actions under user control.**

### Option 2

> **Nova is your assistant, under your rules — helping with home tasks, work tasks, business workflows, and safe automations without secretly acting behind your back.**

### Option 3

> **Nova is a local-first governed assistant that can act as your home helper, work assistant, or business manager while keeping every real action visible, bounded, and approved.**

Preferred short phrase:

> **Your assistant, under your rules.**

---

## Final Direction

Nova’s core future is:

> **A role-based governed assistant for home, work, everyday tasks, and small business.**

The first commercial wedge is:

> **Solo Business Assistant.**

The broader service expansion is:

> **Everyday Task Assistant with eventual lightweight CRM and role packs.**

The governing product rule remains:

> **simple outside, governed inside.**
