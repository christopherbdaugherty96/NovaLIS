# Governed Desktop Runs

This folder documents a possible future governance upgrade for NovaLIS.

It is not implemented runtime behavior yet. It does not change the current capability registry, Governor, OpenClaw execution path, or runtime truth. It is a planning document for how NovaLIS would need to evolve before broad desktop/browser/OpenClaw workflows should be trusted.

---

## Why This Exists

Future workflows such as YouTubeLIS, voice generation, editing support, browser operation, file organization, or app orchestration may require NovaLIS to operate across desktop surfaces and webpages.

That kind of power is only acceptable if it remains governed.

Audit logs alone are not enough. Logging what happened after the fact does not prevent damage. NovaLIS needs enforcement before execution, visibility during execution, and audit after execution.

---

## User-Decided Core Rules

The governing rule should be simple:

> NovaLIS may not act unless permission is given, may not leave the approved scope, and must stop when the task is done.

Expanded rules:

1. No action without permission.
2. Permission is task-scoped, not global.
3. NovaLIS may not leave the approved task scope.
4. NovaLIS may not continue after the approved task is complete.
5. NovaLIS may not perform extra helpful actions unless approved.
6. NovaLIS must pause when uncertain.
7. NovaLIS must pause before sensitive actions.
8. NovaLIS must stop on completion, failure, timeout, user cancellation, or scope violation.
9. Every governed run must be logged.
10. The user must always be able to stop or revoke a run.

---

## Core Design Shift

The future design should not be:

> NovaLIS has full computer access.

The safer design is:

> NovaLIS has temporary permission to complete one approved task envelope.

This preserves broad usefulness without giving unlimited authority.

---

## Governed Run Envelope

A governed run should be represented by an explicit envelope before execution.

Required fields:

- intent
- user goal
- approved steps
- allowed surfaces
- allowed actions
- blocked actions
- required approvals
- risk level
- stop condition
- timeout
- audit requirements

Example:

```text
Intent:
Generate voiceover for an approved script.

Allowed surfaces:
- Browser
- ElevenLabs website
- Downloads folder

Allowed actions:
- Open ElevenLabs
- Paste approved script
- Generate audio
- Download audio file

Blocked actions:
- Purchases
- Account changes
- Publishing
- Sending messages
- Uploading unrelated files
- Browsing unrelated sites
- Continuing after download

Stop condition:
Audio file downloaded, task fails, user cancels, timeout occurs, or scope violation is detected.
```

---

## Risk Tiers

### Low Risk

Examples:

- Open an app
- Read visible page content
- Navigate to an approved URL
- Create a local draft file

Default behavior:

- May be allowed with lightweight confirmation depending on user settings.

### Medium Risk

Examples:

- Download files
- Upload approved files
- Generate paid-service output when no purchase is involved
- Edit local project files
- Create media assets

Default behavior:

- Requires explicit approval of the envelope.

### High Risk

Examples:

- Purchases
- Deleting files
- Sending email or messages
- Publishing public content
- Changing account settings
- Entering credentials
- Installing software
- Running unknown executables

Default behavior:

- Requires fresh explicit approval at the exact moment of action.
- Should not be bundled invisibly inside a long chain.

---

## Required Runtime Changes

Before this becomes real runtime behavior, NovaLIS would need several upgrades.

### 1. Governed Run Envelope Schema

Create a strict schema for task-scoped execution.

The schema should be machine-readable and validated before any OpenClaw or desktop action begins.

### 2. OpenClaw Governed Run Mode

OpenClaw should not receive vague instructions like "do this task."

It should receive a constrained envelope with allowed actions, blocked actions, and stop conditions.

### 3. Scope Monitor

NovaLIS needs a way to detect whether a run is still inside scope.

Possible checks:

- current URL/domain
- active window title
- file path boundaries
- action type
- step number
- elapsed time
- attempted sensitive action

### 4. Stop Conditions

Runs must stop automatically when:

- the goal is completed
- the task fails
- the user cancels
- timeout is reached
- a blocked action is attempted
- the executor becomes uncertain
- the active surface moves outside scope

### 5. Trust Review Card

Before execution, the user should see a clear review card:

- intent
- planned steps
- allowed surfaces
- blocked actions
- risk level
- approval required
- stop condition

This makes governance visible instead of hidden.

### 6. Step Ledger / Run Receipt

Every governed run should produce an audit receipt:

- requested task
- approved envelope
- start time
- steps attempted
- approvals requested
- blocked actions
- result
- stop reason

### 7. Pause / Stop / Revoke Controls

The user must be able to interrupt a governed run.

A future UI should support:

- pause
- resume
- stop
- revoke permission
- view current step

---

## Capability Direction

The next major capability should not be many content-specific actions.

A better first foundation is:

```text
openclaw_governed_run
```

This would become the general governed desktop/browser executor lane.

Future capabilities like YouTubeLIS, Shopify workflows, email drafting, research workflows, or local file organization could use this foundation later.

---

## Relationship to Current NovaLIS Governance

This proposed model should preserve the existing NovaLIS doctrine:

- Intelligence is not authority.
- Reasoning may propose actions.
- Execution authority stays bounded, visible, and reviewable.
- Real actions must pass through governed execution paths.
- No hidden background execution.
- No uncontrolled autonomy.

This document should not override generated runtime truth documents.

---

## What This Improves

This governance change would make NovaLIS safer and more useful by allowing broader workflows without granting broad authority.

It improves:

- desktop automation safety
- browser automation safety
- OpenClaw containment
- user trust
- auditability
- future workflow readiness
- YouTubeLIS readiness
- small-business workflow readiness

---

## What This Does Not Allow

This model does not allow:

- full unrestricted computer access
- hidden background execution
- autonomous purchasing
- autonomous publishing
- uncontrolled app traversal
- credential handling without explicit approval
- indefinite continuation after task completion

---

## Recommended Build Order

1. Keep this as a future planning document.
2. Define the envelope schema.
3. Add a small policy evaluator for envelopes.
4. Add a Trust Review Card UI.
5. Add stop/pause/revoke controls.
6. Add OpenClaw governed run adapter.
7. Add ledger receipt output.
8. Test with harmless desktop/browser tasks.
9. Only then test medium-risk workflows like ElevenLabs voice generation.
10. Only after that consider YouTubeLIS-style workflows.

---

## Current Status

Planning only.

Not implemented.

No runtime claim should say NovaLIS currently supports governed desktop runs until this is built, tested, and represented in generated runtime truth.
