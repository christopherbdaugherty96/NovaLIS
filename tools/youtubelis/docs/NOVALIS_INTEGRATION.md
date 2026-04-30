# NovaLIS Integration Model (YouTubeLIS)

This document defines how YouTubeLIS should integrate with NovaLIS as a governed content operating system.

The core idea is simple: Nova can help with thinking, structure, drafting, validation, and production planning, while the user keeps authority over publishing, accounts, purchases, and public claims.

---

## System Model

YouTubeLIS should treat content creation as a governed workflow, not an uncontrolled automation loop.

```text
Conversation
-> Brain
-> Run System
-> Governor
-> Executor
-> Ledger
```

For YouTube work, that becomes:

```text
Idea
-> Task Understanding
-> Planning Run
-> Content Build
-> Validation
-> Production Plan
-> Review Stop
-> Optional governed execution later
-> Iteration
```

Core invariant:

> No real-world action without a run, a declared envelope, and the required approval path.

---

## Video Runs

Each video should become a run with explicit state.

```text
Run: YouTube - <topic>
Status: planning | waiting_for_approval | running | paused | completed
Current step: <current step>
Next step: <next step>
Envelope: allowed / blocked / limits
Stop condition: explicit delivery boundary
```

A run is the unit of inspectable work. It prevents YouTubeLIS from becoming a vague chat thread or an open-ended automation request.

---

## Canonical Planning Run Template

A standard planning run should produce these artifacts in order:

1. Define the angle and audience
2. Craft the hook
3. Build the outline
4. Expand to script
5. Validate claims and flow
6. Plan production assets and editing
7. Package title and thumbnail variants
8. Stop for user review

Example stop condition:

```text
Script, scene plan, asset list, editing notes, and 3 title/thumbnail directions delivered. No upload, publishing, account access, or external execution.
```

---

## Task Understanding Object

Every non-trivial request should be converted into a Task Understanding Object before deeper work begins.

```text
Goal
Context used
Constraints
Assumptions
Confidence
Clarification needed
```

Clarifying questions should be used only when the answer materially changes the outcome. The system should reduce friction without removing rigor.

---

## Content Build Artifacts

NovaLIS can help produce repeatable, inspectable artifacts:

- Hook options
- 5-7 beat outline
- Time-coded scene plan
- Script draft
- Script improvement pass
- Claim and freshness review
- Asset list
- Editing plan
- Title and thumbnail variants

These artifacts make a video execution-ready without letting the system execute account or publishing actions on its own.

---

## Validation Layer

The validation pass should identify:

- Weak points
- Stronger angles
- Missing evidence
- Outdated examples
- Unsupported claims
- Speculation presented too strongly
- Better proof points or visuals

Every major claim should be framed as one of:

```text
Verified
Supported but uncertain
Opinion
Speculation
Unknown
```

---

## Task Envelope

Before any real action, the run must declare a task envelope.

```text
Allowed: planning, drafting, suggestions, review artifacts
Blocked: upload, publish, account changes, purchases, automation loops
Environment: chat by default
Step limits: explicit
Approval level: none for planning, required for execution
Stop condition: explicit
Failure behavior: pause and ask
```

Memory can inform choices, but memory never grants permission.

---

## Optional Governed Execution

Execution is future-facing and must remain governed.

Possible future execution actions:

- Export a script
- Prepare an upload draft
- Generate captions
- Open an approved tool
- Download an approved asset
- Create a local file

Execution path:

```text
Run
-> Governor
-> Capability
-> ExecuteBoundary
-> NetworkMediator if needed
-> Ledger receipt
```

No execution path should bypass NovaLIS governance.

---

## Hard Boundaries

YouTubeLIS must not perform these actions without explicit user approval and the required governance path:

- Auto-uploading
- Auto-publishing
- Auto-monetization changes
- Background loops
- Account-write actions
- Purchases
- Deletions
- Public claims represented as factual without review

The system may become more intelligent, but authority stays bounded.

---

## Modes of Operation

### Simple Task Mode

Use for one-pass requests such as title ideas, a short hook, or a quick outline.

### Planning Run

Use for multi-step work that should remain inspectable, stateful, and reviewable.

### Execution Run

Future mode only. Requires explicit approval, governed execution, and ledgered results.

---

## Current Implementation Status

This repository is still documentation and workflow design. It should not claim to be a complete automated YouTube production system.

Current intended baseline:

```text
Task Understanding: planning-only
Task Envelope: planning-only
Simple Task Mode: allowed
Planning Run: target workflow model
Execution: not implemented in this repo
Publishing: manual only
```

Do not claim these are fully integrated until the implementation exists and is verified against NovaLIS runtime truth.

---

## Not Live Yet

The following should be treated as planned or future work unless verified in code:

- Persistent runs
- Co-work page UI
- Governor routing from YouTubeLIS runs
- Execution integration
- OpenClaw usage
- Background or scheduled loops
- Upload/publish/account automation

---

## Highest-ROI Build Order

1. Stabilize the planning-only brain/run slice
2. Show the active planning run in chat
3. Add read-only run inspection commands: show, list, pause, cancel
4. Add persistence only after the in-memory model is stable
5. Add a Co-Work page shell
6. Add approval UI and trust receipts
7. Introduce governed execution only after the planning system is reliable

---

## One-Line Summary

YouTubeLIS turns YouTube creation from ad-hoc creativity into a governed, repeatable content system: planning is rich, execution is controlled, and improvement is continuous.
