# Phase 5 Memory Export and Explicit Command Completion Runtime Slice
Updated: 2026-03-27
Status: Implemented

## Purpose
Close the next explicit-memory gap in the Phase-5 governed memory surface without widening autonomy.

This slice adds:
- governed memory export
- more natural explicit-memory phrasing
- Memory-page download support

It does not add:
- silent memory creation
- assistive noticing
- background suggestion behavior
- autonomous deletion or hidden mutation

## What Landed
### Backend
- `nova_backend/src/memory/governed_memory_store.py`
  - adds export payload generation for governed memory
- `nova_backend/src/executors/memory_governance_executor.py`
  - adds governed `export` action
- `nova_backend/src/api/memory_api.py`
  - adds `GET /api/memory/export`
- `nova_backend/src/governor/governor_mediator.py`
  - adds:
    - `what do you remember`
    - `memory export`
    - `export memory`
    - `forget this`
- `nova_backend/src/brain_server.py`
  - registers the memory export route
  - keeps new memory phrases out of bounded relevant-memory retrieval

### Frontend
- `nova_backend/static/index.html`
  - adds `Export memory` button on the Memory page
- `nova_backend/static/dashboard.js`
  - downloads the export payload as:
    - `nova-memory-export-YYYY-MM-DD.json`

## Governance Boundary
- export is read-only
- export is explicit and user-invoked
- `forget this` still routes through the existing governed delete path
- destructive deletion still requires explicit confirmation
- the memory export route does not bypass the governed store model

## User-Facing Result
Users can now:
- ask `what do you remember`
- ask `memory export`
- ask `export memory`
- say `forget this`
- download a governed JSON memory snapshot from the Memory page

## Verification
- `python -m pytest tests/phase5/test_memory_governance_executor.py tests/test_governor_mediator_phase4_capabilities.py tests/test_memory_api.py`
  - `15 passed`
- `python -m py_compile nova_backend/src/memory/governed_memory_store.py nova_backend/src/executors/memory_governance_executor.py nova_backend/src/api/memory_api.py nova_backend/src/governor/governor_mediator.py nova_backend/src/brain_server.py`
  - passed
- `node --check nova_backend/static/dashboard.js`
  - passed

## Honest Scope Note
This is still Phase-5 explicit memory.

It improves inspectability and user ownership.
It does not move Nova into assistive noticing, suggestion surfacing, or policy-bound help.
