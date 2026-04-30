# Governed Desktop Runs

This folder documents the next governance upgrade track for NovaLIS: task-scoped desktop, browser, scheduled, continuous, and OpenClaw runs.

This is not implemented runtime behavior yet. It does not change the current capability registry, Governor, OpenClaw execution path, or generated runtime truth. It is an immediate implementation planning track for what NovaLIS should build next before trusting broad desktop/browser workflows.

---

## Document Map

- `DESIGN_PLAN.md` — reality-grounded architecture comparison and implementation plan.
- `CONTINUOUS_NOVA_MODEL.md` — how NovaLIS can become continuous without becoming uncontrolled.
- `WORKFLOW_EXAMPLE_ELEVENLABS_SCRIPT_LOOP.md` — concrete example for a governed ElevenLabs script-to-voice workflow.
- `README.md` — governing rules, envelope concept, safety defaults, and build order.

---

## Core Principle

> Continuous presence is not continuous authority.

NovaLIS may eventually stay active, check approved signals, prepare plans, and propose workflows, but real execution must remain task-scoped, envelope-bound, interruptible, logged, and stopped when complete.

---

## Why This Needs To Move Near-Term

NovaLIS is reaching the point where useful workflows may require operating across local apps, webpages, files, schedules, queues, and external tools.

Examples:

- OpenClaw-assisted desktop execution
- scheduled script queue checks
- voice generation in ElevenLabs or local voice tools
- video/content workflow preparation
- browser-based research and tool use
- local file organization
- small-business workflow support
- future YouTubeLIS-style production workflows

These workflows should not be added as unrestricted automation. They need a stronger execution contract first.

Audit logs alone are not enough. Logging what happened after the fact does not prevent damage. NovaLIS needs enforcement before execution, visibility during execution, and audit after execution.

---

## User-Decided Core Rule

The governing rule is:

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
11. Scheduled triggers do not equal execution approval.
12. Continuous awareness does not grant execution authority.

---

## Core Design Shift

The design should not be:

> NovaLIS has full computer access.

The safer design is:

> NovaLIS has temporary permission to complete one approved task envelope.

This preserves broad usefulness without giving unlimited authority.

---

## Continuous / Scheduled Model

NovaLIS may eventually run continuously in these ways:

- remain available locally
- check approved queues
- monitor approved schedules
- prepare plans
- draft governed run envelopes
- show readiness notifications
- request approval

NovaLIS should not silently execute medium/high-risk actions just because a timer fired.

Important rule:

> Timer trigger starts review. Approval starts execution.

Example:

```text
9:00 AM
→ Check approved script folder
→ Find 3 scripts
→ Build ElevenLabs voiceover envelope
→ Show Trust Review Card
→ Wait for approval
→ If approved, process approved scripts only
→ Save audio to approved folder
→ Produce receipt
→ Stop
```

---

## Governed Run Envelope

A governed run must be represented by an explicit envelope before execution.

Required fields:

- run id
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
Audio file downloaded, task fails, user cancels, timeout occurs, executor becomes uncertain, or scope violation is detected.
```

---

## Initial Envelope Shape

A first implementation can start with a small JSON-like structure:

```json
{
  "run_id": "generated_id",
  "intent": "generate_voiceover",
  "goal": "Generate audio for the approved script",
  "risk_level": "medium",
  "allowed_surfaces": ["browser", "elevenlabs.com", "downloads_folder"],
  "allowed_actions": ["open_url", "paste_text", "click_generate", "download_file"],
  "blocked_actions": ["purchase", "account_change", "publish", "send_message", "unrelated_browsing"],
  "required_approvals": ["start_run", "high_risk_action", "scope_expansion"],
  "stop_conditions": ["goal_complete", "timeout", "user_cancel", "scope_violation", "executor_uncertain"],
  "timeout_seconds": 600,
  "audit_level": "step_receipt"
}
```

This does not need to be perfect in the first implementation. It needs to be strict enough to prevent vague, open-ended desktop control.

---

## Risk Tiers

### Low Risk

Examples:

- Open an app
- Read visible page content
- Navigate to an approved URL
- Create a local draft file
- Check an approved queue or folder

Default behavior:

- May be allowed with lightweight confirmation depending on user settings.

### Medium Risk

Examples:

- Download files
- Upload approved files
- Generate paid-service output when no purchase is involved
- Edit local project files
- Create media assets
- Execute an approved script-to-voice loop

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

## Hard Safety Defaults

Until a stronger credential and public-action policy exists, these defaults should apply:

1. Credential entry is user-only.
2. Public publishing requires final human approval.
3. Purchases require final human approval.
4. Sending messages or emails requires final human approval.
5. Deleting files requires final human approval.
6. Installing software requires final human approval.
7. Unknown executables are blocked by default.
8. If the executor cannot confidently determine the next action is inside the approved envelope, it must pause.
9. Scheduled triggers may prepare plans, not silently execute medium/high-risk actions.
10. Continuous runs must have quiet hours, rate limits, stop conditions, and receipts.

---

## Scope Violations

A run should pause or stop if any of these happen:

- Current URL leaves the approved domain or URL pattern.
- Active app/window leaves the approved surface.
- The executor attempts a blocked action.
- The executor attempts to access files outside approved paths.
- The executor attempts to continue after the stop condition is met.
- The executor tries to escalate from read-only to write/upload/send/publish.
- The executor becomes uncertain about the page, app, file, or next step.
- The user cancels or revokes permission.
- A scheduled run tries to execute without the required approval.

---

## Required Runtime Changes

### 1. Governed Run Envelope Schema

Create a strict schema for task-scoped execution.

The schema should be machine-readable and validated before any OpenClaw or desktop action begins.

### 2. Envelope Policy Evaluator

Add a small evaluator that can decide:

- Is this envelope valid?
- What is the risk tier?
- Does this require approval?
- Is the next action allowed?
- Should execution pause or stop?

### 3. Scheduled Trigger / Approved Signal Model

Add a way to define approved queues, folders, schedules, and read-only checks.

A trigger should be able to prepare a run envelope without automatically granting execution authority.

### 4. OpenClaw Governed Run Mode

OpenClaw should not receive vague instructions like "do this task."

It should receive a constrained envelope with allowed actions, blocked actions, and stop conditions.

### 5. Scope Monitor

NovaLIS needs a way to detect whether a run is still inside scope.

Possible checks:

- current URL/domain
- active window title
- file path boundaries
- action type
- step number
- elapsed time
- attempted sensitive action

### 6. Stop Conditions

Runs must stop automatically when:

- the goal is completed
- the task fails
- the user cancels
- timeout is reached
- a blocked action is attempted
- the executor becomes uncertain
- the active surface moves outside scope

### 7. Trust Review Card

Before execution, the user should see a clear review card:

- intent
- planned steps
- allowed surfaces
- blocked actions
- risk level
- approvals required
- stop condition
- timeout

This makes governance visible instead of hidden.

### 8. Step Ledger / Run Receipt

Every governed run should produce an audit receipt:

- requested task
- approved envelope
- start time
- steps attempted
- approvals requested
- blocked actions
- result
- stop reason

### 9. Pause / Stop / Revoke Controls

The user must be able to interrupt a governed run.

A UI should support:

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

This should become the general governed desktop/browser executor lane.

Scheduled execution should be treated as a trigger model layered on top of governed envelopes, not as a separate bypass.

Future workflows like YouTubeLIS, Shopify operations, email drafting, research workflows, local file organization, or ElevenLabs voice workflows could use this foundation later.

---

## Immediate Build Order

1. Keep this folder isolated from runtime truth until implementation begins.
2. Add `ENVELOPE_SCHEMA.md` with exact fields, states, and validation rules.
3. Add `TEST_PLAN.md` with adversarial and normal workflow cases.
4. Implement an envelope schema object in code.
5. Implement a small envelope policy evaluator.
6. Add a non-executing dry-run mode.
7. Add scheduled trigger / approved signal design.
8. Add Trust Review Card rendering for envelopes.
9. Add ledger receipt structure.
10. Add stop/pause/revoke state model.
11. Only then connect a harmless OpenClaw/browser run.
12. Test harmless tasks first.
13. Test medium-risk tasks only after blocking, pausing, and receipts are reliable.

---

## Minimum First Workflow

The first workflow should be intentionally boring and safe.

Example:

```text
Task:
Open an approved website, read visible page title, return summary, stop.
```

Allowed:

- open one approved URL
- read visible content
- return summary

Blocked:

- clicking unrelated links
- logging in
- downloading
- uploading
- sending
- purchasing
- continuing after summary

This gives NovaLIS a safe way to validate the control loop before higher-risk workflows.

---

## Relationship to Current NovaLIS Governance

This model must preserve the existing NovaLIS doctrine:

- Intelligence is not authority.
- Reasoning may propose actions.
- Execution authority stays bounded, visible, and reviewable.
- Real actions must pass through governed execution paths.
- No hidden background execution.
- No uncontrolled autonomy.

This document does not override generated runtime truth documents.

---

## What This Improves

This governance change would make NovaLIS safer and more useful by allowing broader workflows without granting broad authority.

It improves:

- desktop automation safety
- browser automation safety
- OpenClaw containment
- continuous Nova readiness
- scheduled workflow readiness
- user trust
- auditability
- workflow readiness
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
- timer-triggered medium/high-risk execution without approved policy

---

## Promotion Criteria

This should not be described as current runtime behavior until:

- envelope schema exists in code
- policy evaluator exists in code
- scheduled trigger behavior is defined if scheduling is included
- tests cover normal and adversarial cases
- Trust Review Card or equivalent approval surface exists
- ledger receipts exist
- stop/pause/revoke controls exist
- OpenClaw adapter respects envelopes
- generated runtime truth reflects the implementation

---

## Current Status

Immediate implementation planning track.

Not implemented yet.

No runtime claim should say NovaLIS currently supports governed desktop runs until this is built, tested, and represented in generated runtime truth.
