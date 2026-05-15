# Active Priority Lock - Trust Panel MVP

Status: ACTIVE

Date: 2026-05-14

This is human-maintained priority guidance, not generated runtime truth. Generated runtime docs
and actual code remain authoritative if they conflict with this lock.

---

## Goal

Expose existing governance and receipt state visibly without adding runtime authority.

---

## Scope

```text
visible receipt / ledger feed
capability label
execution status
approval-required indicator if already present
source path summary: user request -> capability -> governed execution -> receipt
recent action detail view
```

This lock is for the Trust Panel MVP only.

---

## Strict Non-Goals

```text
no new capability
no authority expansion
no approval gate behavior change
no external writes
no OpenClaw expansion
no browser/computer-use
no broad dashboard redesign
no autonomous workflow execution
no Cap 64 P5 work
no Cap 65 P5 work
no Shopify writes
no Google connector runtime work
```

---

## Required Output

```text
1. Show what happened.
2. Show why it was allowed.
3. Show what capability ran.
4. Show whether approval was required, if that field already exists.
5. Show the receipt.
```

---

## Suggested MVP Surfaces

```text
- recent governed activity feed
- receipt rows with capability/risk/context labels
- drill-down detail for one selected receipt
- explicit empty states when no receipts exist
- factual status language only
```

---

## Sequencing Rule

```text
Trust Panel MVP first.
Approval gate wiring second.
```

Do not bundle approval-flow behavior changes into the Trust Panel MVP branch.

---

## Acceptance Criteria

1. The operator can see recent governed actions in one visible panel.
2. Each row identifies the capability and outcome.
3. The panel distinguishes visibility from authority.
4. The panel does not create new execution paths.
5. Approval-state visibility uses existing data only; no new approval behavior is introduced.

---

## Next Step

Review this lock, then implement the Trust Panel MVP in a separate scoped branch.
