# Nova Phase 8 User Operability And Run System Audit

Date:
- 2026-04-05

Status:
- active design audit

Scope:
- Phase 8 user operability
- run lifecycle clarity
- dashboard and operator UX
- execution visibility
- concrete next fixes

Authority note:
- this is a design audit and backlog-shaping packet
- live runtime truth still belongs to `docs/current_runtime/`

## Purpose

This packet captures a blunt product audit of Nova's current Phase 8 operator surface.

The goal is not to question whether Nova has:
- architecture
- governance
- capability structure

The goal is to answer a narrower and more important question:

`Can a real user understand what Nova is doing, control it, and trust it while it runs?`

This is the boundary between:
- powerful system
and
- usable product

## What Is Already Working

### 1. Nova is a real system, not a demo

Grounded strengths:
- live FastAPI + WebSocket runtime
- real runtime endpoints
- real frontend/backend interaction
- real operator and settings surfaces

### 2. Architecture is cleanly separated

The stack is already meaningfully split into:
- backend governance and execution
- frontend dashboard and operator surfaces
- runtime-truth and diagnostics endpoints

This aligns with the Nova principle:
- Governor for law
- Nova for flow

### 3. Phase awareness is real

Nova already exposes:
- runtime state
- phase status
- current capability and operator surfaces

That is unusually strong compared with most AI projects.

### 4. Product surfaces already exist

The dashboard already exposes meaningful surfaces:
- Dashboard
- Chat
- Agent
- Skills
- Workspace
- Memory
- Policies
- Trust
- Settings

That means the problem is not "there is no system."
The problem is that execution still needs to feel clearer and more user-operable.

## Core Diagnosis

Nova's Phase 8 bottleneck is:

`visible, controllable execution coherence`

The system already has:
- governance
- operator foundations
- useful capabilities

What it still needs is a stronger run experience:
- one active task
- visible progress
- visible checkpointing
- obvious stop/recovery controls
- lower interface noise

## Main Risks And Problems

### 1. UI can still feel like an internal panel

Risk:
- too many repeated blocks
- too much stacked surface noise
- sections that explain system internals better than user intent

User-facing failure mode:
- "What am I supposed to do here?"

### 2. Run lifecycle is still not fully first-class

The system now has active-run visibility, but the audit correctly points out that Phase 8 still needs:
- a clearer single active run concept
- a fuller first-class run object across surfaces
- a richer lifecycle than static history plus one live state

### 3. Execution state still needs stronger presentation

Required state clarity:
- running
- paused
- waiting
- failed
- cancelled
- completed

The UI should make these states obvious at a glance.

### 4. Repetition and placeholder-like rendering can destroy trust

Even when the backend is working, repeated prompts or repeated cards create a product-level failure:
- low clarity
- low confidence
- feeling of unfinishedness

### 5. "What Nova is doing" still needs to be stronger

The operator philosophy requires:
- current step
- progress
- next decision point
- waiting reason

Without that, Nova violates its own visible-operator principle.

### 6. WebSocket instability remains a trust risk

Repeated connect/disconnect behavior can cause:
- stale or inconsistent run state
- UI flicker
- delivery confusion
- race conditions in future richer run-state work

Even if partially environment-driven, this belongs in the Phase 8 hardening backlog.

## Critical Missing Pieces For Phase 8

### 1. First-class Run object

Phase 8 should converge on a stronger run entity with fields like:
- id
- goal
- status
- steps
- current_step
- progress
- requires_input
- checkpoint
- error

Current run visibility is meaningful, but this fuller run model remains the stronger target.

Suggested baseline shape:

```json
{
  "id": "RUN-20260405-001",
  "goal": "Prepare a morning brief",
  "status": "running",
  "status_label": "Collecting calendar",
  "started_at": "2026-04-05T07:02:10Z",
  "updated_at": "2026-04-05T07:02:18Z",
  "triggered_by": "dashboard",
  "delivery_mode": "hybrid",
  "progress": {
    "completed_steps": 2,
    "total_steps": 5,
    "percent": 40
  },
  "current_step": {
    "id": "calendar_collect",
    "label": "Collect calendar",
    "state": "running"
  },
  "steps": [
    { "id": "weather", "label": "Load weather", "state": "completed" },
    { "id": "calendar", "label": "Collect calendar", "state": "running" },
    { "id": "news", "label": "Collect headlines", "state": "waiting" }
  ],
  "requires_input": false,
  "checkpoint": null,
  "error": null
}
```

This does not need to be the final exact runtime schema.
It is the minimum level of clarity the product needs.

### 2. Run timeline UI

The user should be able to see:
- what already happened
- what is happening now
- what is waiting next

Timeline style is more understandable than repeated text blocks.

### 3. Control panel

Phase 8 needs stronger visible controls:
- pause
- resume
- stop
- retry

Cancel exists now in the narrow lane.
The broader control model still remains a real Phase 8 gap.

### 4. Single-focus mode

When a run is active, Nova should feel like:
- one main task
- one primary active surface
- supporting context below it

Not:
- everything equally loud

### 5. Checkpoint UX

Tier-3-style outcomes need clearer checkpoint surfaces such as:
- preview
- edit
- confirm
- cancel

This is especially important as Phase 8 widens toward more real operator workflows.

### 6. Failure surface

Failures should not be invisible or low-context.

The user should see:
- what failed
- why it failed
- what they can do next

For example:
- retry
- show me
- skip
- edit input

### 7. Waiting-for-input state

Phase 8 should distinguish:
- actively running
- waiting on Nova
- waiting on the user

The user should never need to infer why a run stopped moving.

This is especially important for:
- checkpoint review
- missing connector data
- missing credentials
- missing form fields
- blocked navigation or page state

## Highest-Value Exact Fixes

### 1. Kill repeated or placeholder-feeling blocks

Any repeated "continue from" or stacked low-signal copies should be:
- collapsed
- merged
- turned into one clear component

### 2. Add an Active Run panel

The top-level operator surface should clearly show:
- current task
- status
- current step
- progress
- immediate controls

### 3. Add a real run timeline component

The strongest target is a visible timeline such as:
- completed steps
- current step
- waiting step
- blocked step

### 4. Stabilize WebSocket behavior

The backlog should explicitly include:
- heartbeat/ping policy
- reconnect debounce
- single-connection guard
- stale-client protection

### 5. Add explicit checkpoint UI

Phase 8 should clearly support:
- preview
- edit
- send/confirm
- cancel

for meaningful outward-facing outcomes.

### 6. Add a persistent "Nova is doing..." strip

A small live execution strip can dramatically improve trust.

It should surface:
- current action
- waiting reason
- whether Nova is blocked or needs input

### 7. Reduce surface noise through modes

The audit recommendation is strong:
- Focus mode
- Overview mode
- History mode

That is a better product model than treating every panel as equally primary.

## Proposed UI Contract

The operator UI should converge toward three simple views.

### 1. Focus

Purpose:
- one active task
- one main progress surface
- one place to pause, stop, retry, or confirm

Should show:
- run title
- status
- current step
- progress
- checkpoint or error if present

### 2. Overview

Purpose:
- general dashboard
- what Nova can do
- what is connected
- whether anything important needs attention

Should show:
- setup state
- delivery inbox
- next useful actions
- lightweight operator summary

### 3. History

Purpose:
- confirm what happened
- compare past runs
- understand failures, cancellations, and deliveries

Should show:
- recent runs
- run outcome
- delivery destination
- failure reason
- retry path when valid

## Run-State Language Contract

Phase 8 should settle on a small state vocabulary.

Recommended core states:
- `running`
- `waiting_for_input`
- `checkpoint_ready`
- `paused`
- `cancel_requested`
- `cancelled`
- `failed`
- `completed`

Recommended product rule:
- one user-facing label
- one short explanation
- one next-action surface

Bad pattern:
- status without an obvious next step

Good pattern:
- `Waiting for your input`
- `Nova needs your email address before it can continue.`
- actions: `Add it` / `Cancel`

## Checkpoint UX Contract

Phase 8 should treat checkpoints as part of the run system, not as detached prompts.

Every checkpoint should show:
- what Nova is ready to do
- what changed or was prepared
- what happens if the user confirms
- how to edit or cancel

Minimum controls:
- `Preview`
- `Edit`
- `Confirm`
- `Cancel`

Examples:
- send this email
- submit this form
- save these changes
- continue with sign-in

## Failure UX Contract

Phase 8 failures should always answer three questions:

1. What failed?
2. Why did it fail?
3. What can I do next?

Minimum actions:
- `Retry`
- `Show details`
- `Skip`
- `Cancel`

Optional when valid:
- `Edit input`
- `Open settings`
- `Reconnect source`

## Backend Implications

This audit implies more than frontend polish.

The run model should eventually support:
- patchable active-run state updates
- explicit step arrays or timeline entries
- waiting and checkpoint states
- richer failure payloads
- delivery destination metadata
- retryable outcome metadata

It should also support:
- stable identifiers across Home, Agent, and Chat surfaces
- one source of truth for run status
- a clean mapping between active run and recent-run history

## Proof And Validation Implications

This packet should influence proof expectations too.

Future Phase 8 verification should include:
- active-run state visible on both Home and Agent
- cancelled runs clearly differentiated from failed runs
- checkpoint state can be rendered without ambiguity
- waiting-for-input state is distinguishable from silent failure
- failure surface includes a reason and next action
- WebSocket reconnect does not duplicate or corrupt active-run state

Suggested verification additions:
- dashboard tests for focus/overview/history mode behavior
- dashboard tests for checkpoint surfaces
- dashboard tests for cancelled vs failed vs completed history rendering
- websocket resilience tests for reconnect with an active run
- end-to-end manual validation for one full run, one cancellation, and one failure

## Relationship To Existing Phase-8 Documents

Read this packet alongside:
- `docs/design/Phase 8/PHASE_8_OPENCLAW_GOVERNED_EXECUTION_PLAN.md`
- `docs/design/Phase 8/NOVA_OPENCLAW_END_TO_END_EXPANSION_MASTER_TODO_2026-04-02.md`
- `docs/design/Phase 8/NOVA_GOVERNED_VISIBLE_OPERATOR_MODE_TODO_2026-04-02.md`

Interpretation:
- the governed execution plan explains the architecture
- the end-to-end expansion TODO explains the broad buildout
- the visible-operator TODO explains widening operator reach
- this audit explains the user-operability bar the product still must clear

## What This Means For Phase 8

The deepest truth in this audit is:

Nova is not blocked on:
- backend structure
- governance law
- capability abstraction

Nova is blocked on:

`turning execution into a visible, calm, controllable user experience`

That should now be read as one of the clearest remaining Phase 8 product truths.

## Recommended Planning Impact

This packet should update how the remaining Phase 8 backlog is read.

Phase 8 is not just:
- more envelopes
- more connectors
- more action breadth

It is also:
- a first-class run system
- timeline and checkpoint UX
- better task focus
- clearer failure/recovery surfaces
- lower-noise operator presentation

## Short Version

Right now Nova can still feel like:

`a powerful system showing its internals`

Phase 8 should push it toward:

`a system doing useful work clearly, visibly, and confidently for the user`

## Strongest Single Priority

If only one idea from this audit is adopted, it should be:

`introduce the fuller Run System as a first-class backend and UI concept`

That means:
- clearer run object
- clearer run timeline
- clearer run controls
- clearer checkpoint and failure UX

Everything else in this packet becomes easier once that exists.

## Practical Build Order From This Audit

The cleanest implementation order is:

1. define the first-class run object
2. add Focus-mode active-run panel
3. add timeline and waiting/checkpoint states
4. add pause/resume/retry controls
5. add explicit failure surface
6. harden WebSocket/session stability around active runs
7. then widen broader Phase 8 execution reach
