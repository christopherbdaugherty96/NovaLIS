# Phase-5 Runtime Surface
Updated: 2026-03-13
Status: Active and closed for the current trust-facing package
Purpose: Explain the live Phase-5 runtime surface in plain operational language.

## What Phase 5 Means In Runtime Terms
Phase 5 is the layer that lets Nova stay useful across time without becoming autonomous.

In the current runtime, that means Nova can:
- preserve explicit durable memory
- track ongoing work through session-scoped project threads
- bridge session continuity into governed memory for durable cross-session preservation
- let the user inspect and control response style
- surface user-created schedules through calm policy-bound delivery
- generate advisory pattern proposals only when the user opts in

## What Phase 5 Does Not Mean
Phase 5 does not mean:
- hidden learning
- autonomous reminders inferred from behavior
- background execution loops
- delegated authority
- implicit memory-driven action

## Code Surfaces

### Governed memory
- `nova_backend/src/memory/governed_memory_store.py`
- `nova_backend/src/executors/memory_governance_executor.py`
- `nova_backend/src/brain_server.py`

### Continuity and threads
- `nova_backend/src/working_context/project_threads.py`
- `nova_backend/src/working_context/context_store.py`
- `nova_backend/src/brain_server.py`

Current interpretation:
- the live thread surface is session-scoped
- durable continuity across sessions is provided by explicit governed memory
- there is no hidden persistent thread substrate in the closed Phase-5 package

### Tone controls
- `nova_backend/src/personality/tone_profile_store.py`
- `nova_backend/src/personality/interface_agent.py`
- `nova_backend/src/brain_server.py`
- `nova_backend/static/dashboard-control-center.js`

### Scheduling
- `nova_backend/src/tasks/notification_schedule_store.py`
- `nova_backend/src/governor/governor.py`
- `nova_backend/src/brain_server.py`
- `nova_backend/src/ledger/event_types.py`
- `nova_backend/static/dashboard-control-center.js`

### Pattern review
- `nova_backend/src/patterns/pattern_review_store.py`
- `nova_backend/src/brain_server.py`
- `nova_backend/static/dashboard-control-center.js`

## Runtime Boundary
All action-capable behavior still flows through the same authority path:

`User -> brain_server -> GovernorMediator -> Governor -> ExecuteBoundary -> Executor -> Ledger`

Phase-5 surfaces add persistence, continuity, and inspectability.
They do not add a second authority path.

## Current Interpretation Rule
Use this document together with:
- `CURRENT_RUNTIME_STATE.md` for activation status
- `RUNTIME_CAPABILITY_REFERENCE.md` for capability descriptions
- `docs/PROOFS/Phase-5/` for closure and evidence
