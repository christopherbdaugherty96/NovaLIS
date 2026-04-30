# Governed Automation Model (YouTubeLIS)

This document defines how YouTubeLIS should use NovaLIS and OpenClaw safely.

The default mode is planning. Execution is optional, future-facing, and must remain governed.

---

## Core Principle

Automation is allowed only inside approved task boundaries.

> Permission is task-scoped, not global.

NovaLIS can help think, structure, draft, validate, and plan. That does not grant permission to publish, upload, purchase, change accounts, delete files, or run background loops.

---

## Planning vs Execution

### Planning Envelope

Planning work can happen without external execution.

Allowed:

- Brainstorming
- Drafting
- Outlining
- Claim labeling
- Scene planning
- Asset planning
- Packaging suggestions

Blocked:

- Uploading
- Publishing
- Account access
- Purchases
- Deletions
- Background loops
- External tool execution

Planning should stop with reviewable artifacts.

### Execution Envelope

Execution starts only when the user approves a specific action scope.

Every execution task must define:

```text
Intent:
Steps:
Allowed:
Blocked:
Environment:
Approval required:
Stop condition:
Failure behavior:
```

---

## Execution Flow

Future execution should follow the NovaLIS governance path:

```text
User
-> NovaLIS
-> Run
-> GovernorMediator
-> CapabilityRegistry
-> ExecuteBoundary
-> OpenClaw or executor
-> Result
-> Ledger
```

OpenClaw should never operate outside this path.

If the integration is not verified in runtime code, this document should be treated as a target model, not a shipped capability claim.

---

## Example Execution Envelope

```text
Intent: Generate voiceover

Steps:
- Open approved voice provider
- Paste approved script
- Generate audio
- Download file

Allowed:
- Browser navigation inside approved provider
- Audio generation from approved script
- File download

Blocked:
- Purchases
- Account changes
- Script changes without review
- Unrelated browsing
- Uploading or publishing

Stop condition:
- Audio file downloaded, then stop.

Failure behavior:
- Pause and ask if login, payment, missing credits, provider error, or scope change occurs.
```

---

## Rules

- No execution without declared intent
- No actions outside approved scope
- No permission inheritance from memory or prior runs
- Stop immediately when the task is complete
- Pause and request approval if scope changes
- Log execution steps when execution exists
- Publishing remains manual unless a future governed publishing path is explicitly implemented and approved

---

## Risk Levels

Low:

- Planning-only work
- Opening local apps
- Reading approved data

Medium:

- Downloading files
- Creating files
- Uploading drafts
- Generating paid-tool outputs without purchase

High:

- Purchases
- Deletions
- Account changes
- Publishing
- Public representation of claims as factual
- Monetization changes

High-risk actions always require explicit approval.

---

## Current Status

This repository is currently documentation and workflow design.

Treat the following as current safe baseline:

```text
Planning: allowed as a design model
Execution: not implemented in this repo
OpenClaw integration: future / target model
Publishing: manual only
Background loops: not allowed
```

Do not claim YouTubeLIS can execute governed browser or desktop actions until that path exists and is verified against NovaLIS runtime truth.

---

## Goal

Provide maximum useful capability while preserving control, visibility, and trust.
