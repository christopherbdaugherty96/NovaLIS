# Auralis Lead Console v1

Status: future planning only.

This document preserves the useful Auralis/Nova planning from stale branches without merging old branch history into `main`.

It is not a runtime claim. It does not expand NovaLIS authority, add capabilities, connect client systems, send email, publish websites, or activate business automation.

---

## Purpose

Nova Lead Console v1 is the first narrow Auralis/Nova overlap.

Goal:

> Turn structured website inquiries into lead summaries, missing-information checks, draft replies, follow-up suggestions, and visible review records.

The simplest near-term framing:

> Auralis builds the website. Nova helps handle the leads.

The strongest customer promise:

> We help you stop missing opportunities from your website.

---

## Product Model

### Auralis

Auralis is the storefront and commercial wrapper.

Its job is to:

- sell websites first;
- build trust with local businesses;
- structure website intake forms;
- create Nova-ready lead flows;
- keep the public offer simple and understandable.

### NovaLIS

NovaLIS is the governed backend intelligence layer.

Its job is to:

- summarize inquiries;
- detect missing information;
- draft replies;
- suggest follow-ups;
- explain uncertainty;
- record what was read, drafted, and not sent;
- keep owner review and governance boundaries visible.

### Client Website

The website is the intake surface.

Its job is to:

- show services;
- collect inquiries;
- collect quote requests;
- collect customer context;
- feed structured business signals into a future Nova workflow.

---

## MVP Boundary

### In Scope

- Structured website inquiry intake
- Business profile context
- Lead summary
- Intent and urgency classification
- Missing information detection
- Draft reply generation
- Follow-up suggestion
- Visible action/history record
- Owner review before external action

### Out of Scope

- Autonomous email sending
- Autonomous booking
- Autonomous website publishing
- Payment processing
- Full CRM
- Regulated industry workflows
- Client-facing claim that Nova is a full business agent
- Hidden background automation
- Google/Gmail/Calendar runtime connector work
- Shopify writes
- OpenClaw browser expansion

---

## Example User Story

A small business owner receives a website inquiry.

Nova summarizes what the customer wants, identifies missing information, drafts a response, and suggests the next step.

The owner reviews, edits, sends manually, or saves for later.

Nova records what it did and what it did not do.

---

## MVP Flow

1. Customer submits website form.
2. Form creates structured lead payload.
3. Lead payload enters the Auralis/Nova intake path.
4. Nova reads the business profile.
5. Nova produces lead summary and draft response.
6. Owner reviews the draft.
7. Owner manually sends, copies, saves, or ignores.
8. Nova records the reviewed outcome and what it did not do.

---

## Data Inputs

- Customer name
- Customer phone/email
- Service requested
- Location or service area
- Timeline
- Notes/photos if applicable
- Preferred contact method
- Business profile
- Owner approval rules

Data collection should remain minimal and business-appropriate. Avoid unnecessary sensitive data.

---

## Outputs

- Lead summary
- Urgency level
- Missing fields
- Suggested next step
- Draft response
- Follow-up reminder suggestion
- Action/trust record

---

## Success Criteria

- Lead is summarized accurately.
- Draft reply is useful and editable.
- Missing information is clearly identified.
- No customer-facing action happens without owner review.
- Failure mode does not lose the inquiry.
- Workflow is understandable to a nontechnical small business owner.
- Runtime claims match generated runtime truth, tests, and proof artifacts.

---

## Build Order

### Phase 1: Static Prototype

- Use sample lead JSON.
- Use sample business profile JSON.
- Generate summary and draft reply.
- No live website integration.
- No email send path.

### Phase 2: Lead Schema

- Define lead payload schema.
- Define business profile schema.
- Define owner approval rules.
- Add sample mock leads.

### Phase 3: Owner Review Surface

- Display lead card.
- Display missing information.
- Display draft reply.
- Add copy/save/manual-review behavior.

### Phase 4: Trust Record

- Record what Nova read.
- Record what Nova drafted.
- Record what Nova did not send.
- Show clear owner-review status.

### Phase 5: Demo Client Test

- Test with a low-risk demo business.
- Collect failure cases.
- Update schemas, prompts, and proof docs.

---

## Governance Boundary

This is planning only.

Any future runtime implementation must still pass through NovaLIS governance:

- GovernorMediator
- CapabilityRegistry
- ExecuteBoundary
- NetworkMediator where applicable
- Ledger / trust receipts
- explicit owner review before external action

Planning docs are not runtime authority.

Memory, search, daily brief, and recommendations may inform planning, but they do not authorize external action.

---

## Customer-Facing Language

Safe early wording:

> Auralis builds websites that are ready to grow into smarter business workflows.

Lead-console wording:

> Auralis can help structure your website inquiries so Nova can summarize leads, draft replies, and suggest follow-ups while you stay in control.

Avoid early claims like:

- fully autonomous AI agent;
- runs your business for you;
- automatic email sending;
- automatic booking;
- automatic website publishing;
- complete business automation.

---

## Best Early Customer Types

Good early targets:

- lawn care;
- mobile detailing;
- barbers;
- salons;
- cleaning services;
- handymen;
- small contractors;
- photographers;
- mobile bartending or event vendors;
- local restaurants with simple inquiry or catering needs.

Avoid early medical, legal, finance, insurance, and other regulated services until governance, terms, privacy, and support practices are mature.

---

## Current Priority

Do not build this before the daily operating baseline is stronger.

Current order remains:

1. Daily memory loop
2. Search feedback loop
3. Recommendation polish
4. OpenClaw UX polish, not expansion
5. Auralis Lead Console static prototype
6. Auralis/business workflow runtime later

---

## Relation to Current Nova Work

Current implemented daily-use foundation:

- Daily Brief MVP
- Daily Brief continuity hardening
- conversation continuity fields
- deterministic recommendations
- Search Evidence Synthesis
- proof docs for daily operating baseline

Missing before Auralis runtime should begin:

- durable explicit memory loop
- search feedback UX
- recommendation wording polish
- OpenClaw visibility/receipt polish
- clearer business data handling expectations

---

## Final Strategy Statement

Auralis should sell websites first. Nova should become the governed intelligence layer behind those websites later.

The narrow future product is:

> Nova Lead Console v1: structured website inquiries become summaries, missing-info checks, draft replies, follow-up suggestions, and visible review records.

The owner stays in control.
