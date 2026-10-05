# Approval Grant Receipt Policy

Date: 2026-10-05

Status: Owner decision / authorized for implementation

## Decision

An approval grant is authority and must not exist without a durable issuance receipt.

The earlier Slice 1 policy explicitly allowed authority to exist when the
`APPROVAL_GRANTED` receipt failed. The owner replaces that policy with this
fail-closed rule:

```text
no durable APPROVAL_GRANTED receipt
-> no approval grant
-> no execution authority
```

The Governor may construct a candidate grant before writing the receipt, but it
must revoke that candidate and report issuance failure if persistence fails. A
grant becomes usable only after the real ledger accepts the canonical
`APPROVAL_GRANTED` event.

## Scope

This decision authorizes only the approval-issuance receipt correction and its
regression proof. It does not change capability policy, add authority, implement
timeout reconciliation, or expand any execution surface.
