# Governed Workflow Workspace Architecture

Status: product / architecture planning note; not generated runtime truth
Date: 2026-05-01
Scope: Product-layer shape for Nova as a governed AI workspace for everyday use, independent workflows, and independent business automation

Generated runtime truth, code, tests, and proof artifacts win if they conflict with this note.

---

## Product Framing

Nova should be framed as:

```text
A governed AI workspace for everyday workflows.
AI can research, plan, draft, organize, and operate approved workflows.
Execution stays bounded, visible, permissioned, and receipted through a governor spine.
```

Independent business owners are an important use case, but not the only use case.

Nova should support:

- everyday personal workflows
- household / life admin workflows
- independent creator workflows
- independent contractor workflows
- small business workflows
- research and learning workflows
- content and media workflows
- local-first assistant workflows
- approved automation routines

Avoid provider-first framing:

```text
multi-platform AI workspace wrapped around OpenClaw
```

Prefer product-first framing:

```text
governed AI workspace for everyday workflows and independent automation
```

OpenClaw, Gemma, ElevenLabs, Google, Shopify, GoDaddy, YouTubeLIS, and other tools are components inside the workspace, not the product identity.

---

## What Is Missing Most

Nova already has a strong governance concept.

The missing layer is the everyday workflow workspace that makes governance useful.

The product must answer:

```text
What needs my attention?
What can Nova help me do today?
What did Nova already do?
What needs approval?
What did Nova find?
What is safe to automate?
What should stay manual?
```

---

## 1. Everyday Workflow Workspace Shell

Nova needs a simple operator shell for everyday users and independent operators.

Suggested top-level workspace areas:

```text
Today
Tasks
Projects
People / Contacts
Files / Notes
Messages / Drafts
Content
Research
Automations
Proof / Receipts
Settings / Permissions
```

Business-focused installs may add:

```text
Leads
Clients
Campaigns
Products / Services
Invoices / Payments
Store / Website
```

This is the user-facing product layer above capabilities, connectors, and agents.

Users should not need to understand capability IDs, mediators, or internal agent paths to get value.

---

## 2. Canonical Workflow Object Model

Nova should define shared workflow objects so automations do not become disconnected tool silos.

Minimum objects:

```text
WorkspaceProfile
Workflow
Project
Task
Person
Contact
Conversation
ContentAsset
FileReference
ResearchNote
Approval
Receipt
Automation
Connector
```

Business-oriented optional objects:

```text
BusinessProfile
Lead
Client
Campaign
Invoice
PaymentStatus
Estimate
Contract
Event
Product
Service
Vendor
AssetLibrary
```

Why this matters:

- Everyday tasks, business workflows, content workflows, Google, Shopify, GoDaddy, YouTubeLIS, email, OpenClaw, and future connectors need a shared vocabulary.
- Workflows should operate on durable objects, not one-off prompt output.
- Receipts and approvals should attach to workflow objects.

Example everyday flow:

```text
Project
-> gather context
-> draft plan
-> create task list
-> ask for approval
-> schedule reminders or produce manual next steps
-> receipt
```

Example business flow:

```text
Lead
-> research
-> score
-> draft outreach
-> user approves
-> send manually or through a future governed send path
-> follow-up task
-> receipt
```

---

## 3. Permission Profiles

Nova's governance should be surfaced in everyday user language.

Suggested permission profiles:

| Profile | User-facing meaning |
|---|---|
| Observer | Can only read and summarize. |
| Draft | Can draft emails, posts, reports, plans, and tasks. |
| Assistant | Can prepare actions but needs approval before external effects. |
| Operator | Can run approved bounded workflows. |
| Admin | Can change settings, integrations, permissions, and billing-risk providers. |

These profiles should map to the existing Governor / CapabilityRegistry / approval model, but users should not need to reason in internal capability IDs.

---

## 4. Trust Review Card As A Primary Product Surface

The Trust Review Card is not polish. It is a core product surface.

Every meaningful action should show:

```text
What Nova wants to do
Why Nova wants to do it
What data it will use
What account, connector, file, browser, or tool it may touch
Whether it costs money or uses a free-tier provider
Whether it reads, drafts, writes, sends, publishes, buys, deletes, or changes anything
What happens if approved
What receipt will be created
Approve / deny / edit
```

The governance spine becomes product value only when users can see it.

---

## 5. Cost Posture Runtime Metadata

The Free-First Principle should become runtime-visible metadata before paid-provider expansion.

Recommended values:

```text
free
free_tier
paid
unknown_cost
```

Cost posture should appear in:

- capability metadata
- generated runtime docs
- Trust Review Card
- connector setup screens
- receipts when relevant
- workflow template descriptions

Rule:

```text
Capability does not imply cost permission.
```

---

## 6. Connector Permission Model

Before adding many connectors, Nova should define one common connector permission model.

Each connector should expose:

```text
provider
connector id
connected / disconnected state
scopes
read/write level
cost posture
data accessed
actions allowed
actions blocked
token storage status
last used
receipts
revoke / disconnect control
```

This prevents Google, Shopify, GoDaddy, YouTube, email, social media, and future connectors from becoming separate governance designs.

Connector rule:

```text
A connector can provide context.
A connector does not authorize action by itself.
```

---

## 7. Workflow Template System

Nova should become useful through repeatable everyday and business workflows.

Everyday workflow templates:

```text
Daily planning brief
Personal task organizer
Document / file summarizer
Research pack builder
Appointment prep brief
Follow-up reminder queue
Household checklist builder
Learning plan builder
Decision comparison brief
Travel / errand planner
Content idea organizer
```

Independent business / operator templates:

```text
Website lead finder
Restaurant social media planner
Mobile bar event planner
Shopify store health report
Weekly business briefing
Competitor monitor
Client follow-up queue
Invoice / reminder assistant
Content repurposing flow
Local SEO review
Review response drafter
Proposal / estimate drafter
```

Each workflow template should declare:

```text
inputs
workflow objects touched
tools / connectors used
permissions needed
cost posture
approval points
blocked actions
outputs
receipts
```

This is how Nova becomes an everyday workflow workspace instead of a collection of tools.

---

## 8. Proof / Demo Loops

Nova needs repeatable proof flows that show value quickly while proving governance.

Recommended everyday demo:

```text
Plan my week from tasks, notes, calendar context, and priorities
-> gather local/context sources
-> summarize conflicts and priorities
-> draft task plan
-> ask before scheduling or sending anything
-> receipt shows exactly what was read and proposed
```

Recommended business demo:

```text
Find 5 local businesses that need better websites
-> governed search
-> evidence synthesis
-> lead list
-> draft website improvement notes
-> create outreach draft
-> user approves or edits
-> receipt shows exactly what happened
```

These demonstrate:

- current-information search
- context handling
- useful planning
- draft generation
- approval boundary
- receipts
- no hidden autonomy

---

## 9. Onboarding And First-Run Workspace Profile

Nova needs a first-run workspace profile wizard.

General questions:

```text
What do you want Nova to help with?
What workflows do you repeat every week?
Where do your files and notes live?
Which accounts or connectors do you want available?
What should Nova never do?
What actions require approval every time?
What providers should stay free/local-first?
What should Nova help with first?
```

Business-specific questions:

```text
What business are you running?
What do you sell?
Who are your customers?
What tools/accounts do you use?
What workflow wastes the most time?
```

Outputs:

```text
WorkspaceProfile
optional BusinessProfile
initial permission profile
recommended safe workflows
connector setup checklist
blocked-action preferences
first proof/demo task
```

---

## 10. Architecture Layering

Recommended product architecture:

```text
Workflow Workspace UI
-> Workflow Objects
-> Workflow Templates
-> Task Understanding / Run Preview
-> Trust Review Card
-> Governor / CapabilityRegistry / ExecuteBoundary
-> Connectors / OpenClaw / Executors
-> Ledger / Receipts
```

The Brain may reason and propose.
The workspace organizes context.
The workflow layer structures repeatable work.
The Trust Review Card makes action boundaries visible.
The Governor authorizes execution.
Receipts prove what happened.

---

## Implementation Priority

After Cap 16 conversation/search proof is stable, recommended order:

```text
1. Trust Review Card / action approval UI
2. Workflow object model
3. Workflow template schema
4. Cost posture metadata
5. Connector permission model
6. OpenClaw hardening
7. First everyday demo workflow
8. First business demo workflow
9. First-run workspace profile onboarding
```

Do not prioritize broad autonomy or more integrations before this product spine exists.

---

## Do Not Overstate

Do not claim any of the following until code, tests, generated runtime truth, and proof artifacts agree:

- Nova is a complete everyday workflow OS today
- Nova is full personal SaaS today
- Nova can autonomously run a business
- Nova can send emails, publish, buy, delete, or modify accounts without governed capability support
- Google / Gmail / Calendar / Drive runtime connectors are implemented
- OpenClaw browser/computer-use expansion is ready
- cost posture is runtime-enforced
- workflow templates are runtime products
- workflow object model is implemented
- onboarding wizard exists

---

## Short Public Description

Use this framing in posts and outreach:

```text
I am building a governed AI workspace for everyday workflows and independent automation — a local-first system where AI can research, plan, draft, and help operate workflows, but real actions stay visible, permissioned, and reviewable through a governor spine.
```
