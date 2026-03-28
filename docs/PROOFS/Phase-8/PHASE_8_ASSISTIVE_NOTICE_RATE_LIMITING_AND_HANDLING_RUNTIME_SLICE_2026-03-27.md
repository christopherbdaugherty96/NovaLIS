# Phase 8 Assistive Notice Rate Limiting and Handling Runtime Slice
Date: 2026-03-27
Status: Landed
Scope: Mode-specific assistive behavior, cooldowns, and session-scoped handled-state controls

## What Landed
- mode-specific assistive notice filtering in `nova_backend/src/working_context/assistive_noticing.py`
- cooldown-based auto-surface suppression so repeated notices do not reappear on every refresh
- session-scoped dismiss and resolve handling for surfaced assistive notices
- websocket command handling for:
  - `dismiss assistive notice <id>`
  - `resolve assistive notice <id>`
- UI controls on assistive notice cards for:
  - `Dismiss`
  - `Mark resolved`
- additional ledger taxonomy for assistive notice dismissal and resolution

## What The Current Slice Does
- keeps `Silent`, `Suggestive`, `Workflow Assist`, and `High Awareness` meaningfully different
- suppresses repeated automatic resurfacing until the cooldown window passes
- keeps handled notices hidden for the current continuity window unless the underlying condition changes
- allows explicit `assistive notices` review to bypass cooldown so the user can still inspect the current state
- keeps the whole layer bounded to notice, ask, then assist

## What It Does Not Do
- no silent action taking
- no hidden durable memory writes
- no manipulative nudge loop
- no cross-session assistive-profile building
- no policy-bound automatic support actions yet

## Validation
- focused Phase-8 assistive unit tests passed
- focused websocket assistive command tests passed
- focused dashboard static contract tests passed
- backend compile checks passed
- frontend mirror sync and syntax checks passed

## Interpretation
This slice makes assistive noticing calmer and more usable.

It should be read as proof that:
- the layer is now less repetitive
- the user can explicitly handle surfaced notices
- settings modes now have clearer runtime effect

It should not be read as proof that broad helpfulness or autonomous assist behavior is live.
