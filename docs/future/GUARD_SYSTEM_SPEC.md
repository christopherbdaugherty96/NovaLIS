# Guard System Specification

Status: planning.

This document defines planned guard layers for Nova. It is not implemented runtime behavior.

## Purpose

Guards prevent reasoning, routines, memory, learning, and execution surfaces from crossing authority boundaries.

## Guard layers

- BrainGuard
- ModeGuard
- ContextPackGuard
- RoutineGuard
- MemoryGuard
- LearningGuard
- OpenClawGuard

## BrainGuard

Protects Brain reasoning.

Blocks:

- Brain execution
- Brain authorization
- silent memory writes
- memory as permission
- planning docs as runtime truth
- direct OpenClaw handoff

## ModeGuard

Enforces behavior by mode.

### Brainstorm mode

- no file writes
- no issues
- no commits
- no PRs
- explore ideas only unless explicitly asked

### Repo-review mode

- inspect state before recommending
- summarize truth/gaps/next step
- no code changes unless asked

### Implementation mode

- create branch before edits
- focused diff
- validation
- summary

### Merge mode

- review diff/PR
- avoid stale branches
- merge only requested branch
- update docs/status if needed

### Action-review mode

- show planned action
- show boundary
- require user/Governor approval where needed

## ContextPackGuard

Enforces:

- source labels
- authority labels
- budget limits
- stale/conflict warnings
- no forgotten memory
- no candidate-as-truth behavior

## RoutineGuard

Controls routine behavior.

Fields:

- allowed sources
- allowed blocks
- max runtime
- max outputs
- approval points
- receipt requirements

RoutineGuard blocks:

- hidden execution
- unsurfaced schedule changes
- external actions without approval
- memory/learning promotion

## MemoryGuard

Controls durable memory lifecycle.

Blocks:

- autosave as confirmed memory
- memory without scope
- memory without source
- forgotten memory reuse
- memory as authority

## LearningGuard

Controls adaptation.

Blocks:

- hidden learning
- sensitive inference
- learning from client data by default
- learning as permission
- learning that conflicts with current user instruction

## OpenClawGuard

Controls future OpenClaw execution.

Requires:

- mandatory envelope
- allowed paths/domains/tools
- max steps/time
- boundary detection
- approval checkpoints
- stop/pause/recovery
- run/step/action receipts

Blocks:

- freeform unbounded goals
- login/payment/publish/upload/delete without explicit boundary review
- browser/computer-use expansion before hardening

## Success criteria

Guard system is successful when:

- Brain cannot execute
- routines cannot silently act
- memory cannot authorize
- learning cannot change permission
- OpenClaw cannot run outside envelope
- all boundary crossings are visible and reviewable
