# Nova Capability Master
Updated: 2026-03-13
Status: Active plain-language guide

## Purpose
This is the easy-to-read capability guide for Nova.

If you need exact runtime truth, use:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`

## Nova's Current Capability Surface

Nova currently has four major capability families:

### 1) Research and intelligence
Nova can:
- search the web through governed network mediation
- build multi-source intelligence reports
- summarize headlines or drill into story pages
- generate daily/intelligence briefs
- show topic maps across the current news cycle
- verify claims or responses for likely issues
- create session-scoped analysis documents
- track developing stories over time

Key runtime capabilities:
- `16` search
- `31` verification
- `48` multi-source reporting
- `49` headline/story summary
- `50` intelligence brief
- `51` topic memory map
- `52` story tracker update
- `53` story tracker view
- `54` analysis document

### 2) Local computer help and control
Nova can:
- open websites and source pages
- open approved files and folders
- speak text aloud
- adjust volume
- control media play/pause/resume
- adjust brightness
- report system health and model readiness

Key runtime capabilities:
- `17` open website
- `18` speak text
- `19` volume
- `20` media control
- `21` brightness
- `22` open file/folder
- `32` system diagnostics

### 3) Snapshots and perception
Nova can:
- load weather, news, and calendar snapshots
- capture a bounded screenshot on request
- analyze the visible screen with OCR and visual heuristics
- explain what the user is looking at

Key runtime capabilities:
- `55` weather snapshot
- `56` news snapshot
- `57` calendar snapshot
- `58` screen capture
- `59` screen analysis
- `60` explain anything

### 4) Continuity and memory
Nova can:
- track ongoing work in project threads
- show blocker, health, latest decision, and what changed
- save thread snapshots and decisions into governed memory
- explicitly list, show, lock, defer, unlock, delete, or supersede memory items

Key runtime capability:
- `61` memory governance

Supporting runtime surfaces:
- Working Context Engine
- Project continuity threads
- Thread-memory bridge
- Thread detail panel and dashboard continuity UI

## Newer Capabilities Worth Calling Out

### Screen capture and screen analysis are live
These are active runtime capabilities:
- `58` `screen_capture`
- `59` `screen_analysis`
- `60` `explain_anything`

They are invocation-bound only.
Nova does not watch the screen in the background.

### Wake word is not live runtime yet
Wake word (`Hey Nova`) is still design-stage in this repository.

Current truth:
- STT voice transcription is active
- TTS voice output is active
- wake word is documented, but not active in the runtime capability registry

See:
- `docs/design/Phase 4.5/NOVA_WAKE_WORD_SCREEN_CONTEXT_IMPLEMENTATION.md`

## Best Reference For Full Details
For the full explanation of every active capability, typical prompts, and whether something is active vs design-stage, use:

- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
