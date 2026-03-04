# CURRENT_RUNTIME_STATE.md

Auto-generated runtime snapshot. Do not edit manually.

- Generated (UTC): 2026-03-04T05:42:00.148785+00:00
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

## Capability Governance Matrix

| id | name | enabled | authority_class | confirmation_required | network_access | execution_layer |
| --- | --- | --- | --- | --- | --- | --- |
| 16 | governed_web_search | True | read_only | False | True | Governor → NetworkMediator |
| 17 | open_website | True | system_action | False | False | Governor → Executor |
| 18 | speak_text | True | speech_output | False | False | Governor → Speech |
| 19 | volume_up_down | True | system_action | False | False | Governor → Executor |
| 20 | media_play_pause | True | system_action | False | False | Governor → Executor |
| 21 | brightness_control | True | system_action | False | False | Governor → Executor |
| 22 | open_file_folder | False | confirm_required | True | False | Governor → Executor |
| 32 | os_diagnostics | True | system_action | False | False | Governor → Executor |
| 48 | multi_source_reporting | False | read_only | False | True | Governor → NetworkMediator |

## Governor Enforcement Summary

- single_action_queue_enforced: True
- execution_timeout_guard_active: True
- dns_rebinding_protection_active: True
- ledger_logging_active: True
- execution_gate_enabled: True

## Network Surface Summary

- Capabilities using NetworkMediator: [16, 48]
- Direct LLM calls detected: deepseek_uses_ollama_chat_directly=True
- Allowed_analysis_only surfaces: escalation_policy.ALLOW_ANALYSIS_ONLY=True

## Skill → Capability Routing Map

- brightness -> capability_id=21
- diagnostics -> capability_id=32
- media -> capability_id=20
- open_folder -> capability_id=22
- open_website -> capability_id=17
- report -> capability_id=48
- search -> capability_id=16
- speak -> capability_id=18
- volume -> capability_id=19

## Runtime Fingerprint

- git_commit_hash: 74e8f1bcd3fbbe5d99b88da4d4df76ca5e9c2ec6
- generated_at_utc: 2026-03-04T05:42:00.177251+00:00
- phase_marker: Phase-4 runtime active

## Mediator mapped capability IDs

- [16, 17, 18, 19, 20, 21, 22, 32, 48]

## Runtime truth discrepancies

- [hard_fail] ENABLED_ID_SET_MISMATCH: Enabled capability ID set differs between docs/current_runtime/CURRENT_RUNTIME_STATE.md and registry.json.
- [warning] MEDIATOR_ROUTES_TO_DISABLED_CAPABILITY: Mediator routes include capabilities that are currently disabled in registry.
- [warning] DIRECT_MODEL_CALL_BYPASS: DeepSeekBridge appears to call ollama.chat directly instead of a centralized LLM gateway.
