# Nova Coherence, Memory, And Background Reasoning Alignment Map

Date: 2026-04-27

Status: Architecture alignment map / future implementation guide

Purpose: explain how Nova's request understanding, conversation coherence, governed learning/memory, and background reasoning plans fit together without contradicting Nova's execution-governance model.

This is not current runtime truth. Exact runtime truth remains in `docs/current_runtime/` and live code.

---

## Core Alignment

The four related tracks are separate on purpose:

```text
Request Understanding = understand the user's goal and boundary.
Conversation Coherence = choose the right answer shape and context.
Governed Learning / Memory = remember confirmed preferences and corrections visibly.
Background Reasoning = think, draft, summarize, and propose without acting.
```

They all share the same rule:

> **Intelligence may improve. Authority must stay governed.**

---

## The Unified User-Facing Loop

Nova should eventually make this loop visible:

```text
User asks
→ Nova understands the goal
→ Nova classifies current ability: can do / draft-only / manual help / planned / paused / blocked / not allowed
→ Nova chooses the right response style and context
→ Nova may remember user-confirmed preferences or corrections
→ Nova may reason in the background only when allowed
→ Nova proposes a draft, answer, review card, or next step
→ User approves any real action
→ Governed execution path handles the action
→ Trust/action history records what happened and what did not happen
```

Short product expression:

> **Nova understands first, explains the boundary, proposes safely, waits for approval, then logs what happened.**

---

## Layer Responsibilities

### 1. Request Understanding Contract

Reference:

```text
docs/future/NOVA_REQUEST_UNDERSTANDING_CONTRACT.md
nova_backend/src/conversation/request_understanding.py
nova_backend/tests/conversation/test_request_understanding.py
```

Responsibility:

```text
understood_goal
request_type
capability_status
confidence
needs_clarification
safe_next_step
must_not_do
authority_effect = none
```

What it can do:

```text
explain what Nova understood
identify paused work
separate memory vs docs requests
identify draft-only email boundary
identify background reasoning vs automation boundary
preserve policy-blocked and clarification-needed states
```

What it must not do:

```text
execute actions
approve actions
lock/sign off capabilities
persist memory
start background jobs
call connectors
change governance
```

---

### 2. Conversation Coherence Layer

Reference:

```text
docs/future/NOVA_CONVERSATION_COHERENCE_LAYER_PLAN.md
```

Responsibility:

```text
choose answer shape
load relevant context
respect active/paused/future-only state
avoid overstating future plans
handle project-status and next-step questions consistently
ask clarification only when needed
```

What it can do:

```text
route status questions to current-truth/gap/next-action format
route Claude/Codex questions to best-ROI format
route paused-work questions to pause-preserve-unpause format
route capability signoff questions to evidence/blocker format
```

What it must not do:

```text
replace the conversation router wholesale
execute governed actions
persist learning/memory by itself
start background reasoning jobs by itself
```

---

### 3. Governed Learning / Memory

Reference:

```text
docs/future/NOVA_GOVERNED_LEARNING_PLAN.md
```

Responsibility:

```text
remember explicit user preferences
remember corrections
remember command meanings
remember project glossary terms
remember accepted answer patterns
allow review/delete/supersede
```

Learning can affect:

```text
wording
format
context selection
intent classification
clarification behavior
project glossary recognition
answer structure
```

Learning must not affect:

```text
action approval
capability signoff
capability locks
GovernorMediator
ExecuteBoundary
NetworkMediator
OpenClaw authority
connector authority
```

Required invariant:

```text
authority_effect = none
```

---

### 4. Background Reasoning

Reference:

```text
docs/future/NOVA_BACKGROUND_REASONING_NOT_AUTOMATION_PLAN.md
```

Responsibility:

```text
think in the background
summarize
analyze
prepare drafts
prepare recommendations
prepare proposed actions
show review cards
```

Background reasoning may produce:

```text
summary
draft
recommendation
status card
proposed action
question for the user
```

Background reasoning must not produce direct external-world change:

```text
no sending
no posting
no deleting
no booking
no purchasing
no file/account/customer changes
no silent OpenClaw execution
```

Every future background reasoning job should include:

```text
job_type
provider_lane
allowed_outputs
blocked_outputs
budget
expiration
staleness policy
cancel/stop path
receipt/non-action statement
```

---

## Correct Ordering

The recommended build order is:

```text
1. Cap 64 P5 live signoff and lock
2. Trust/action-history dashboard proof
3. Request Understanding integration into general-chat wording/review cards
4. Conversation Coherence Layer
5. Governed Learning / Memory review surface
6. Background Reasoning review cards
7. OpenClawMediator / Business Follow-Up Brief
8. Model/provider upgrades
```

Why:

```text
Cap 64 proves draft-only action boundaries.
Trust/action-history proves the user can review what happened.
Request Understanding explains can/cannot/must-not-do states.
Coherence makes Nova answer consistently.
Learning makes Nova adapt visibly.
Background reasoning makes Nova more proactive in thought.
OpenClaw comes after the review/approval loop is proven.
```

---

## What Is Implemented Now

Implemented foundation:

```text
RequestUnderstanding contract module
targeted RequestUnderstanding tests
architecture doc for request understanding
```

Not yet implemented:

```text
live response wiring for RequestUnderstanding
trust/action-history cards for RequestUnderstanding
governed learning persistence/review UI
background reasoning jobs
background reasoning review cards
OpenClawMediator hands-layer execution
```

---

## The Required Trust Surface

All four tracks eventually need the same review surface.

Trust/action-history should be able to show:

```text
what Nova understood
what Nova can do
what Nova cannot do
what Nova must not do
what Nova proposed
what the user approved or rejected
what Nova actually did
what Nova did not do
whether output is fresh/stale/expired
whether local or cloud reasoning was used
```

Without this surface, background reasoning and learning risk feeling hidden.

---

## Key Non-Contradiction Rules

### Understanding vs Permission

```text
RequestUnderstanding may say "can_draft_only".
It must not create or send the draft by itself.
```

### Coherence vs Execution

```text
Conversation coherence may choose a safer response template.
It must not execute a capability.
```

### Learning vs Authority

```text
Governed learning may remember that the user prefers "second pass" to mean gap review.
It must not learn that approvals are no longer required.
```

### Background Reasoning vs Automation

```text
Background reasoning may prepare a proposed OpenClaw envelope.
It must not execute OpenClaw silently.
```

### Local-First vs Local-Only

```text
Local-first means local trust anchor and user control.
It does not ban optional governed cloud reasoning.
Cloud reasoning may expand intelligence, not authority.
```

---

## First Good Future Proof

The cleanest next proof after Cap 64/trust is:

```text
Request Understanding Review Card
```

Example:

```text
Understood goal: draft a follow-up email
Capability state: draft-only
Safe next step: prepare draft for review
Must not do: send automatically
Result: draft prepared / not sent
```

This proves the whole product philosophy in a way a normal user can understand.

---

## Final Alignment Statement

These plans align if Nova keeps this rule:

> **Nova can become better at understanding, remembering, and reasoning before it becomes broader at acting.**

The future product should feel more capable because Nova explains and proposes better, not because it quietly gains hidden authority.
