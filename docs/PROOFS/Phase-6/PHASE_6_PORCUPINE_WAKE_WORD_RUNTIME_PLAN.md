# PHASE_6_PORCUPINE_WAKE_WORD_RUNTIME_PLAN
Updated: 2026-03-13
Status: Planned next step only. Not implemented in runtime.
Classification: Governance-safe implementation plan

## Purpose
This document describes the next planned step for adding a local wake-word gate to Nova using Picovoice Porcupine.

The goal is to improve voice usability without changing Nova's authority boundaries.

This step must preserve the existing execution path:

`User -> brain_server -> GovernorMediator -> Governor -> ExecuteBoundary -> Executor`

The wake-word layer must remain outside the authority path.
It may wake Nova.
It may not act as Nova.

## Why This Exists
Nova already has:
- typed input
- push-to-talk speech transcription
- text-to-speech
- request-time screen understanding

What it does not yet have as active runtime truth is a wake-word entrypoint.

The purpose of this plan is to define the safest first step for adding that capability without drifting into hidden autonomy.

## Why Porcupine
Picovoice Porcupine is a dedicated wake-word engine.

That makes it a stronger fit for this job than trying to force the general STT stack to behave like a wake-word detector.

Recommended initial phrase:
- `Hey Nova`

Possible future option:
- a custom `.ppn` model for a branded wake phrase

## Core Architectural Rule
Wake word may wake Nova.
It may not act as Nova.

Allowed behavior:
- detect the wake phrase
- emit a `wake_detected` event
- open a short command-listening window
- hand off spoken command audio to the existing STT path

Forbidden behavior:
- direct capability execution
- bypassing `GovernorMediator`
- background reasoning
- persistent audio logging by default
- chaining multiple actions from wake detection alone

## Safe Integration Shape

```text
Microphone
-> Porcupine Wake Listener
-> wake_detected
-> short STT command window
-> brain_server
-> GovernorMediator
-> Governor
-> ExecuteBoundary
-> Executor
```

## Non-Negotiable Boundary
The wake-word service must be non-authorizing.

That means:
- it may emit events
- it may arm a short listening window
- it may not decide intent
- it may not call capabilities
- it may not talk directly to executors

## Suggested Implementation Slice 1
Goal: add a local wake-word gate without changing Nova's current authority model.

### Suggested new module
- `nova_backend/src/voice/wake_word_service.py`

Suggested responsibilities:
- initialize Porcupine
- open microphone stream
- process PCM frames
- detect wake phrase
- emit callback or event only
- expose `start()`, `stop()`, and `is_enabled()` behavior

### Suggested config / env vars
- `NOVA_WAKE_WORD_ENABLED=false`
- `NOVA_PORCUPINE_ACCESS_KEY=...`
- `NOVA_PORCUPINE_KEYWORD_PATH=models/porcupine/hey_nova.ppn`
- `NOVA_WAKE_COMMAND_WINDOW_SECONDS=6`
- `NOVA_WAKE_WORD_COOLDOWN_SECONDS=2`

Suggested behavior:
- disabled by default
- fail closed if key or model is missing
- manual voice still works if wake word is unavailable

### Suggested event path
Suggested websocket or UI event:
- `wake_detected`

Example payload:
```json
{
  "type": "wake_detected",
  "source": "porcupine",
  "window_seconds": 6
}
```

This event should only inform UI and session state.
It must not trigger capability execution.

## Suggested `brain_server.py` Integration
The safest integration pattern is:
- keep the current STT path intact
- accept wake-word events from the wake service
- set session state such as:
  - `wake_window_open = true`
  - `wake_window_expires_at = ...`
- only accept microphone command transcription during that short window
- auto-close the window after timeout or first completed command

This preserves the current mediated authority chain.

## Suggested UI Behavior
The UI may:
- show a small `Wake: On` style indicator
- briefly show `Listening...` after wake detection
- make the wake-listening window visible to the user

The UI should not:
- auto-run commands from wake detection alone
- make the orb behave like a semantic authority indicator
- hide wake state from the user

## Safety Constraints
1. Wake service must not call executors.
2. Wake service must not call capabilities directly.
3. Wake service must not interpret user intent.
4. Wake service must not persist audio by default.
5. Wake detection must be easy to disable globally.
6. One wake event should open one bounded command window.
7. Timeout should be short and deterministic.
8. Failure should fall back to manual voice activation rather than partial unsafe behavior.

## Suggested Repo Additions
Suggested files:
- `nova_backend/src/voice/wake_word_service.py`
- `nova_backend/src/voice/wake_word_config.py`
- `nova_backend/tests/voice/test_wake_word_service.py`
- `nova_backend/tests/voice/test_wake_word_window.py`
- `nova_backend/tests/governance/test_wake_word_non_authorizing.py`

Optional future docs:
- a future wake-word runtime slice in the `docs/PROOFS/Phase-6/` folder
  - only after implementation actually lands

## Suggested Test Targets

### Functional
- Porcupine service initializes when enabled
- service fails closed when access key is missing
- service fails closed when keyword model is missing
- wake detection emits only `wake_detected`
- command window opens and closes deterministically

### Governance
- no direct capability execution from wake-word service
- no Governor bypass
- no background command execution
- no action without post-wake user speech
- no multi-step chain from wake detection alone

### UX
- UI receives `wake_detected`
- UI can show subtle listening state
- manual voice remains usable when wake word is disabled

## Recommended First Commit Scope
Keep the first implementation commit very small.

Recommended scope:
1. add Porcupine service skeleton
2. add config/env handling
3. emit `wake_detected`
4. open bounded STT window
5. add non-authorizing governance tests

Do not include in the first commit:
- custom wake-word training flow
- personalization
- multi-command sessions
- autonomous listening behaviors
- execution shortcuts

## Recommended Commit Name
`feat(phase6): add non-authorizing porcupine wake-word gate`

## Plain-English Summary
This step gives Nova a wake word without turning wake detection into an authority surface.

Porcupine should only open a short listening window.
All actual commands must still flow through:
- STT
- `brain_server`
- `GovernorMediator`
- `Governor`
- `ExecuteBoundary`

That is what keeps the feature aligned with Nova's governance model.
