# Continuous Nova Model

This document explains how a future continuous NovaLIS should work without violating NovaLIS governance.

Continuous Nova does not mean uncontrolled autonomy. It means NovaLIS can remain active, watch approved signals, prepare work, notice conditions, and request permission when execution is needed.

This is an implementation planning document, not current runtime truth.

---

## Core Distinction

Continuous awareness is not the same as continuous authority.

NovaLIS may eventually be continuous in these ways:

- staying awake locally
- checking approved queues
- monitoring approved schedules
- noticing approved events
- preparing drafts and plans
- reminding the user
- proposing governed run envelopes
- resuming approved workflows

NovaLIS should not become continuous in these ways without explicit policy:

- unrestricted desktop control
- hidden background execution
- silent purchasing
- silent publishing
- silent messaging
- uncontrolled browser/app traversal
- indefinite execution after task completion

---

## Governing Rule

> Continuous Nova may observe approved signals continuously, but execution authority remains task-scoped, envelope-bound, interruptible, and revocable.

---

## Continuous Layers

### 1. Continuous Presence

NovaLIS can stay available as a local assistant process.

This does not grant execution authority by itself.

### 2. Continuous Sensing / Checking

NovaLIS may check approved local or connector signals, such as:

- approved folders
- approved queues
- approved calendar windows
- approved RSS/news feeds
- approved Shopify read-only reports
- approved script queues

This layer should be read-only unless a governed run is approved.

### 3. Continuous Planning

NovaLIS may prepare:

- summaries
- suggested next steps
- draft envelopes
- workflow readiness reports
- reminders

Planning is not execution.

### 4. Governed Execution

Any real-world action must still pass through a governed run envelope.

Examples:

- open app
- operate browser
- download file
- upload file
- generate media
- edit files
- send message
- publish content
- purchase

Execution must be scoped, approved when required, logged, and stopped on completion.

---

## Scheduled Runs

Scheduled triggers are allowed only as triggers.

A schedule may:

- check a queue
- prepare a plan
- generate a Trust Review Card
- notify the user
- request approval

A schedule should not automatically execute medium/high-risk actions unless a separate trusted automation policy exists.

Important rule:

> Scheduled trigger does not equal execution approval.

---

## Example: Daily ElevenLabs Script Queue

A safe continuous workflow:

```text
9:00 AM
→ Check approved script folder
→ Find 3 scripts
→ Build voiceover run envelope
→ Show Trust Review Card
→ Wait for approval
→ If approved, process approved scripts only
→ Save audio to approved folder
→ Produce receipt
→ Stop
```

Unsafe version:

```text
9:00 AM
→ Open browser silently
→ Use ElevenLabs account
→ Spend credits if needed
→ Continue until it thinks it is done
```

The unsafe version violates NovaLIS governance.

---

## Trusted Automation Ladder

Continuous Nova should earn autonomy gradually.

### Level 0 — Manual Only

User starts every run.

### Level 1 — Scheduled Check

NovaLIS checks approved queues and reports readiness.

### Level 2 — Scheduled Plan

NovaLIS prepares a governed run envelope and asks for approval.

### Level 3 — Approved Scheduled Execution

NovaLIS executes only after user approves the envelope.

### Level 4 — Limited Auto-Approval

NovaLIS may auto-run low-risk or previously trusted workflows under strict limits.

Example limits:

- approved folder only
- approved domain only
- max item count
- max runtime
- no purchases
- no publishing
- no credential entry
- stop after completion

### Level 5 — Conditional Autonomous Execution

Only for narrow, tested, low-risk workflows with explicit user policy.

This should not be the default.

---

## Continuous Safety Rules

1. Continuous presence does not grant authority.
2. Continuous checks should be read-only by default.
3. Execution requires a task envelope.
4. Medium/high-risk execution requires approval.
5. Public output requires final human approval.
6. Purchases require final human approval.
7. Credential entry is user-only by default.
8. Stop conditions must be explicit.
9. The user can pause, stop, or revoke.
10. Every run produces a receipt.

---

## Required Architecture Support

Continuous Nova requires:

- scheduler trigger model
- approved signal registry
- queue/readiness checker
- governed run envelope builder
- policy evaluator
- trust review card
- run state machine
- pause/stop/revoke controls
- ledger receipt output
- quiet hours / rate limits
- failure and retry policy

---

## Relationship To Current Runtime

The current runtime already has some scheduler and home-agent surfaces, but broader envelope-governed execution remains a stated gap.

This document should guide the next implementation path without claiming the capability already exists.

---

## Implementation Direction

First build continuous Nova as:

> continuous read-only noticing + scheduled envelope preparation

Not as:

> continuous unrestricted execution

The first useful version should be boring:

```text
Check approved folder once daily → prepare envelope → ask for approval → stop.
```

Then build toward limited auto-approval only after repeated successful receipts and tests.
