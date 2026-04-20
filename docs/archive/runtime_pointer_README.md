# Runtime Docs Pointer

Canonical runtime docs currently live in `docs/current_runtime/`.

Authoritative files:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`

This folder exists as a stable naming alias for future migration.

## Runtime Concurrency Model

- The runtime intentionally uses one shared governor instance per process (`RUNTIME_GOVERNOR`).
- All governed actions pass through a single `SingleActionQueue` execution surface.
- Result: only one governed execution runs at a time per runtime process, even across multiple UI sessions.
- This is a deliberate safety-first, single-operator default for the current phase.
