# Run System (Planning Only)

Defines Nova's future governed run orchestration model.

This is planning only. It does not change runtime behavior, active capabilities, generated runtime truth, or execution authority.

---

## Core Rule

> All execution must originate from a Run.

Global Chat may create, inspect, steer, pause, resume, or cancel runs.

Global Chat must not directly execute capabilities outside a Run.

---

## RunManager (Authoritative)

RunManager is the single authority for future run state.

It owns:

- creating runs
- updating runs
- resolving runs
- pausing/cancelling runs
- applying steering messages
- tracking lifecycle state
- tracking active run focus
- tracking last-interacted run
- enforcing run limits
- recording run receipts

No system may:

- create hidden runs
- execute outside RunManager
- bypass run lifecycle tracking
- mutate run state without a recorded transition

---

## Run Model

```text
Run
- run_id
- title
- project_or_thread
- goal
- run_type
- status
- current_step
- steps[]
- required_approvals[]
- allowed_actions[]
- blocked_actions[]
- environment_scope
- receipts[]
- created_at
- updated_at
- last_interacted_at
- focused_at
- max_steps
- max_runtime_seconds
- loop_policy
```

---

## Active Run Context

Nova should track active work context explicitly.

Required concepts:

```text
active_run_id
last_interacted_run_id
focused_run_id
recent_runs[]
waiting_for_user_runs[]
```

### active_run_id

The run currently doing work or being actively inspected.

### last_interacted_run_id

The run most recently referenced by the user or Nova.

Used for follow-ups like:

```text
pause that
make it less hype
show me where it is
```

### focused_run_id

The run selected in the Co-Work page or equivalent UI.

Focus does not grant execution authority.

---

## Focus Switching Behavior

The user may switch focus at any time.

Examples:

```text
switch to the YouTube run
show the prospecting run
pause the current run
go back to the Nova docs run
```

When focus changes, Nova should show:

- run title
- current status
- current step
- pending decisions
- next safe action

Switching focus should not resume execution automatically.

---

## Run Types

```text
planning_only
analysis
execution
hybrid
```

### planning_only

Allowed:

- clarify
- understand
- plan
- draft
- suggest

Blocked:

- tool execution
- browser action
- file mutation
- account action

### analysis

Allowed:

- read-only tool use when governed
- source-backed analysis
- summaries

Blocked:

- write actions
- account mutation
- publishing

### execution

Requires:

- task envelope
- approval gate
- Governor path
- receipts

### hybrid

Staged run:

```text
plan → review → approve → execute bounded steps
```

---

## Simple Task Mode vs Run Mode

Not every request needs a full Run.

### Simple Task Mode

Use for:

- low complexity
- low risk
- chat-only or planning-only output
- no external execution
- no ongoing lifecycle required

Examples:

- summarize a provided note
- turn a script into a scene outline
- suggest five topic angles

### Run Mode

Use when the task is:

- multi-step
- stateful
- tool-using
- approval-sensitive
- requires visible progress
- needs pause/cancel/steering

Examples:

- research five local business prospects and open review tabs
- create a YouTubeLIS planning package from a script
- prepare a multi-source report with follow-up decisions

Rule:

> A workflow is a chain of tasks. A Run is how Nova keeps that chain visible and governed.

---

## Run Lifecycle

```text
created
planning
waiting_for_approval
approved
running
pausing
paused
failed
completed
cancelled
expired
```

Terminal states:

```text
completed
failed
cancelled
expired
```

A terminal run cannot resume. A new run is required.

---

## Step Model

Each step must define:

```text
step_id
description
capability
requires_approval
risk_level
status
expected_output
failure_behavior
safe_pause_point
```

Approval is step-level, not blanket permission for the whole run.

A run-level approval may approve planning. It does not automatically approve every execution step.

---

## Interruption and Pause Behavior

If the user interrupts, Nova should not ignore them.

Default behavior:

```text
finish the current safe step
pause before the next step
summarize what happened
show what remains
ask for next direction
```

If the current step is unsafe to continue, Nova should stop immediately.

A pause summary should include:

- completed step
- current state
- remaining steps
- pending approvals
- any risk or uncertainty

Examples:

```text
Paused after verifying the first two prospects. Three remain. No outreach has been done.
```

```text
Paused before opening tabs because browser action requires approval.
```

---

## Time, Step, and Resource Limits

Every run should define limits before work begins.

Possible limits:

- max steps
- max runtime
- max browser tabs
- max sources
- max retries
- max results
- max cost/credits if future paid services are involved

Defaults should be conservative.

If a run reaches a limit, Nova should pause and summarize instead of continuing.

---

## Automation Loop Policy

Automation loops must not start silently.

Any recurring or repeated run must be:

- scheduled by the user
- explicitly initiated by the user
- or proposed by Nova and approved by the user

Recurring loops require:

- visible schedule
- clear purpose
- run envelope
- stop condition
- rate limit
- quiet hours if relevant
- receipt or summary output
- easy disable control

Nova may propose a loop, but proposal is not approval.

Examples:

```text
I can check approved AI-tool sources once a week and summarize only the top updates. Want to schedule that?
```

Blocked by default:

- unapproved continuous polling
- hidden background automation
- autonomous publishing loops
- autonomous trading loops
- account-action loops

---

## Run Persistence

Runs may begin as session-only.

Future persistence should distinguish:

```text
session run
persistent run
scheduled run
archived run
```

### session run

Exists only during the current session unless saved.

### persistent run

Saved for later continuation.

Requires visible state and user awareness.

### scheduled run

Runs at approved times or intervals.

Requires explicit schedule approval.

### archived run

Closed for history and receipt review.

Persistence does not imply execution permission.

Resuming a persisted run should re-check:

- current state
- stale assumptions
- expired approvals
- changed capabilities
- changed environment

---

## Run Concurrency Model

Multiple runs may exist.

Rules:

- multiple planning runs may exist
- multiple paused or waiting runs may exist
- only one active execution run should run at a time unless a future scheduler explicitly supports more
- user may switch focus between runs
- no run may hide its state from the user

This supports co-working without broad autonomy.

---

## Run Steering Rules

The user may steer a run through Run Chat or Global Chat.

User may:

- change the goal
- narrow scope
- expand scope
- add/remove constraints
- skip a step
- reorder steps
- reject a source/result
- pause/cancel the run

Nova must then:

- update the Run Script visibly
- re-check the task envelope
- re-score risk/confidence if needed
- ask for approval if scope or risk increased
- record the steering event

Steering does not bypass governance.

---

## Run Chat vs Global Chat

### Global Chat

Primary co-working surface.

It can:

- start runs
- list runs
- switch focus
- ask about run status
- route steering messages
- continue unrelated conversation

### Run Chat

Scoped communication for one specific run.

It can:

- refine the run
- clarify decisions
- approve/reject steps
- modify the Run Script
- pause/cancel that run

Rule:

> Global Chat is conversation. Run Chat is scoped work steering.

---

## Coworking Behavior

Nova should communicate like a helpful coworker while operating like a governed system.

This means Nova should:

- acknowledge direction briefly
- show useful progress
- ask focused questions
- suggest improvements naturally
- avoid unnecessary friction
- stay clear about limits

Nova should not:

- dump excessive internal structure for simple tasks
- act overly casual or sloppy
- hide important decisions
- continue work beyond the approved task

---

## Run Script

The Run Script is the visible working plan.

It is not hidden chain-of-thought.

It should show:

- current step
- completed steps
- next steps
- blocked steps
- approval points
- expected output

Example:

```text
1. Understand the script.
2. Extract claims.
3. Verify claims.
4. Build scene plan.
5. Build asset list.
6. Prepare approval envelope.
7. Stop for review.
```

---

## Environment Awareness

Each run must declare environment scope.

Possible scopes:

- chat
- memory
- browser
- local filesystem
- local system controls
- OpenClaw governed environment
- external account read-only
- external account write (blocked unless future policy exists)

The environment scope must appear in the task envelope before execution.

---

## Execution Rules

- No execution outside a Run.
- Planning may run in background only if visible and stoppable.
- Execution must be approved and visible.
- Execution must use the Governor path.
- Execution must produce a receipt.
- Execution must stop at the defined stop condition.

---

## Completion Rule

Every run must define:

- exact success condition
- stop condition
- what not to continue doing

Example:

```text
Success: 5 qualified prospects found and summarized.
Stop: after summary and opened tabs.
Do not continue: no outreach, no email, no CRM entry.
```

---

## Result Quality Criteria

A run result is valid only if it:

- matches the original goal
- respects constraints
- is useful/actionable
- includes expected outputs
- does not include unnecessary work
- states uncertainty when relevant

---

## Result Confidence

Nova should state confidence when relevant:

```text
high / medium / low
```

It should also state uncertainty areas.

Example:

```text
Confidence: medium. These businesses appear to have weak web presence, but two may have social pages that need manual review.
```

---

## Failure Handling

On failure:

- mark the step failed
- pause the run
- surface the error clearly
- suggest recovery options
- require user decision before continuing when risk or scope changes

Recovery options may include:

- retry
- adjust scope
- skip step
- cancel run
- convert to manual instructions

---

## Visibility Rule

All runs must be:

- visible
- pausable
- stoppable
- auditable
- resumable if not terminal

Nova can work in the background, but it cannot hide in the background.

---

## Status

Planning only. Not implemented.
