# Nova Approval Queue Product Plan

Date: 2026-04-27

Status: Future product/architecture plan / not current runtime truth

Purpose: define the future approval queue that lets Nova prepare work, explain risk, and ask the user before any durable or external action.

---

## Active Priority Note

This is not the current active implementation task. Build RequestUnderstanding trust/action-history visibility first.

---

## Executive Summary

The approval queue should become a first-class Nova product surface.

Core rule:

> **Nova may prepare proposed actions. The user keeps authority over real-world changes.**

The queue should make proposed actions visible, editable, approvable, deniable, expirable, and auditable.

---

## What Belongs In The Queue

```text
email draft creation
Gmail draft creation
calendar event proposal
file write/move/delete proposal
GitHub issue/PR/commit proposal
CRM/customer update proposal
Shopify/customer/order action proposal
browser submit/save/send/book/buy proposal
Home Assistant security/safety-sensitive action
OpenClaw durable/external proposed action
```

Read-only summaries usually do not need approval, but should still produce receipts when useful.

---

## Proposed Action Fields

```text
proposed_action_id
source: Nova / OpenClaw / connector / browser / user command
request_understanding_snapshot
action_type
risk_level
target_system
what_will_happen
what_will_not_happen
input_summary
output_or_draft_preview
requires_approval_reason
allowed_until / expiration
status: pending / approved / denied / expired / cancelled / executed / failed
created_at
updated_at
approved_by
receipt_id
```

---

## User Experience

A useful approval card should show:

```text
Action proposed
Target system
Risk level
What will happen
What will not happen
Preview of draft/change
Approve / Deny / Edit / Ask why
Expiration if any
Receipt after decision
```

Example:

```text
Proposed action: Create Gmail draft to Sarah
What will happen: one draft will be created in Gmail
What will not happen: the email will not be sent
Requires approval: yes
```

---

## Approval Rules

```text
READ → usually no approval, receipt if meaningful
DRAFT_ONLY → approval may be required to create external draft; never sends
LOCAL_REVERSIBLE → may be allowed after signoff/settings
DURABLE_MUTATION → pending approval
EXTERNAL_WRITE → pending approval
FINANCIAL / SECURITY / SAFETY → blocked by default or hard approval after maturity
```

---

## Receipts

Every queue decision should create trace/receipt evidence:

```text
proposed
approved
denied
expired
executed
failed
blocked
```

Non-action statements are required:

```text
Nothing was sent.
No calendar event was created.
No files were changed.
The proposed action was denied.
The draft was created but not sent.
```

---

## Guardrails

```text
Approval cannot bypass GovernorMediator or ExecuteBoundary.
Approval must be scoped to one proposed action, not broad future permission.
Expired approvals cannot execute.
Edited actions require revalidation.
High-risk actions cannot be auto-approved.
Queue items must not contain secrets in plain text.
```

---

## Build Order

```text
1. Define proposed action schema.
2. Add read-only pending action store.
3. Add approval/deny states without execution.
4. Add trust/action-history UI card.
5. Wire first draft-only or local reversible action.
6. Add expiration/cancel/edit.
7. Add OpenClaw proposed action integration.
```

---

## Final Rule

> **Approval is narrow, visible, revocable, and logged.**
