# Auralis Digital Client Intake OS

Last updated: 2026-05-06

Status: future / planning document for NovaLIS and Auralis Digital integration.

This document defines the stronger version of a website chat widget: not a generic support box, but the Auralis Digital intake layer — the front door where new clients enter the business system, get qualified, and flow into a structured sales, project, delivery, and support workflow.

This is not a runtime implementation claim for NovaLIS. It does not expand Nova’s current execution authority. It does not override generated runtime truth, the current priority lock, or any governed capability boundary.

For NovaLIS, this document is a future integration concept: Nova may eventually act as the governed internal review layer behind Auralis Digital, but only after the relevant governed connector, review-card, workflow, capability, ledger, and approval boundaries exist.

---

## Core Idea

Auralis Digital sells and manages websites.

Nova becomes the governed operating engine behind the business.

The public customer should see a simple assistant or guided intake experience. Behind the scenes, the system should become a sales intake, project routing, client memory, backlog, and delivery-control layer.

The customer-facing object may look like a chat widget, but the actual business object is an intake pipeline.

The goal is not only to answer questions. The goal is to:

1. Capture new website leads.
2. Qualify the project.
3. Sort the client into the correct service path.
4. Create a structured backlog or project record.
5. Trigger a manual follow-up workflow.
6. Preserve the intake as usable client context.
7. Feed structured information into Nova later.
8. Keep everything reviewable, logged, and non-autonomous.

The correct framing:

```text
Auralis Digital = client-facing website and service business
Auralis Intake Layer = public front door and structured lead capture
Backlog / CRM = operational source of truth for leads and projects
Nova = governed internal operator that reviews, summarizes, drafts, and organizes without uncontrolled action
```

---

## Do Not Treat This As Generic Live Chat

Do not label this as generic live support unless Auralis is actually ready to answer quickly.

A normal chat widget creates three risks:

1. It creates an expectation of real-time human support.
2. It captures messy unstructured messages instead of clean business data.
3. It can become disconnected from the actual sales and project workflow.

Auralis needs a guided lead intake and qualification system.

Better public labels:

```text
Start Your Website Project
Website Project Assistant
Request a Website Quote
Start a Website Request
```

Best public label:

```text
Start Your Website Project
```

Best internal name:

```text
Auralis Intake Layer
```

Best full operating name:

```text
Auralis Digital Client Intake OS
```

---

## One-Line Product Definition

A governed business workflow where every website lead becomes a structured record, every record becomes a project path, and Nova can later help review, summarize, draft, organize, and monitor the work without taking uncontrolled action.

The widget is not just a chat bubble.

It is the front door to the Auralis operating system.

---

## Public Widget Opening

The widget should not start with a vague prompt such as:

```text
How can I help?
```

That creates messy answers.

It should start with structured choices that turn the visitor into a usable lead record.

Recommended opening:

```text
Hi — I can help get your website project started.

What are you looking for?

1. New website
2. Redesign an existing website
3. Fix or improve a current website
4. Add online booking, forms, or payments
5. Ongoing website maintenance
```

This immediately routes the lead.

---

## Intake Flow

### Step 1 — Project Type

Question:

```text
What are you looking for?

1. New website
2. Redesign an existing website
3. Fix or improve a current website
4. Add online booking, forms, or payments
5. Ongoing website maintenance
```

Purpose:

- Separates new builds from redesigns.
- Separates one-time work from maintenance.
- Detects whether the project needs ecommerce, booking, forms, or payment integration.
- Gives Auralis an early sense of scope.

Stored field examples:

```text
project_type = new_website | redesign | fix_or_improve | add_functionality | maintenance
```

---

### Step 2 — Business Type

Question:

```text
What type of business is this website for?
```

The system should recognize and normalize business types such as:

- lawn care
- real estate
- barber / salon
- contractor
- restaurant
- mobile bartending
- cleaning / detailing
- ecommerce
- personal brand
- nonprofit
- local service business
- other

Purpose:

- Helps qualify fit.
- Helps select a niche-specific offer.
- Helps route to the correct page structure.
- Helps Nova later draft a more relevant follow-up, proposal, and project checklist.

Stored field examples:

```text
business_type = lawn_care
business_category = local_service
```

---

### Step 3 — Current Online Presence

Question:

```text
Do you already have any of the following?

1. A domain name
2. A current website
3. Hosting
4. Logo or branding
5. Google Business Profile
6. Social media pages
```

Purpose:

- Identifies whether Auralis needs to handle domain, hosting, branding, Google profile, or migration concerns.
- Prevents underquoting.
- Creates a clean asset checklist before discovery.

Stored field examples:

```text
has_domain = true | false | unknown
has_current_website = true | false | unknown
has_hosting = true | false | unknown
has_logo_or_branding = true | false | unknown
has_google_business_profile = true | false | unknown
has_social_pages = true | false | unknown
```

---

### Step 4 — Main Goal

Question:

```text
What is the main goal of the website?

1. Get more leads
2. Look more professional
3. Let customers book online
4. Sell products
5. Show services/pricing
6. Replace an outdated site
7. Not sure yet
```

Purpose:

- Connects the project to a business outcome.
- Helps avoid selling only design when the customer actually needs lead capture, booking, ecommerce, or trust-building.
- Helps Auralis explain value in the follow-up.

Stored field examples:

```text
main_goal = get_more_leads | professional_presence | online_booking | ecommerce | services_pricing | replace_outdated_site | unsure
```

---

### Step 5 — Timeline

Question:

```text
When would you like the website completed?

1. As soon as possible
2. Within 2–4 weeks
3. Within 1–2 months
4. No rush, just planning
```

Purpose:

- Helps determine urgency.
- Helps decide whether this needs a quick follow-up.
- Helps avoid accepting a timeline that cannot be met.

Stored field examples:

```text
timeline = asap | 2_4_weeks | 1_2_months | planning
urgency = high | medium | low
```

---

### Step 6 — Budget Range

Question:

```text
What budget range are you most comfortable with?

1. Under $500
2. $500–$1,000
3. $1,000–$2,500
4. $2,500+
5. Not sure yet
```

Purpose:

- Filters bad-fit leads early.
- Helps route to refresh, basic, standard, premium, audit, or maintenance paths.
- Prevents spending too much time on leads that are not ready.

Stored field examples:

```text
budget_range = under_500 | 500_1000 | 1000_2500 | 2500_plus | unsure
```

Budget handling rule:

Do not shame or reject the lead inside the widget. The widget should collect the answer and route the lead. Auralis can decide manually whether to follow up, offer a smaller package, defer, or decline.

---

### Step 7 — Contact Method

Question:

```text
What is the best way to follow up with you?

Please leave your name, phone number, and email.
```

Purpose:

- Turns the visitor into an actual lead.
- Gives Auralis a follow-up path.
- Prevents anonymous intake records from becoming unusable.

Stored field examples:

```text
contact_name = ""
email = ""
phone = ""
preferred_contact_method = text | phone | email | unknown
```

---

## Lead Record Shape

Every submitted intake should become a structured lead record.

Minimum record:

```json
{
  "lead_name": "",
  "business_name": "",
  "business_type": "",
  "business_category": "",
  "project_type": "",
  "current_website": "",
  "has_domain": null,
  "has_hosting": null,
  "has_logo_or_branding": null,
  "has_google_business_profile": null,
  "has_social_pages": null,
  "main_goal": "",
  "timeline": "",
  "budget_range": "",
  "preferred_contact_method": "",
  "email": "",
  "phone": "",
  "lead_score": "",
  "status": "new_lead",
  "next_action": "manual_review",
  "source": "website_intake_widget",
  "created_at": "",
  "notes": ""
}
```

Important rule:

Do not only collect messages. Collect structured business data.

That is what makes the intake useful for Auralis operations and compatible with Nova later.

---

## Lead Scoring

The intake system should support a simple manual or semi-automated lead score.

Suggested scores:

```text
A = strong fit, clear need, realistic budget, near-term timeline
B = good fit, some missing info, follow up manually
C = weak fit, low budget, unclear need, long timeline
D = not a fit right now
```

Lead scoring should not automatically reject or accept a project.

It should only help Auralis prioritize manual follow-up.

Example scoring hints:

```text
New website + local service business + $1,000+ budget + 2–4 week timeline = likely A/B lead
Redesign + current website + unclear budget + no rush = likely B/C lead
Under $500 + ecommerce + ASAP = scope/budget mismatch, likely C/D lead
Maintenance request from existing client = route to support path, not new sales path
```

---

## Workflow States

Every lead or project should move through clear operating states.

Canonical flow:

```text
New Lead
→ Qualified Lead
→ Discovery Needed
→ Quote Needed
→ Proposal Sent
→ Contract Sent
→ Deposit Paid
→ In Production
→ Client Review
→ Revision Round
→ Final Delivery
→ Maintenance Offer
→ Completed
→ Archived
```

Optional states:

```text
Not a Fit
Deferred
Waiting on Client
Waiting on Assets
Waiting on Domain Access
Waiting on Hosting Access
Waiting on Payment
Paused
Cancelled
```

This turns Auralis into an operating system instead of scattered messages, texts, emails, notes, and memory.

---

## Widget Modes

The widget should eventually have multiple modes.

### Mode 1 — New Lead

For people who want a new website, redesign, or quote.

Goal:

```text
Collect project info and create a new lead record.
```

Primary fields:

- project type
- business type
- current online presence
- goal
- timeline
- budget
- contact info

---

### Mode 2 — Existing Client

For current Auralis clients.

Goal:

```text
Route support or update requests without mixing them into new sales leads.
```

Questions:

```text
What website is this for?
What change do you need?
Is it urgent?
Do you have files, images, or text to upload?
Is this a bug, edit, content change, or new feature?
```

Stored request types:

```text
bug_fix
content_update
image_update
new_section
new_page
pricing_update
hours_update
feature_request
urgent_issue
```

---

### Mode 3 — Maintenance Request

For monthly support clients.

Goal:

```text
Collect clean website update instructions.
```

Examples:

- update text
- add photos
- change hours
- add a new service
- fix a broken link
- update pricing
- add an announcement
- update contact information
- post a seasonal offer

Maintenance requests should become tickets or backlog items.

---

### Mode 4 — Quote Request

For people who already know what they want.

Goal:

```text
Collect enough information to prepare a quote.
```

Required quote fields:

- project type
- page count estimate
- needed features
- current website URL, if any
- desired launch date
- budget range
- contact info

---

### Mode 5 — Book a Call

For qualified leads.

Goal:

```text
Move the person to a discovery call or manual scheduling path.
```

This mode should not be the default until Auralis has a scheduling system and follow-up process ready.

---

## Auralis Service Routing

The widget should be able to route leads toward the likely offer, without promising final pricing.

### Website Refresh

Best for:

- Auralis-built sites that need updates.
- Small improvements after launch.
- Minor polish, content updates, or layout refreshes.

Internal route:

```text
project_type = maintenance or fix_or_improve
existing_client = true
likely_offer = website_refresh_or_care_plan
```

Rule:

Third-party websites should not automatically receive the $250 refresh offer. They may require audit, rebuild, migration, or custom quote.

---

### Basic Website

Best for:

- New local businesses.
- Simple online presence.
- 1–3 page sites.
- Clear contact and quote-request path.

Includes:

- 1–3 pages
- mobile responsive layout
- contact form
- basic SEO setup
- simple launch checklist
- Google Business Profile link when available

Internal route:

```text
project_type = new_website
budget_range = 500_1000 or 1000_2500
main_goal = professional_presence or services_pricing or get_more_leads
likely_offer = basic_website
```

---

### Standard Website

Best for:

- Local businesses needing a stronger site.
- Multiple services.
- Trust-building content.
- Better lead capture.

Includes:

- 4–7 pages
- service pages
- lead form
- testimonials
- gallery or portfolio
- basic analytics
- SEO page titles and descriptions

Internal route:

```text
project_type = new_website or redesign
budget_range = 1000_2500 or 2500_plus
main_goal = get_more_leads or replace_outdated_site
likely_offer = standard_website
```

---

### Growth Website

Best for:

- Businesses that need automation or stronger conversion paths.
- Booking.
- Payments.
- CRM intake.
- Email capture.
- Lead routing.
- Monthly reporting.

Includes:

- booking or scheduling flow
- payments if needed
- CRM or lead intake integration
- email capture
- maintenance system
- analytics/reporting setup
- more advanced project checklist

Internal route:

```text
project_type = add_functionality or new_website or redesign
main_goal = online_booking or ecommerce or get_more_leads
budget_range = 2500_plus
likely_offer = growth_website
```

---

### Paid Audit / Rebuild Consultation

Best for:

- Third-party websites.
- Broken sites.
- Messy hosting/domain situations.
- Unclear migration work.
- Scope/budget mismatch.

Internal route:

```text
has_current_website = true
built_by_auralis = false
project_type = fix_or_improve or redesign
likely_offer = paid_audit_or_rebuild_consultation
```

---

## Full Auralis + Nova System Design

### 1. Public Website Layer

This is what the customer sees.

Includes:

- Auralis homepage
- services page
- portfolio page
- pricing or package page
- contact page
- intake widget
- optional booking form

The public site should feel simple and professional.

Its job is to turn visitors into structured leads.

---

### 2. Intake Layer

This is the widget or guided form.

Its job is to qualify people before Auralis spends time manually chasing unclear leads.

It should collect:

- business type
- project type
- website goal
- existing assets
- timeline
- budget
- contact info
- urgency
- notes

This becomes the first source of truth for the lead.

---

### 3. Backlog / CRM Layer

This is where the lead gets stored.

Simple options:

- Trello
- Notion
- Airtable
- Google Sheets
- HubSpot free CRM
- Zoho free CRM

Recommended starting point:

```text
Airtable or Notion for project backlog
Google Sheets backup/export
Gmail templates for follow-up
Google Drive client folder once qualified
```

Start simple. Do not overbuild before there are real leads.

---

### 4. Proposal Layer

Once the lead is qualified, Auralis prepares a proposal or quote.

Nova can later help draft this, but Auralis must review before sending.

Proposal should include:

- project summary
- recommended package
- deliverables
- timeline estimate
- price or price range
- exclusions
- revision policy
- payment terms
- next steps

---

### 5. Production Layer

After a deal is accepted, the lead should become a project checklist.

Example build checklist:

```text
Client Intake Complete
Brand Assets Collected
Domain Access Confirmed
Hosting / Platform Confirmed
Homepage Drafted
Service Pages Drafted
Contact Form Built
Mobile Review Complete
SEO Basics Complete
Client Review Sent
Revision Round Complete
Launch Approved
Website Published
Maintenance Offered
```

This becomes the project control board.

---

### 6. Nova Internal Review Layer

Nova’s role is internal and governed.

Correct flow:

```text
Lead comes in
→ Nova summarizes the lead
→ Nova identifies missing info
→ Nova recommends the likely package
→ Nova drafts a follow-up message
→ User reviews
→ User sends or approves outside Nova’s authority boundary
```

Nova should help Auralis think, organize, and draft.

Nova should not automatically:

- send quotes
- accept jobs
- promise deadlines
- message clients
- charge payments
- change project statuses as final truth without review
- create binding commitments

Governance rule:

```text
Intelligence can recommend.
Execution stays governed.
```

This fits Nova’s core principle: intelligence is not authority.

---

## Nova-Compatible Lead Summary

When a new intake arrives, Nova should eventually produce a structured review like this:

```text
Lead Summary
- Business: [business name]
- Type: [business type]
- Request: [project type]
- Goal: [main goal]
- Timeline: [timeline]
- Budget: [budget]
- Existing assets: [domain / hosting / site / branding]
- Fit: [A/B/C/D]
- Likely route: [package or audit]
- Missing info: [questions]
- Recommended next action: [manual follow-up / discovery / quote / defer]
```

Nova should also produce a draft follow-up, clearly marked as draft.

Example:

```text
Draft Follow-Up

Hi [Name], thanks for reaching out about your website project for [Business]. Based on what you shared, it sounds like you may need [recommended path]. A few things I would want to confirm before giving you a clean quote are [missing questions].

Would you prefer to go over this by text, email, or a quick call?
```

The draft should not send itself.

---

## Backlog Record Fields

Recommended CRM/backlog fields:

```text
Lead ID
Date Created
Source
Name
Business Name
Business Type
Phone
Email
Preferred Contact Method
Current Website URL
Project Type
Main Goal
Timeline
Budget Range
Has Domain
Has Hosting
Has Branding
Has Google Business Profile
Has Social Pages
Likely Package
Lead Score
Status
Next Action
Follow-Up Due Date
Assigned To
Notes
Nova Summary
Missing Info
Quote Link
Proposal Link
Client Folder Link
```

Keep this simple at first. Add fields only when they help execution.

---

## Automation Events

The intake system should eventually support these events:

```text
intake.submitted
lead.created
lead.review_needed
lead.qualified
lead.needs_discovery
quote.draft_needed
proposal.sent
contract.sent
deposit.paid
project.created
project.waiting_on_assets
project.in_production
project.client_review
project.completed
maintenance.offer_needed
```

These events should not imply autonomous action by Nova.

They should create visibility, reminders, and review tasks.

---

## Customer-Facing Boundaries

The widget should not overpromise.

Avoid:

```text
We can definitely build this by [date].
Your project will cost [exact amount].
Your site will generate [specific result].
You are approved.
We started your project.
```

Safer language:

```text
Thanks — this gives us enough to review your project request.
Auralis will follow up to confirm scope, timeline, and pricing.
Final pricing depends on project details, content, integrations, and launch requirements.
```

---

## Recommended Simple MVP

Do not build the full system immediately.

Start with:

```text
Website button:
“Start Your Website Project”

Widget asks:
1. New site or redesign?
2. Business type?
3. Current website/domain?
4. Main goal?
5. Timeline?
6. Budget?
7. Contact info?

Submission creates:
- lead record
- project status: New Lead
- manual follow-up task
```

That is enough to start selling and learning.

Then add:

```text
Nova lead summary
Nova quote draft
Nova project checklist
Nova follow-up reminder
Nova maintenance tracking
```

---

## Recommended Free-First Stack

Free-first, simple-first stack:

```text
Auralis website
→ Tally form or custom intake widget
→ Airtable / Notion / Google Sheets backlog
→ Gmail follow-up template
→ Google Drive client folder after qualification
→ Nova internal review later
```

Possible tools:

```text
Website: custom static site, Vite/React, Framer, Webflow, WordPress, or Carrd
Intake: Tally, Formspree, custom form, Crisp, Tidio, or HubSpot form
Storage: Airtable, Notion, Google Sheets, HubSpot free CRM, Zoho free CRM
Automation: Make free tier, Zapier free tier, manual export first
Internal AI: Nova later
```

Auralis should prefer free-first tools unless a paid tool is clearly justified.

---

## Implementation Ladder

### Phase 1 — Manual Structured Intake

- Add a clear “Start Your Website Project” button.
- Use a simple guided form or widget.
- Save submissions into one backlog.
- Manually review every lead.
- Manually follow up.

Definition of done:

```text
A visitor can submit structured website project info.
Auralis can see the lead in one place.
Auralis knows the next manual action.
```

---

### Phase 2 — CRM / Backlog Discipline

- Add statuses.
- Add lead score.
- Add follow-up due date.
- Add proposal/quote links.
- Add client folder links after qualification.

Definition of done:

```text
Every lead has a status, next action, and follow-up path.
```

---

### Phase 3 — Proposal and Quote System

- Route leads to likely package.
- Create quote/proposal templates.
- Standardize discovery questions.
- Track proposal sent / accepted / declined.

Definition of done:

```text
Auralis can move from intake to quote without rewriting the process every time.
```

---

### Phase 4 — Production Project Conversion

- Turn accepted leads into project checklists.
- Track assets, domain, hosting, pages, revisions, launch, and handoff.
- Connect care plan offer after launch.

Definition of done:

```text
A closed lead becomes a controlled delivery workflow.
```

---

### Phase 5 — Nova Internal Review

- Nova reads or receives structured lead records.
- Nova summarizes lead context.
- Nova identifies missing info.
- Nova recommends likely package.
- Nova drafts follow-up.
- User reviews before action.

Definition of done:

```text
Nova helps review and draft without sending, promising, charging, or executing uncontrolled business actions.
```

---

## NovaLIS Implementation Boundary

For NovaLIS, this concept must stay behind current governance rules.

Before any active NovaLIS implementation, the following must be true:

```text
[ ] The active priority lock allows this workstream.
[ ] The lead source is read-only or explicitly user-provided.
[ ] Any connector used for CRM, email, forms, or storage has a governed capability path.
[ ] Nova can display a review card before any external action.
[ ] Drafting and sending are separate authority states.
[ ] No quote, deadline, acceptance, payment, or client-facing message is executed without explicit user approval.
[ ] Ledger/receipt records exist for every reviewed recommendation and every approved action.
[ ] Generated runtime truth reflects any newly added capability surface.
```

This document is not permission to add uncontrolled business automation.

---

## Minimum Acceptance Criteria

Before calling this system live, confirm:

```text
[ ] Public label does not imply 24/7 live support.
[ ] Intake asks structured questions.
[ ] Contact info is required before submission.
[ ] Submission creates a durable lead record.
[ ] Lead record has source, status, and next action.
[ ] Budget/timeline are captured without making promises.
[ ] Existing-client support requests are distinguishable from new leads.
[ ] Third-party website refresh requests are not automatically treated as $250 refreshes.
[ ] Auralis manually reviews before sending a quote or proposal.
[ ] Nova, if used, only summarizes/recommends/drafts unless governed approval exists.
```

---

## Hard Rules

1. Do not build a chatbot that stores only conversation text.
2. Do not pretend it is live support if it is not staffed.
3. Do not let the widget promise price, timeline, or acceptance.
4. Do not let Nova autonomously sell, quote, charge, message, or commit.
5. Do not create scattered lead storage across messages, email, notes, and spreadsheets.
6. Do not overbuild before real leads exist.
7. Do not treat Auralis website intake as separate from delivery workflow.
8. Do not let maintenance requests mix with new sales leads.
9. Do not implement this in NovaLIS as an active capability until governance, connector, review-card, ledger, and runtime-truth boundaries are ready.

---

## Operating Summary

The final system should be:

```text
Visitor
→ Auralis public website
→ Start Your Website Project widget
→ Structured intake
→ Lead record
→ Manual review
→ Nova summary/draft support later
→ Follow-up
→ Quote/proposal
→ Contract/deposit
→ Project checklist
→ Website delivery
→ Maintenance offer
→ Client support path
```

The core idea:

```text
Auralis captures and serves the client.
Nova helps govern, organize, summarize, and draft behind the scenes.
The customer sees a simple intake experience.
The business gets a structured operating system.
```

This is the robust version of the chat-widget idea.