# Trace and Observability Specification

Status: planning.

## Purpose

Provide safe, structured visibility into how Nova reasons, selects context, proposes actions, and executes routines.

Trace must not expose private chain-of-thought. It must expose useful, structured signals for trust and debugging.

## Trace layers

- BrainTrace
- RoutineTrace
- ContextPackTrace
- BoundaryTrace
- MemoryTrace
- LearningTrace
- OpenClawRunTrace

## BrainTrace

Fields:

- detected_intent
- selected_mode
- context_sources_used
- memories_used
- learning_items_used
- uncertainty_flags
- recommendation_reason
- action_boundary_detected
- next_required_user_decision

## RoutineTrace

Fields:

- routine_id
- trigger
- blocks_run
- sources_accessed
- approvals_required
- outputs_created
- failures
- receipts_written

## ContextPackTrace

Fields:

- sources_selected
- budget_usage
- warnings
- dropped_items_due_to_budget
- why_selected

## BoundaryTrace

Fields:

- boundary_type
- detection_reason
- action_required
- approval_state

## MemoryTrace

Fields:

- memory_used
- why_used
- scope
- authority_level

## LearningTrace

Fields:

- learning_used
- why_used
- category
- confidence

## OpenClawRunTrace (future)

Fields:

- envelope
- steps
- tools_used
- approvals
- stop/pause events
- receipts

## Rules

- no hidden execution
- no hidden memory use
- no hidden learning influence
- no chain-of-thought exposure
- must be human-readable

## Success criteria

Trace is successful when:

- user can understand why Nova responded a certain way
- user can see what context influenced output
- user can see when a boundary is detected
- user can review routine execution
- system is debuggable without exposing private reasoning
