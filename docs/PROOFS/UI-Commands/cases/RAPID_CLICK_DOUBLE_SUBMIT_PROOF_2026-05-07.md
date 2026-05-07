# Rapid Click / Double Submit Proof - 2026-05-07

Status: contract pass / screenshot proof blocked

## Purpose

This proof records deterministic guard coverage for repeated chat submits, duplicate assistant events, stale manual turns, and confirmation isolation.

This proof does not add a capability, does not expand OpenClaw, does not add browser/computer-use, and does not authorize execution.

## What Was Tested

- Chat send is blocked while `waitingForAssistant` or `manualTurnInFlight` is active.
- Send button binding is single-use through `sendBtn.dataset.bound`.
- Manual turns carry a turn id.
- Widget hydration pauses during manual turns.
- Repeated assistant text within a manual turn is deduped.
- Stale pending website confirmations do not swallow unrelated commands.
- Confirmation resolution accepts only explicit yes/no/cancel style responses.

## Expected Behavior

- No duplicate unintended action.
- No hidden execution.
- No misleading success state.
- No confirmation token reuse bug.
- No stuck pending state.
- Unrelated commands should not be swallowed by a stale pending confirmation.

## Evidence

- `../evidence/2026-05-07/raw/ui_malformed_rapid_click_contract.json`
- `../evidence/2026-05-07/raw/ui_malformed_rapid_click_pytest_results.txt`
- `../evidence/2026-05-07/raw/ui_blocker_fix_probe.json`

## Result

Pass for the covered contract layer.

The focused dashboard/session proof suite passed with:

```text
25 passed
```

Confirmed guards:

- overlapping manual chat sends are blocked with a visible loading hint
- send button listeners are bound once
- repeated assistant text for the same manual turn is deduped
- widget hydration pauses while a manual turn is active
- stale website confirmation can be canceled before handling unrelated commands

## Remaining Gap

This proof does not include direct browser click automation, visual screenshots, or high-frequency DOM event replay. Browser Use screenshot/click-path capture remains blocked by runtime asset setup.
