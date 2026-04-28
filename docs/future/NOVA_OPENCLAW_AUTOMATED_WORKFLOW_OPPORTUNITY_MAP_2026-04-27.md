# Nova OpenClaw Automated Workflow Opportunity Map

Date: 2026-04-27

Status: Future truth / opportunity map / workflow design record

Purpose: capture the recommended OpenClaw workflow direction for Nova, grounded in Nova's current OpenClaw plan, current repo truth, and observed public OpenClaw usage patterns. This document is future planning only. It does not claim these workflows are implemented today.

---

## Executive Summary

OpenClaw should become Nova's hands, but only under Nova's law.

The correct workflow pattern is:

```text
read → analyze → draft → propose → wait for approval → log what happened
```

The wrong pattern is:

```text
connect OpenClaw to tools/accounts → let it decide and act broadly → hope logs are enough later
```

Nova's advantage is not that it can automate everything. Nova's advantage is that it can prepare, explain, ask, act only inside permission, and record what happened.

Short product rule:

> **Nova gets the work ready. The user keeps authority. OpenClaw only acts inside Nova-issued envelopes.**

---

## Current Nova Truth

The current Nova OpenClaw plan already has the right hard architecture:

```text
OpenClawMediator
EnvelopeFactory
EnvelopeStore
TaskEnvelope
approval queue
envelope-aware tool execution
role-aware worker envelopes
receipts and non-action statements
Business Follow-Up Brief first proof
```

Current truth to preserve:

```text
OpenClaw is real in Nova, but it is not yet full hands.
Current OpenClaw should be described as governed home-agent templates and narrow worker foundations.
Full Phase-8 governed envelope execution remains deferred.
The OpenClaw approval endpoint is still transitional/passthrough.
```

Reference:

```text
docs/future/NOVA_OPENCLAW_HANDS_LAYER_IMPLEMENTATION_PLAN.md
```

---

## Source Hygiene / Evidence Boundary

This document uses public OpenClaw/community patterns as planning inputs, not as authoritative implementation truth for Nova.

Use this distinction:

```text
Nova repo truth → authoritative for Nova current status.
Official/project docs → useful for understanding OpenClaw concepts and common setup patterns.
Community articles/workflow examples → useful for opportunity discovery.
Security/news articles → useful risk signals that must be rechecked before public/security claims.
```

Do not copy raw public claims into README, marketing, security docs, or implementation commitments without rechecking current sources.

Nova implementation truth must come from:

```text
live repo code
generated runtime truth docs
capability verification docs
tests
owner direction / priority override
```

---

## Observed Public OpenClaw Usage Patterns

Public/community OpenClaw usage generally clusters around these patterns:

```text
morning / daily intelligence briefs
email triage and summaries
calendar/task reminders
scheduled reports and cron jobs
receipt and expense tracking
GitHub pull-request review
CI/CD monitoring
log analysis and alerts
browser automation
form filling
social/content workflows
smart-home / Home Assistant control
multi-agent routing by channel/account/persona
chat-app access through Telegram, WhatsApp, Slack, Discord, Signal, or iMessage-style channels
```

Public references reviewed during planning:

```text
Remote OpenClaw — operator workflows and morning intelligence briefs
https://www.remoteopenclaw.com/blog/openclaw-operator-workflows
https://www.remoteopenclaw.com/blog/openclaw-daily-briefing-setup-guide

OpenClaw docs — multi-agent workspaces, state, memory, providers, and channel bindings
https://clawdocs.org/guides/multi-agent/
https://openclawlab.com/en/docs/concepts/multi-agent/
https://openclawlab.com/en/docs/concepts/agent-workspace/

OpenClaw scheduled task / cron-style usage
https://docs.openclaw.ai/automation/cron-jobs
https://openclawai.io/guides/first-automation/

Security/risk reporting and guidance around OpenClaw-like self-hosted agents
https://www.microsoft.com/en-us/security/blog/2026/02/19/running-openclaw-safely-identity-isolation-runtime-risk/
https://www.techradar.com/pro/security/the-math-is-simple-openclaw-trojan-horse-ai-agents-give-hackers-full-control-of-28-000-systems
https://www.techradar.com/pro/security/microsoft-says-openclaw-is-unsuited-to-run-on-standard-personal-or-enterprise-workstation-so-should-you-be-worried
https://www.mcafee.com/learn/is-openclaw-safe-to-install/
```

---

## What Nova Should Copy

Nova should copy the useful workflow shapes, not the broad authority model.

Good patterns to adapt:

```text
daily briefings
scheduled reports
multi-agent separation by role
separate workspaces/state per role
read-only digests
email/calendar/task summaries
GitHub/repo review summaries
log and health monitoring
operator reminders
assistant by channel or role
```

But Nova should wrap those patterns in:

```text
RequestUnderstanding
GovernorMediator
OpenClawMediator
Nova-issued envelopes
explicit allowed/blocked tools
approval queue
ledger and receipts
non-action statements
trust/action-history review
```

---

## What Nova Should Not Copy

Do not copy the common risky pattern:

```text
chat app connected directly to an agent with broad powers
browser/file/email/shell access without Nova envelope constraints
agent sending email on a schedule
agent auto-filling and submitting forms
agent installing plugins/capabilities freely
internet-exposed OpenClaw control panels
shared credentials across roles/agents
unbounded workspace access
always-on browser automation with stored sessions
```

Why:

```text
Self-hosted agents with broad local files, credentials, plugins, browser control, code execution, or exposed ports create high-risk failure modes.
Prompt injection, malicious plugins, stored-token exposure, and remote-control surfaces can turn productivity workflows into system compromise paths.
```

Nova's product position should be the opposite:

> **OpenClaw may be powerful, but Nova is the governor that prevents uncontrolled authority.**

---

## Workflow Ladder

Nova should not jump directly to full automation. Build in this order:

```text
1. Read-only briefs
2. Draft-only proposals
3. Local reversible actions
4. Approval-required external actions
5. Real OpenClaw hands
```

This ladder keeps the user in control while still adding value early.

---

## Tier 1 — Read-Only Briefs

These are the best first workflows because they are useful and low-risk.

### Morning / Daily Operator Brief

Purpose:

```text
Give the user one concise daily briefing.
```

Possible inputs:

```text
calendar
weather
tasks
flagged emails
project status
news/topics being tracked
reminders
```

Nova-safe output:

```text
summary
priority list
prep notes
suggested actions
nothing changed statement
```

Required receipt:

```text
Nova read available sources and produced a brief. No messages were sent, no calendar events were changed, and no files were modified.
```

### Project Foreman Brief

Purpose:

```text
Tell the owner what changed, what is blocked, what is next, and what not to touch.
```

This is probably the best first Nova-specific OpenClaw workflow because it matches the owner's real work pattern.

Possible inputs:

```text
git status
git log
recent changed files
test results
current priority override
BackLog.md
handoff docs
runtime truth docs
```

Nova-safe output:

```text
current status
completed work
blocked work
stale docs
tests run
best next prompt for Claude/Codex
what not to touch
```

Required non-action statement:

```text
No files were changed. No commits were made. No capabilities were executed. This is a read-only recommendation.
```

### Repo Health Brief

Purpose:

```text
Review the repo for drift, stale docs, failed tests, TODO clusters, or governance inconsistencies.
```

Allowed early scope:

```text
read files
read test output
compare docs to code
prepare report
```

Blocked early scope:

```text
no edits
no commits
no pushes
no merges
no branch changes
```

### Local System Health Brief

Purpose:

```text
Summarize local runtime health before any hands-layer work.
```

Possible inputs:

```text
Nova server status
model lock status
Ollama reachability
token budget state
configured local capabilities
recent ledger errors
bootstrap logs
```

Required non-action statement:

```text
No system settings were changed.
```

---

## Tier 2 — Draft-Only Proposals

Draft-only workflows are the next best product tier.

Rules:

```text
OpenClaw may prepare.
Nova may display.
User approves.
Nothing sends or submits automatically.
```

Recommended workflows:

```text
draft follow-up email
draft client reply
draft meeting agenda
draft GitHub issue
draft PR summary
draft daily plan
draft customer quote/proposal
draft social/content post
draft form-fill plan
```

Required user-facing state:

```text
Draft prepared.
Not sent.
Not submitted.
Waiting for approval or manual user action.
```

Required receipt:

```text
Nova/OpenClaw prepared a draft only. Nothing was transmitted.
```

---

## Tier 3 — Local Reversible Actions

This should come after the local capability signoff matrix.

Candidate actions:

```text
open app
open folder
open file
change volume
pause/play media
adjust brightness
take screenshot
read diagnostics
explain screen
```

Required before OpenClaw can call them:

```text
capability exists in registry
request routes correctly
confirmation behavior is correct if needed
executor works on target platform
bad input fails safely
ledger/trust receipt records attempt/result
limits are documented
```

OpenClaw should not call unverified local capabilities.

---

## Tier 4 — Approval-Required External Actions

These are valuable but should not be early.

Candidate workflows:

```text
Gmail draft creation
calendar event creation
CRM/customer update
Shopify/customer operations
posting content
submitting forms
booking appointments
purchases/payments
```

Default policy:

```text
READ → may be auto-allowed inside envelope
DRAFT_ONLY → may prepare, not send
LOCAL_REVERSIBLE → may be allowed only after signoff and settings permit
DURABLE_MUTATION → pending approval
EXTERNAL_WRITE → pending approval
FINANCIAL / billing / purchase → hard approval or blocked first
```

Required receipt examples:

```text
Nova summarized 3 email threads. No emails were sent.
Nova prepared one Gmail draft. It was not sent.
Nova proposed a calendar event. It was not created until approved.
Nova proposed a CRM update. No customer record was changed.
```

---

## Tier 5 — Do Not Build Early

Avoid early implementation of:

```text
autonomous purchases
autonomous email sending
calendar auto-booking
file deletion/moving
bulk inbox changes
customer record mutation
financial actions
credential handling
always-on browser automation
third-party plugin execution without isolation
internet-exposed agent control
unreviewed code execution
```

These should only be considered after:

```text
OpenClawMediator exists
EnvelopeFactory is mandatory or deprecated direct-run accounting is complete
approval queue is real
ThinkingLoop and tools are envelope-aware
receipts are visible
local capabilities are signed off
connector scopes are governed
security posture is documented
```

---

## Specific Nova Workflow Opportunities

### 1. Nova Project Foreman Brief

Best first OpenClaw workflow.

User prompt:

```text
Nova, review the project and tell me what changed, what is blocked, and what Claude should do next.
```

Inputs:

```text
git status
git log
changed files
test output
current priority override
BackLog.md
handoff docs
runtime truth docs
```

Outputs:

```text
current truth
completed work
blocked work
stale docs
risk notes
next prompt
what not to touch
```

Receipt:

```text
No files changed. No commits made. No capabilities executed.
```

Why it matters:

```text
It solves the recurring token/session handoff problem and fits the user's real work pattern.
```

### 2. Token Recovery / Session Continuity Brief

Purpose:

```text
When Claude/Codex/OpenClaw runs out of tokens, Nova prepares a recovery handoff.
```

Outputs:

```text
what was completed
what files changed
what tests ran
what failed/blocked
what still needs review
next best prompt
```

This is one of the highest-value workflows for this project.

### 3. Local Capability Signoff Assistant

Purpose:

```text
Help the owner verify every local capability before OpenClaw can rely on it.
```

Workflow:

```text
read registry
list enabled local capabilities
run available tests
ask owner to perform live action where required
record pass/fail/blocked
record limits and platform caveats
suggest small fixes
```

Blocked behavior:

```text
Do not silently fix everything.
Do not broaden capability scope.
Do not sign off without evidence.
```

### 4. Safe GitHub Review Assistant

Purpose:

```text
Review repo changes and prepare human-friendly GitHub summaries.
```

Outputs:

```text
commit summary
PR notes
test report
risk review
doc drift review
next suggested prompt
```

Approval boundary:

```text
No push, merge, branch deletion, release creation, or repo mutation without explicit approval.
```

### 5. Business Follow-Up Brief

This is already in the OpenClaw hands-layer plan and should remain the first business proof.

Workflow:

```text
read local/sample customer data
identify follow-up opportunities
draft suggested messages
show approval queue
state nothing was sent or changed
```

Why it matters:

```text
It proves Nova can create business value without uncontrolled external writes.
```

### 6. Screen-To-Action Review

Purpose:

```text
Nova sees or is given screen/page context and prepares the next safe step.
```

Examples:

```text
email reply screen → draft response, do not send
form page → draft field values, do not submit
GitHub page → summarize PR, do not merge
calendar page → suggest event details, do not create
settings page → explain, do not change
```

Required statement:

```text
I can help draft/review this. I will not click submit, send, save, buy, or change settings without approval.
```

### 7. Find-The-Gap Auditor

Purpose:

```text
Find mismatches between docs, code, tests, and roadmap.
```

Outputs:

```text
overstated docs
under-tested code
stale roadmap
missing receipts
missing tests
unsafe action path
recommended fix order
```

Boundary:

```text
Read-only by default. Edits require explicit approval.
```

### 8. Household / Personal Daily Brief

Later, after connectors are ready:

```text
calendar
weather
tasks
emails needing response
reminders
project status
shopping list
```

Boundary:

```text
No email sent, event created, item purchased, or form submitted automatically.
```

### 9. Document Pack Builder

Purpose:

```text
Prepare bundles of docs for a human task.
```

Examples:

```text
interview prep packet
client proposal packet
capability signoff packet
launch readiness packet
legal/insurance question packet
```

Boundary:

```text
May gather and format. Must not submit, send, sign, or file anything.
```

### 10. Local Workspace Organizer Preview

Purpose:

```text
Suggest file/folder organization without changing files.
```

Output:

```text
recommended folder moves
duplicates found
stale files
safe cleanup proposal
```

Boundary:

```text
No moving, renaming, deleting, or overwriting without approval.
```

---

## Multi-Agent Opportunity For Nova

Public OpenClaw patterns use multiple isolated agents by workspace, memory, provider, and channel.

Nova should adapt this carefully as role-bound workers, not uncontrolled personalities.

Candidate Nova roles:

```text
Project Foreman
Business Assistant
Household Assistant
Repo Auditor
Capability Tester
Research Analyst
Voice Concierge
```

Each role should have:

```text
own workspace or scoped input context
own allowed tools
own blocked tools
own risk level
own receipt format
own approval rules
own data access policy
```

Do not let roles inherit broad system access just because OpenClaw supports multi-agent routing.

Nova role rule:

> **A role is a bounded policy envelope, not just a personality.**

---

## Scheduled Task Opportunity

Public OpenClaw usage often centers on cron/scheduled tasks such as daily briefs, email digests, reports, and reminders.

Nova should support scheduled reasoning before scheduled action.

Good scheduled jobs:

```text
morning operator brief
weekly project status
weekly repo drift review
local system health summary
business follow-up opportunities
reminder digest
news/topic tracker summary
```

Bad early scheduled jobs:

```text
send emails every morning
book appointments automatically
submit forms automatically
move/delete files automatically
purchase items automatically
modify customer records automatically
```

Scheduler rule:

> **Scheduled jobs may think and prepare. Scheduled jobs must not perform external-world actions without an approval path and receipt.**

---

## Required UX Pattern

Every OpenClaw workflow should end with a trust statement.

Examples:

```text
Nothing was sent.
Nothing was posted.
No files were changed.
No customer records were changed.
No purchases were made.
One draft was prepared and is waiting for approval.
Two proposed actions require review.
```

This should not be optional. It is the user-facing proof that Nova remains the governor.

---

## Required Data Model Concepts

Future OpenClaw run records should capture:

```text
run_id
user_goal
nova_role
request_understanding_id or snapshot
task_type
risk_level
input_sources
allowed_tools
blocked_tools
budget
provider_lane
approval_requirements
proposed_actions
actions_executed
actions_blocked
receipts
non_action_statements
final_summary
```

This makes the workflow auditable.

---

## What To Build First

Do not start with broad hands.

Recommended first workflow after RequestUnderstanding visibility and local capability limits are clearer:

```text
Nova Project Foreman Brief
```

Why this first:

```text
It matches the owner's actual work pattern.
It solves token/session handoff pain.
It is read-only by default.
It can use existing docs and repo state.
It proves OpenClaw can be useful without uncontrolled authority.
It produces a clear receipt: no files changed, no commits made, no capabilities executed.
```

Second workflow:

```text
Token Recovery / Session Continuity Brief
```

Third workflow:

```text
Local Capability Signoff Assistant
```

Fourth workflow:

```text
Business Follow-Up Brief
```

---

## OpenClaw Implementation Order For These Workflows

Before any workflow is treated as real hands:

```text
1. RequestUnderstanding trust/action-history visibility exists.
2. Local capability signoff matrix has started or is complete for relevant actions.
3. OpenClawMediator skeleton exists.
4. EnvelopeFactory is mandatory in controlled mode or deprecated-direct-run accounting is complete.
5. Approval queue is real for non-read actions.
6. ThinkingLoop/tool execution is envelope-aware.
7. Receipts and non-action statements are visible.
```

---

## What To Add To The Existing OpenClaw Plan

The existing plan is strong. Missing or under-emphasized additions:

```text
read-only automation lane
explicit draft-only automation lane
local reversible action lane
scheduled reasoning lane
project/session continuity workflows
capability signoff assistant workflow
screen-to-action review workflow
workspace organizer preview workflow
mandatory non-action statement on every OpenClaw run
role = policy envelope, not personality
```

---

## Final Recommendation

Nova should not compete with other OpenClaw setups by being the most autonomous.

Nova should win by being the most governable.

The opportunity is:

```text
AI that prepares the work humans hate, while keeping authority visible, reversible, and logged.
```

Final sequence:

```text
RequestUnderstanding trust/action-history card
→ local capability signoff matrix
→ OpenClawMediator skeleton
→ read-only Project Foreman Brief
→ Token Recovery / Session Continuity Brief
→ Local Capability Signoff Assistant
→ Business Follow-Up Brief
→ draft-only workflows
→ approval-required external workflows
```

Final rule:

> **OpenClaw gives Nova hands. Nova keeps the law.**
