# Active Priority Lock - 2026-05-06 Runtime Truth Audit

Status: active priority lock.

This is human-maintained priority guidance, not generated runtime truth. Generated runtime docs and actual code remain authoritative if they conflict with this lock.

This lock selects a narrow verification workstream after the completed OpenClaw priority-lock chain.

## Selected Workstream

```text
Runtime truth regeneration / audit after OpenClaw proof chain
```

## Purpose

Verify whether generated runtime truth and human-maintained runtime docs accurately reflect the newly merged OpenClaw governance/proof surfaces.

This is a verification and alignment lock, not a product expansion lock.

## Required Inputs

- PR #103 planning-task preview runtime handoff proof
- PR #104 RequestUnderstanding review-card payload contract
- PR #105 local capability signoff matrix
- PR #106 OpenClawMediator skeleton
- PR #107 first read-only OpenClaw workflow proof
- PR #108 OpenClaw priority-lock closeout
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- `docs/status/OPENCLAW_PRIORITY_LOCK_CLOSEOUT_2026-05-06.md`

## Allowed Work

- run the runtime auditor/generator if needed
- compare generated runtime truth against code and proof packages
- update generated runtime docs only through the generator path
- update human-maintained status/todo docs if they are stale
- add a small proof/audit package under `docs/demo_proof/` if useful
- record any mismatch as a blocker or follow-up rather than patching truth by hand

## Not Approved

- no broad OpenClaw automation
- no browser/computer-use expansion
- no external writes
- no email/calendar/Shopify/account actions
- no direct Cap 63 shortcut use
- no autonomous workflow execution
- no Google connector expansion
- no capability registry expansion
- no workflow automation expansion
- no claim that OpenClaw has full governed hands

## Acceptance Gate

This lock is complete only when a reviewable branch answers:

1. Do generated runtime docs need regeneration after PRs #103-#108?
2. If regenerated, are changes generator-consistent and code-grounded?
3. Do runtime docs distinguish active runtime surfaces from proof-only/supporting artifacts?
4. Do docs preserve that OpenClawMediator and first read-only workflow proof do not grant execution authority?
5. Are any discrepancies listed with exact files and recommended next action?

## Expected Output

A small audit/regeneration PR that either:

- confirms runtime truth is already aligned, or
- updates generated runtime truth through the generator and records why, or
- records blockers/discrepancies without manually inflating runtime claims.

## Boundary Rule

If work is not runtime-truth audit/regeneration/alignment, it is outside this lock.
