# Nova Request Understanding Contract

Date: 2026-04-27

Status: Implemented foundation / non-authorizing conversation architecture

Purpose: define the missing user-facing loop between what Nova understands, what Nova can do, what Nova cannot do yet, what Nova may safely propose, and what must remain governed.

---

## Core Loop

Nova should make the following loop explicit:

```text
User asks
→ Nova understands the goal
→ Nova classifies the request type
→ Nova identifies current capability state
→ Nova states the safe next step
→ Nova states what it must not do
→ governed action path handles any real execution
→ trust/action history shows what happened or did not happen
```

Short version:

> **I understand what you want. Here is what I can do. Here is what I cannot do. Here is the safe next step.**

This contract improves coherence without granting authority.

---

## Current Implementation

Implemented foundation:

```text
nova_backend/src/conversation/request_understanding.py
nova_backend/tests/conversation/test_request_understanding.py
```

The module exposes:

```text
CapabilityStatus
UnderstandingConfidence
RequestUnderstanding
build_request_understanding(...)
```

This is conversation-layer architecture only. It does not execute actions.

---

## Contract Fields

`RequestUnderstanding` includes:

```text
understood_goal
request_type
capability_status
confidence
needs_clarification
safe_next_step
must_not_do
notes
authority_effect
```

Required invariant:

```text
authority_effect = "none"
```

This makes the object impossible to treat as a governor approval without violating the contract.

---

## Capability Status Values

```text
CAN_DO_NOW
CAN_DRAFT_ONLY
CAN_HELP_MANUALLY
CAN_EXPLAIN
CAN_SUMMARIZE_IF_PROVIDED
REQUIRES_CONNECTOR
REQUIRES_APPROVAL
PLANNED_NOT_BUILT
PAUSED
BLOCKED
NOT_ALLOWED
NEEDS_CLARIFICATION
UNKNOWN
```

These are explanatory states, not execution permissions.

---

## Current Covered Request Types

Initial deterministic coverage includes:

```text
blocked_request
clarification_needed
paused_work_reference
email_draft_boundary
background_reasoning_boundary
memory_or_learning_request
doc_or_repo_update
project_status_or_next_step
explanation
general
```

Examples:

```text
"draft an email" → email_draft_boundary / CAN_DRAFT_ONLY
"continue Shopify" → paused_work_reference / PAUSED
"save this to memory" → memory_or_learning_request / REQUIRES_APPROVAL
"add this to docs" → doc_or_repo_update / CAN_HELP_MANUALLY
"what should Claude do next" → project_status_or_next_step / CAN_EXPLAIN
"think in the background" → background_reasoning_boundary / PLANNED_NOT_BUILT
```

---

## Boundaries

The request understanding contract may:

```text
shape conversation
choose clearer wording
explain can/cannot/not-yet/paused states
preserve paused-work awareness
support future UI review cards
feed trust/action-history summaries
```

It must not:

```text
approve an action
execute a capability
lock or sign off a capability
resume paused work
call OpenClaw
call Google/Shopify/ElevenLabs connectors
change GovernorMediator
change ExecuteBoundary
change NetworkMediator
change confirmation requirements
```

---

## Relationship To Existing Router

The existing `ConversationRouter` remains the deterministic routing surface for broad conversation mode and clarification handling.

The request understanding contract sits beside it:

```text
ConversationRouter.route(...)
→ ConversationDecision
→ build_request_understanding(...)
→ RequestUnderstanding
→ response wording / UI review card
```

This avoids rewriting the router or changing governed action paths.

---

## Relationship To Trust / Action History

Future trust/action-history UI should be able to display request understanding fields before and after governed operations.

Example card:

```text
Understood goal: prepare an email reply
Capability state: draft-only
Safe next step: create a draft for review
Must not do: send automatically
Result: draft created / not sent
```

This creates the missing visible trust loop.

---

## Relationship To Cap 64

Cap 64 remains the model proof:

> **Nova drafts. User sends.**

The request understanding contract identifies email requests as:

```text
request_type = email_draft_boundary
capability_status = CAN_DRAFT_ONLY
must_not_do = send email automatically
```

This keeps the user-facing explanation aligned with the governed implementation.

---

## Relationship To Paused Work

The contract currently recognizes paused scopes:

```text
Auralis / website merger work
Shopify / Cap 65 P5 live work
```

It returns:

```text
request_type = paused_work_reference
capability_status = PAUSED
```

This prevents general next-step advice from drifting back into paused work.

---

## Relationship To Background Reasoning

The contract distinguishes background reasoning from background automation.

```text
background reasoning → planned / can explain / propose only
background automation → requires approval and governed path
```

It must not start background reasoning jobs by itself. That belongs to the future background reasoning implementation.

---

## Relationship To Governed Learning

The contract distinguishes:

```text
"save this to memory" → memory_or_learning_request
"add this to docs" → doc_or_repo_update
```

It does not persist memories by itself. Governed learning persistence belongs to the future governed learning implementation.

---

## Tests

Current tests assert that the contract:

```text
uses Cap 64 draft-only boundary for email requests
keeps Shopify paused
keeps Auralis paused
separates memory-save from GitHub docs updates
returns project-status / next-step shape
blocks background automation
preserves policy-blocked requests
preserves clarification prompts from the router
remains authority_effect = none
```

---

## Next Integration Step

Do not wire this into execution yet.

Best next integration after Cap 64/trust work:

```text
Use RequestUnderstanding in the general-chat response path to add clearer boundary language for status, paused work, email draft, memory/doc, and background reasoning requests.
```

Possible later UI integration:

```text
show RequestUnderstanding cards in Trust / Action History
show must_not_do statements before approvals
show capability_status in review cards
```

---

## Final Rule

> **Understanding is not permission.**

Nova should understand the user better while keeping all real authority inside the governed execution spine.
