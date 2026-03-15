# Phase-6 Policy Executor Gate Runtime Slice
Date: 2026-03-13
Status: Implemented runtime slice
Scope: Manual review delegation without trigger runtime

## Purpose
This slice moves Phase 6 past draft-only policy storage and into the first lawful delegated execution review path.

It adds:
- Governor-side executor-gate enforcement
- capability topology classification
- explicit policy simulation
- explicit one-shot manual policy review runs

It does **not** add:
- background triggers
- autonomous policy execution
- chained policy orchestration

## What Was Added
- capability topology metadata for active governed capabilities
- Governor executor-gate enforcement for delegated-policy review
- `policy simulate <id>`
- `policy run <id> once`
- persistent simulation/manual-run metadata in the policy draft store
- ledger-visible policy simulation and manual-run lifecycle events
- operator-health policy counts for simulations and manual review runs

## Runtime Shape
Nova can now:
- validate atomic policy drafts
- store those drafts as disabled items
- simulate a policy through the Governor executor gate
- manually run a safe delegated policy once
- block unsafe delegated policies with explicit Governor verdicts

Nova still cannot:
- run delegated triggers in the background
- enable stored policies for autonomous execution
- delegate persistent-write or external-effect capabilities

## Current Delegated Boundary
The active delegated review path is intentionally narrow:
- only capabilities marked `policy_delegatable`
- only capabilities within the current authority limit
- only manual, invocation-bound runs
- only one run at a time through the Governor

The current authority limit remains:
- `read_only_local`

That means safe examples can be simulated and review-run, while higher classes such as network or persistent-change actions remain blocked.

## User-Facing Command Surface
- `policy overview`
- `policy create weekday calendar snapshot at 8:00 am`
- `policy create daily weather snapshot at 7:30 am`
- `policy show <id>`
- `policy simulate <id>`
- `policy run <id> once`
- `policy delete <id> confirm`

## Core Files
- `nova_backend/src/governor/capability_topology.py`
- `nova_backend/src/governor/policy_executor_gate.py`
- `nova_backend/src/governor/governor.py`
- `nova_backend/src/policies/atomic_policy_store.py`
- `nova_backend/src/brain_server.py`
- `nova_backend/src/executors/os_diagnostics_executor.py`
- `nova_backend/src/ledger/event_types.py`

## Tests Added Or Expanded
- `nova_backend/tests/phase6/test_capability_topology.py`
- `nova_backend/tests/phase6/test_policy_executor_gate.py`
- `nova_backend/tests/phase6/test_atomic_policy_store.py`
- `nova_backend/tests/phase6/test_policy_foundation_contract.py`
- `nova_backend/tests/phase45/test_system_status_reporting_contract.py`

## Verification
- full backend suite: `420 passed`
- frontend mirror sync check: passed
- runtime documentation drift check: passed

## Correct Interpretation
This slice means:
- delegated policy review is now real in code
- Nova can simulate and manually review-run safe policies through the Governor

It does not mean:
- delegated trigger runtime is active
- background monitoring exists
- Nova has crossed into autonomous behavior
