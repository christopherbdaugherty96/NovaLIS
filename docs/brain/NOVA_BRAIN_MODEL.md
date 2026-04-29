# Nova Brain Model

The Nova Brain is a governed cognitive loop.

It is not a new executor. It is the reasoning layer that prepares structured, Governor-safe plans.

## Loop

```text
Task Intake
→ Task Understanding
→ Task Clarifier
→ Working Memory
→ Environment Reasoner
→ Authority Question
→ Plan Builder
→ Dry Run / Preview
→ Governor Gate
→ Execution
→ Proof
→ Reflection
```

## Layers

### 1. Task Intake

Identify what the user is trying to accomplish.

### 2. Task Understanding

Classify task type, ambiguity, evidence need, risk, and whether the task is single-step or multi-step.

### 3. Task Clarifier

If the goal is underspecified, ask the smallest useful question before planning.

Examples:

- `Find contractors` → ask for city/service area.
- `Update Shopify product` → ask which product/field, and note current Shopify support is read-only.
- `Use browser` → ask whether isolated OpenClaw browser or personal signed-in browser is meant.

### 4. Working Memory

Track current goal, known facts, unknowns, active project, current environment, blocker, and next decision.

### 5. Environment Reasoner

Decide what environment the task requires: local conversation, memory, runtime docs, web search, isolated browser, personal browser, local OS, email draft, Shopify, OpenClaw, or future connector lane.

### 6. Authority Question

Ask what boundary is crossed, which capability grants access, whether confirmation is required, whether setup is missing, and what proof should exist.

### 7. Plan Builder

Create steps with environment, capability, confirmation points, fallbacks, and expected receipts.

### 8. Dry Run / Preview

Generate a non-executing plan preview so the user can inspect the intended route before execution.

### 9. Governor Gate

The existing Nova governance spine decides whether execution is allowed.

### 10. Execution

Only the existing governed runtime path executes actions.

### 11. Proof

Receipts, source URLs, screenshots, state change, and run timeline evidence are collected where applicable.

### 12. Reflection

Determine whether the task was satisfied, what remains blocked, what should be remembered, what should be asked next, and what proof package should be updated.

## Current Status

This model is conceptual until runtime implementation proves otherwise.