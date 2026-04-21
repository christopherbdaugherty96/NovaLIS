# GOVERNANCE_MATRIX

Deterministic capability governance matrix derived from allowlisted runtime sources.

| id | name | enabled | status | phase_introduced | risk_level | data_exfiltration | authority_class | confirmation_required | reversible | external_effect | network_access | execution_surface | execution_gate | single_action_queue | ledger_allowlist | dns_rebinding_guard | timeout_guard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 16 | governed_web_search | True | active | 4 | low | True | read_only_network | False | True | False | True | Governor -> NetworkMediator | True | True | True | True | True |
| 17 | open_website | True | active | 4 | low | False | reversible_local | False | True | False | False | Governor -> Executor | True | True | True | True | True |
| 18 | speak_text | True | active | 4 | low | False | reversible_local | False | True | False | False | Governor -> Speech | True | True | True | True | True |
| 19 | volume_up_down | True | active | 4 | low | False | reversible_local | False | True | False | False | Governor -> Executor | True | True | True | True | True |
| 20 | media_play_pause | True | active | 4 | low | False | reversible_local | False | True | False | False | Governor -> Executor | True | True | True | True | True |
| 21 | brightness_control | True | active | 4 | low | False | reversible_local | False | True | False | False | Governor -> Executor | True | True | True | True | True |
| 22 | open_file_folder | True | active | 4 | confirm | False | reversible_local | True | True | False | False | Governor -> Executor | True | True | True | True | True |
| 31 | response_verification | True | active | 4 | low | False | read_only_local | False | True | False | False | Governor -> Executor | True | True | True | True | True |
| 32 | os_diagnostics | True | active | 4 | low | False | read_only_local | False | True | False | False | Governor -> Executor | True | True | True | True | True |
| 48 | multi_source_reporting | True | active | 4 | low | True | read_only_network | False | True | False | True | Governor -> NetworkMediator | True | True | True | True | True |
| 49 | headline_summary | True | active | 4 | low | True | read_only_network | False | True | False | True | Governor -> NetworkMediator | True | True | True | True | True |
| 50 | intelligence_brief | True | active | 4 | low | True | read_only_network | False | True | False | True | Governor -> NetworkMediator | True | True | True | True | True |
| 51 | topic_memory_map | True | active | 4 | low | False | read_only_local | False | True | False | True | Governor -> NetworkMediator | True | True | True | True | True |
| 52 | story_tracker_update | True | active | 4 | low | False | persistent_change | False | False | False | False | Governor -> Executor | True | True | True | True | True |
| 53 | story_tracker_view | True | active | 4 | low | False | read_only_local | False | True | False | False | Governor -> Executor | True | True | True | True | True |
| 54 | analysis_document | True | active | 4 | low | False | read_only_local | False | True | False | False | Governor -> Executor | True | True | True | True | True |
| 55 | weather_snapshot | True | active | 4 | low | True | read_only_network | False | True | False | True | Governor -> NetworkMediator | True | True | True | True | True |
| 56 | news_snapshot | True | active | 4 | low | True | read_only_network | False | True | False | True | Governor -> NetworkMediator | True | True | True | True | True |
| 57 | calendar_snapshot | True | active | 4 | low | False | read_only_local | False | True | False | False | Governor -> Executor | True | True | True | True | True |
| 58 | screen_capture | True | active | 4 | low | False | persistent_change | False | False | False | False | Governor -> Executor | True | True | True | True | True |
| 59 | screen_analysis | True | active | 4 | low | False | read_only_local | False | True | False | False | Governor -> Executor | True | True | True | True | True |
| 60 | explain_anything | True | active | 4 | low | False | read_only_local | False | True | False | False | Governor -> Executor | True | True | True | True | True |
| 61 | memory_governance | True | active | 5 | low | False | persistent_change | False | False | False | False | Governor -> Executor | True | True | True | True | True |
| 62 | external_reasoning_review | True | active | 7 | low | False | read_only_local | False | True | False | False | Governor -> Executor | True | True | True | True | True |
| 63 | openclaw_execute | True | active | 8 | low | False | read_only_network | False | True | True | True | Governor -> NetworkMediator | True | True | True | True | True |
| 64 | send_email_draft | True | active | 8 | confirm | True | persistent_change | True | False | True | False | Governor -> Executor | True | True | True | True | True |
| 65 | shopify_intelligence_report | True | active | 9 | low | False | read_only_network | False | True | True | True | Governor -> NetworkMediator | True | True | True | True | True |

## Derivation notes

- authority_class / confirmation_required / reversible / external_effect use explicit registry governance metadata when present; older stub inputs fall back to legacy heuristics.
- network_access is derived from explicit `read_only_network` authority or from Governor execution branches that pass `self.network` to an executor.
- execution_gate/single_action_queue/dns_rebinding_guard/timeout_guard/ledger_allowlist are code-presence checks from allowlisted modules.
- If a field cannot be proven from allowlisted runtime sources, value must be `unknown` (none currently unresolved under present code).
