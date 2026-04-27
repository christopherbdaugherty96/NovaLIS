# Nova Governed Learning Plan

Date: 2026-04-27

Status: Future architecture direction / owner preference

Purpose: define how Nova should learn from user corrections, preferences, repeated project context, and accepted patterns without becoming hidden automation or silently changing authority.

This is a planning document, not current runtime truth. Exact runtime truth remains in `docs/current_runtime/` and live code.

---

## Core Decision

Nova should learn, but only in a governed, visible, reviewable way.

Short version:

> **Nova may learn preferences, corrections, and patterns. Nova must not silently learn new authority.**

This means Nova can become more coherent over time without becoming an uncontrolled autonomous agent.

---

## What Learning Means

Allowed learning:

```text
remembering user corrections
remembering preferred wording
remembering command meanings
remembering recurring project context
remembering paused/active decisions
remembering accepted answer formats
remembering rejected behaviors
remembering project glossary terms
improving future classification from user-confirmed rules
```

Not allowed learning:

```text
changing model weights from private data
hidden background self-training
silent policy changes
silent action permission changes
new connector authority
new file/network/action capability
bypassing approval because a pattern was learned
resuming paused work automatically
```

---

## Learning Is Not Authority

Learning may influence:

```text
wording
format
context selection
intent classification
clarification behavior
project glossary recognition
answer structure
```

Learning must not influence:

```text
action approval
capability signoff
capability lock state
GovernorMediator rules
ExecuteBoundary behavior
NetworkMediator permissions
OpenClaw execution authority
Google/Shopify/ElevenLabs connector authority
```

Rule:

> **Learning can make Nova understand better. It cannot make Nova act without governance.**

---

## Learnable Item Types

Use explicit categories instead of one vague memory bucket.

```text
USER_STYLE_PREFERENCE
PROJECT_GLOSSARY
COMMAND_MEANING
ACTIVE_TASK_STATE
PAUSED_SCOPE
CORRECTION
REJECTED_BEHAVIOR
ACCEPTED_RESPONSE_PATTERN
CAPABILITY_STATUS_HINT
CONTEXT_DISAMBIGUATION_RULE
```

Examples:

```text
USER_STYLE_PREFERENCE: user prefers brutally honest repo-grounded answers.
PROJECT_GLOSSARY: Cap 64 = send_email_draft.
COMMAND_MEANING: “second pass” means re-check for gaps/errors/missed risks.
PAUSED_SCOPE: Auralis merger is paused.
CORRECTION: “save to memory” does not mean create a GitHub file.
REJECTED_BEHAVIOR: do not call Nova “Jarvis”.
ACCEPTED_RESPONSE_PATTERN: use current truth / gap / next action for Nova status.
```

---

## Learning States

Every learned item should have a state.

```text
PROPOSED
USER_CONFIRMED
ACTIVE
SUPERSEDED
EXPIRED
REJECTED
```

Default rule:

> Durable learning should require explicit user confirmation or a clearly explicit user instruction.

Examples of explicit learning instructions:

```text
Remember this.
Save this.
Use this going forward.
Do not do that again.
From now on, when I say X, I mean Y.
```

---

## Visibility Requirements

Nova should be able to show the user:

```text
what it learned
when it learned it
why it applies
what scope it applies to
whether it affects conversation only or action flow
how to edit/delete it
what it does not authorize
```

At minimum, a learned item should include:

```text
id
type
summary
scope
authority_effect
state
created_at
updated_at
source
```

Required invariant:

```text
authority_effect = none
```

for all conversation/coherence learning.

---

## Learning From Corrections

Corrections should be first-class.

Example correction:

```text
User: Why are you creating files in GitHub? I wanted ChatGPT memory.
```

Nova should learn:

```json
{
  "type": "CORRECTION",
  "summary": "When the user says save to memory, do not create GitHub files unless they explicitly say add to docs, repo, or commit.",
  "scope": "conversation_behavior",
  "authority_effect": "none",
  "state": "USER_CONFIRMED"
}
```

Future behavior:

```text
“Save to memory” → memory/work-context response, not GitHub write.
“Add to docs” → repo/doc write may be appropriate.
```

---

## Learning From Repeated Patterns

Nova may propose learning from repeated patterns, but should not silently make durable rules from weak evidence.

Example:

```text
I notice you often ask for a second pass after repo changes. Should I treat “second pass” as a request to check for missed gaps, broken links, overstated docs, and next-step alignment?
```

If the user says yes, save it as a `COMMAND_MEANING` item.

This prevents overfitting while still allowing Nova to improve.

---

## Learning And Safety Examples

Bad learned rule:

```text
User usually approves email drafts, so send automatically.
```

Allowed learned rule:

```text
User prefers email draft summaries to include recipient, subject, body preview, and a “not sent” statement.
```

Bad learned rule:

```text
User often asks for Shopify reports, so run them automatically in the background.
```

Allowed learned rule:

```text
When discussing Shopify, mention Cap 65 is paused unless owner explicitly unpauses it.
```

Bad learned rule:

```text
User often asks OpenClaw to work on code, so let OpenClaw run without approval.
```

Allowed learned rule:

```text
When preparing OpenClaw work, include branch creation, bounded scope, tests, and review/approval instructions.
```

---

## Relationship To Background Reasoning

Background reasoning can support governed learning, but not hidden self-training.

Allowed background learning support:

```text
notice repeated corrections
prepare suggested memory items
summarize recurring preferences
ask user whether to save a pattern
review past user-confirmed rules before answering
```

Not allowed:

```text
silently train model weights
silently create memories from sensitive data
silently change policies
silently grant tool permissions
silently decide actions no longer need approval
```

---

## Relationship To Conversation Coherence

Governed learning should feed the Conversation Coherence Layer.

Examples:

```text
User correction improves future intent classification.
Command meaning improves response routing.
Project glossary improves status answers.
Paused scope prevents bad next-step recommendations.
Accepted response pattern improves formatting.
```

But learning must remain subordinate to runtime truth.

Rule:

> **Learned memory can help Nova find the right answer shape. It cannot override live repo/runtime truth.**

---

## First Proof

The first proof should be low-risk:

```text
Memory-vs-doc correction proof
```

Flow:

```text
User says: “Save to memory.”
Nova recognizes MEMORY_SAVE_REQUEST.
Nova does not create a GitHub file.
Nova records or proposes a visible conversation preference.
Nova says what it understood and what it did not do.
```

Success criteria:

```text
no repo write occurs
preference/correction is visible
user can review/delete it
future “save to memory” requests do not trigger GitHub writes
no action authority changes
```

---

## Test Cases To Require

```text
“Remember that I do not want Jarvis used” → learning/preference path
“No, I meant memory, not GitHub” → correction path
“Use this format going forward” → accepted response pattern path
“From now on, second pass means review for gaps” → command meaning path
“Forget that rule” → learned item can be rejected/superseded
```

Negative tests:

```text
Learning must not mark Cap 64 P5 passed.
Learning must not mark Cap 65 P5 passed.
Learning must not change capability locks.
Learning must not issue OpenClaw envelopes.
Learning must not call Google/Shopify/ElevenLabs connectors.
Learning must not change action approval policy.
Learning must not persist sensitive data without explicit user intent.
```

---

## Done Means

Governed learning is done only when Nova can:

```text
recognize explicit learning/correction requests
store or propose learned items visibly
label scope and authority_effect
apply learned conversation preferences later
allow review/delete/supersede
prove learning does not change action authority
```

---

## Final Rule

> **Nova should learn how to understand the user better, not how to bypass the user.**
