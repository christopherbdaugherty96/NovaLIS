# Auralis Digital and NovaLIS Integration Goals

Date: 2026-04-26

Status: Future strategy / commercial integration plan

Scope: Auralis Digital as the first early business startup and commercial surface for NovaLIS. This is a staged product direction, not a claim that the integration is already implemented.

Implementation note: This document describes product and business direction. It does not expand NovaLIS runtime authority by itself. Any real integration must still pass through NovaLIS governance, capability registration, execution boundaries, network mediation where applicable, and ledger visibility.

---

## Executive Summary

NovaLIS should be treated as the backend intelligence and governance system. Auralis Digital should be treated as the first early business startup and commercial launch vehicle.

The initial Auralis offer should remain simple: web design for small businesses. Over time, Auralis-built websites can become Nova-ready and eventually connect to Nova-powered agent software for lead handling, business information, metrics, email, calendar requests, customer communication, and governed workflow actions.

The simplest near-term version is:

> Auralis builds the website. Nova helps handle the leads.

The long-term product direction is:

> Auralis Smart Website System powered by NovaLIS: a website plus governed business intelligence backend that helps small businesses manage leads, emails, metrics, follow-ups, and customer communication without giving AI uncontrolled authority.

---

## Non-Goals

This plan does not mean NovaLIS should immediately become a public SaaS, multi-tenant platform, or autonomous business operator.

Do not treat this document as permission to:

- connect NovaLIS directly to client systems without explicit design and review;
- send emails automatically by default;
- book appointments automatically by default;
- publish website changes automatically by default;
- ingest sensitive client data without a data-handling model;
- bypass GovernorMediator, CapabilityRegistry, ExecuteBoundary, NetworkMediator, or ledger requirements;
- market unfinished runtime capabilities as available product features.

The near-term goal is staged readiness, not premature coupling.

---

## Corrected Model

### NovaLIS

NovaLIS is the backend operating intelligence.

Its role is to:

- understand business context;
- read and organize business information;
- summarize leads and customer inquiries;
- draft replies and follow-ups;
- monitor business signals;
- support decision-making;
- route actions through governance;
- keep authority bounded, visible, and reviewable;
- log what happened;
- prevent uncontrolled automation.

Nova is the engine.

### Auralis Digital

Auralis Digital is the business wrapper, storefront, and first commercial launch vehicle.

Its role is to:

- sell websites first;
- build trust with local businesses;
- create real client relationships;
- collect real workflow needs;
- create Nova-ready website structures;
- later offer Nova-powered software as an upgrade.

Auralis is the storefront.

### Client Websites

Client websites are the front-end business surfaces.

Their role is to:

- show services;
- collect inquiries;
- collect quote requests;
- show business information;
- connect forms and customer messages;
- feed structured business signals into Nova when the integration is ready.

The website becomes the input and output layer.

---

## System Vision

Auralis builds a business website. The website collects customer activity and inquiries. Nova sits behind it as the governed intelligence layer. Nova organizes the data, drafts responses, tracks business context, reviews metrics, and recommends next actions. The business owner stays in control before anything important is sent, changed, booked, or published.

That is the clean product direction.

Not just:

> I make websites.

More like:

> I build websites that can grow into intelligent business systems.

---

## Why This Direction Matters

Most small business websites are static.

They usually show:

- business name;
- logo;
- services;
- phone number;
- contact form.

That is useful, but limited.

The Auralis/Nova model is different:

> The website becomes the front door, and Nova becomes the behind-the-scenes operator that helps the business handle what comes through that door.

This can help small businesses with:

- missed leads;
- slow replies;
- messy inboxes;
- no follow-up system;
- poor content updates;
- unclear customer questions;
- no visibility into inquiries;
- no organized customer history;
- no simple way to understand what is working.

The strongest customer promise is not “we use AI.”

The stronger promise is:

> We help you stop missing opportunities from your website.

---

## Staged Rollout

### Stage 1: Auralis Sells Websites

This is the starting product.

Offer:

- starter website;
- local business website;
- landing page;
- redesign;
- contact form;
- quote request form;
- basic SEO;
- mobile optimization;
- maintenance.

Exit criteria:

- Auralis public offer is clear;
- intake and quote process are defined;
- at least one demo or client-style site proves the offer;
- launch and maintenance checklists exist.

### Stage 2: Website + Business Intake Structure

The next step is not full AI. It is better structure.

Auralis adds:

- better contact forms;
- quote request forms;
- booking request forms;
- service-area forms;
- FAQ sections;
- customer intake questions;
- business info capture;
- lead notification emails.

Exit criteria:

- structured lead payload is documented;
- form outputs are consistent across demo sites;
- lead notification format is readable without Nova;
- client data fields avoid unnecessary sensitive data.

### Stage 3: Nova Business Profile

For each client, Nova should eventually have a business profile.

A business profile may include:

- business name;
- industry;
- services;
- pricing notes;
- service area;
- hours;
- policies;
- tone of voice;
- FAQs;
- contact preferences;
- owner approval rules;
- website pages;
- common customer questions;
- current promotions;
- important limits.

Exit criteria:

- business profile schema exists;
- owner approval rules are explicit;
- profile data can be reviewed and edited by the owner;
- profile storage and retention expectations are documented.

### Stage 4: Nova Reads Website Inquiries

When a customer submits a form, Nova receives or reads the inquiry and produces:

- summary;
- customer intent;
- urgency;
- suggested reply;
- recommended next step;
- missing information;
- confidence level.

Example:

> New inquiry: customer wants lawn mowing and spring cleanup in Belleville within two weeks. They included phone number but no yard size. Suggested next step: ask for address, approximate lot size, and photos. Draft reply prepared.

Exit criteria:

- inquiry ingestion is read-only or draft-only;
- summaries clearly identify uncertainty and missing information;
- no customer message is sent automatically;
- lead handling is logged.

### Stage 5: Nova Connects to Email

Email is a high-value integration, but it must be governed.

Recommended progression:

1. Manual forwarding or copied email text.
2. Read-only inbox connection.
3. Draft creation.
4. Approval-gated sending.
5. Narrow trusted sends only for low-risk templates after governance is mature.

Initial rule:

> Nova drafts. Owner approves before sending.

Exit criteria:

- read-only and draft-only modes are tested before any send path;
- approval language is clear;
- sent/drafted/ignored actions are visible;
- failures do not silently drop leads or messages.

### Stage 6: Nova Connects to Metrics

Metrics give the business owner visibility.

Nova could eventually summarize:

- website visits;
- form submissions;
- missed inquiries;
- inquiry type breakdown;
- most requested services;
- conversion rate;
- email response time;
- repeat questions;
- source of leads;
- seasonal demand.

Exit criteria:

- metric sources are documented;
- reports distinguish observed data from recommendations;
- low-confidence or incomplete data is labeled;
- no private analytics credentials are exposed.

### Stage 7: Nova Connects to Calendar / Booking

Calendar should come after email and lead handling are stable.

Recommended early behavior:

- summarize appointment request;
- suggest possible available times;
- draft confirmation;
- prepare a tentative calendar event;
- require owner approval before confirming with the customer.

Exit criteria:

- calendar changes require explicit approval;
- tentative vs. confirmed status is clear;
- conflicts and time zones are handled visibly;
- customer-facing confirmations are never hidden.

### Stage 8: Nova Becomes the Business Agent Layer

This is the mature version.

Nova helps with leads, inquiries, email, calendar, business metrics, website updates, content, customer follow-up, review requests, service recommendations, and simple reporting.

Exit criteria:

- each real action maps to a registered capability;
- approval and delegation levels are documented;
- ledger/trust visibility exists for client-facing actions;
- recovery, pause, and failure behavior are defined.

---

## MVP Definition

The first shippable Auralis/Nova overlap should be narrow.

### MVP Name

Nova Lead Console v1.

### MVP Goal

Turn website inquiries into structured lead summaries and response drafts without sending anything automatically.

### MVP Inputs

- structured website form submission;
- business profile;
- service list;
- preferred contact method;
- owner approval rules.

### MVP Outputs

- lead summary;
- urgency level;
- missing information;
- suggested next step;
- draft reply;
- follow-up reminder suggestion;
- visible record of what Nova did and did not do.

### MVP Hard Boundaries

- no autonomous email sending;
- no autonomous booking;
- no autonomous website publishing;
- no sensitive-data expansion beyond required inquiry fields;
- no client-facing claim that Nova is a full business agent.

---

## Capability Planning Map

This section is directional. Actual capability IDs and implementation status must be checked against generated runtime truth before work begins.

| Product Need | Likely Nova Surface | Status Expectation |
| --- | --- | --- |
| summarize website inquiry | analysis / explanation path | should start read-only |
| draft customer reply | email draft or local draft capability | draft-only first |
| open client website | governed website open capability | user-visible action |
| review website metrics | future connector / reporting capability | read-only first |
| read business email | future email connector | read-only before draft/send |
| create email draft | existing or future draft capability | owner sends first |
| calendar review | calendar connector | read-only before write |
| create calendar event | future governed calendar action | approval required |
| suggest website update | analysis document / drafting path | no publish by default |
| publish website update | future governed deploy/publish action | high-risk, approval required |

Any new Auralis-facing runtime work should be added only through registered capabilities, mediator checks, and visible logs.

---

## Revenue Model Direction

Pricing should not be locked until the workflow is real, but the likely ladder is:

### Website Build Revenue

One-time project fees for:

- starter site;
- local business site;
- redesign;
- landing page;
- industry-specific template site.

### Maintenance Revenue

Monthly support for:

- content edits;
- uptime checks;
- minor updates;
- form testing;
- basic SEO upkeep;
- monthly website review.

### Nova-Backed Add-On Revenue

Monthly add-on for:

- lead summaries;
- draft replies;
- follow-up reminders;
- monthly inquiry report;
- basic metrics explanation;
- later email/calendar support.

### Managed Intelligence Revenue

Higher tier service where Auralis reviews Nova-generated insights and sends the client a human-reviewed monthly action plan.

This avoids prematurely selling unsupported automation while still creating recurring value.

---

## Risk Register

| Risk | Why It Matters | Mitigation |
| --- | --- | --- |
| overpromising Nova capabilities | damages trust and creates support burden | sell websites first; label Nova features as staged |
| hidden or uncontrolled actions | violates Nova philosophy | require approval and ledger visibility |
| client data mishandling | business and legal risk | define collection, retention, deletion, and access rules |
| email/calendar mistakes | can damage customer relationships | read-only/draft-only first; approval before send/book |
| analytics misinterpretation | bad business advice | label confidence and distinguish data from recommendation |
| support overload | small business clients need help | start with narrow MVP and managed service layer |
| brand confusion | customers may not understand Nova | sell outcomes, not architecture |
| technical drift from runtime truth | docs may outrun code | verify against generated runtime docs before claiming readiness |

---

## Customer-Facing Explanation

For normal business owners:

> We start by building you a clean, professional website. As your business grows, that website can connect to an intelligent backend that helps organize inquiries, draft replies, track leads, review metrics, and keep your customer communication under control.

Stronger version:

> Your website should not just sit there. It should help your business operate. Auralis starts with your website, then can connect it to a governed assistant that helps manage leads, emails, customer questions, and business insights — with you staying in control.

---

## Governance Translation

Nova’s governance is the trust layer.

Technical Nova language:

- GovernorMediator;
- CapabilityRegistry;
- ExecuteBoundary;
- NetworkMediator;
- Ledger;
- approval-gated action;
- bounded execution.

Customer-facing language:

- the assistant cannot take important actions without permission;
- email drafts are reviewed before sending;
- calendar bookings can require approval;
- website changes can require approval;
- actions are logged;
- the business owner stays in control;
- there is no hidden automation.

---

## Auralis Package Path

### Package 1: Starter Website

Website only.

Includes mobile-friendly site, services, about, contact, contact form, and basic SEO.

### Package 2: Growth Website

Website with stronger conversion and lead capture.

Includes everything in Starter Website plus additional pages, stronger calls to action, trust sections, gallery or testimonials, better-structured inquiry form, expanded SEO basics, and service-area language where appropriate.

### Package 3: Website + Lead System

Website plus a structured system for capturing and organizing inquiries.

Includes Growth Website foundation plus structured quote/request form, lead notification formatting, basic lead tracker template, follow-up templates, and customer intake questions.

### Package 4: Website + Nova Lead Console

First Nova-linked tier. Do not sell as live until Nova Lead Console exists and passes decision gates.

Includes structured lead intake, business profile basics, inquiry summaries, lead categorization, missing information detection, draft replies, follow-up suggestions, weekly lead report, and visible record of what Nova drafted and did not send.

### Package 5: Managed Intelligence Layer

Long-term premium service tier. Do not sell as live until runtime support is verified.

Includes monthly insight review, human-reviewed recommendations, content ideas, website improvement suggestions, lead trend review, follow-up improvement suggestions, and higher-touch support. Framed as a managed service, not autonomous AI operation.

---

## Architecture

```text
Client Website
  ↓
Structured Form / Inquiry / Email
  ↓
Auralis Connector Layer
  ↓
Nova Business Profile + Context
  ↓
Nova Intelligence / Reasoning
  ↓
Governor / Approval Boundary
  ↓
Drafts, Summaries, Reports, Suggested Actions
  ↓
Business Owner Review
  ↓
Approved Action / Manual Send / Logged Result
```

The important boundary:

> Nova should not directly control the business website, email, calendar, or customer communication until the permission model is mature.

First it summarizes and drafts. Later it can act with approval.

---

## Best Early Customer Types

Start with simple service businesses, not complex regulated ones.

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

Avoid early medical, legal, finance, insurance, and other highly regulated services until governance, terms, privacy, and support practices are mature.

---

## Messaging Sequence

Early public wording:

> Auralis builds websites that are ready to grow into smarter business workflows.

Later wording:

> Auralis can connect your website to an approval-based assistant that helps summarize inquiries, draft replies, track leads, and explain business metrics.

Mature wording:

> Powered by NovaLIS, Auralis websites can connect to a governed business assistant that helps manage customer communication, reporting, and routine workflows while keeping the owner in control.

Avoid early claims such as fully autonomous AI agent, runs your business for you, automatic email sending, automatic booking, or complete business automation.

---

## Roadmap

### Phase A: Auralis Web Design

Goal: get customers, build sites, and create proof.

### Phase B: Nova-Ready Websites

Goal: every site has structured data and workflow-friendly forms.

### Phase C: Auralis Lead Console

Goal: simple dashboard and reporting around inquiries.

### Phase D: Nova Lead Intelligence

Goal: Nova summarizes, classifies, drafts, and recommends.

### Phase E: Email + Metrics

Goal: read or draft email and generate weekly or monthly insights.

### Phase F: Calendar + Workflow Actions

Goal: approval-gated booking and follow-up workflows.

### Phase G: Full Nova Business Agent

Goal: governed assistant software connected to the website, business profile, email, calendar, metrics, and approved actions.

---

## Decision Gates Before Public Nova-Backed Sales

Before Auralis sells Nova-backed services as a real customer product, verify:

- the feature exists in runtime, not only in docs;
- the user approval path is clear;
- the capability surface is registered and bounded;
- outbound network/email/calendar paths use the intended mediators;
- action logs or trust receipts are visible enough for users;
- client data handling, retention, and deletion expectations are documented;
- support expectations are realistic;
- the service can fail safely without losing customer inquiries.

---

## Final Strategy Statement

NovaLIS is the backend intelligence system. Auralis Digital is the first business startup that sells websites first, then grows those websites into Nova-connected business systems.

Auralis is not separate from Nova forever. It is the first commercial surface for Nova.

But the order matters.

The correct sequence is:

1. Sell websites through Auralis.
2. Make those websites structured and Nova-ready.
3. Use forms, business profiles, and lead data as Nova’s first inputs.
4. Add Nova summaries, draft replies, and lead tracking.
5. Add email and business metrics.
6. Add calendar and workflow tools.
7. Eventually sell Nova as the governed agent backend for small business websites.

The strongest long-term product is:

> Auralis Smart Website System powered by NovaLIS: a website plus governed business intelligence backend that helps small businesses manage leads, emails, metrics, follow-ups, and customer communication without giving AI uncontrolled authority.

The simplest near-term version is:

> Auralis builds the website. Nova helps handle the leads.
