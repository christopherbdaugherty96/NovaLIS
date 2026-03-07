# CONTRIBUTING - Nova (Governance-First Rules)

This repository is governance-constrained.

## Runtime Behavior Authority

For all runtime behavior, capability status, and execution authority truth, use:

`docs/current_runtime/CURRENT_RUNTIME_STATE.md`

Do not restate runtime capability truth in other docs.

## Canonical Governance Authority

Constitutional and governance constraints are defined by:

- `docs/canonical/NOVA COMPLETE CONSTITUTIONAL BLUEPRINT v1.9.txt`
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`

## Allowed Contributions

- Bug fixes that preserve governed behavior
- Clarifying docs that defer runtime truth to `CURRENT_RUNTIME_STATE.md`
- Tests that enforce existing boundaries
- Refactors with no behavior drift

## Forbidden Contributions

- New autonomous behavior
- Background execution loops
- Direct executor bypasses
- Direct network bypasses around `NetworkMediator`
- Any capability change without explicit runtime/governance update

## Review Standard

Every change should declare:

- behavior change: yes/no
- impacted runtime surfaces
- required test updates

If there is a conflict between docs, `docs/current_runtime/CURRENT_RUNTIME_STATE.md` wins for runtime truth.
