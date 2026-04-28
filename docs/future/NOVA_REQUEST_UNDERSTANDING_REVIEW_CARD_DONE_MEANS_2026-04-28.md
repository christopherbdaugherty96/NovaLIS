# Nova RequestUnderstanding Review Card — Done-Means Spec

Date: 2026-04-28

Status: Execution-control spec / future implementation guide / not runtime truth until implemented

Purpose: define exactly what counts as done for the current active task: building the minimal RequestUnderstanding trust/action-history review card.

---

## Active Priority

Current active task:

```text
Build the minimal RequestUnderstanding trust/action-history review card.
```

This card must make Nova's understanding visible without giving it authority.

Core rule:

> **Understanding is not permission.**

---

## Done Means

The task is done only when Nova can show a user-facing or trust/action-history card containing the latest RequestUnderstanding result for relevant conversations.

Required fields:

```text
understood_goal
request_type
capability_status
confidence
safe_next_step
must_not_do
authority_effect
result_status: not_executed / blocked / routed / draft_only / informational
non_action_statement when relevant
```

Required behavior:

```text
The card is visible in a trust/action-history surface.
The card does not execute capabilities.
The card does not approve actions.
The card does not change capability locks.
The card does not call OpenClaw.
The card does not call Google, Shopify, ElevenLabs, MCP, or other connectors.
The card does not persist governed memory.
The card does not resume paused work.
```

---

## Minimum UI / Surface Requirement

Acceptable first surface:

```text
Trust/action-history panel, recent action card, debug trust surface, or equivalent local dashboard card.
```

Not required for first pass:

```text
full polished UI
approval queue
connector registry
OpenClaw integration
new memory system
background reasoning
```

---

## Example Card States

### General Question

```text
Nova understood: User is asking a general/explanatory question.
Capability status: no action needed.
Safe next step: answer normally.
Must not do: execute capabilities or claim an action was taken.
Authority effect: none.
```

### Email / Draft Request

```text
Nova understood: User wants help preparing an email/message.
Capability status: draft-only pattern; email live signoff is paused.
Safe next step: explain draft-only boundary or prepare text for review where allowed.
Must not do: send email automatically or claim a sent email.
Authority effect: none.
```

### Paused Work Continuation

```text
Nova understood: User may be asking to continue paused Shopify/Auralis/Cap 64 work.
Capability status: paused by owner direction.
Safe next step: summarize paused status or ask for explicit unpause.
Must not do: resume paused implementation or credential/signoff work.
Authority effect: none.
```

### Capability / Local Action Request

```text
Nova understood: User requested a local capability action.
Capability status: requires governed capability route and possibly confirmation.
Safe next step: route through governed execution path if allowed.
Must not do: bypass GovernorMediator / ExecuteBoundary.
Authority effect: none from understanding card itself.
```

---

## Tests Required

At minimum add tests proving:

```text
review card data can be produced from RequestUnderstanding
all required fields exist
card has authority_effect = none
email/draft request shows draft-only / no-send boundary
paused Shopify/Auralis/Cap64 wording remains paused
card creation does not invoke capabilities
card creation does not call OpenClaw/connectors
card creation does not persist memory
```

Regression tests should cover:

```text
"draft an email to..."
"continue Shopify"
"second pass review"
"what should I work on next?"
"save this to memory and add it to docs"
```

---

## Live Verification Steps

After implementation:

```text
1. Start Nova locally.
2. Ask a general question and verify the card shows informational/no-action status.
3. Ask an email/draft question and verify no-send boundary is visible.
4. Ask "continue Shopify" and verify paused status is visible.
5. Ask "what should I work on next?" and verify current active priority is respected.
6. Confirm no capability was executed unless separately routed and approved.
7. Confirm no paused work resumed.
```

---

## What Not To Touch

Do not use this task to modify:

```text
GovernorMediator authority
ExecuteBoundary authority
NetworkMediator authority
Capability locks
OpenClaw execution
Google connectors
ElevenLabs provider
Shopify / Cap 65
Cap 64 P5/P6
Auralis / website merger
background reasoning jobs
governed learning persistence
```

---

## Final Rule

> **The review card explains Nova's understanding. It does not authorize action.**
