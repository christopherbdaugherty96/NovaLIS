# Browser Use Visual Capture Recovery - 2026-05-08

Status: blocked / setup-required

This is proof-infrastructure evidence, not runtime authority.

## Purpose

This pass attempted to recover screenshot/click-path proof capture for existing Nova UI surfaces.

The question was:

```text
Can Nova reliably capture visual proof for existing UI behavior?
```

The question was not:

```text
Can Nova automate a browser?
```

## Scope

Allowed in this pass:

- Browser Use screenshot capture
- click-path proof capture
- visual artifact saving
- proof classification
- documentation of failure if capture remained unavailable

Not allowed in this pass:

- new Nova browser/computer-use capability
- autonomous browsing
- browser execution path in Nova
- workflow orchestration
- OpenClaw expansion
- external writes
- direct Cap 63 shortcut use

## Attempted Capture

Browser Use/iab was attempted through the required Browser Use skill path and Node REPL `browser-client.mjs` bootstrap.

The attempt failed before tab creation, page navigation, DOM inspection, screenshot capture, or click-path recording.

Observed error:

```text
failed to write kernel assets: The system cannot find the path specified. (os error 3)
```

After resetting the Node REPL kernel, a trivial Node REPL metadata cell failed with the same error before JavaScript execution. That places the blocker below Nova and below Browser Use page interaction.

## Diagnostics

Raw evidence:

- `../evidence/2026-05-08/raw/browser_use_visual_capture_recovery_attempt.txt`
- `../evidence/2026-05-08/raw/browser_use_visual_capture_diagnostics.json`

Environment checks recorded:

- shell `node` works from the repo
- `TEMP` and `TMP` exist
- `C:\Users\Chris\package.json` is invalid JSON

The invalid user-level `package.json` matches older Browser Use friction, but this pass did not modify user-level files outside the repository.

## Classification

```text
blocked / setup-required
```

The visual proof infrastructure remains unavailable in this environment.

## What Did Not Happen

- No Nova browser/computer-use capability was added.
- No Browser Use execution path was added to Nova.
- No OpenClaw expansion occurred.
- No external write path was added.
- No autonomous workflow path was added.
- No direct Cap 63 shortcut was used.
- No screenshot was captured.
- No screenshot was substituted or faked.
- No click-path proof was captured.

## Impact

Existing contract-level and WebSocket/static evidence remains valid, but the following remain visual proof debt:

- Trust Review Card render screenshot
- degraded/stale search evidence state screenshot
- unsupported widget fallback screenshot
- blocked/setup-required state screenshot
- rapid-click/double-submit physical click-path proof

## Next Recommendation

Repair the Codex/Browser Use/Node REPL runtime asset setup outside Nova runtime authority, then rerun screenshot-only proof capture.

Do not treat this blocker as approval to add browser/computer-use capability to Nova.
