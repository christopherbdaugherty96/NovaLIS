# Nova Everyday Task Service Expansion

Date: 2026-04-26

Status: Product direction correction / expansion note

Related docs:

- [`NOVA_SOLO_BUSINESS_ASSISTANT_PRODUCT_VISION.md`](NOVA_SOLO_BUSINESS_ASSISTANT_PRODUCT_VISION.md)
- [`NOVA_SOLO_BUSINESS_ASSISTANT_DECISION_RECORD_2026-04-26.md`](NOVA_SOLO_BUSINESS_ASSISTANT_DECISION_RECORD_2026-04-26.md)
- [`NOVA_EVERYDAY_MODE_PRODUCT_VISION.md`](NOVA_EVERYDAY_MODE_PRODUCT_VISION.md)

---

## Purpose

The Solo Business Assistant is the first focused market wedge for Nova, but it should **not** become Nova’s only identity or only use case.

Nova should also become a governed everyday task/workflow assistant for people who are not highly technical and simply need help getting small digital tasks done safely.

This includes people with basic jobs, side work, life admin, online forms, email overload, documents, articles, pages, news, and simple computer workflows.

---

## Corrected Product Direction

Nova should be able to serve two connected groups:

1. **Independents and small local businesses**
   - leads
   - quotes
   - follow-ups
   - appointments
   - website/social drafts
   - customer admin
   - eventual lightweight CRM

2. **Everyday users with basic digital tasks**
   - filling out forms
   - summarizing pages/articles/news
   - consolidating email
   - reviewing and organizing information
   - helping with basic work tasks
   - drafting messages
   - organizing files/documents
   - explaining what is on screen
   - preparing safe actions for approval

The product should not become only a small-business service.

The broader identity should be:

> **Nova is a governed everyday workflow assistant that helps people and small businesses complete digital tasks, organize information, and safely prepare or perform actions while keeping the user in control.**

---

## CRM Direction

Nova should eventually include a CRM-like layer, but it should not start as a full CRM.

The correct path is:

```text
lead tracker
follow-up board
quote history
appointment history
customer notes
conversation/task history
simple customer pipeline
lightweight governed CRM
```

Do not start with:

```text
full Salesforce-style CRM
complex pipelines
enterprise team permissions
sales forecasting
large database administration
full marketing automation
```

The CRM should grow naturally out of the first workflows:

```text
Who messaged me?
Who needs a reply?
Who got a quote?
Who needs a follow-up?
Who has an appointment?
What did we last talk about?
What did Nova draft or prepare for them?
```

That means Nova should first become useful for customer admin, then later organize that customer admin into a CRM.

The user-facing wording should be simple:

```text
Customers
Leads
Follow-ups
Quotes
Appointments
Notes
History
```

Not:

```text
CRM object model
sales pipeline architecture
account hierarchy
enterprise lifecycle management
```

---

## Who This Expansion Is For

This broader Nova service is for people who may not be good with computers, do not want to manage lots of tools, or just need small tasks done for them.

Examples:

```text
someone with a basic office job
someone applying for jobs
someone filling out online forms
someone managing too much email
someone trying to understand bills, policies, or documents
someone who needs help summarizing articles or news
someone with a side hustle
someone running a small local business
someone who wants help organizing files, notes, or tasks
```

They may not think of themselves as needing an “AI agent.”

They think:

```text
I need this form filled out.
I need this article summarized.
I need my email organized.
I need help replying to this message.
I need to understand this page.
I need to keep track of follow-ups.
I need basic work tasks done faster.
```

---

## Everyday Task Categories

Nova should eventually support these everyday task categories.

### 1. Forms And Website Tasks

User-facing examples:

```text
Help me fill out this form.
Explain what this form is asking.
Save this as a draft before submitting.
Check this application for mistakes.
Fill in the parts you know and ask me for the missing details.
```

Governance rule:

```text
Nova may prepare or fill draft form fields, but submitting forms, applications, purchases, payments, account changes, or legal/official documents should require explicit user approval.
```

---

### 2. Page / Article / News Summaries

User-facing examples:

```text
Summarize this page.
What is this article saying?
Give me the main points.
Is this news important for me?
Compare these articles.
Make this easier to understand.
```

Nova should provide:

```text
short summary
key points
what matters
what to watch
source/context when available
plain-language explanation
```

---

### 3. Email Consolidation And Review

User-facing examples:

```text
Summarize my important emails.
What do I need to reply to?
Group these emails by topic.
Draft replies for these messages.
Show me bills, appointments, customers, and work items separately.
What can I ignore for now?
```

Governance rule:

```text
Nova can read, summarize, organize, and draft by permission. Sending, deleting, forwarding, unsubscribing, or changing email state should require clear approval unless the user has created an explicit low-risk rule.
```

---

### 4. Document And File Help

User-facing examples:

```text
Summarize this PDF.
Explain this bill.
Find the important date.
Turn this document into a checklist.
Organize these files.
Rename these files safely.
Find the document I need.
```

Governance rule:

```text
Reading and summarizing are low-risk. Moving, renaming, deleting, or uploading files should be governed and approval-based depending on risk.
```

---

### 5. Basic Job Workflow Help

For people with ordinary jobs, Nova should help with:

```text
drafting emails
summarizing meeting notes
making checklists
tracking tasks
preparing reports
organizing documents
turning instructions into steps
reviewing policies
building simple schedules
```

The experience should feel like:

> “Nova helps me get through my work tasks without needing to be good with software.”

---

### 6. Everyday Admin And Life Tasks

Nova should also help with life-admin tasks:

```text
understand a bill
compare options
make a phone call script
prepare questions before an appointment
track reminders
organize household tasks
summarize insurance/medical/financial paperwork in plain language
```

Important boundary:

```text
Nova can explain and organize, but should not pretend to be a lawyer, doctor, accountant, or financial advisor. It can help prepare questions and summaries, but high-stakes decisions remain with the user/professional.
```

---

## Service Model

Nova can become a service without being limited to small businesses.

The service promise can be:

> **Nova helps people get everyday digital tasks done safely — forms, messages, summaries, emails, files, reminders, and small-business workflows — while keeping the user in control of real actions.**

For non-technical users:

> **Nova helps with the computer tasks you do not want to fight with.**

For small businesses:

> **Nova helps you stop missing customers, quotes, and follow-ups.**

For workers:

> **Nova helps you organize work, summarize information, and prepare messages or documents faster.**

---

## Product Surface

A broader Nova home screen could include:

```text
What do you need help with?

[Fill out a form]
[Summarize a page]
[Review my email]
[Organize files]
[Help with work]
[Help my business]
[Customers / CRM]
[Draft a message]
[Explain what I’m looking at]
[What did Nova do?]
```

The Solo Business Assistant can remain one mode inside the broader product:

```text
Personal Tasks
Work Tasks
Business Tasks
Customers / CRM
Owner / Advanced
```

---

## Action Authority Levels

The same automation/action ladder still applies across all uses.

### Low Risk / Usually Okay With Minimal Friction

```text
summarize
explain
organize information
make checklists
draft messages
prepare form fields
suggest next steps
```

### Medium Risk / Confirm Before Acting

```text
open websites
open files/folders
save drafts
create reminders
move or rename files
mark emails as organized
prepare calendar events
```

### High Risk / Always Require Explicit Approval

```text
submit forms
send email
post online
make purchases
charge customers
change prices
delete files
forward private information
change account settings
publish website changes
modify official/business records
```

Nova’s product advantage is that it can help with all three levels while making the authority boundary clear.

---

## Relationship To Solo Business Assistant

Solo Business Assistant remains the first focused commercial wedge because it has a clear paying user and painful repeatable workflows.

But Nova’s broader future should include everyday task service use cases.

Correct relationship:

```text
Nova Everyday Task Assistant = broader platform direction
Nova Solo Business Assistant = first focused market wedge
Nova Lightweight CRM = eventual business layer grown from leads/follow-ups/quotes
Owner Mode = advanced/developer/operator surface
```

This prevents the product from becoming too narrow while still keeping the first go-to-market focused.

---

## What Not To Do

Do not position Nova only as:

```text
small-business CRM
lead tracker only
email assistant only
browser automation tool only
coding assistant
enterprise agent platform
```

Nova should become a governed workflow assistant that can serve several everyday task domains.

Do not make it broad in implementation too early, but do preserve the broader identity.

---

## Implementation Guidance

The right implementation strategy is:

1. Keep the first commercial wedge focused: Solo Business Assistant.
2. Design the underlying flows generically enough to support everyday tasks later.
3. Build reusable primitives:
   - draft message
   - summarize content
   - extract tasks
   - create checklist
   - prepare form fields
   - save draft
   - ask for approval
   - record action receipt
   - create/update simple customer record
   - create follow-up item
4. Keep all real actions governed.
5. Add broader everyday task modes after the first workflows feel useful.
6. Add CRM depth after leads, follow-ups, quotes, appointments, and history are useful in simple form.

Reusable primitives are more important than one-off vertical features.

Example:

```text
Draft Reply
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
Summarize Page
```

can serve:

```text
news article
work policy
insurance page
product page
government form instructions
```

Example:

```text
Prepare Form Fields
```

can serve:

```text
job application
business intake
customer form
appointment form
website contact form
```

Example:

```text
Customer Record
```

can serve:

```text
lead tracker
quote history
appointment history
follow-up list
lightweight CRM
```

---

## CRM Guardrail

Nova should eventually have CRM capability, but it should be a **simple governed CRM for independents**, not a complicated enterprise CRM clone.

The first CRM version should answer:

```text
Who are my leads?
Who needs follow-up?
What quotes are open?
What appointments are coming up?
What did I last draft or send?
What is waiting for approval?
```

It should not begin with complex sales forecasting, teams, territories, or enterprise admin.

---

## Final Direction

The corrected future direction is:

> **Nova should be a governed everyday workflow assistant for people and small businesses. Solo Business Assistant is the first focused commercial wedge, but Nova’s broader service should help non-technical users complete common digital tasks like forms, summaries, email review, file organization, work tasks, and safe automations. Nova should eventually include a lightweight governed CRM for independents, grown naturally from leads, quotes, follow-ups, appointments, and customer history.**

The product should stay simple outside and governed inside.

The user should feel:

> “Nova helps me get things done on the computer, but it does not secretly act without me.”
