# Active Priority Lock - Approval Gate Wiring

Status: ACTIVE

Date: 2026-05-15

This is human-maintained priority guidance, not generated runtime truth. Generated runtime docs
and actual code remain authoritative if they conflict with this lock.

---

## Goal

Make approval-required governed actions genuinely execution-blocking while keeping the approval
state visible and inspectable.

---

## Scope

```text
approval-required actions must stop at a pending state until explicitly approved
approved actions may proceed only through the governed execution path
denied actions must remain blocked with a visible non-execution outcome
pending / approved / denied state should be visible through existing receipt / trust surfaces where possible
receipt and ledger state should stay consistent with the approval decision
factual status language only
```

This lock is for approval gate wiring only.

---

## Strict Non-Goals

```text
no new capability
no authority expansion
no OpenClaw expansion
no browser/computer-use
no external writes beyond already-authorized capability boundaries
no broad dashboard redesign
no autonomous workflow execution
no Shopify writes
no Google connector runtime work
no Cap 64 P5 work
no Cap 65 P5 work
no bundling unrelated trust/dashboard cleanup
```

---

## Required Output

```text
1. Approval-required governed actions stop before execution when approval is pending.
2. Approval decisions are visible as pending / approved / denied.
3. No approval path bypasses GovernorMediator / execution boundaries / receipts.
4. Denied actions do not execute.
5. Existing visibility surfaces remain visibility-only and do not become hidden authority paths.
```

---

## Implementation Boundaries

```text
- prefer wiring existing approval-required capability paths before adding any new approval concepts
- preserve ledger / receipt inspectability
- preserve explicit user invocation and confirmation discipline
- keep Trust Panel / receipt surfaces factual and non-authorizing
```

---

## Acceptance Criteria

1. An approval-required action remains non-executed while pending.
2. An explicit approval transitions the action from pending to governed execution.
3. An explicit denial records the denial and leaves the action unexecuted.
4. Tests prove no execution occurs on pending or denied paths.
5. Tests prove approval does not widen authority or introduce a new bypass surface.

---

## Sequencing Rule

```text
Approval gate wiring lock first.
Approval gate wiring implementation second.
```

Do not bundle approval-gate runtime implementation into this lock/continuity branch.
