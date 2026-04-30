# Governed Run Policy Evaluator

This document defines the first policy-evaluator logic for governed desktop/browser/OpenClaw runs.

This is a planning document. It is not current runtime behavior until implemented and reflected in generated runtime truth.

---

## Purpose

The policy evaluator decides whether a governed run or attempted action is allowed, requires approval, should pause, should stop, or must be denied.

It is the enforcement layer between an approved envelope and actual execution.

---

## Core Rule

> If the evaluator cannot prove an action is allowed, it must fail closed.

---

## Policy Outcomes

```text
ALLOW
REQUIRE_APPROVAL
PAUSE
STOP
DENY
```

### ALLOW

The action is inside the approved envelope and may proceed.

### REQUIRE_APPROVAL

The action may be possible, but needs explicit user approval before execution.

### PAUSE

The run should pause because more information, clarification, or approval is needed.

### STOP

The run must stop because a stop condition was reached.

### DENY

The action is not allowed and should not be retried without a new envelope or policy change.

---

## Evaluation Inputs

The evaluator should receive:

- governed run envelope
- current run state
- proposed action
- current surface context
- approval state
- elapsed time
- previous step result
- user cancellation / revoke signal

---

## Run-Level Evaluation

Before execution starts:

```text
if envelope is missing:
    DENY

if envelope fails schema validation:
    DENY

if run state is terminal:
    DENY

if required start approval is missing:
    REQUIRE_APPROVAL

if timeout is invalid or exceeded:
    STOP

otherwise:
    ALLOW
```

---

## Action-Level Evaluation

For each proposed action:

```text
if user cancelled or revoked permission:
    STOP

if run state is terminal:
    DENY

if action is in blocked_actions:
    STOP

if action is not in allowed_actions:
    DENY

if current surface is outside allowed_surfaces:
    STOP

if action requires approval and approval is missing:
    REQUIRE_APPROVAL

if action escalates risk level:
    REQUIRE_APPROVAL or STOP

if executor is uncertain:
    PAUSE

if goal is complete:
    STOP

otherwise:
    ALLOW
```

---

## Risk Escalation Rules

A run escalates risk when it attempts to move from:

- read-only → write
- local-only → external service
- draft → public output
- free action → paid action
- approved path → unapproved path
- approved domain → unapproved domain
- non-sensitive action → credential/account action

Risk escalation should require approval or stop the run depending on severity.

---

## Hard Deny Actions

These should be denied or stopped unless separately approved by a specific high-risk policy:

- credential entry
- purchases
- public publishing
- sending messages or emails
- deleting files
- installing software
- running unknown executables
- disabling security controls
- changing account settings

---

## Scheduled Trigger Rule

A scheduled trigger may start checks or prepare an envelope.

A scheduled trigger does not automatically approve execution.

```text
if trigger_type == scheduled and action_risk in [medium, high] and approval_missing:
    REQUIRE_APPROVAL
```

---

## Continuous Run Rule

Continuous presence does not grant execution authority.

```text
if continuous_process attempts real action without active envelope:
    DENY
```

---

## Stop Conditions

The evaluator must stop the run when:

- goal is complete
- timeout is reached
- user cancels
- scope violation occurs
- blocked action is attempted
- policy denies continuation
- runtime error prevents safe continuation

---

## Pause Conditions

The evaluator should pause when:

- executor is uncertain
- UI/page/app state is unclear
- required approval is missing
- a retry would change scope
- user clarification is needed

---

## Fail-Closed Defaults

- Unknown action: DENY
- Unknown surface: DENY or STOP
- Unknown risk level: DENY
- Missing approval: REQUIRE_APPROVAL or DENY
- Missing stop condition: DENY
- Missing blocked actions: DENY
- Missing allowed actions: DENY

---

## First Implementation Target

Start with pure dry-run evaluation.

No OpenClaw desktop/browser execution should occur until the evaluator can pass validation, action, scope, stop, and receipt tests.
