# Task Understanding and Envelope (Planning Only)

Defines how Nova converts user intent into structured, governed tasks.

This is planning only. It does not change runtime behavior.

---

## Purpose

This layer ensures Nova:

- understands user intent correctly
- uses memory responsibly
- defines clear boundaries
- does not over-act or drift

---

## Task Understanding Object

Every task should produce:

```text
Goal
Context Used
Constraints
Assumptions
Confidence
```

---

## Memory Use Rules

Memory must be treated in tiers.

### Stable Memory
Explicit, user-approved memory.

### Session Memory
Temporary context.

### Derived Context
Inferred patterns (low authority).

Rule:

- Stable memory can influence decisions.
- Derived context may only influence suggestions.
- Memory must never expand execution authority.

---

## Task Envelope

Defines what Nova is allowed to do.

```text
Allowed Actions
Blocked Actions
Environment Scope
Step Limit
Approval Level
Stop Condition
Failure Behavior
```

---

## Example

Task: Find 5 local business website prospects.

Allowed:
- search
- read listings
- open tabs (limited)

Blocked:
- contact businesses
- send messages
- scrape at scale

Stop:
- after 5 results + summary

---

## Principle

> Nova should complete exactly what was asked, safely, visibly, and then stop.

---

## Status

Planning only. Not implemented.
