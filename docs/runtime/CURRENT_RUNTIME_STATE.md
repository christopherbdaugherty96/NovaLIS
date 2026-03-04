# CURRENT RUNTIME STATE

**Generated baseline:** 2026-03-04  
**Scope:** Runtime-truth snapshot aligned to current code paths.

## Enabled Capability IDs (registry truth)

The following capability IDs are currently enabled in `nova_backend/src/config/registry.json`:

- 16: enabled
- 17: enabled
- 18: enabled
- 19: enabled
- 20: enabled
- 21: enabled
- 32: enabled

## Disabled Capability IDs

- 22: disabled
- 48: disabled

## Capability Table

| ID | Name | Enabled | Status | Risk Level | Data Exfiltration |
|---:|---|---|---|---|---|
| 16 | governed_web_search | enabled | active | low | true |
| 17 | open_website | enabled | active | low | false |
| 18 | speak_text | enabled | active | low | false |
| 19 | volume_up_down | enabled | active | low | false |
| 20 | media_play_pause | enabled | active | low | false |
| 21 | brightness_control | enabled | active | low | false |
| 22 | open_file_folder | disabled | active | confirm | false |
| 32 | os_diagnostics | enabled | active | low | false |
| 48 | multi_source_reporting | disabled | active | low | true |

## Mediator Route Notes (current code)

- `GovernorMediator` contains parse routes for IDs 22 and 48 (`open <folder>` and `report|summarize <q>`), but both capabilities remain disabled by registry gate and fail closed at execution admission.

## Execution Gate

- `GOVERNED_ACTIONS_ENABLED`: true
