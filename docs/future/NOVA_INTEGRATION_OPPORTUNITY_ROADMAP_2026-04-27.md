# Nova Integration Opportunity Roadmap

Date: 2026-04-27

Status: Future roadmap / integration opportunity record / not current runtime truth

Purpose: capture the major integration opportunities that could improve Nova over time, based on observed patterns in modern agent projects and Nova's governance-first architecture. This document is future planning only. It does not claim these integrations are implemented today.

Related docs:

```text
docs/future/NOVA_COHERENCE_MEMORY_BACKGROUND_ARCHITECTURE_ALIGNMENT.md
docs/future/NOVA_GOOGLE_ACCOUNT_AND_CONNECTOR_ONBOARDING_PLAN.md
docs/future/NOVA_OPENCLAW_AUTOMATED_WORKFLOW_OPPORTUNITY_MAP_2026-04-27.md
docs/future/NOVA_ELEVENLABS_VOICE_OPPORTUNITY_MAP_2026-04-27.md
docs/future/NOVA_BACKGROUND_REASONING_NOT_AUTOMATION_PLAN.md
4-15-26 NEW ROADMAP/CURRENT_PRIORITY_OVERRIDE_2026-04-27.md
```

---

## Active Priority Note

This document is **not** the current active implementation task.

Current active path remains:

```text
RequestUnderstanding trust/action-history review card
→ local capability signoff matrix
→ OpenClawMediator skeleton
→ first read-only OpenClaw workflow proof
→ Google/email connector direction before Cap 64 P5
→ voice provider implementation when the trust/action loop is ready
```

Do not use this roadmap to skip directly into broad connectors, MCP tools, external workflow runners, browser automation, smart-home control, or background automation.

Important sequencing note:

```text
The build order in this document is strategic sequencing after the current trust/action visibility foundation, not permission to start all listed integrations now.
```

---

## Executive Summary

The highest-value integrations for Nova are not the ones that give the model the most power. They are the integrations that make Nova more useful while preserving governed authority.

The strategic pattern is:

```text
connect data carefully
summarize and draft first
require approval for actions
log what happened
state what did not happen
```

Bad pattern:

```text
LLM gets direct tools and credentials
→ LLM acts across email/calendar/files/GitHub/browser/home systems
→ user finds out after the fact
```

Good Nova pattern:

```text
Connector/tool exposes data or proposed action
→ Nova classifies risk
→ GovernorMediator / ExecuteBoundary / NetworkMediator enforce boundaries
→ approval queue handles real-world changes
→ ledger/trust receipt records access, action, and non-action statements
```

Short rule:

> **Integrations may expand Nova's reach. They must not expand authority without governance.**

---

## Source Hygiene / Evidence Boundary

This document uses public agent ecosystem patterns as planning inputs, not as authoritative Nova implementation truth.

Use this distinction:

```text
Nova repo truth → authoritative for Nova current status.
Official product/docs pages → useful for understanding integration concepts and API possibilities.
Community articles/examples → useful for opportunity discovery.
Security/news articles → useful risk signals that must be rechecked before public/security claims.
```

Do not copy public claims into README, marketing, security docs, or implementation commitments without rechecking current sources.

Nova implementation truth must come from:

```text
live repo code
generated runtime truth docs
capability verification docs
tests
owner direction / priority override
```

---

## Current Nova Truth To Preserve

Nova is a governed local-first AI system that separates intelligence from execution.

Current architectural principle:

```text
Intelligence is not authority.
```

Current active priority:

```text
RequestUnderstanding trust/action-history visibility first.
```

Paused / not active:

```text
Cap 64 P5/P6 email signoff
Shopify / Cap 65 live work
Auralis / website merger
Google connector implementation
ElevenLabs implementation
broad OpenClaw execution
background reasoning jobs
governed learning persistence
CRM/SaaS packaging
```

These integrations should be treated as future work and sequenced after the current trust/action loop is visible.

---

## Integration Design Principles

Every integration should answer these questions before implementation:

```text
What data can it read?
What actions can it propose?
What actions can it execute?
Which actions require approval?
What is explicitly blocked?
What gets logged?
What non-action statement is shown?
How can the user disconnect/revoke it?
What happens offline or when the provider fails?
```

Core integration requirements:

```text
connector registry entry
scopes/permissions listed
read/write boundary declared
approval requirements declared
NetworkMediator route for outbound calls where applicable
ledger/trust receipt events
visible status in settings/dashboard
safe failure behavior
disconnect/revoke path
```

---

## Foundation Gates Before Any Integration Becomes Active

Before any roadmap item below moves from future planning into active implementation, verify these gates:

```text
current priority override allows the work
RequestUnderstanding trust/action visibility is complete or explicitly not required for that narrow item
read/write scope is declared
connector/provider status can be shown to the user
approval requirements are defined
receipt and non-action statement behavior is defined
safe failure and disconnect/revoke behavior is defined
no paused scope is accidentally resumed
```

If an integration touches external accounts, files, browser state, smart-home devices, money, customer data, email, calendar, or public posting, it must default to read-only or draft-only until approval and receipts are proven.

---

# 1. MCP-Style Connector Layer

## Opportunity

MCP-style connectors standardize how AI systems connect to data and tools. Many agent projects are moving in this direction because it avoids hardcoding every integration separately.

For Nova, MCP-style integration is useful because it could provide a common layer for:

```text
GitHub / Git
Google Drive
Gmail read-only
Google Calendar read-only
Slack / Discord read-only
Postgres / SQLite
filesystem read-only
browser / Puppeteer-style browsing
Figma / Canva-style design review
```

## Nova Improvement

Nova should eventually support a governed adapter for MCP-style tools.

Good Nova pattern:

```text
MCP server exposes data/tool
→ Nova connector registry registers it
→ Nova classifies read/draft/write risk
→ GovernorMediator / ExecuteBoundary checks policy
→ NetworkMediator controls outbound network if needed
→ ledger/trust receipt records use
```

Blocked pattern:

```text
LLM receives MCP tools directly
→ LLM calls files/GitHub/Gmail/Slack/browser without Nova governance
```

## Recommended Workflows

```text
read GitHub issue/PR data
summarize Google Drive docs
retrieve local project docs
read Slack/Discord thread summaries
query local SQLite/Postgres data
read-only browser page summary
design file review / critique
```

## Guardrails

```text
MCP is connector access, not authority.
Every MCP server must declare read/write capability.
External writes require approval.
Filesystem mutation should be blocked until local capability signoff is complete.
Browser form submission must be blocked unless explicitly approved.
Prompt-injection risks from retrieved content must be treated as untrusted input.
```

## Build Later When

```text
connector registry exists
approval queue exists
trust/action-history receipts are visible
local capability signoff has started
NetworkMediator policy for connector calls is clear
```

---

# 2. Durable Workflow Execution / Run Checkpoints

## Opportunity

Modern agent systems increasingly need durable execution: workflows that can pause, resume, checkpoint, recover, and produce handoffs.

This directly matches Nova's recurring workflow problem:

```text
Claude runs out of tokens
Codex stops mid-task
OpenClaw pauses or fails
user needs to know what changed and what to do next
```

## Nova Improvement

Nova should add a simple run/task-state system before broad OpenClaw work.

Core concept:

```text
Run starts
→ checkpoint after each major step
→ save files read/changed
→ save commands/tests run
→ save blocker/error state
→ save next recommended action
→ resume or handoff cleanly
```

## Recommended Workflows

```text
Token Recovery / Session Continuity Brief
Project Foreman Brief
Background Project Status Review
OpenClaw run handoff
Claude/Codex handoff builder
capability signoff session recorder
repo audit progress tracker
```

## Suggested Data Model

```text
run_id
user_goal
active_priority_snapshot
status: active / paused / blocked / complete / failed
started_at
updated_at
actor: user / Claude / Codex / Nova / OpenClaw
files_read
files_changed
commands_run
tests_run
commits_created
blockers
next_recommended_step
do_not_touch
receipt_ids
handoff_summary
```

## Guardrails

```text
Run state is evidence, not permission.
A checkpoint cannot approve actions.
A resumed task must re-check current priority and policy.
Stale run state must not override current owner direction.
```

## Build Later When

```text
RequestUnderstanding trust/action-history card exists
basic trust receipt surface exists
current priority override is readable by runtime or by a helper
```

---

# 3. Human-In-The-Loop Workflow Runner / n8n-Style Pattern

## Opportunity

Workflow automation platforms show a useful pattern: triggers, branches, scheduled jobs, external integrations, and human-in-the-loop review.

Nova can learn from this without surrendering governance.

## Nova Improvement

Nova should eventually support external workflow runners such as n8n/OpenClaw-style execution as governed executors, not governors.

Good pattern:

```text
Nova approves workflow envelope
→ external runner executes bounded workflow
→ result returns to Nova
→ Nova logs receipt and asks approval for real actions
```

Bad pattern:

```text
workflow runner holds Gmail/Calendar/Slack credentials
→ AI node sends/updates/deletes directly
→ Nova only sees result later
```

## Recommended Workflows

```text
scheduled read-only morning brief
Gmail read-only triage → draft suggestions
Calendar read-only agenda summary
webhook intake → draft response
lead form intake → owner review card
weekly repo/doc drift report
business follow-up opportunity digest
```

## Guardrails

```text
external runner cannot be authority layer
credentials must be scoped
write actions require Nova approval queue
workflow result must include non-action statements
scheduled jobs may reason and prepare, not act silently
```

## Build Later When

```text
OpenClawMediator exists
approval queue exists
connector registry exists
receipts and non-action statements are visible
```

---

# 4. Google Workspace Integration

## Opportunity

Google Workspace is one of the highest-value integration areas because it unlocks everyday usefulness:

```text
calendar awareness
email triage
document search
contact lookup
meeting prep
draft replies
daily briefings
```

## Nova Improvement

Google should be added incrementally and scoped.

Recommended order:

```text
Google Sign-In identity only
→ connector registry / connected apps page
→ Calendar read-only
→ Gmail read-only
→ Drive read-only
→ Contacts read-only
→ Gmail draft-only
→ Calendar event proposal/draft
→ approval-required writes later
```

## Recommended Workflows

```text
today's calendar summary
meeting prep brief
emails needing response
thread summary
turn email thread into tasks
draft reply for review
find relevant Drive doc
summarize selected doc
find contact for draft addressing
calendar conflict summary
```

## Guardrails

```text
Google tokens/scopes grant access, not permission.
No Gmail sending early.
No bulk inbox actions early.
No Calendar creation/editing early.
No Drive file mutation early.
No Contacts mutation early.
Every read/draft/write path needs receipts.
User must be able to disconnect/revoke.
```

## Cap 64 Relationship

Cap 64 P5/P6 remains paused until Google/email direction is clear.

Future decision:

```text
Cap 64 remains standalone mailto draft path
OR Cap 64 becomes Gmail-aligned draft creation
OR Cap 64 is replaced by connector-backed draft flow
```

Do not treat current Cap 64 confirmation-gate behavior as Gmail/email signoff completion.

---

# 5. GitHub / Repo Automation

## Opportunity

GitHub/Git integration is one of the best fits for Nova because the owner already works through repo audits, Claude/Codex prompts, commits, tests, and documentation drift reviews.

## Nova Improvement

Start read-only. Let Nova become excellent at repo understanding before repo mutation.

Recommended workflows:

```text
Project Foreman Brief
Safe GitHub Review Assistant
Doc Drift Auditor
Commit Summary Generator
PR Risk Review
Test Failure Explainer
Branch/commit status summary
Claude/Codex Handoff Builder
Release note draft
```

## Good Early Pattern

```text
read git status
read recent commits
read changed files
read tests/output
compare docs to code
prepare summary and next prompt
```

## Block Early

```text
no push
no merge
no branch deletion
no release creation
no file edits unless explicitly approved
no secret exposure
no automatic issue/PR creation without approval
```

## Future Approval Pattern

```text
Nova proposes commit/PR summary
User reviews
Nova creates draft PR text or issue text
User approves actual repo write separately
Receipt records what happened
```

## Why It Matters

This integration improves Nova itself faster than most business integrations.

It directly supports:

```text
continuity after token exhaustion
repo truth audits
document coherence
phase closeouts
test/report summaries
next-prompt generation
```

---

# 6. Tracing, Spans, And Observability

## Opportunity

Modern agent systems increasingly include tracing: structured records of runs, routes, tool calls, guardrail decisions, model calls, and handoffs.

Nova already has ledger/trust concepts. It should turn those into a user-facing trace model without exposing private chain-of-thought.

## Nova Improvement

Add trace cards or trust spans.

Suggested span types:

```text
conversation_received
request_understanding_created
route_decision_made
model_provider_selected
capability_considered
capability_blocked
approval_required
tool_called
tool_blocked
receipt_created
non_action_statement_created
response_delivered
```

## Recommended Workflows

```text
show why Nova refused something
show what Nova understood
show what model/provider was used
show which capability was considered
show whether anything executed
show which receipt was created
show what did not happen
```

## Guardrails

```text
Do not expose private chain-of-thought.
Do not show secrets or sensitive payloads.
Summarize reasoning as safe trace metadata.
Use hashes/summaries for sensitive text.
```

## Build Later When

```text
RequestUnderstanding trust/action-history card exists
receipt store is stable
OpenClaw run records exist or are planned
voice provider events exist or are planned
```

---

# 7. Tool Guardrails / Pre-Post Capability Checks

## Opportunity

Agent frameworks often separate input guardrails, output guardrails, and tool guardrails. Nova already has a stronger governance model, but it can still benefit from explicit pre/post tool guardrail objects.

## Nova Improvement

Add pre/post checks around capability execution and OpenClaw tool calls.

Before tool/capability:

```text
capability registered?
request type allowed?
role allowed?
risk allowed?
confirmation required?
connector scope sufficient?
within budget?
sensitive content involved?
NetworkMediator required?
```

After tool/capability:

```text
result safe to show?
receipt-worthy?
non-action statement needed?
any overclaim in response?
any policy mismatch?
should capability status update?
```

## Recommended Workflows

```text
screen-to-action review
Gmail draft creation
Calendar proposal
OpenClaw tool call
browser automation proposal
Home Assistant device control
file operation proposal
```

## Guardrails

```text
Guardrails cannot override GovernorMediator.
Guardrails should fail closed.
Guardrail decisions should be logged.
Bypass routes should be tested.
```

## Build Later When

```text
local capability signoff matrix has started
OpenClawMediator skeleton exists
approval queue is planned or active
```

---

# 8. Vector Search / Governed Memory Retrieval

## Opportunity

Many AI projects use vector search for semantic retrieval over documents, notes, conversations, code, and memory.

Nova needs this, but governed.

## Nova Improvement

Build local-first governed retrieval for:

```text
uploaded docs
runtime handoffs
project glossary
owner-approved memories
capability docs
audit reports
conversation summaries
repo planning docs
```

## Recommended Workflows

```text
find relevant Nova docs
retrieve current priority
answer project status questions
explain capability status
recover previous session context
search audit reports
find stale docs
support user preference memory
```

## Guardrails

```text
no hidden memory writes
saved memory must be visible/reviewable
memory cannot change authority
retrieved text is untrusted input
sensitive docs should not be sent to cloud models without disclosure/approval
user can delete/supersede memory
```

## Suggested Data Model

```text
memory_id
source_type
source_path_or_ref
summary
embedding
tags
sensitivity_level
owner_confirmed
created_at
updated_at
expires_at optional
superseded_by optional
authority_effect = none
```

## Build Later When

```text
RequestUnderstanding trust/action visibility exists
governed learning plan is ready to implement
memory review/delete UX exists or is planned
```

---

# 9. Home Assistant / Smart Home Integration

## Opportunity

Home Assistant is a strong future integration for Nova's household-node direction because it already provides access to sensors, lights, media, switches, automations, and household devices.

## Nova Improvement

Start with read-only and low-risk reversible controls.

Good early workflows:

```text
summarize home status
read temperature/sensor state
turn on/off simple lights
pause/play media
read door sensor status
explain current device state
suggest automations
```

Approval-required or blocked early:

```text
unlock doors
open garage
disable alarms
change security cameras
change thermostat aggressively
control safety-critical devices
run broad automations silently
```

## Guardrails

```text
device classes must be risk-classified
security/safety devices require hard approval or remain blocked
actions must be reversible where possible
receipts must state what changed
non-action receipts must state when nothing changed
local network calls must route through NetworkMediator or an equivalent local device mediator
```

## Build Later When

```text
local capability signoff matrix is mature
approval queue exists
local network/device mediation is clear
trust/action-history can display device actions
```

---

# 10. Browser Automation / Computer-Use Sandbox

## Opportunity

Browser and computer-use automation can be powerful for website QA, form review, account navigation, dashboard summaries, and screen-to-action help.

For Nova, the safe first version is not auto-clicking. It is screen/page review and draft preparation.

## Nova Improvement

Start with:

```text
summarize current page
explain what user is looking at
draft form fields
draft reply on visible email page
review GitHub PR page
compare website pages
find next safe step
```

Block early:

```text
auto-submit forms
auto-purchase
auto-book
auto-send
delete files
change account settings
log into sensitive accounts automatically
run shell commands outside sandbox
```

## Screen-To-Action Review Pattern

```text
Nova sees page/screen
→ explains what it thinks the task is
→ drafts next step
→ states what it will not do
→ asks user before click/submit/save/send
→ logs result
```

## Guardrails

```text
browser session is untrusted input
page content can prompt-inject the agent
submit/save/send/buy/book/delete are approval-required
credentials must not be exposed to model unnecessarily
sandbox boundaries must be explicit
screen capture and analysis must be logged
```

## Build Later When

```text
screen analysis is stable
approval queue exists
OpenClawMediator exists
local capability signoff is mature
browser sandbox policy is documented
```

---

## Cross-Cutting Missing Pieces

Across all 10 ideas, the biggest missing or underweighted pieces are:

```text
task/run-state store
connector registry
approval queue as first-class product surface
non-action receipts
provider abstraction
governed retrieval/memory review
trace cards / trust spans
sensitive-content routing
budget controls for cloud providers
safe disconnect/revoke UX
```

These should be treated as foundation work before wide connector expansion.

---

## Recommended Overall Build Order

This order is strategic. It is not a single sprint and not permission to work on every item now.

```text
1. RequestUnderstanding trust/action-history card
2. Task/run-state store
3. Connector registry
4. Approval queue
5. Google Calendar read-only
6. Gmail read-only
7. Gmail draft-only
8. GitHub/Git read-only review assistant
9. Local governed memory/retrieval
10. OpenClawMediator skeleton
11. Project Foreman Brief
12. Token Recovery / Session Continuity Brief
13. ElevenLabs TTS provider
14. Voice setup diagnostic
15. Home Assistant read/reversible controls later
16. MCP adapter only after connector registry/governance exists
17. n8n/external workflow runner only as governed executor, not governor
18. Browser/computer-use sandbox only as screen-to-action review first
```

Do not start items 2+ until the active priority override allows the next step.

---

## Highest ROI For This Owner

Given the owner's actual work style, prioritize:

```text
GitHub/Git review
Task/run-state store
Google Calendar read-only
Gmail read-only/draft-only
visible governed memory/retrieval
ElevenLabs TTS
OpenClaw Project Foreman Brief
Home Assistant later
```

Why:

```text
GitHub/Git review improves Nova development directly.
Task/run-state store solves token exhaustion and handoff pain.
Google/Gmail unlock daily usefulness.
Memory/retrieval improves coherence.
ElevenLabs improves user experience without expanding authority if output-only.
OpenClaw Project Foreman Brief proves useful hands safely.
Home Assistant supports household-node vision later.
```

---

## What Nova Should Avoid

Avoid becoming a generic agent with every integration wired directly to the model.

Do not build early:

```text
ungoverned MCP tools
full Gmail send/delete/archive/label automation
auto-calendar booking
unreviewed browser form submission
autonomous purchases
Home Assistant security/door/garage automation
n8n workflows with direct credentials and AI writes
hidden vector memory writes
unbounded computer-use shell access
ElevenAgents direct webhooks into business systems
```

---

## Final Product Position

Most agent projects are racing toward:

```text
more tools
more connectors
more autonomy
```

Nova should race toward:

```text
better connector governance
better approval UX
better receipts
better run continuity
better visible memory
```

Final rule:

> **Nova can integrate widely, but every integration must remain bounded, visible, reversible where possible, approved when necessary, and logged.**
