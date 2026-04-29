# Brain Trace UI Spec

The Brain Trace UI makes Nova's operational reasoning visible without exposing hidden chain-of-thought.

It should show structured state, not private reasoning.

## Pre-Execution View: Dry Run

Before higher-authority or multi-step work, Nova can show a plan preview.

Fields:

- user task
- clarification status
- proposed steps
- environments to enter
- capability contracts involved
- confirmation points
- expected receipts
- fallback ladder
- what Nova will not do

Example:

```text
Plan preview:
1. Use Cap 16 governed web search.
   Proof: source URLs.
2. Summarize candidates.
   Proof: cited summary.
3. Prepare Cap 64 email draft.
   Confirmation required before opening local mail client.
   Proof: EMAIL_DRAFT_CREATED if opened.

Nova will not send email.
```

## Execution View: Governor Dashboard

Represent the brain loop as visible states:

```text
Task Intake → Clarifier → Environment Reasoner → Authority Question → Plan Preview → Governor Gate → Execution → Proof
```

If Nova pauses at authority, the UI should show `CONFIRMATION REQUIRED` instead of hiding the reason.

If blocked, the UI should show the blocker and fallback ladder.

## Post-Execution View: Proof Package

After a governed action, show:

- receipt ID/event
- capability used
- environment entered
- confirmation state
- source URLs or screenshots if applicable
- state change summary
- next safe step

## Receipts As Journaling

Receipts should also support learning and reflection.

The trace can show:

- what memory was used
- what context was pruned or ignored
- what proof was created
- whether the user rejected or accepted the plan

This should be operational metadata, not hidden chain-of-thought.