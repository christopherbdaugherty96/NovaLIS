# Phase 8 Project Snapshot Operator Slice
Date: 2026-04-13
Status: Implemented and verified
Scope: First coding-oriented OpenClaw expansion slice for Nova through a bounded read-only local project-analysis template

## What Landed
The OpenClaw home-agent foundation now includes a new manual template:
- `project_snapshot`

This slice gives Nova:
- a read-only OpenClaw operator run for local workspace analysis
- bounded local file reading for `README.md` and `REPO_MAP.md`
- project-surface summarization for the current workspace
- local-first summarization
- deterministic fallback when local summarization is not available
- no OpenAI fallback for this template

## Why This Matters
This is the first direct bridge between:
- Nova's existing local repo/project understanding tools
- Nova's OpenClaw operator lane

It means the future coding workflow now has a clean first step:
- understand the project before proposing or applying changes

## Runtime Boundaries
This slice is intentionally narrow.

It is:
- manual
- read-only
- local-first
- bounded by strict preflight and envelope budgets

It is not:
- patch proposal
- write-capable apply
- hidden automation
- unrestricted repo mutation

## Files Added Or Updated

### Runtime
- `nova_backend/src/openclaw/strict_preflight.py`
- `nova_backend/src/openclaw/agent_runtime_store.py`
- `nova_backend/src/openclaw/agent_runner.py`

### Verification
- `nova_backend/tests/openclaw/test_strict_preflight.py`
- `nova_backend/tests/openclaw/test_agent_runtime_store.py`
- `nova_backend/tests/openclaw/test_agent_runner.py`
- `nova_backend/tests/test_openclaw_agent_api.py`

### Design and human-guide alignment
- `docs/design/Phase 8/NOVA_LOCAL_CODE_OPERATOR_ROADMAP_2026-04-13.md`
- `docs/reference/HUMAN_GUIDES/31_LOCAL_CODE_OPERATOR_AND_PROJECT_ANALYSIS.md`

## Implementation Notes

### Template model
`project_snapshot` is stored beside the existing OpenClaw templates and inherits the same:
- runtime-store model
- envelope preview model
- delivery handling
- active-run handling
- recent-run history

### Envelope posture
The template uses:
- `project_read`
- `summarize`

and keeps:
- `max_network_calls = 0`
- `max_files_touched = 2`
- `max_bytes_written = 0`

### Summarization policy
For `project_snapshot`:
- local summarizer is allowed
- deterministic fallback is allowed
- metered OpenAI fallback is intentionally skipped

This keeps the first coding-oriented slice local-first and cost-light.

## Verification Run
Verified on 2026-04-13 with:

- `python -m pytest nova_backend\tests\openclaw\test_strict_preflight.py nova_backend\tests\openclaw\test_agent_runtime_store.py nova_backend\tests\openclaw\test_agent_runner.py nova_backend\tests\test_openclaw_agent_api.py -q`
- `python -m py_compile nova_backend\src\openclaw\agent_runner.py nova_backend\src\openclaw\agent_runtime_store.py nova_backend\src\openclaw\strict_preflight.py`

Observed result:
- `33 passed`
- `py_compile` passed

## Product Interpretation
This slice should be interpreted as:
- the first coding-operator foundation
- not a broad coding agent

The correct next order remains:
1. project snapshot
2. patch proposal
3. approval-gated apply
4. verify-and-repair

## Reading Rule
Read this packet with:
- `docs/design/Phase 8/NOVA_LOCAL_CODE_OPERATOR_ROADMAP_2026-04-13.md`
- `docs/reference/HUMAN_GUIDES/31_LOCAL_CODE_OPERATOR_AND_PROJECT_ANALYSIS.md`
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`

Runtime truth still wins if a later generated runtime packet diverges.
