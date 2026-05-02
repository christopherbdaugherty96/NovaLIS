# Routine Layer Specification

Status: planning

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

- RoutineGraph
- RoutineBlock
- RoutineRun
- RoutineState
- RoutineReceipt

## First routine

Daily Brief

## Rules

- no silent execution
- no authority
- all outputs inspectable
