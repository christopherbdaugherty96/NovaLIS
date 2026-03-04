# CURRENT_RUNTIME_STATE.md

Auto-generated runtime snapshot. Do not edit manually.

- Generated (UTC): 2026-03-04T05:13:16.281107+00:00
- Audit status: **FAIL**
- Execution gate enabled: True

## Enabled capability IDs

- [16, 17, 18, 19, 20, 21, 32]

## Disabled capability IDs

- [22, 48]

## Capability table

| id | name | enabled | status | risk_level | data_exfiltration |
| --- | --- | --- | --- | --- | --- |
| 16 | governed_web_search | True | active | low | True |
| 17 | open_website | True | active | low | False |
| 18 | speak_text | True | active | low | False |
| 22 | open_file_folder | False | active | confirm | False |
| 19 | volume_up_down | True | active | low | False |
| 20 | media_play_pause | True | active | low | False |
| 21 | brightness_control | True | active | low | False |
| 32 | os_diagnostics | True | active | low | False |
| 48 | multi_source_reporting | False | active | low | True |

## Mediator mapped capability IDs

- [16, 17, 18, 19, 20, 21, 22, 32, 48]

## Runtime truth discrepancies

- [hard_fail] ENABLED_ID_SET_MISMATCH: Enabled capability ID set differs between docs/current_runtime/CURRENT_RUNTIME_STATE.md and registry.json.
- [warning] MEDIATOR_ROUTES_TO_DISABLED_CAPABILITY: Mediator routes include capabilities that are currently disabled in registry.
- [warning] DIRECT_MODEL_CALL_BYPASS: DeepSeekBridge appears to call ollama.chat directly instead of a centralized LLM gateway.
