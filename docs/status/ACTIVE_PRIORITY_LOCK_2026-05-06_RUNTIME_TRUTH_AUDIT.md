# Active Priority Lock - 2026-05-06 Runtime Truth Audit

Status: completed.

Completed by PR #110: `docs: audit runtime truth after OpenClaw proof`.

This is human-maintained priority guidance, not generated runtime truth. Generated runtime docs and actual code remain authoritative if they conflict with this lock.

This lock selected a narrow verification workstream after the completed OpenClaw priority-lock chain.

## Completed Workstream

```text
Runtime truth regeneration / audit after OpenClaw proof chain
```

## Purpose

Verified whether generated runtime truth and human-maintained runtime docs accurately reflected the newly merged OpenClaw governance/proof surfaces.

This was a verification and alignment lock, not a product expansion lock.

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

## Completed Actions

- runtime docs were regenerated through `scripts/generate_runtime_docs.py`
- generated runtime truth changed through the generator path only
- runtime fingerprint/hash alignment was updated
- audit evidence was added under `docs/demo_proof/2026-05-06_runtime_truth_audit_after_openclaw/`
- OpenClawMediator remained documented as non-executing
- first read-only workflow proof remained documented as non-authorizing
- proof-artifact over-indexing in generated MOCs was found and corrected
- `docs/demo_proof/**/raw/*` and `docs/demo_proof/**/screenshots/*` are excluded from generated MOC indexing while proof reports remain browsable

## Still Not Approved

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

## Acceptance Gate Result

This lock is complete.

1. Generated runtime docs needed regeneration after PRs #103-#108 for fingerprint/hash alignment.
2. Regenerated changes were generator-consistent and code-grounded.
3. Runtime docs and MOCs now better distinguish active runtime surfaces from proof-only/supporting artifacts.
4. Docs preserve that OpenClawMediator and first read-only workflow proof do not grant execution authority.
5. The discovered discrepancy, proof raw/screenshot over-indexing in generated MOCs, was recorded and fixed through generator policy.

## Boundary Rule

Do not start new feature or runtime expansion from this completed lock. Select the next workstream only through a new reviewed priority lock.
