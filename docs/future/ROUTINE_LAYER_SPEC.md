# Routine Layer Specification

Status: v0 implemented (RoutineGraph v0 — PR #93 2026-05-03); remaining objects and scheduling future

## Definition

Routine Layer defines how workflows run.

It is separate from Brain and OpenClaw.

## Responsibilities

- orchestrate steps
- gather context
- call Brain for synthesis
- present outputs
- create receipts

## Not responsible for

- reasoning (Brain)
- execution authority (Governor)
- raw execution (OpenClaw)

## Core objects

| Object | Status |
|---|---|
| RoutineGraph | Implemented (PR #93) |
| RoutineBlock | Implemented (PR #93) |
| RoutineRun | Implemented (PR #93) |
| RoutineReceipt | Implemented (PR #93) |
| RoutineState | Not implemented — covered by RoutineRun outputs dict |

## Implemented routines

| Routine | Status |
|---|---|
| Daily Brief | Implemented — `run_daily_brief_routine()` wraps `compose_daily_brief()` with 8 named blocks and a RoutineReceipt (PR #93) |
| Plan My Week | Implemented — two-phase runner with `PlanMyWeekProposal` approval boundary (PR #98) |

## Rules

- no silent execution
- no authority
- all outputs inspectable
