# Trust Flow Integration

Defines how signals, context, planning, and execution connect through the Trust Flow.

---

## Core Principle

> Every meaningful action must pass through a visible trust surface before execution.

---

## Integrated Flow

```text
Signal or user input
→ Context Assembler
→ Plan Draft
→ Trust Card
→ Approval (if required)
→ Run Lifecycle (execution)
→ Receipt
→ Memory / Learning proposal
```

---

## Inputs

- signal registry
- user request
- context assembler output
- domain permission profile

---

## Trust Card Responsibilities

Must show:

- intent
- plan
- risk
- allowed actions
- blocked actions
- approval requirements
- stop conditions

---

## Integration Rules

- signals cannot bypass trust flow
- context cannot override governance
- approval must be explicit
- execution must reflect approved plan

---

## Failure Handling

Trust Flow must handle:

- missing context
- conflicting memory
- blocked actions
- expired approval
- runtime mismatch

---

## Output

Trust Flow produces:

- execution decision
- approval state
- run lifecycle entry

---

## Status

Planning only
