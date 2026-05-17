# Nova Basic Workflow Verification - 2026-05-17

Branch: `test/nova-basic-workflow-verification`

## Current Truth

Nova is in a clean verification phase.

Current repo truth remains:

```text
Approval gate wiring - focused coverage merged / certification pending.
```

Focused approval-gate regression coverage and behavioral live-session coverage are merged for tested Cap 22 / Cap 64 confirmation paths. Full approval-gate certification remains pending until broader/full-suite proof exists.

This pass verifies everyday usability and workflow coverage only. It does not add features, expand authority, change runtime behavior, or certify the approval gate globally.

## Test Commands Run

```powershell
python -m pytest nova_backend/tests/websocket/test_session_layer_pipeline.py nova_backend/tests/websocket/test_session_handler_proof_blockers.py nova_backend/tests/websocket/test_behavioral_session_approval_gate.py nova_backend/tests/governance/test_approval_gate_wiring.py nova_backend/tests/test_brain_server_session_cleanup.py nova_backend/tests/conversation/test_session_router.py nova_backend/tests/conversation/test_session_conversation_context.py -q
```

Result:

```text
179 passed in 15.96s
```

```powershell
python -m pytest nova_backend/tests/conversation/test_conversation_router.py nova_backend/tests/conversation/test_response_style_router.py nova_backend/tests/conversation/test_meta_intent_handler.py nova_backend/tests/conversation/test_general_chat_runtime.py nova_backend/tests/conversation/test_general_chat_tone.py nova_backend/tests/conversation/test_request_understanding.py nova_backend/tests/conversation/test_request_understanding_formatter.py nova_backend/tests/phase45/test_brain_server_basic_conversation.py nova_backend/tests/test_tierb_conversation.py -q
```

Result:

```text
282 passed, 7 failed in 6.46s
```

```powershell
python -m pytest nova_backend/tests/test_governor_mediator_phase4_capabilities.py nova_backend/tests/test_news_skill.py nova_backend/tests/executors/test_news_intelligence_executor.py nova_backend/tests/test_weather_skill.py nova_backend/tests/test_weather_service.py nova_backend/tests/test_calendar_skill.py nova_backend/tests/phase45/test_dashboard_calendar_integration.py nova_backend/tests/phase45/test_dashboard_news_header_weather_widget.py -q
```

Result:

```text
53 passed in 3.91s
```

```powershell
python -m pytest nova_backend/tests/test_open_folder_executor.py nova_backend/tests/executors/test_open_folder_executor.py nova_backend/tests/test_governor_mediator_tts.py nova_backend/tests/test_system_control_executor.py nova_backend/tests/test_websocket_local_guard.py nova_backend/tests/test_send_email_draft_routing.py nova_backend/tests/certification/cap_64_send_email_draft/test_p1_unit.py nova_backend/tests/certification/cap_64_send_email_draft/test_p2_routing.py nova_backend/tests/certification/cap_64_send_email_draft/test_p3_integration.py nova_backend/tests/certification/cap_64_send_email_draft/test_p4_api.py -q
```

Result:

```text
90 passed in 62.31s
```

```powershell
python -m pytest nova_backend/tests/test_memory_api.py nova_backend/tests/test_governed_memory_store.py nova_backend/tests/memory/test_memory_skill.py nova_backend/tests/phase5/test_memory_governance_executor.py nova_backend/tests/executors/test_os_diagnostics_openclaw_agent.py nova_backend/tests/test_runtime_settings_api.py -q
```

Result:

```text
92 passed in 7.24s
```

```powershell
python -m pytest nova_backend/tests/openclaw/test_first_read_only_workflow_proof.py nova_backend/tests/openclaw/test_openclaw_execute_executor.py nova_backend/tests/openclaw/test_freeform_goal_governance.py nova_backend/tests/openclaw/test_tool_registry.py nova_backend/tests/openclaw/test_user_tool_permissions.py nova_backend/tests/openclaw/test_strict_preflight.py nova_backend/tests/openclaw/test_agent_runner_inbox_check_guard.py nova_backend/tests/openclaw/test_agent_runner.py nova_backend/tests/openclaw/test_agent_runner_goal.py nova_backend/tests/openclaw/test_openclaw_mediator.py nova_backend/tests/test_openclaw_agent_api.py nova_backend/tests/test_openclaw_bridge_api.py -q
```

Result:

```text
137 passed, 1 failed in 34.29s
```

```powershell
python -m pytest nova_backend/tests/adversarial/test_governor_bypass.py nova_backend/tests/adversarial/test_conversation_non_authorizing.py nova_backend/tests/governance/test_ledger_only_governor_logs_actions.py nova_backend/tests/governance/test_mediator_registry_enforcement.py nova_backend/tests/governance/test_no_background_execution.py nova_backend/tests/governance/test_no_skill_executes_capabilities.py nova_backend/tests/test_governor_fail_closed.py nova_backend/tests/test_governor_execution_timeout.py nova_backend/tests/test_registry_fail_closed.py nova_backend/tests/test_ledger_event_allowlist.py -q
```

Result:

```text
36 passed in 2.10s
```

```powershell
python -m pytest nova_backend/tests -q
```

Result:

```text
2565 passed, 13 failed in 307.21s (0:05:07)
```

## Basic Conversation Latency

Measured with scripted WebSocket turns and model calls patched out for local fast paths.

| Prompt | Mean | Max observed | Result |
| --- | ---: | ---: | --- |
| `what can you do?` | 14.61ms | 23.85ms | Returned capability help message |
| `what can you di?` | 11.55ms | 12.65ms | Returned capability help message |
| `what can you doo` | 11.99ms | 12.90ms | Returned capability help message |
| `what time is it` | 10.37ms | 11.60ms | Failed internally on Windows date formatting, then fell back to generic greeting |
| `explain GPU supply` then `tell me more` | 41.18ms total | 41.18ms | Prior user/assistant context reached the follow-up handler |

Latency is acceptable for patched local fast paths. Current user-facing slowness is more likely to appear in LLM-backed, I/O-backed, or workflow paths than in the local router itself.

## Everyday Workflow Matrix

| Area | Evidence | Status |
| --- | --- | --- |
| Conversation basics | Conversation/router chunk mostly passed; full suite found time-query and stale capability-help assertion failures | Needs patch |
| Help / `what can you do` | Runtime returns full current help message quickly; existing tests expect older copy | Runtime works, tests stale |
| News workflows | News/weather/calendar chunk passed | Pass |
| Weather workflows | News/weather/calendar chunk passed | Pass |
| Calendar snapshot | News/weather/calendar chunk passed | Pass |
| Local device commands | Local action chunk passed | Pass |
| File/folder open confirmation | Local action + approval-gate chunks passed | Pass |
| Email draft confirmation | Cap 64 P1-P4 and session confirmation tests passed | Pass, not P5 locked |
| Memory governance | Memory/diagnostics chunk passed | Pass |
| Diagnostics | Memory/diagnostics chunk passed | Pass |
| OpenClaw read-only workflows | OpenClaw chunk mostly passed; execution-memory bookkeeping failed | Needs patch |
| Approval-gated actions | 179 focused/session approval tests passed | Pass for tested paths |

## News / Weather / Calendar

The focused news/weather/calendar command passed:

```text
53 passed in 3.91s
```

Covered areas include capability parsing, news skill fallback/deduping, news intelligence behavior, weather service behavior, calendar skill behavior, and dashboard widget integration.

## Local Actions

The focused local action and Cap 64 command passed:

```text
90 passed in 62.31s
```

Covered areas include:

- open folder executor behavior
- TTS/governor mediator path
- media / brightness / system-control executor behavior
- WebSocket local guard
- Cap 64 send-email-draft routing and P1-P4 certification tests

This does not lock Cap 64 P5. It only confirms existing tests for the local/draft path.

## Approval-Gated Actions

The focused approval-gate/session command passed:

```text
179 passed in 15.96s
```

Covered areas include:

- pending approval-required Cap 22 / Cap 64 action does not execute
- approved action resumes through governed invocation
- denied / cancel / unrelated input does not execute pending action
- governor/ledger expectations for tested paths

Full approval-gate certification remains pending because the full suite is not clean.

## Memory / Diagnostics

The focused memory/diagnostics command passed:

```text
92 passed in 7.24s
```

Covered areas include:

- memory API
- governed memory store
- memory skill
- memory governance executor
- OS diagnostics / OpenClaw agent diagnostic surface
- runtime settings API

## OpenClaw Read-Only Workflows

The focused OpenClaw command result:

```text
137 passed, 1 failed in 34.29s
```

Failure:

```text
nova_backend/tests/openclaw/test_agent_runner_goal.py::test_run_goal_records_execution_memory
```

Observed issue:

```text
runner._execution_memory.stats("system") returned {}
expected total_calls >= 1
```

Interpretation: this is not an authority-expansion issue. It is a workflow bookkeeping/proof gap: the goal path can run without recording the expected tool execution memory statistic.

## Regressions Found

### 1. Full suite is not clean

Full suite:

```text
2565 passed, 13 failed in 307.21s
```

This blocks any approval-gate certification closeout claim.

### 2. Cap 16 P5 WebSocket search widget failures

Failures:

```text
nova_backend/tests/certification/cap_16_governed_web_search/test_p5_ws_widget.py::test_websocket_search_emits_search_widget_type
nova_backend/tests/certification/cap_16_governed_web_search/test_p5_ws_widget.py::test_websocket_search_widget_data_has_results
```

Observed issue:

```text
No WebSocket message with type='search' and data dict was received.
```

This is important because Cap 16 is currently locked. It should be reviewed before treating current main as fully certification-clean.

### 3. Windows local-time formatting crash

Failures:

```text
nova_backend/tests/phase45/test_brain_server_basic_conversation.py::test_what_time_is_it_returns_local_time_without_model_call
nova_backend/tests/phase45/test_brain_server_followups_and_voice.py::test_voice_time_query_auto_speaks_response
nova_backend/tests/phase45/test_brain_server_memory_and_continuity.py::test_save_this_uses_last_response_and_routes_to_governed_memory
```

Observed exception:

```text
ValueError: Invalid format string
```

Cause:

```text
brain_server._render_local_time_message() uses now.strftime("%A, %B %-d").
```

`%-d` is not portable on Windows. This breaks the basic "what time is it" path and dependent "save this" continuity after a time answer.

### 4. Capability-help test assertions are stale against current runtime copy

Failures:

```text
test_what_can_you_do_with_question_mark_stays_on_capability_path
test_websocket_echoes_client_turn_id_on_chat_and_done
test_help_typo_variant_still_uses_capability_help
test_help_double_o_typo_variant_still_uses_capability_help
test_capability_help_explains_local_first_when_no_live_sources
test_capability_help_uses_live_setup_state_for_actions
test_capability_discoverability_prompt_and_categories_exist
```

Observed runtime message starts with:

```text
Here's what Nova can do right now:
```

The tests expect older strings such as:

```text
Nova Capabilities Right Now
No live sources are connected yet
Connected live sources:
```

Scripted checks showed the capability-help path still returns a complete local help message, including typo variants, and did not require an LLM call. This appears to be stale test wording rather than a missing help route.

### 5. OpenClaw execution-memory bookkeeping failure

Failure:

```text
test_run_goal_records_execution_memory
```

Observed issue:

```text
Execution-memory stats for "system" remain empty after run_goal("System health check").
```

This should be investigated as a workflow proof/bookkeeping bug.

## Robustness Gaps

- Full suite does not pass, so approval-gate certification remains pending.
- Locked Cap 16 has two failing P5 WebSocket widget tests on this Windows run.
- Basic local time query crashes on Windows due non-portable date formatting.
- Capability help tests are copy-fragile and stale against current help text.
- OpenClaw goal execution memory does not record the expected tool stats in one test.
- Local action / Cap 64 focused suite took 62.31s. It passed, but this is a latency watch item.

## Required Patches

Recommended narrow follow-up patches:

1. Fix Windows-safe local date formatting for `_render_local_time_message()`.
2. Update capability-help tests to assert stable semantic markers in the current help message rather than old headings.
3. Investigate Cap 16 WebSocket search widget emission in `test_p5_ws_widget.py`.
4. Investigate OpenClaw `run_goal` execution-memory recording.
5. Re-run full suite after those patches before any certification closeout.

Do not combine these with capability expansion, UI simplification, OpenClaw expansion, browser/computer-use expansion, Shopify writes, email sending, finance automation, social posting automation, or autonomous workflow execution.

## Next Action

Create a narrow fix branch for basic-usability regressions:

```text
fix/nova-basic-workflow-regressions
```

Suggested first patch order:

1. Windows-safe local time formatting.
2. Capability-help test wording refresh.
3. Cap 16 WebSocket widget investigation.
4. OpenClaw execution-memory bookkeeping investigation.

Then re-run:

```powershell
python -m pytest nova_backend/tests/phase45/test_brain_server_basic_conversation.py nova_backend/tests/phase45/test_brain_server_followups_and_voice.py nova_backend/tests/phase45/test_brain_server_memory_and_continuity.py nova_backend/tests/phase45/test_capability_discoverability_contract.py -q
python -m pytest nova_backend/tests/certification/cap_16_governed_web_search/test_p5_ws_widget.py -q
python -m pytest nova_backend/tests/openclaw/test_agent_runner_goal.py -q
python -m pytest nova_backend/tests -q
```

## Final Verdict

Nova basic workflow verification is in progress. Focused approval-gate coverage is merged. Full approval-gate certification remains pending until broader/full-suite proof exists.

Current evidence says Nova is broadly functional across many daily-use areas, but it is not clean enough to call stabilized or certified:

```text
Focused verification chunks: mostly pass.
Full suite: 2565 passed / 13 failed.
Approval-gate certification: pending.
Daily-use patch needed: yes.
```
