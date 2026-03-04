# CURRENT RUNTIME STATE

**Generated at (UTC):** 2026-03-04T03:20:31.266392+00:00
**Scope:** Runtime-truth snapshot aligned to current code paths.

## Enabled Capability IDs (registry truth)

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

- Mediator currently maps capability IDs: [16, 17, 18, 19, 20, 21, 22, 32, 48]
- Routes to disabled capability IDs are expected to fail closed at Governor admission.

## Execution Gate

- `GOVERNED_ACTIONS_ENABLED`: true
