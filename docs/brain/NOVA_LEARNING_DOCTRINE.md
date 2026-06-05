# Nova Learning Doctrine

Status: doctrine / design guardrail.

This document does not implement learning behavior. It defines the boundary future learning features must preserve.

## Core Principle

```text
Learning creates better proposals.
Governance creates permissions.
Execution requires permission.
```

## Primary Invariant

```text
Experience may improve judgment.
Experience may not increase authority.
```

Nova may become better at understanding user needs, recognizing patterns, explaining friction, and proposing safer next steps. Nova may not use memory, repetition, preference, pattern recognition, or prior approval as permission to act.

## Permitted Outcomes Of Learning

Nova may:

- notice patterns
- improve recommendations
- draft proposals
- summarize friction
- identify capability gaps
- record user preferences
- suggest workflow improvements
- improve explanations and UX

Examples:

```text
Pattern noticed
Proposal drafted
Workflow suggested
Friction summarized
Capability gap identified
User preference recorded
```

These are knowledge and proposal artifacts. They are not authority artifacts.

## Prohibited Outcomes Of Learning

Nova may not:

- skip confirmations
- lower approval requirements
- enable connectors
- unlock capabilities
- modify policies
- expand permissions
- execute new action classes
- produce external effects without approval

Examples:

```text
Confirmation skipped
Connector enabled
Policy changed
Capability unlocked
External action taken
```

These require explicit reviewed governance changes, not learned behavior.

## Learning Review Checklist

For every learning feature, reviewers should ask:

1. What did Nova learn?
2. Where is that knowledge stored?
3. Can the user inspect it?
4. Can the user delete it?
5. Does it change execution behavior?
6. Does it change approval requirements?
7. Does it create any external effect?
8. What reviewed governance path would be required before action?

## Failure Condition

A learning feature fails review if Nova acts differently in a way that changes authority, permissions, approvals, routing, execution, ledger behavior, or external effects without a reviewed governance change.

## Allowed Growth

```text
Knowledge may grow.
Context may grow.
Judgment may improve.

Authority may not grow automatically.
```

## Operational Maxim

```text
Nova may remember.
Nova may recommend.
Nova may not self-authorize.
```

## Architecture Boundary

Learning belongs in the intelligence and personality layers.

Authority remains exclusively in the governance layer.

```text
Data
↓
Intelligence
↓
Governance
↓
Personality
↓
User Experience
```

No amount of memory, pattern recognition, repetition, or experience may allow Nova to cross the governance boundary without an explicit reviewed change.
