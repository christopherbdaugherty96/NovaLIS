# Auralis Interface Plan

Status: planning document

Date: 2026-04-30

## Relationship to Nova

Auralis is not a separate intelligence or execution system.

Auralis is the interface layer for Nova.

Nova remains:
- the governed execution engine
- the source of truth for actions
- the owner of jobs, decisions, approvals, and execution

Auralis only:
- renders Nova jobs
- presents decisions and proposed actions
- captures user approval or rejection
- shows results and history

## Core principle

Auralis must never bypass Nova governance.

All actions:
- originate as Nova jobs
- pass through Nova approval contracts
- execute through GovernorMediator, CapabilityRegistry, ExecuteBoundary, and Ledger

## What Auralis shows

### 1. Active jobs

- job id
- job type
- current status
- summary

### 2. Pending approvals

Primary surface for v1.

Card example:

```text
Website Lead Detected

Business: Mobile bar
Scope: 5 pages + booking

Recommended package:
Standard Website

Estimated price:
Starting at $1,000+; final quote depends on scope.

Proposed action:
Draft proposal email

Capability:
send_email_draft

Requires approval:
Yes

[Approve] [Edit] [Reject]
```

### 3. Job detail view

- raw input
- parsed input
- decision
- alternatives
- risks
- proposed action
- approval history
- execution steps
- result

### 4. Completed jobs

- summary
- outcome
- timestamps

### 5. Follow-up queue

- jobs scheduled for follow-up
- next action preview

## What Auralis does not do

- does not execute actions directly
- does not decide authority
- does not bypass approval
- does not replace Nova conversation/cognition

## Minimal v1 surface

Auralis v1 only needs:

- list of jobs
- approval card view
- basic job detail

No complex UI required.

## Integration points

Auralis should read from Nova:

- job store
- approval requests
- job status

Auralis should send to Nova:

- approval decisions
- optional modifications to proposed actions

Auralis must not construct executable payloads directly. Nova owns proposal creation, proposal versioning, payload snapshots, and execution routing.

## Data flow

```text
Nova creates job
  -> Nova analyzes and proposes action
  -> Nova creates ApprovalRequest
  -> Auralis renders approval card
  -> User approves or rejects
  -> Auralis sends decision back to Nova
  -> Nova executes through governed path
  -> Nova updates job + ledger
  -> Auralis reflects updated state
```

## First supported workflow

Auralis v1 should only support:

Website Lead -> Proposal -> Email Draft

All UI elements should be optimized for this single flow.

## Expansion after v1

Once Nova jobs are stable:

- add Shopify workflow surfaces
- add service business workflows
- add real estate workflows

All reuse the same job + approval + execution model.

## Final directive

Auralis must remain thin.

Nova owns:
- logic
- decisions
- execution
- truth

Auralis only exposes and controls Nova's structured jobs.