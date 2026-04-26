# Nova OpenClaw Hands-Layer Implementation Plan

Date: 2026-04-26

Status: Future implementation plan / build sequence

Purpose: convert the OpenClaw docs-to-code alignment audit into an actionable build plan. This document does **not** claim the full hands layer is implemented today.

Related docs:

- [`../audits/2026-04-26/NOVA_OPENCLAW_DOCS_TO_CODE_ALIGNMENT_AUDIT_2026-04-26.md`](../audits/2026-04-26/NOVA_OPENCLAW_DOCS_TO_CODE_ALIGNMENT_AUDIT_2026-04-26.md)
- [`NOVA_FULL_STACK_DIRECTION_FINAL_LOCK_2026-04-26.md`](NOVA_FULL_STACK_DIRECTION_FINAL_LOCK_2026-04-26.md)
- [`NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md`](NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md)
- [`../reference/HUMAN_GUIDES/28_OPENCLAW_SETUP_AND_RUNTIME_GUIDE_2026-03-27.md`](../reference/HUMAN_GUIDES/28_OPENCLAW_SETUP_AND_RUNTIME_GUIDE_2026-03-27.md)

---

## Final Direction

The future stack direction is:

> **ElevenLabs speaks. Gemma reasons. OpenClaw acts. Nova governs.**

This plan focuses on making the OpenClaw part true:

> **OpenClaw acts only inside Nova-issued envelopes, with Nova retaining policy, approval, logging, and execution authority.**

---

## Current Truth Baseline

OpenClaw is already real in Nova, but it is not yet the full hands layer.

Current accurate description:

> **OpenClaw currently supports governed home-agent templates and narrow worker foundations.**

Current implemented foundations include:

```text
Cap 63 openclaw_execute
TaskEnvelope
EnvelopeFactory foundation
EnvelopeStore
OpenClawAgentRunner
OpenClawAgentScheduler
OpenClaw API router
ThinkingLoop
ToolRegistry
RobustExecutor
ExecutorSkillAdapter
OpenClawProposedAction model
runtime store / active run tracking
cancel request support
ledger events
```

Known current gap:

> **Full Phase-8 governed envelope execution remains deferred, and the OpenClaw approval endpoint is still a transitional passthrough.**

---

## Target Architecture

Future OpenClaw handoff path:

```text
User voice/text request
→ Nova role/session controller
→ GovernorMediator
→ OpenClawMediator
→ EnvelopeFactory
→ EnvelopeStore
→ OpenClaw runner / thinking loop
→ proposed action gate if needed
→ approval queue / user decision
→ ledger / trust receipt
→ ElevenLabs voice response or local/text fallback
→ dashboard transcript, result, and receipt
```

Blocked future path:

```text
User/channel request
→ OpenClaw directly decides and acts
→ email/social/calendar/CRM/payment/file mutation happens without Nova approval
```

---

## Build Sequence

### Phase 0 — Preserve Current Cap 63 Behavior

Goal: do not break current read-only home-agent templates while refactoring.

Tasks:

```text
confirm Cap 63 tests pass
confirm manual template runs still work
confirm scheduler remains settings-gated
confirm current runtime docs still reflect active/deferred state truthfully
```

Done means:

```text
Existing OpenClaw template behavior is unchanged.
No broad autonomy is introduced.
Generated runtime docs still match code.
```

---

### Phase 1 — Add OpenClawMediator Skeleton

Goal: create one obvious delegation boundary without changing behavior yet.

Tasks:

```text
add src/openclaw/openclaw_mediator.py
route new code through mediator behind a feature flag or test-only path
mediator accepts requested role, goal, template/task type, trigger, and source
mediator calls EnvelopeFactory
mediator records an issued-run ledger event
mediator returns normalized run request metadata
```

Done means:

```text
There is one central OpenClaw delegation object.
No new authority is granted.
Manual/scheduler code can be migrated gradually.
```

---

### Phase 2 — Make EnvelopeFactory Mandatory In Controlled Mode

Goal: stop legacy direct envelope construction from being the normal future path.

Tasks:

```text
add tests for EnvelopeFactory manual run path
add tests for EnvelopeFactory scheduler path
add tests for refused envelopes
add tests for settings hash and feature flag snapshot
add tests for expired envelope handling if supported
flip factory-on path in staging/test mode
keep legacy fallback only during migration
```

Done means:

```text
All OpenClaw runs in controlled mode require a Nova-issued envelope.
Legacy direct construction is visibly deprecated.
```

---

### Phase 3 — Real Approval Queue For Proposed Actions

Goal: replace passthrough auto-allow with real decision states.

Tasks:

```text
create pending OpenClaw action store
store OpenClawProposedAction records
return pending for durable/external/high-risk actions
add approve endpoint
add deny endpoint
add expire/cancel behavior
log proposed/approved/denied/expired events
surface pending actions in dashboard/trust UI
support voice prompt: "This needs approval."
```

Decision defaults:

```text
READ → auto-allowed
LOCAL_MUTATION → auto-allowed only if reversible and user settings permit
DURABLE_MUTATION → pending
EXTERNAL_WRITE → pending
FINANCIAL / payment / purchase / charge → hard approval or blocked first
```

Done means:

```text
No durable mutation or external write can auto-run through OpenClaw.
User can approve or deny proposed actions.
Ledger records the decision.
```

---

### Phase 4 — Make Tool Execution Envelope-Aware

Goal: make every tool call respect the task envelope.

Before each tool call, check:

```text
tool is in envelope.tools_allowed
network host is allowed if network tool
budget remains for steps/network/files/bytes/time
action class is permitted for the role/task
action does not violate sensitive-data policy
approval state permits execution
```

Tasks:

```text
add envelope context to ThinkingLoop
add envelope context to RobustExecutor or wrapper gate
block tools not listed in envelope
block network calls outside allowed_hostnames
classify registry tools by action class
add tests for blocked tool selection
add tests for budget exceeded
add tests for network host blocked
```

Done means:

```text
The thinking loop cannot execute a tool merely because it exists in the registry.
It must also be allowed by Nova's envelope and policy.
```

---

### Phase 5 — Govern Executor-Backed Tools

Goal: prevent executor-backed OpenClaw tools from bypassing Nova governance.

Current risk:

```text
ExecutorSkillAdapter can wrap a Governor executor and call it directly with a duck-typed request.
```

Preferred future path:

```text
Executor-backed OpenClaw tools route through GovernorMediator or a mediator-controlled equivalent boundary.
```

Tasks:

```text
identify all executor-backed OpenClaw tools
classify each as read/local/durable/external
add tests proving mutation tools require permitted envelope and approval where needed
route adapter through governed action dispatch where possible
or block direct executor adapter use outside low-risk/reversible paths
```

Done means:

```text
OpenClaw cannot use executor-backed tools as a hidden action back door.
```

---

### Phase 6 — Add Role-Aware Worker Envelopes

Goal: make OpenClaw task envelopes match Nova roles.

Add or model fields:

```text
nova_role
user_goal
task_type
risk_level
allowed_actions
blocked_actions
requires_approval_for
input_context
output_format
receipt_required
sensitive_data_policy
voice_summary_required
```

Example role policies:

```text
Business Assistant:
- may read local/sample customer records
- may draft replies
- may suggest follow-ups
- may not send messages
- may not change CRM records without approval

Owner Mode:
- may inspect repo
- may run approved tests
- may prepare reports
- may not commit/push/merge without approval

Home Assistant:
- may summarize reminders/docs
- may create reminder drafts
- may not submit forms or purchase items without approval
```

Done means:

```text
OpenClaw runs are role-aware and cannot inherit broad tool access just because a tool exists.
```

---

### Phase 7 — Receipts And Non-Action Statements

Goal: make OpenClaw work reviewable and user-trustworthy.

Each run should record:

```text
what was requested
role/task/risk classification
what envelope allowed
what tools ran
what files/network/resources were touched
what output was produced
what was proposed for approval
what was denied or blocked
what did not happen
```

User-facing statements:

```text
Nothing was sent.
Nothing was posted.
No customer records were changed.
No files were deleted.
Two drafts are waiting for approval.
```

Done means:

```text
A normal user can ask "What did Nova/OpenClaw do?" and get a clear, bounded answer.
```

---

### Phase 8 — First Proof: Business Follow-Up Brief

Goal: prove OpenClaw can be useful hands without uncontrolled authority.

Workflow:

```text
User:
Nova, act as my business assistant. Who do I need to follow up with?

Nova:
classifies Business Assistant role and read-only/draft-only scope

Gemma:
reasons/summarizes/drafts

OpenClaw:
reads sample/local customer data inside a Nova envelope
identifies follow-ups
drafts suggested replies

ElevenLabs:
speaks the result when online

Nova:
shows transcript, drafts, approval queue, and receipt
confirms nothing was sent or changed
```

Done means:

```text
useful result exists
nothing sent automatically
nothing changed without approval
OpenClaw stayed inside envelope
Gemma did not approve actions
ElevenLabs only spoke/provided voice
Nova logged and governed the run
```

---

## Test Gates

Before claiming the hands layer is working, tests should prove:

```text
OpenClaw cannot run a tool outside envelope.tools_allowed.
OpenClaw cannot call a blocked hostname.
OpenClaw cannot exceed network/file/step/time budgets.
OpenClaw cannot use mutation tools without policy allowance.
Durable mutation becomes pending approval.
External write becomes pending approval.
Denied actions do not execute.
Expired approvals do not execute.
Every worker run creates ledger/receipt data.
Business Follow-Up Brief sends nothing and changes nothing.
```

---

## Documentation Update Requirements

When implementation advances, update:

```text
docs/current_runtime/ generated docs only through generator
docs/reference/HUMAN_GUIDES/28_OPENCLAW_SETUP_AND_RUNTIME_GUIDE_2026-03-27.md
docs/capability_verification/live_checklists/cap_63_openclaw_execute.md
4-15-26 NEW ROADMAP/Now.md
4-15-26 NEW ROADMAP/BackLog.md
```

Do not manually edit generated runtime truth docs.

---

## Guardrail

Do not describe OpenClaw as full hands until this is true:

> **Nova can safely direct OpenClaw to do useful work without giving OpenClaw uncontrolled authority.**

Until then, describe current OpenClaw as:

> **governed home-agent templates and narrow worker foundations.**
