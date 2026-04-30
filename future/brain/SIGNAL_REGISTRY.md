# Signal Registry

Defines approved triggers that future NovaLIS Brain systems may respond to in a controlled way.

This is planning only. It does not enable background execution or new runtime authority.

---

## Core Principle

> NovaLIS should not react to everything. Only approved signals should trigger behavior.

Signals may start awareness, planning, or review. Signals do not automatically grant execution authority.

---

## Signal Types

### User-Requested

Direct user request in chat, voice, or UI.

Default: allowed to create a plan or answer.

### Scheduled

Time-based trigger.

Examples:

- daily script queue check
- weekly learning review
- morning intelligence brief

Default: may check/read/prepare, not execute medium/high-risk actions without approval.

### File / Folder

Approved local folder or queue change.

Examples:

- approved scripts folder changed
- export file added
- project folder updated

Default: read-only unless a governed envelope authorizes more.

### External Data

Approved connector or data update.

Examples:

- market data snapshot
- Shopify report refresh
- RSS/news update

Default: read-only summary or plan.

### Domain-Specific

A signal defined by a domain module.

Examples:

- market thesis warning
- paper-wallet loss limit
- YouTubeLIS script ready
- governed desktop run completed

Default: domain permission profile decides risk.

---

## Signal Definition

```text
Signal
- signal_id
- name
- domain
- source
- trigger_type
- frequency
- allowed_checks
- allowed_actions
- blocked_actions
- required_approval
- risk_level
- max_runtime
- quiet_hours
- rate_limit
- receipt_required
```

---

## Signal Outcomes

A signal may produce:

```text
IGNORE
NOTICE
SUMMARY
PLAN_PREVIEW
TRUST_CARD
REQUIRE_APPROVAL
BLOCKED
```

A signal should not jump directly to execution unless an explicit auto-approval policy allows it.

---

## Frequency Rules

Every recurring signal must define:

- frequency
- maximum run time
- rate limit
- quiet hours behavior
- duplicate suppression
- failure behavior

Signals must avoid infinite loops and recursive triggering.

---

## Approval Rules

Signals may prepare work without approval when read-only.

Signals require approval when they lead to:

- file changes
- browser/desktop action
- account action
- publishing
- purchases
- financial action
- credential handling
- sending messages

---

## Signal Receipt

Every non-trivial signal should produce a receipt or event record:

- signal id
- trigger time
- source
- action taken
- result
- approval state
- stop reason

---

## Safety Rules

Signals must:

- be bounded
- be stoppable
- respect quiet hours
- respect rate limits
- produce receipts
- respect domain permission profiles
- stop on uncertainty

---

## Anti-Patterns

- reacting to all events
- unlimited polling
- recursive triggers
- unbounded automation
- treating a schedule as approval
- treating repeated success as authority

---

## First Safe Signals

Good first signals:

```text
Daily read-only folder check
Weekly learning review reminder
Approved news/topic summary refresh
Paper-wallet weekly report
```

Bad first signals:

```text
Auto-open browser and operate account
Auto-publish content
Auto-trade real money
Auto-send messages
```

---

## Current Status

Planning only.

No runtime claim should say NovaLIS has a generalized Signal Registry until code, tests, and runtime truth support it.
