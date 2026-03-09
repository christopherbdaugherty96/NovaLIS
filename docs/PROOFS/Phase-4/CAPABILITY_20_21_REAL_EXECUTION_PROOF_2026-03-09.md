# Capability 20/21 Real Execution Proof
Date: 2026-03-09
Commit: 3bd772e
Scope: Proof that capabilities 20 (`media_play_pause`) and 21 (`brightness_control`) are no longer message-only stubs.

## Previous Mismatch (Resolved)
Older audit/proof artifacts described cap 20/21 as message-only paths.
Current runtime code routes both through concrete OS control methods in `SystemControlExecutor`.

## Capability 20 (`media_play_pause`) Evidence
Registry enablement:
- `nova_backend/src/config/registry.json` -> ID 20 `enabled: true`

Invocation mapping:
- `governor_mediator.py` maps `play | pause | resume` to capability 20.

Execution route:
- `governor.py` dispatches cap 20 to `MediaExecutor`.
- `media_executor.py` calls `SystemControlExecutor.control_media(action)`.

OS action boundary:
- `system_control_executor.py` implements `control_media(...)` with platform branches:
  - Linux: `playerctl`
  - macOS: AppleScript/media key fallback
  - Windows: media virtual key event

## Capability 21 (`brightness_control`) Evidence
Registry enablement:
- `nova_backend/src/config/registry.json` -> ID 21 `enabled: true`

Invocation mapping:
- `governor_mediator.py` maps brightness commands (`up/down/set`) to capability 21.

Execution route:
- `governor.py` dispatches cap 21 to `BrightnessExecutor`.
- `brightness_executor.py` calls `SystemControlExecutor.set_brightness(...)`.

OS action boundary:
- `system_control_executor.py` implements `set_brightness(...)` with platform branches:
  - Linux: `brightnessctl`
  - macOS: AppleScript key-code path
  - Windows: WMI brightness set path

## Fail-Closed Behavior
Unsupported platform/tooling paths return `False` and produce non-authorizing request-status responses (for example, `... requested.`), rather than fabricating success with side effects.

## Test Evidence
- `tests/executors/test_local_control_executors.py`
- `tests/test_governor_mediator_phase4_capabilities.py`
- `tests/test_system_control_executor.py`
- Included in full suite pass: `211 passed`

## Conclusion
Capabilities 20 and 21 are runtime-enabled and wired to concrete local OS control surfaces via the governed execution spine.
