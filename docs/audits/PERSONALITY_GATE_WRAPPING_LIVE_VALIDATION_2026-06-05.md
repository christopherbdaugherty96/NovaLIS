# Personality Gate Wrapping Live Validation - 2026-06-05

Status: COMPLETE

## Original Drift

Post-wiring live validation found UX coverage drift in Cap 22 and Cap 64 confirmation prompts.

Personality gate wrapping existed and was used by the GovernorMediator confirmation path, but not every live confirmation path showed the same personality-wrapped wording.

The deterministic live prompts still used older confirmation language for some Cap 22/64 flows.

## Root Cause

The live WebSocket route has more than one confirmation path:

- GovernorMediator-routed Cap 22/64 confirmations.
- Deterministic local helper paths, including local folder open handling.

The personality wrapper was present in the mediated path, while deterministic helper output still constructed legacy confirmation text directly.

## Patch

The patch:

- Added a shared `_personality_gate_message()` helper in `nova_backend/src/brain_server.py`.
- Updated deterministic local-open confirmation output to use the same personality gate wrapper.
- Injected the shared helper into `run_websocket_session()` so mediated Cap 22/64 gates and deterministic gates use the same wrapper source.
- Updated live simulation confirmation markers for the personality-wrapped prompt shape.
- Updated stale approval recovery assertions to check governance identity rather than retired literal text.

The patch did not change:

- Capability IDs.
- Executor count.
- GovernorMediator routing.
- Pending confirmation state shape.
- Yes/no parser behavior.
- Ledger semantics.
- Execution paths.

## Tests

Focused regression coverage added:

- `test_cap22_deterministic_prompt_uses_personality_gate_wrapper`
- `test_cap64_deterministic_prompt_uses_personality_gate_wrapper`
- `test_cap22_deterministic_yes_still_executes_same_path`
- `test_cap64_deterministic_yes_still_executes_same_path`
- `test_cap22_deterministic_no_still_cancels`
- `test_cap64_deterministic_no_still_cancels`
- `test_recipientless_cap64_clarification_does_not_create_pending_confirm`
- `test_bare_yes_after_recipientless_clarification_does_not_execute`

Validation results:

```text
Focused deterministic gate tests: 8 passed
Approval/personality group: 37 passed
Fast suite: 3025 passed, 153 deselected
Live user simulation: 33/33 passed
Errors: 0
Timeouts: 0
```

The first fast-suite attempt timed out while scanning the live runtime ledger. The passing fast-suite run used an isolated `NOVA_RUNTIME_DIR`.

## Live Simulation Result

Live user simulation passed on a patched validation server:

```text
Turns: 33
Passes: 33/33
Responses received: 33/33
Errors: 0
Timeouts: 0
Confirmation prompts: 8
Denial/cancel replies: 5
```

Cap 22 and Cap 64 confirmations now consistently show personality-wrapped governance identity:

```text
[open_file_folder · Cap 22 · local_write]
[send_email_draft · Cap 64 · local_write]
```

## Governance Result

Governance invariant preserved:

```text
Personality may increase initiative.
Personality may never increase authority.
```

Confirmed:

- `yes` still executes only from pending confirmation state.
- `no` still cancels pending confirmation.
- A follow-up command cancels pending confirmation before continuing.
- Recipientless Cap 64 clarification does not create pending confirmation.
- Bare `yes` after recipientless clarification does not execute.
- No new capability or executor was added.
- Capability count remains 27.
- Executor count remains 22.

## Remaining UX Notes

- Trust Center live output includes raw trust state plus "by design" explanation text.
- Morning brief returned "Nothing to report right now" in the validation runtime state.
- Voice Cap 64 confirmation remained safe: a follow-up command cancelled the pending action rather than implying approval.

## Next Action

Resume live validation for TrustPresenter, ProactiveBriefing, and VoicePersonality surfaces. Treat future findings as UX validation issues unless routing, approval, ledger, receipt, capability, or executor behavior changes.
