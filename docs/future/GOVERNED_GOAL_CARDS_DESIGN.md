# Governed Goal Cards Design

Status: future / product design; not implemented runtime truth
Date: 2026-05-21
Scope: Permission-based goal planning, visible task state, and bounded governed execution design for Nova

Generated runtime truth, code, tests, and proof artifacts win if they conflict with this note.

---

## Purpose

Governed Goal Cards define how Nova can help users work toward goals without becoming a hidden autonomous agent.

A Goal Card is a visible state surface that shows what Nova is planning, what Nova is doing now, what Nova has already done, what needs approval, what is blocked, and what receipt proves the result.

Goal Cards are meant to make governed workflows understandable to normal users while preserving Nova's execution boundaries.

---

## Non-Goals

This design does not authorize runtime autonomy, hidden background execution, infinite agent loops, browser/computer-use expansion, Shopify writes, automatic email sending, purchases, publishing, account changes, new capabilities, or capability lock changes.

This document is planning only.

---

## Governance Invariants

Planning is not authority.

Goal state is not permission.

The planner never executes directly.

Connectors do not authorize action by themselves.

All real actions pass through GovernorMediator.

All capability execution remains bounded by CapabilityRegistry.

Required confirmations remain required.

External writes require explicit confirmation.

Ledger receipts remain the source of execution truth.

The user can pause or cancel a goal.

Goal Cards may organize work, but they do not bypass the existing governor spine.

---

## GoalCard Object

Example shape:

```json
{
  "goal_id": "goal_auralis_launch_001",
  "title": "Prepare Auralis Shopify launch",
  "status": "planning",
  "created_by": "user",
  "permission_envelope_id": "perm_001",
  "steps": [],
  "current_step_id": null,
  "ledger_refs": [],
  "created_at": "2026-05-21T12:00:00Z",
  "updated_at": "2026-05-21T12:00:00Z"
}
```

Allowed statuses:

```text
draft
planning
waiting_for_approval
ready
running
paused
blocked
completed
failed
canceled
```

---

## PermissionEnvelope Object

The permission envelope defines what the goal is allowed to propose or execute.

Example shape:

```json
{
  "permission_envelope_id": "perm_001",
  "allowed_capabilities": [16, 22, 64, 65],
  "blocked_capabilities": [
    "browser_control",
    "shopify_write",
    "purchase",
    "publish",
    "customer_message"
  ],
  "requires_confirmation": [22, 64],
  "network_allowed": true,
  "external_write_allowed": false,
  "max_steps": 10,
  "expires_at": "2026-05-21T18:00:00Z",
  "pause_state": "active"
}
```

Permission envelopes bound planning and continuation. They do not grant new capabilities, override required confirmations, or authorize writes unless an existing governed capability supports the write and the user approves it.

---

## TaskStep State Machine

Each step should have:

```json
{
  "step_id": "step_001",
  "goal_id": "goal_auralis_launch_001",
  "title": "Run Shopify read-only intelligence report",
  "status": "planned",
  "required_capability": 65,
  "approval_required": false,
  "blocked_reason": null,
  "ledger_ref": null,
  "result_summary": null
}
```

Step statuses:

```text
planned
proposed
waiting_for_approval
approved
running
completed
failed
blocked
skipped
canceled
```

Only the governed execution path can move a step into `running`.

---

## Goal Card UI Fields

Minimum visible fields:

```text
goal title
goal status
current step
next proposed step
allowed capabilities
blocked capabilities
approval needed
recent receipts
last update
pause button
cancel button
```

Expanded fields may include step timeline, permission envelope summary, connector scopes, read/write boundary, cost posture, ledger links, failure reason, and retry option.

---

## Approval Behavior

A goal can contain planned or proposed steps without approval.

Approval is required before any step with an external effect or an existing confirmation-gated capability executes.

Approval should apply to the smallest meaningful action, not to an unbounded goal.

A permission envelope may allow bounded read-only continuation, but it may not authorize external writes, publishing, sending, buying, deleting, account modification, or autonomous browser/computer-use.

---

## Ledger / Receipt Behavior

Every executed step should attach ledger references and trust receipts back to the Goal Card.

Receipts should show what was proposed, what was approved, what capability ran, what data or connector was touched, whether an external effect occurred, whether anything was blocked, and the final result.

The Goal Card summarizes receipt state; the ledger remains the source of truth.

---

## Pause / Cancel Behavior

Users must be able to pause or cancel a goal.

Paused goals cannot start new steps.

Canceled goals cannot resume without creating a new goal or explicit user action.

Pending approval should be cleared or marked stale when a goal is paused, canceled, expired, or disconnected.

---

## MVP Phases

Phase 1: Goal cards only. Create, display, update, pause, cancel, and persist visible goal state. No execution.

Phase 2: Proposal-only planning. Nova proposes steps and permission envelopes. User edits or approves the plan. No execution.

Phase 3: Governed single-step execution. User starts one step; the step passes through the existing governed capability path.

Phase 4: Bounded read-only continuation. Nova may proceed through pre-approved read-only steps within a visible permission envelope and step budget.

Phase 5: Workflow templates. Goal Cards attach to repeatable workflow templates after the object model and approval surfaces are stable.

---

## Acceptance Tests

A future implementation should prove:

- a goal can be created without executing anything
- a proposed plan does not execute actions
- an allowed read-only step routes through the governor path
- a confirmation-gated step waits for user approval
- a denied step does not execute
- a paused goal cannot start new steps
- a canceled goal cannot resume silently
- an expired permission envelope blocks continuation
- every executed step attaches a receipt
- blocked browser, purchase, Shopify write, and automatic email-send attempts remain blocked

---

## Do-Not-Do List

Do not use Goal Cards to create hidden autonomy.

Do not allow infinite loops.

Do not let the planner execute directly.

Do not let permission envelopes bypass CapabilityRegistry or GovernorMediator.

Do not add browser/computer-use authority.

Do not add Shopify writes.

Do not automatically send emails.

Do not treat connector access as action permission.

Do not claim Goal Cards are implemented until runtime code, tests, generated runtime truth, and proof artifacts agree.

---

## Example: Auralis Shopify Launch

Goal: Prepare Auralis Shopify launch.

Allowed capabilities may include governed web search, local file/folder opening, email draft creation, and Shopify read-only intelligence if Cap 65 P5 is complete.

Blocked actions include Shopify writes, Printify actions, customer messaging, theme edits, product edits, order edits, purchases, publishing, and browser/computer-use.

Example steps:

1. Run a read-only Shopify intelligence report.
2. Summarize products, inventory, and order signals.
3. Draft a launch checklist.
4. Draft an outreach or announcement email for user review.
5. Wait for user approval before any external effect.

---

## Example: Nova Repo Cleanup

Goal: Clean up Nova repo continuity.

Allowed capabilities may include governed search, file/folder opening, analysis document generation, and read-only issue/PR review if connector access exists.

Blocked actions include merging PRs, deleting branches, changing runtime code, modifying capability locks, or closing issues unless explicitly requested and governed.

Example steps:

1. Review current priority and active TODO docs.
2. Identify stale or conflicting docs.
3. Draft a cleanup plan.
4. Ask for approval before modifying files.
5. Create receipts for each applied change.

---

## Final Boundary

Governed Goal Cards are a visibility and coordination layer.

They should make Nova feel more useful and continuous without making Nova more autonomous than the user explicitly permits.
