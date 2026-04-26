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

Do not overcomplicate the first sale.

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

The customer buys something simple:

> I need a better website.

That gets Auralis in the door.

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

This prepares the data Nova will eventually use.

Nova works better when the website collects clean structured information.

Instead of a basic contact form with only name, phone, and message, use structured fields such as:

- name;
- phone;
- email;
- service needed;
- location or service area;
- timeline;
- budget range, when appropriate;
- preferred contact method;
- notes or photos, when appropriate.

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

This profile gives Nova the context required to summarize, draft, and recommend accurately.

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

This is useful and safe.

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

Example insight:

> Most inquiries this month were for spring cleanup, but your homepage still leads with weekly mowing. Consider adding a spring cleanup call-to-action.

This can become a monthly report or dashboard Auralis sells.

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

Do not start with autonomous booking.

Exit criteria:

- calendar changes require explicit approval;
- tentative vs. confirmed status is clear;
- conflicts and time zones are handled visibly;
- customer-facing confirmations are never hidden.

### Stage 8: Nova Becomes the Business Agent Layer

This is the mature version.

Nova helps with:

- leads;
- inquiries;
- email;
- calendar;
- business metrics;
- website updates;
- content;
- customer follow-up;
- review requests;
- service recommendations;
- simple reporting.

It must remain governed.

Exit criteria:

- each real action maps to a registered capability;
- approval and delegation levels are documented;
- ledger/trust visibility exists for client-facing actions;
- recovery, pause, and failure behavior are defined.

---

## Product Concept

This could become:

> Auralis Digital Website + Agent System

Basic idea:

> Auralis builds the business website and connects it to a governed Nova backend that helps the owner manage inquiries, information, follow-ups, and business signals.

Possible product names:

- Auralis Business Assistant;
- Auralis Agent Layer;
- Auralis Intelligence Backend;
- Auralis Client Console;
- Auralis Business OS;
- Auralis Smart Website System;
- Nova for Auralis;
- Auralis powered by Nova.

Avoid “autonomous agent” language early.

Better terms:

- assistant;
- backend;
- dashboard;
- workflow system;
- approval-based agent;
- business intelligence layer.

---

## Customer-Facing Explanation

For normal business owners:

> We start by building you a clean, professional website. As your business grows, that website can connect to an intelligent backend that helps organize inquiries, draft replies, track leads, review metrics, and keep your customer communication under control.

Stronger version:

> Your website should not just sit there. It should help your business operate. Auralis starts with your website, then can connect it to a governed assistant that helps manage leads, emails, customer questions, and business insights — with you staying in control.

This explains the Nova concept without technical overload.

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

That is how to sell the trust model.

---

## Web Design First

A small business owner may not immediately buy:

> governed AI backend agent software.

But they understand:

> I need a website.

After the website is built, they may realize:

- inquiries are coming in;
- they forget to follow up;
- customers ask repeat questions;
- they need quote organization;
- they want help posting updates;
- they want email drafts;
- they want appointment reminders.

That is when Nova becomes valuable.

The sales ladder is:

1. Website.
2. Forms and intake.
3. Lead tracking.
4. Email support.
5. Metrics and reporting.
6. Assistant dashboard.
7. Deeper Nova agent workflows.

---

## First Nova-Linked Product

The first Nova-linked Auralis product should be modest.

Do not start with a full agent.

Start with:

### Nova Lead Console v1

For a client website, collect form submissions and show:

- new lead summary;
- service requested;
- urgency;
- contact information;
- suggested reply;
- missing details;
- follow-up status.

Example:

> New lead: Rob’s Lawn Care. Customer wants weekly mowing in Belleville. They prefer text contact. Missing information: yard size and start date. Suggested reply prepared. Recommended next step: ask for address and photos.

That product alone is useful.

Then add:

### Nova Email Draft v1

- read or receive inquiry emails;
- summarize;
- draft response;
- require owner approval before sending.

Then add:

### Nova Metrics Snapshot v1

- weekly summary of form submissions;
- most common services requested;
- unanswered leads;
- suggested website update.

---

## Auralis Package Path

### Package 1: Website Foundation

Website only.

Includes:

- mobile-friendly site;
- services;
- about;
- contact;
- form;
- basic SEO.

### Package 2: Website + Lead System

Website plus structured inquiries.

Includes:

- quote form;
- lead email formatting;
- lead tracker;
- follow-up templates.

### Package 3: Website + Nova Lead Console

First Nova-linked tier.

Includes:

- inquiry summaries;
- lead categorization;
- draft replies;
- basic business profile;
- weekly lead report.

### Package 4: Nova Business Assistant

Later.

Includes:

- email connection;
- metrics dashboard;
- appointment request support;
- content suggestions;
- follow-up reminders;
- approval-gated actions.

### Package 5: Nova Managed Agent Layer

Long-term.

Includes:

- deeper integrations;
- calendar;
- CRM-like tracking;
- business intelligence;
- governed workflow actions;
- audit trail;
- advanced automation under strict approval and policy boundaries.

---

## Build Order

### First: Structured Website Inquiry System

Every Auralis client website should have strong forms that produce clean structured data.

Example for lawn care:

- name;
- phone;
- email;
- address or service area;
- service type;
- property size;
- timeline;
- photos;
- notes;
- preferred contact method.

Example for restaurant or catering:

- name;
- event date;
- guest count;
- service type;
- location;
- budget range;
- food or drink needs;
- contact information.

Example for barber or salon:

- name;
- service wanted;
- preferred date/time;
- stylist preference;
- phone/email;
- notes.

### Second: Business Profile Schema

Nova needs business context.

For each client:

- business name;
- industry;
- services;
- pricing notes;
- service area;
- hours;
- contact preferences;
- tone;
- FAQs;
- policies;
- owner approval settings;
- important limits.

### Third: Lead Summary and Draft System

When a lead comes in:

- summarize;
- classify;
- draft response;
- suggest next step;
- log it.

That is the first real Nova/Auralis product.

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

## Website Updates

Website changes are sensitive.

Nova can first suggest:

- headline updates;
- seasonal calls to action;
- FAQ additions;
- promotion copy;
- testimonial placement;
- content drafts.

Auralis or the client approves before anything is published.

A future Auralis service could be:

> Monthly website intelligence and update recommendations.

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

Avoid early:

- medical;
- legal;
- finance;
- insurance;
- highly regulated services;
- businesses with complex compliance requirements.

Start where risk is lower and value is obvious.

---

## Messaging Sequence

Early public wording:

> Auralis builds websites that are ready to grow into smarter business workflows.

Later wording:

> Auralis can connect your website to an approval-based assistant that helps summarize inquiries, draft replies, track leads, and explain business metrics.

Mature wording:

> Powered by NovaLIS, Auralis websites can connect to a governed business assistant that helps manage customer communication, reporting, and routine workflows while keeping the owner in control.

Avoid early claims such as:

- fully autonomous AI agent;
- runs your business for you;
- automatic email sending;
- automatic booking;
- complete business automation.

---

## Important Boundary

Avoid saying:

> Nova is linked to every client website from day one.

Safer and more accurate:

> Auralis websites are designed to be Nova-ready.

That means:

- forms are structured;
- business data is organized;
- leads are trackable;
- content is clean;
- future integrations are possible.

Auralis can sell web design now while preparing the backend path.

---

## Roadmap

### Phase A: Auralis Web Design

Goal:

- get customers;
- build sites;
- create proof.

### Phase B: Nova-Ready Websites

Goal:

- every site has structured data and workflow-friendly forms.

### Phase C: Auralis Lead Console

Goal:

- simple dashboard and reporting around inquiries.

### Phase D: Nova Lead Intelligence

Goal:

- Nova summarizes, classifies, drafts, and recommends.

### Phase E: Email + Metrics

Goal:

- read or draft email;
- generate weekly or monthly insights.

### Phase F: Calendar + Workflow Actions

Goal:

- approval-gated booking and follow-up workflows.

### Phase G: Full Nova Business Agent

Goal:

- governed assistant software connected to the website, business profile, email, calendar, metrics, and approved actions.

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
