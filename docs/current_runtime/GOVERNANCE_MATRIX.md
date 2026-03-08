# GOVERNANCE_MATRIX

Deterministic capability governance matrix derived from allowlisted runtime sources.

| id | name | enabled | status | phase_introduced | risk_level | data_exfiltration | authority_class | confirmation_required | network_access | execution_surface | execution_gate | single_action_queue | ledger_allowlist | dns_rebinding_guard | timeout_guard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 16 | governed_web_search | True | active | 4 | low | True | read_only | False | True | Governor â†’ NetworkMediator | True | True | True | True | True |
| 17 | open_website | True | active | 4 | low | False | system_action | False | False | Governor â†’ Executor | True | True | True | True | True |
| 18 | speak_text | True | active | 4 | low | False | speech_output | False | False | Governor â†’ Speech | True | True | True | True | True |
| 19 | volume_up_down | True | active | 4 | low | False | system_action | False | False | Governor â†’ Executor | True | True | True | True | True |
| 20 | media_play_pause | False | active | 4 | low | False | system_action | False | False | Governor â†’ Executor | True | True | True | True | True |
| 21 | brightness_control | False | active | 4 | low | False | system_action | False | False | Governor â†’ Executor | True | True | True | True | True |
| 22 | open_file_folder | True | active | 4 | confirm | False | confirm_required | True | False | Governor â†’ Executor | True | True | True | True | True |
| 31 | response_verification | True | active | 4 | low | False | system_action | False | False | Governor â†’ Executor | True | True | True | True | True |
| 32 | os_diagnostics | True | active | 4 | low | False | system_action | False | False | Governor â†’ Executor | True | True | True | True | True |
| 48 | multi_source_reporting | True | active | 4 | low | True | read_only | False | True | Governor â†’ NetworkMediator | True | True | True | True | True |
| 49 | headline_summary | True | active | 4 | low | False | read_only | False | True | Governor â†’ NetworkMediator | True | True | True | True | True |
| 50 | intelligence_brief | True | active | 4 | low | False | read_only | False | True | Governor â†’ NetworkMediator | True | True | True | True | True |
| 51 | topic_memory_map | True | active | 4 | low | False | read_only | False | True | Governor â†’ NetworkMediator | True | True | True | True | True |
| 52 | story_tracker_update | True | active | 4 | low | False | system_action | False | False | Governor â†’ Executor | True | True | True | True | True |
| 53 | story_tracker_view | True | active | 4 | low | False | system_action | False | False | Governor â†’ Executor | True | True | True | True | True |
| 54 | analysis_document | True | active | 4 | low | False | system_action | False | False | Governor â†’ Executor | True | True | True | True | True |

## Derivation notes

- authority_class derivation: `speech_output` for capability 18, `confirm_required` when risk_level is `confirm`, `read_only` for network-mediated/data-exfil surfaces, else `system_action`.
- network_access is derived from Governor execution branches that pass `self.network` to an executor.
- execution_gate/single_action_queue/dns_rebinding_guard/timeout_guard/ledger_allowlist are code-presence checks from allowlisted modules.
- If a field cannot be proven from allowlisted runtime sources, value must be `unknown` (none currently unresolved under present code).
