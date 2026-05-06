# First Read-Only OpenClaw Workflow Report - 2026-05-06

Status: draft / review required

## Purpose

This package proves the fourth priority-lock step: a first read-only OpenClaw workflow proof.

The workflow is a Project Foreman Brief produced from safe caller-provided sample input through the reviewed OpenClawMediator boundary.

## What Was Added

- `nova_backend/src/openclaw/read_only_workflow_proof.py`
- `nova_backend/tests/openclaw/test_first_read_only_workflow_proof.py`

The proof adapter defines:

- `ProjectForemanBriefInput`
- `ReadOnlyOpenClawWorkflowReceipt`
- `ProjectForemanBriefProof`
- `build_project_foreman_brief_proof()`

## Path Proven

```text
Project Foreman Brief sample input
-> OpenClawDelegationEnvelope
-> OpenClawMediator
-> preview_allowed decision
-> deterministic read-only proof output
-> receipt/non-action statement
```

## Runtime Boundary

The workflow proof:

- uses explicit allowed input scope
- uses caller-provided sample input only
- renders deterministic read-only proof output
- emits a receipt/non-action statement
- blocks missing scope
- blocks browser/computer-use
- blocks filesystem writes
- blocks external/account actions
- blocks direct Cap 63 shortcut use

The workflow proof does not:

- execute OpenClaw
- call Cap 63
- call Governor
- call capabilities
- write files from runtime code
- open browsers
- make network calls
- touch email, calendar, Shopify, or account systems
- add runtime routes
- expand workflow automation

## Evidence

Focused pytest:

```text
32 passed
```

Raw evidence:

- `raw/focused_pytest_results.txt`
- `raw/first_read_only_workflow_payload.json`

The JSON evidence includes:

- `workflow: "Project Foreman Brief"`
- `mediator_decision.decision: "preview_allowed"` for the scoped read-only case
- blocked cases for:
  - missing input scope
  - browser request
  - filesystem write request
  - external/account request
  - direct Cap 63 shortcut
- `execution_performed: false`
- `authorization_granted: false`
- `openclaw_called: false`
- `governor_called: false`
- `capabilities_called: false`
- `filesystem_write_performed: false`
- `browser_opened: false`
- `network_called: false`

## Review Notes

This is proof-first and deterministic. It is not a live runtime route and does not make OpenClaw broadly capable.

The next work should be review/merge only. Any future expansion must stay behind the mediator, explicit envelopes, policy checks, and receipts.
