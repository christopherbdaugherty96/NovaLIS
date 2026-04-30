# Run System (Planning Only)

Defines Nova's future governed run orchestration model.

## Core Rule
All execution must originate from a Run.

## RunManager (Authoritative)
Single authority for:
- creating runs
- updating runs
- resolving runs

No system may execute outside RunManager.

## Run Model
Run:
- run_id
- title
- goal
- run_type
- status
- steps[]
- current_step
- approvals_needed[]
- receipts[]

## Run Types
- planning_only (no execution)
- analysis (read-only)
- execution (approval required)
- hybrid (plan → approve → execute)

## Run Lifecycle
- created
- planning
- waiting_for_approval
- approved
- running
- paused
- failed
- completed
- cancelled

## Step Model
Each step:
- step_id
- description
- capability
- requires_approval
- risk_level
- status

Approval is step-level.

## Execution Rules
- No execution outside a Run
- Planning may run in background
- Execution must be approved and visible

## Failure Handling
On failure:
- mark step failed
- pause run
- surface error
- require user decision

## Run Chat vs Global Chat
Global Chat:
- creates and manages runs

Run Chat:
- steers a specific run

## Visibility Rule
All runs must be:
- visible
- pausable
- stoppable
- auditable

## Status
Planning only. Not implemented.