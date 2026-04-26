# Nova OpenClaw Docs-To-Code Alignment Audit

Date: 2026-04-26

Status: Documentation alignment audit / current truth vs future direction

Scope: OpenClaw first. This document compares the new full-stack future truth against the current OpenClaw implementation and records what must eventually change.

Related docs:

- [`../../future/NOVA_FULL_STACK_DIRECTION_FINAL_LOCK_2026-04-26.md`](../../future/NOVA_FULL_STACK_DIRECTION_FINAL_LOCK_2026-04-26.md)
- [`../../future/NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md`](../../future/NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md)
- [`../../reference/HUMAN_GUIDES/28_OPENCLAW_SETUP_AND_RUNTIME_GUIDE_2026-03-27.md`](../../reference/HUMAN_GUIDES/28_OPENCLAW_SETUP_AND_RUNTIME_GUIDE_2026-03-27.md)
- [`../../current_runtime/CURRENT_RUNTIME_STATE.md`](../../current_runtime/CURRENT_RUNTIME_STATE.md)

---

## Final Stack Truth Being Aligned Toward

The accepted future direction is:

> **Nova is the governor. Gemma is the local-first reasoning brain. OpenClaw is the hands. ElevenLabs is the standard online voice experience. Local voice/text remains the offline and privacy fallback. Every real-world action stays visible, bounded, approved, logged, and reviewable.**

Short form:

> **ElevenLabs speaks. Gemma reasons. OpenClaw acts. Nova governs.**

This audit focuses on the OpenClaw part:

> **OpenClaw acts, but Nova governs.**

---

## Current OpenClaw Truth

OpenClaw is already real inside Nova.

Current generated runtime truth identifies `openclaw_execute` as active Cap 63 and describes it as the Phase 8 canonical governed execution surface for OpenClaw home-agent templates.

Current runtime truth also states that broader/full Phase-8 governed envelope execution remains deferred.

That means the accurate current description is:

> **OpenClaw currently exists as governed home-agent templates and narrow worker foundations, not yet as a fully general hands layer.**

---

## Current Implemented Pieces

The codebase already contains meaningful OpenClaw machinery:

```text
TaskEnvelope
EnvelopeFactory foundation
OpenClawAgentRunner
OpenClawAgentScheduler
OpenClaw API router
ThinkingLoop
ToolRegistry
RobustExecutor
ExecutorSkillAdapter
OpenClawProposedAction model
EnvelopeStore
runtime store / active run tracking
cancel request support
scheduler suppression/rate controls
ledger events for OpenClaw runs
```

This is not merely a future idea.

The system has real worker foundations.

---

## Primary Alignment Gap

The final future truth says:

> **OpenClaw is the hands. Nova is the governor.**

Current code is closer to:

> **OpenClaw runs governed home-agent templates and some transitional tool paths under partial envelope/budget controls.**

The most important gap is that OpenClaw has not yet fully crossed from template-based governed runs into a production-grade, mediator-controlled worker layer.

---

## Key Code Findings

### 1. Cap 63 Is Still Read-Only Template-Oriented

Current registry truth classifies Cap 63 as:

```text
authority_class: read_only_network
risk_level: low
requires_confirmation: false
external_effect: true
```

That is appropriate for current read-only templates.

It is not sufficient for future broad OpenClaw hands behavior.

Future OpenClaw may need either:

```text
separate capability IDs for OpenClaw lanes
```

or:

```text
internal sub-authority lanes under Cap 63
```

Recommended future lanes:

```text
openclaw_readonly_execute
openclaw_draft_worker
openclaw_local_control_worker
openclaw_durable_mutation_proposal
openclaw_external_write_proposal
```

---

### 2. TaskEnvelope Is Strong But Needs Role/Intent Expansion

Current `TaskEnvelope` already supports:

```text
tools_allowed
allowed_hostnames
max_steps
max_duration_s
max_network_calls
max_files_touched
max_bytes_read
max_bytes_written
triggered_by
delivery_mode
status
```

This is a strong base.

Future task envelopes should also include:

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

This turns a template envelope into a role-aware worker envelope.

---

### 3. EnvelopeFactory Is Correct But Transitional

`EnvelopeFactory` is architecturally aligned with the future.

It is intended to be the sole authorized constructor of task envelopes.

However, it is feature-flagged through:

```text
NOVA_FEATURE_ENVELOPE_FACTORY
```

When the flag is off, legacy direct construction can still occur.

Future alignment requires:

```text
EnvelopeFactory becomes mandatory for all OpenClaw runs.
Legacy direct envelope construction is removed or restricted to tests.
Manual, scheduler, bridge, and goal runs all issue through the factory.
```

---

### 4. Approval Endpoint Is Currently Passthrough

The current OpenClaw action approval endpoint is a transitional passthrough.

It logs an action proposal and then returns allow/auto_allowed.

This must change before OpenClaw becomes full hands.

Future approval behavior:

```text
READ → auto-allowed
LOCAL_MUTATION → auto-allowed only if reversible and permitted by user settings
DURABLE_MUTATION → pending approval
EXTERNAL_WRITE → pending approval
FINANCIAL → hard approval / likely blocked first
```

Needed states:

```text
pending
approved
denied
auto_allowed
expired
cancelled
```

---

### 5. ToolRegistry Already Includes Mutation-Capable Tools

OpenClaw’s tool registry includes collection tools and executor-backed mutation/control tools.

Examples include:

```text
weather
calendar
news
system
web_search
volume
brightness
media
open_webpage
screen_capture
```

This proves OpenClaw is already moving toward being hands.

But it also means governance must be stronger.

---

### 6. ExecutorSkillAdapter Needs Governance Parity

The `ExecutorSkillAdapter` wraps existing executors as skills and calls the executor directly with a duck-typed request.

This is useful for integration, but it can become dangerous if treated as full governed execution.

Future safe options:

```text
Option A: ExecutorSkillAdapter calls GovernorMediator / governed action dispatch.
Option B: ExecutorSkillAdapter is only called after OpenClawMediator enforces equivalent policy, queue, boundary, and ledger checks.
Option C: Direct executor calls are restricted to tests or read-only/non-risk paths.
```

Preferred option:

> **Executor-backed OpenClaw tools should route through Nova’s governed action path where possible.**

---

### 7. ThinkingLoop Is Real But Must Become Envelope-Aware

OpenClaw’s thinking loop can reason, select tools, extract parameters, execute tools, evaluate results, and synthesize a response.

It is bounded to max steps and uses phase-based cost reduction.

Future alignment requires that before any selected tool runs, Nova/OpenClaw checks:

```text
Is the tool allowed by this envelope?
Is this action READ, LOCAL_MUTATION, DURABLE_MUTATION, or EXTERNAL_WRITE?
Does this Nova role allow it?
Does this action require approval?
Is sensitive data involved?
Will this create a receipt?
Is the budget still available?
```

The thinking loop should not be allowed to select and execute tools solely because they exist in the registry.

---

### 8. Scheduler Is Narrow And Mostly Aligned

The OpenClaw scheduler is currently narrow and bounded.

It checks:

```text
home_agent_enabled
home_agent_scheduler_enabled
due templates
delivery suppression policy
daily run limits
claiming schedule slots
schedule outcome records
ledger events
```

This is good.

Future scheduled worker tasks should preserve this pattern but route through mandatory envelopes and approval rules.

---

## What Must Eventually Change

### A. Add OpenClawMediator

Create a clear central handoff:

```text
GovernorMediator
→ OpenClawMediator
→ EnvelopeFactory
→ EnvelopeStore
→ OpenClaw runner / thinking loop
→ approval queue if needed
→ ledger / receipt
```

The mediator should enforce:

```text
role
risk level
tool permissions
allowed actions
blocked actions
network/file limits
approval requirements
receipt requirements
```

---

### B. Make EnvelopeFactory Mandatory

Transition from:

```text
feature-flagged factory + legacy direct construction
```

to:

```text
all OpenClaw runs require a Nova-issued envelope
```

Do this after tests cover manual, scheduler, bridge, and goal runs.

---

### C. Replace Auto-Approval With Real Approval Queue

The approval endpoint must support:

```text
propose action
store pending action
notify user/dashboard/voice
approve action
deny action
expire action
resume or cancel run
ledger decision
receipt outcome
```

No `EXTERNAL_WRITE` or `DURABLE_MUTATION` should auto-run.

---

### D. Make Tool Execution Envelope-Aware

Before execution:

```text
tool must be in envelope.tools_allowed
network host must be allowed
budget must be available
action type must be permitted
approval state must permit execution
role policy must allow the action
```

---

### E. Split OpenClaw Lanes

Either add separate capability IDs or internal sub-lanes.

Recommended lanes:

```text
Read-only run
Draft-only run
Local reversible control
Durable mutation proposal
External write proposal
Owner-mode repo worker
```

This prevents one broad `openclaw_execute` capability from becoming too powerful.

---

### F. Add Receipts And Non-Action Statements

Every OpenClaw worker run should be able to say:

```text
what was requested
what OpenClaw did
what it touched
what it produced
what it did not do
what is waiting for approval
whether anything was sent/changed/deleted/submitted
```

User-facing examples:

```text
Nothing was sent.
Nothing was posted.
No customer records were changed.
No files were deleted.
Two drafts are waiting for approval.
```

---

## First Proof Workflow

The first alignment proof should be:

```text
Business Follow-Up Brief
```

Flow:

```text
User speaks or types:
"Nova, act as my business assistant. Who do I need to follow up with?"

Nova:
classifies Business Assistant role and read-only/draft-only risk

Gemma:
helps reason, summarize, and draft

OpenClaw:
reads sample/local customer data inside a Nova envelope
finds follow-ups
drafts suggested replies

ElevenLabs:
speaks the result when online

Nova:
shows transcript, drafts, approval queue, and receipt
confirms nothing was sent or changed
```

Success criteria:

```text
useful follow-up result
nothing sent automatically
nothing changed without approval
OpenClaw stayed inside envelope
Gemma did not approve actions
ElevenLabs only spoke/provided voice
Nova logged and governed the whole flow
```

---

## Documentation Rules Going Forward

Current docs should say:

> **OpenClaw currently supports governed home-agent templates and narrow worker foundations.**

Future docs may say:

> **OpenClaw is intended to become Nova’s hands.**

Do not say yet:

```text
OpenClaw is fully autonomous hands.
OpenClaw can safely run any task.
OpenClaw can send/post/delete/submit/change records freely.
OpenClaw full worker execution is complete.
```

---

## Final Recommendation

Do not rewrite OpenClaw from scratch.

The bones are strong.

The needed work is governance alignment:

```text
OpenClawMediator
mandatory EnvelopeFactory
real approval queue
role-aware task envelopes
envelope-aware thinking loop/tool execution
governed executor adapter path
receipts and non-action statements
Business Follow-Up Brief proof
```

Final target:

> **OpenClaw becomes Nova’s bounded hands only after Nova can prove it can direct OpenClaw to do useful work without giving OpenClaw uncontrolled authority.**
