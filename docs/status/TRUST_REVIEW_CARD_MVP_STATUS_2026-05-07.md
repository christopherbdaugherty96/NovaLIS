# Trust Review Card MVP Status - 2026-05-07

Status: implementation proof / review required

This is a human-maintained status note, not generated runtime truth.

## Purpose

The Trust Review Card MVP makes Nova's boundedness visible in chat as a deterministic non-action receipt surface.

Core principle:

```text
derive, don't invent
```

The card is a display layer over existing request-understanding/review-card state. It is not a planner, router, executor, workflow engine, reasoning trace, or LLM-generated trust narration surface.

## What It Displays

When an existing `request_understanding_review_card` payload is present, the chat renderer can show:

- Understood
- Status
- Authorized
- Needs confirmation
- Boundary
- Why no action happened
- Evidence

Fields are derived from the existing immutable request-understanding review-card payload. Missing fields are omitted or rendered as honest absence.

## What It Does Not Do

The card does not:

- dispatch actions
- authorize actions
- accept confirmations
- call GovernorMediator
- invoke capabilities
- call OpenClaw
- open browser/computer-use paths
- mutate state from rendering
- show chain-of-thought or private reasoning
- create workflow suggestions or action buttons

## Implementation Boundary

This MVP propagates the existing non-authorizing review-card payload from general-chat fallback results into the chat WebSocket payload and renders it in the dashboard as a read-only card.

The existing backend `RequestUnderstandingReviewCard` invariants remain authoritative:

- `authority_effect = "none"`
- `execution_performed = false`
- `authorization_granted = false`
- `private_reasoning_exposed = false`

## Verification

Focused verification recorded:

```text
20 passed
node --check passed
```

Covered checks include:

- review card payload remains non-authorizing
- general-chat result carries display-only review-card data
- chat payload can include `trust_review_card` without suggested actions
- dashboard renderer has no action buttons
- dashboard renderer has no event listeners
- dashboard renderer does not call WebSocket dispatch helpers
- dashboard renderer does not call navigation or injected-command helpers
- partial/missing card data is guarded

Verification friction:

- A wider adjacent dashboard pytest slice was attempted but did not complete because the local Python process hit an import-time `MemoryError` before collecting tests. This is recorded as local verification friction, not a passing result and not a runtime authority claim.

## Boundaries Preserved

No new capability was added.

No execution authority was added.

No OpenClaw expansion was added.

No browser/computer-use expansion was added.

No external write or autonomous workflow path was added.
