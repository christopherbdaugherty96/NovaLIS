# Phase 4 Runtime Truth

This document records current runtime-reachable execution authority for Phase 4.

## Live governed capabilities

- `16` — `governed_web_search` (enabled)
- `17` — `open_website` (enabled)
- `18` — `speak_text` (enabled)

## Declared but disabled

- `19` — `volume_up_down`
- `20` — `media_play_pause`
- `21` — `brightness_control`
- `22` — `open_file_folder`
- `32` — `os_diagnostics`
- `48` — `multi_source_reporting`

## Runtime invariants

- Single authority spine: all actions execute only through Governor.
- Conversation modules are non-authorizing and cannot create `ActionRequest`.
- No autonomous/background execution loop is introduced.
- No persistent cognition memory is introduced by conversation staging.
- ExecuteBoundary and SingleActionQueue remain active for governed calls.


## Risk-level note

- `risk_level: "confirm"` is retained as a policy-confirmation marker in the current registry schema.
- It denotes explicit confirmation sensitivity and is not interpreted as a numeric risk tier.
