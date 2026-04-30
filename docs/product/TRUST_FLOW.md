# Trust Flow

This document defines the user-facing trust flow NovaLIS should use when moving from reasoning to action.

This is a product/design document. Runtime truth remains generated from the codebase.

---

## Core Principle

> The user should be able to see what NovaLIS thinks it is about to do before anything meaningful happens.

Trust is not only internal policy. Trust must be visible.

---

## Standard Flow

```text
Intent detected
→ Context assembled
→ Plan preview created
→ Risk / authority classified
→ Allowed and blocked actions shown
→ User approval requested if needed
→ Governed execution begins
→ User can pause / stop / revoke
→ Result and receipt shown
→ Optional memory / learning record proposed
```

---

## Trust Card Fields

A Trust Flow card should include:

- detected intent
- user goal
- planned steps
- required capability
- authority tier
- risk level
- allowed actions
- blocked actions
- required approvals
- timeout / stop condition
- expected receipt
- next safe step

---

## Approval States

```text
NOT_REQUIRED
REQUIRED
APPROVED
DENIED
REVOKED
EXPIRED
```

---

## Execution States

```text
PLANNED
PENDING_APPROVAL
RUNNING
PAUSED
COMPLETED
FAILED
CANCELLED
BLOCKED
```

---

## High-Risk Final Review

These actions require final human approval even if earlier planning was approved:

- sending email or messages
- publishing public content
- purchases
- money movement
- account changes
- credential entry
- file deletion
- broker/trading actions

---

## Receipt

Every meaningful governed action should produce a receipt:

- what was requested
- what was approved
- what happened
- what was blocked
- stop reason
- result
- whether anything should become memory

---

## Memory Boundary

A receipt should not automatically become long-term memory.

NovaLIS may propose a memory or learning record, but user approval should be required for persistent learning unless a specific policy allows it.

---

## Anti-Patterns

Avoid:

- hidden action
- vague approval
- approval bundled with unrelated actions
- silent scope expansion
- success without receipt
- memory written without visibility

---

## Current Status

Design target.

Do not claim complete Trust Flow implementation until code, UI, receipts, and generated runtime truth support it.
