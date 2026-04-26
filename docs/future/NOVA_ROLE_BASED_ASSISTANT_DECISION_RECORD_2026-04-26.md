# Nova Role-Based Assistant — Product Decision Record

Date: 2026-04-26

Status: Accepted as umbrella future product direction

Related docs:

- [`NOVA_ROLE_BASED_ASSISTANT_CORE_VISION.md`](NOVA_ROLE_BASED_ASSISTANT_CORE_VISION.md)
- [`NOVA_EVERYDAY_TASK_SERVICE_EXPANSION_2026-04-26.md`](NOVA_EVERYDAY_TASK_SERVICE_EXPANSION_2026-04-26.md)
- [`NOVA_SOLO_BUSINESS_ASSISTANT_DECISION_RECORD_2026-04-26.md`](NOVA_SOLO_BUSINESS_ASSISTANT_DECISION_RECORD_2026-04-26.md)

---

## Decision

Nova’s umbrella future product direction is:

> **A role-based governed assistant for home, work, everyday tasks, and small business.**

The accepted short phrase is:

> **Your assistant, under your rules.**

This means Nova should not be reduced to only one vertical such as small business, CRM, browser automation, coding, or enterprise agents.

Nova should let the user direct the assistant into practical roles, such as:

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

Each role may have different dashboards, language, workflows, automations, and visible rules.

The governance model must remain underneath every role.

---

## Why This Decision Was Made

The prior Solo Business Assistant direction is still valuable and remains the first focused commercial wedge.

However, Nova’s broader purpose is not only small business.

Nova should also help people who are not highly technical and need common digital tasks done for them:

```text
fill out forms
summarize pages, articles, and news
review and organize email
organize files and documents
help with basic job workflows
draft messages
explain what is on screen
prepare safe actions for approval
```

The role-based model keeps Nova broad without becoming vague.

It gives Nova a clear structure:

```text
Core product identity: role-based governed assistant
First market wedge: Solo Business Assistant
Broader expansion: Everyday Task Service
Eventual business layer: lightweight governed CRM
Advanced surface: Owner Mode
```

---

## Product Principle

The product principle is:

> **simple outside, governed inside.**

Everyday users should see plain-language roles and tasks.

They should not be forced to understand:

```text
GovernorMediator
CapabilityRegistry
ExecuteBoundary
NetworkMediator
LedgerWriter
runtime hashes
certification locks
branches
commits
```

But those governance systems still matter and must not be bypassed.

---

## Authority Rule

Nova may help, prepare, organize, summarize, draft, and automate safe steps.

Nova must not silently perform high-risk real-world actions.

Always require approval for:

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

Role-specific rules should translate this into language users understand:

```text
Home Rules
Work Rules
Business Rules
Action Rules
```

---

## Relationship To Solo Business Assistant

Solo Business Assistant remains the first commercial wedge because independent workers and small local businesses have a clear painful workflow:

```text
missed messages
missed follow-ups
late quotes
appointment confusion
customer admin overload
```

But Solo Business is one role/product pack inside the larger Nova direction.

Correct relationship:

```text
Role-Based Assistant = umbrella direction
Solo Business Assistant = first paid/useful wedge
Everyday Task Service = broader non-technical user expansion
Lightweight CRM = later business layer
Owner Mode = advanced technical/operator surface
```

---

## SaaS / Service Constraint

Nova can become a SaaS/service, but the service should be built around useful role packs and repeatable workflows, not a vague generic chatbot.

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

SaaS features such as accounts, billing, cloud dashboard, sync, and templates should come after the core workflows are useful and trustworthy.

---

## Non-Goals

Nova should not become:

```text
only a CRM
only a small-business assistant
only a browser automation tool
only a coding assistant
only an enterprise platform
an unrestricted fantasy assistant
```

Nova should become the practical version:

> **A useful assistant under user-defined rules.**

---

## Accepted Product Statement

Use this as the stable umbrella direction:

> **Nova is your assistant, under your rules — a role-based governed assistant for home, work, everyday tasks, and small business that helps people get things done while keeping real-world actions visible, bounded, and approved.**
