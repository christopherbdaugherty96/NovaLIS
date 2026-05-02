# Daily Brief Routine Specification

Status: planning.

## Definition

Daily Brief is a routine and user-facing surface.

It is not the Brain.
It is not an executor.
It is not an authority system.

## Purpose

Package the current operating state of Nova into a clear, actionable summary for the user.

## Inputs

Daily Brief may consume:

- session continuity
- project capsule
- memory health
- learning health
- receipts
- open loops
- search summaries
- calendar/weather summaries
- optional Brain synthesis

## RoutineGraph

```text
Trigger
→ Gather Session State
→ Gather Project Capsule
→ Gather Memory Health
→ Gather Learning Health
→ Gather Receipts
→ Gather Search/Calendar/Weather
→ Build Context Pack
→ Optional Brain Summary
→ Render Brief
→ Write Receipt
```

## Outputs

- current focus
- project summary
- open loops
- recommended next step
- memory candidates to review
- learning candidates to review
- warnings (stale/conflict)

## Rules

- no execution
- no authority
- no automatic memory promotion
- no learning promotion
- no external action

## Future

May become a scheduled routine only after Routine Layer and OpenClaw governance are hardened.
