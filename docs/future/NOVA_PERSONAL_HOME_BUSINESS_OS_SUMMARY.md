# Nova Personal/Home/Business Operating System Summary

Status: full planning synthesis / not shipped runtime capability

This document captures the conclusions from the Google Workspace, agent operating model, email coordination, and Personal Personality Layer planning pass.

It is a planning artifact. It does not modify runtime authority, grant new execution rights, or claim that the future capabilities described here are currently implemented.

---

## Core Product Direction

Nova should evolve into a voice-first, governed personal/home/business AI operating platform.

The product direction is not simply "a chatbot with tools" and not an uncontrolled autonomous agent. The intended direction is a controlled AI command layer that can coordinate personal life, home operations, and small-business workflows while preserving bounded authority.

Best framing:

```text
Nova is a governed AI operating layer for personal life, home operations, and small-business coordination.
```

Nova should feel personal and useful, but its authority must remain bounded, visible, and reviewable.

---

## Runtime Truth Boundary

Current runtime truth remains authoritative.

Future docs may describe the desired operating model, but shipped behavior must still be verified against generated runtime truth and the runtime codebase.

The future direction must preserve Nova's core invariants:

- no broad autonomy
- no hidden background execution outside explicit governed carve-outs
- all actions pass through GovernorMediator
- all outbound HTTP passes through NetworkMediator
- all execution is logged to the ledger
- intelligence is not authority

---

## Operating Model

The future hierarchy is:

```text
Owner / Human Authority
-> Personal Personality Layer
-> Nova Core
-> Global Manager
-> Domain Managers
-> Task Assistants
-> Connector Packages
-> Capability Registry
-> Governor / Execute Boundary / NetworkMediator / Ledger
```

Plain-language meaning:

- the user remains the owner and final authority
- the Personal Personality Layer makes Nova feel like one coherent assistant
- Nova Core routes intent and preserves system coherence
- the Global Manager coordinates multiple domains
- Domain Managers own areas such as Personal, Home, Auralis, Pour Social, Commerce, Code, Research, and Admin
- Task Assistants perform narrow reasoning work under managers
- Connectors provide data surfaces such as Google Workspace or Shopify
- Capabilities define what can actually be done
- the Governor, Execute Boundary, NetworkMediator, and Ledger enforce control

Agents reason and coordinate. Capabilities execute. The Governor authorizes. The user approves risky actions. The ledger records what happened.

---

## Personal Personality Layer

The Personal Personality Layer is the unified presentation, continuity, and relationship layer for Nova.

Canonical detailed doc:

```text
docs/design/brain/PERSONAL_PERSONALITY_LAYER.md
```

This layer receives structured feeds from Nova Core, Global Manager, domain managers, and task assistants. It presents those feeds to the user in a natural voice/text style.

It should:

- make many agents feel like one assistant
- preserve the user's communication style and briefing preferences
- decide what is spoken versus routed to dashboard/text
- maintain continuity across personal, home, and business contexts
- preserve trust, risk, and approval information

It must not:

- execute actions
- call tools directly
- bypass Nova Core
- bypass GovernorMediator
- bypass Capability Registry
- bypass Execute Boundary
- bypass NetworkMediator
- override approval requirements
- create hidden authority

Best mental model:

```text
The Personality Layer is the shell.
The managers and agents are internal processes.
The capabilities are system calls.
The Governor is the authority kernel.
The ledger is the receipt trail.
```

---

## Agent Feed System

The backbone of the future multi-agent system should be structured feeds.

Recommended flow:

```text
Agents / Managers
-> structured feeds
-> Personal Personality Layer
-> voice/text briefing or dashboard handoff
```

Feeds should preserve operational and governance details, including:

- source agent
- workspace
- summary
- priority
- items
- suggested actions
- risk tier
- approval requirement
- safe-to-speak flag
- dashboard-review flag
- sensitivity flag when needed

This avoids a fragmented multi-agent user experience and gives the Personality Layer a safe, structured way to summarize the whole system.

---

## Workspaces

Nova should support workspaces as first-class product objects.

A workspace groups agents, memory, connectors, dashboards, workflows, and policy.

Examples:

- Personal
- Home
- Auralis Digital
- Pour Social
- Shopify Store
- NovaLIS Development
- Real Estate
- Admin/Finance

Each workspace should define:

- memory scope
- allowed connectors
- allowed capabilities
- domain managers and task assistants
- dashboards
- approval policy
- reporting format

This keeps business and personal contexts from blurring.

---

## Google Workspace Direction

Google Workspace should become a governed connector package, not a single broad permission.

Canonical detailed doc:

```text
docs/future/GOOGLE_WORKSPACE_CONNECTOR_PLAN.md
```

Google should be split by product surface:

```text
google_workspace
├─ gmail
├─ calendar
├─ drive
├─ docs
└─ sheets
```

Initial priority:

1. Gmail and Calendar read-only surfaces
2. Multi-email summary and action extraction
3. Draft replies and draft calendar suggestions
4. Batch approval support
5. Confirmed writes
6. High-risk operations last

Nova should not have blanket access to the user's Google account. Access must be scoped by product, capability, approval policy, and ledgered execution.

---

## Email Coordination Board

Email should become a core daily command surface.

Canonical detailed doc:

```text
docs/future/EMAIL_COORDINATION_BOARD.md
```

The key product move is:

```text
Turn email into an action board instead of a passive inbox.
```

Nova should process multiple emails or threads at once, then group and summarize them by sender, client, project, workspace, urgency, and required action.

Core sections:

- Needs reply
- Needs scheduling
- Needs decision
- Waiting on someone else
- Business/client related
- Personal/admin
- No action

For each thread, Nova should identify:

- summary
- domain/workspace
- urgency
- requested action
- missing information
- suggested reply
- calendar relevance
- tracker/project relevance
- risk tier
- approval requirement

This is one of the strongest first practical workflows because it can make Nova useful daily.

---

## Calendar and Email Coordination

Calendar and email should work together.

Nova should be able to:

- read calendar snapshots
- detect availability
- identify scheduling requests in email
- suggest time windows
- draft replies with available slots
- draft calendar events
- create or update events only after confirmation

The desired user experience:

```text
Nova, review my emails and calendar.
```

Nova returns:

- what needs a reply
- what needs scheduling
- what conflicts exist
- what can be drafted
- what requires approval

---

## Business Agent Direction

Nova should support domain-specific assistants for each business or life area.

Examples:

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

```text
Pour Social Manager
├─ Event Inquiry Assistant
├─ Quote / Package Assistant
├─ Contract Assistant
├─ Menu / Inventory Assistant
├─ Calendar / Staffing Assistant
├─ Client Follow-up Assistant
└─ Event Prep Checklist Assistant
```

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

These assistants should not have independent execution authority. They should reason, summarize, draft, and request capability calls through Nova Core and the governed path.

---

## Authority Tiers

Future capabilities and agent proposals should use risk tiers.

### Tier 0 — Reasoning Only

Examples:

- summarize
- classify
- recommend
- compare
- detect missing information
- personalize briefing style

No external effect.

### Tier 1 — Read Connector

Examples:

- read Gmail
- read Calendar
- read Drive/Docs/Sheets
- read Shopify
- read GitHub
- read approved local files

Requires connector enablement.

### Tier 2 — Prepare / Draft

Examples:

- create email draft
- prepare calendar event
- prepare tracker update
- prepare document
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

Voice is best for:

- command
- briefing
- navigation
- status checks
- quick low-risk flow

Text/dashboard is best for:

- detailed review
- batch approvals
- email drafts
- calendar proposals
- Trust Panel review
- receipts
- high-risk confirmations

Rule of thumb:

```text
Voice summarizes.
Dashboard reviews and approves.
```

---

## Batch Approval Requirement

Multi-email and multi-agent workflows require batch approval.

The user should be able to approve, reject, or defer selected actions rather than handling one action at a time.

Example grouped actions:

- approve all drafts
- approve only Auralis drafts
- reject high-risk actions
- defer Pour Social follow-ups
- open dashboard review

Batch approval should preserve:

- source agent
- source workspace
- action label
- capability
- risk tier
- approval status
- expected external effect

---

## Trust Panel Requirement

For this future model, Trust Panel is not cosmetic. It is required.

It should show:

- what Nova read
- what Nova inferred
- which agent requested the action
- which workspace the action belongs to
- which capability would execute
- risk tier
- approval requirement
- expected external effect
- receipt after completion

This is how Nova makes governance visible and useful to the user.

---

## Implementation Order

Recommended order:

1. Lock the agent operating model, personality layer, and feed contract.
2. Build a mock Email Coordination Board without live Google API.
3. Produce structured feeds from mock email threads.
4. Add a simple Personality Layer formatter over those feeds.
5. Render the board in dashboard form.
6. Add BatchActionEnvelope output.
7. Add Trust Panel preview.
8. Add Gmail/Calendar read-only connector surfaces.
9. Add draft-only reply/calendar capabilities.
10. Add confirmed writes only after trust and batch approval are mature.
11. Defer high-risk actions such as send, delete, share, deploy, purchase, or DNS changes.

---

## What Is Documented Now

Current planning docs added or updated through this pass:

- `docs/future/NOVA_AGENT_OPERATING_MODEL.md`
- `docs/future/GOOGLE_WORKSPACE_CONNECTOR_PLAN.md`
- `docs/future/EMAIL_COORDINATION_BOARD.md`
- `docs/design/brain/PERSONAL_PERSONALITY_LAYER.md`
- `docs/future/NOVA_PERSONAL_HOME_BUSINESS_OS_SUMMARY.md`

Issue tracker:

- GitHub Issue #67 tracks the implementation path for agent workspaces and Google email/calendar coordination.

---

## Bottom Line

Nova should become a controlled operating system for personal, home, and business coordination.

Its differentiator is not raw autonomy. Its differentiator is controlled coordination:

```text
many inputs
-> many specialized assistants
-> one personal interface
-> governed capabilities
-> visible approval
-> ledgered receipts
```

That is the direction that best fits Nova.
