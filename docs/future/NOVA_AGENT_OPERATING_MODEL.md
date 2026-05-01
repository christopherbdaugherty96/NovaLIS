# Nova Agent Operating Model

Status: future architecture plan / not shipped runtime capability

This document defines a future operating model for Nova as a voice-first, governed personal/home/business AI platform.

It is a planning artifact. It does not change the current runtime authority model, does not grant agents execution authority, and does not represent implemented multi-agent autonomy.

---

## Runtime Alignment

Nova's current runtime truth must remain the authority for shipped behavior.

The future model in this document must preserve these invariants:

- no broad autonomy
- no hidden background execution outside explicitly governed carve-outs
- all actions pass through GovernorMediator
- all outbound HTTP passes through NetworkMediator
- all execution is logged to the ledger
- intelligence is not authority

Future agents are reasoning and coordination surfaces. They do not bypass the governed capability path.

---

## Product Definition

Nova should evolve into a controlled AI operating layer for personal life, home operations, and small-business coordination.

Best framing:

```text
Nova is a voice-first, governed personal/home/business AI operating platform.

It coordinates specialized assistants across life and business domains, but every real-world action remains capability-scoped, approval-aware, mediated, and logged.
```

Avoid framing Nova as:

- a general chatbot with tools
- a fully autonomous employee
- an uncontrolled agent swarm
- a cloud service that silently controls local devices or business accounts

---

## Operating Hierarchy

Recommended hierarchy:

```text
Owner / Human Authority
-> Nova Core
-> Global Manager
-> Domain Managers
-> Task Assistants
-> Connector Packages
-> Capability Registry
-> Governor / Execute Boundary / NetworkMediator / Ledger
```

The human remains the final authority for risky or external actions.

Agents reason and coordinate. Capabilities execute. The Governor authorizes. The user approves risky actions. The ledger records what happened.

---

## Nova Core

Nova Core is the primary assistant identity the user interacts with by voice or text.

Nova Core responsibilities:

- receive voice and text input
- preserve owner context
- detect intent
- route work to the Global Manager or the right domain manager
- request memory through governed memory surfaces
- frame approvals clearly
- synthesize final responses
- surface trust and receipt information

Nova Core should not contain every business workflow directly. It should coordinate and delegate.

Example:

```text
User: Nova, what needs my attention today?

Nova Core:
- routes to Global Manager
- requests snapshots from Personal, Email/Calendar, Auralis, Pour Social, Commerce, and Home managers
- merges the findings into one command briefing
- separates safe actions from approval-required actions
```

---

## Global Manager

The Global Manager is an orchestration role, not an independent executor.

Responsibilities:

- decide which domain managers should be involved
- combine their findings
- deduplicate suggested actions
- detect conflicts across domains
- rank importance
- produce one action board
- identify which actions need approval
- prevent cross-domain confusion

Example:

```text
Auralis suggests a discovery call Tuesday at 2 PM.
Personal Calendar detects a conflict at Tuesday 2 PM.
Global Manager blocks that suggestion and proposes alternate windows.
```

---

## Domain Managers

Domain managers organize work for one area of life or business.

Suggested initial managers:

- Personal Manager
- Home Manager
- Email/Calendar Coordination Manager
- Auralis Manager
- Pour Social Manager
- Commerce/Shopify Manager
- Code/Repo Manager
- Research Manager
- Admin/Finance Manager

Each domain manager should define:

- memory scope
- allowed connectors
- allowed capabilities
- workflow templates
- risk rules
- checklist templates
- reporting schema
- approval expectations

Domain managers should not own raw credentials or bypass connector/capability boundaries.

---

## Task Assistants

Task assistants are narrow reasoning helpers under a domain manager.

Example Auralis structure:

```text
Auralis Manager
├─ Lead Intake Assistant
├─ Requirements Assistant
├─ Website Strategy Assistant
├─ Copy Draft Assistant
├─ QA / Launch Gate Assistant
├─ Client Communication Assistant
├─ Project Tracker Assistant
└─ Proof Package Assistant
```

Example Email/Calendar structure:

```text
Email/Calendar Coordination Manager
├─ Inbox Triage Assistant
├─ Multi-Email Summary Assistant
├─ Action Extraction Assistant
├─ Draft Reply Assistant
├─ Scheduling Assistant
├─ Follow-Up Assistant
└─ Batch Approval Assistant
```

Task assistants may analyze, classify, summarize, draft, and request capability calls. They do not execute actions directly.

---

## Agent Registry

Future implementation should add an Agent Registry similar in spirit to the Capability Registry.

Example shape:

```json
{
  "agent_id": "auralis_manager",
  "label": "Auralis Manager",
  "domain": "business/auralis",
  "status": "planned",
  "authority": "reasoning_only",
  "memory_scope": "business/auralis",
  "allowed_capabilities": [
    "gmail_thread_summary",
    "gmail_draft_reply",
    "google_calendar_availability",
    "auralis_project_profile",
    "auralis_launch_gate"
  ],
  "requires_manager_route": true
}
```

Hard rule:

```text
Agents never bypass capabilities.
Agents can only request capability calls through Nova Core, Global Manager, and the governed execution path.
```

---

## Workspaces

Nova should support workspaces as first-class product objects.

A workspace groups agents, memory, connectors, dashboards, and policy.

Examples:

- Personal
- Home
- Auralis Digital
- Pour Social
- Shopify Store
- NovaLIS Development
- Real Estate

Example shape:

```json
{
  "workspace_id": "auralis",
  "label": "Auralis Digital",
  "type": "business",
  "agents": [
    "auralis_manager",
    "lead_intake_assistant",
    "requirements_assistant"
  ],
  "connectors": [
    "gmail",
    "google_calendar",
    "google_drive",
    "google_sheets"
  ],
  "memory_scope": "business/auralis",
  "approval_policy": "business_external_actions_confirmed",
  "dashboards": [
    "lead_board",
    "project_board",
    "email_action_board",
    "launch_gate"
  ]
}
```

---

## Memory Boundaries

Future multi-agent behavior requires clear memory boundaries.

Recommended memory scopes:

- global/user
- personal/home
- business/auralis
- business/pour_social
- business/shopify
- code/novalis
- research
- admin/finance

Rules:

- domain agents read their own memory by default
- Global Manager may request cross-domain summaries
- cross-domain memory use should be visible
- sensitive memory should be lockable
- business records should not silently leak into unrelated domains

---

## Authority Tiers

Authority tiers should be used by agents, capabilities, Trust Panel, and batch approvals.

### Tier 0 — Reasoning Only

Examples:

- summarize
- classify
- recommend
- compare
- draft internally
- score readiness
- detect missing information

No external effect.

### Tier 1 — Read Connector

Examples:

- read Gmail
- read Calendar
- read Drive/Docs/Sheets
- read Shopify
- read GitHub
- read approved local files

Requires connector enablement and setup.

### Tier 2 — Prepare / Draft

Examples:

- create email draft
- prepare calendar event
- prepare tracker update
- prepare document
- prepare PR text
- prepare deployment plan

Review required.

### Tier 3 — Bounded Write

Examples:

- create calendar event
- apply email label
- archive email
- append sheet row
- create Google Doc
- create GitHub issue
- open PR

Explicit approval required.

### Tier 4 — High-Risk External Effect

Examples:

- send email
- delete email or data
- share files externally
- deploy website
- merge PR
- buy domain
- change DNS
- change billing settings
- message client
- spend money

Strong confirmation and receipt required.

---

## Voice-First, Text-Confirmed UX

Nova should be voice-first, not voice-only.

Principle:

```text
Voice is for command, briefing, navigation, and low-risk flow.
Text/dashboard is for review, precision, batch approvals, and receipts.
```

Voice examples:

- Nova, brief me.
- Nova, check business.
- Nova, clean up my inbox.
- Nova, what do I owe people?
- Nova, prepare Auralis replies.

Example voice response:

```text
I found six emails needing action: three Auralis leads, one Pour Social follow-up, and two personal items. I prepared draft replies and found two scheduling conflicts. Open the review board?
```

The dashboard should then show:

- email action board
- calendar suggestions
- draft replies
- approve/reject/defer controls
- risk tiers
- receipts

---

## Trust Panel Requirement

For this operating model, Trust Panel is required product infrastructure.

It should show:

- what Nova read
- what Nova inferred
- which agent requested the action
- which capability would execute
- risk tier
- approval requirement
- expected external effect
- receipt after completion

Example:

```text
Auralis Client Communication Assistant wants to create a Gmail draft reply.

Source:
- Gmail thread from GreenEdge Lawn Care

Will do:
- create draft reply

Will not do:
- send email
- archive thread
- create calendar event

Requires:
- user review before send
```

---

## Local-First / SaaS Hybrid

Nova can support a personal/home SaaS-style experience without becoming a cloud-controlled agent.

Best model:

```text
Local sovereign core + optional SaaS convenience layer.
```

Possible optional services:

- account login
- encrypted backup
- multi-device sync
- hosted dashboard relay
- connector setup wizard
- billing/licensing
- agent pack distribution
- managed templates and checklists

Execution authority should remain governed, transparent, and user-controlled.

---

## Implementation Order

Recommended path:

1. Define the agent operating model and workspace model.
2. Define Google Workspace connector plan.
3. Define Email Action Board and Batch Action Envelope.
4. Build read-only connector capabilities first.
5. Add domain/workspace overlays.
6. Add draft/prepare capabilities.
7. Add Trust Panel and batch approvals.
8. Add bounded writes.
9. Defer high-risk external effects until trust UX, receipts, and tests are strong.

---

## Honest Framing

Best framing:

```text
Nova is a manager of controlled assistants, not one uncontrolled autonomous agent.
```

Each assistant has a job. Each connector has a boundary. Each capability has a risk tier. Each risky action requires approval. Each execution creates a receipt.

This keeps Nova powerful enough to become a personal/home/business operating system while preserving its central principle: intelligence is not authority.
