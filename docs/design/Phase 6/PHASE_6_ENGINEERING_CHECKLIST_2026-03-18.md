# Phase 6 Engineering Checklist
Date: 2026-03-18
Status: Execution checklist only; implementation packet for Phase-6 alignment work
Scope: Turns the Phase-6 sovereignty-alignment plan into concrete engineering workstreams before any external reasoning or external execution expansion

## Purpose
This checklist is the execution bridge between:
- `docs/design/Phase 6/PHASE_6_SOVEREIGNTY_ALIGNMENT_AND_TRUST_LOOP_PLAN.md`
- current runtime truth
- concrete implementation work in `nova_backend/src/`, `nova_backend/static/`, and `nova_backend/tests/`

This checklist does not replace any earlier planning material.
It translates that material into ordered implementation work.

## Use This Packet In Order
1. baseline the surfaced capability inventory
2. complete the trust-loop surfaces and contracts
3. repair reliability gaps in user-facing active features
4. harden governance boundaries and parity checks

## Workstream 1 - Capability Truth Audit

### Goal
Make every surfaced capability truthful across:
- registry
- Governor routing
- executors
- UI wording
- runtime docs
- tests

### Source Files To Audit
- `nova_backend/src/config/registry.json`
- `nova_backend/src/governor/governor_mediator.py`
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/index.html`

### Capability Matrix Task
- build one matrix row for every surfaced capability or trust-facing runtime surface
- record:
  - capability/surface name
  - capability ID if applicable
  - where it is surfaced in UI/docs
  - intended path through Governor and executor
  - observed behavior in real use
  - classification: `reliable`, `partial`, `broken`, `design_only`, or `misstated`
  - partial subtype when applicable: `environment_blocked`, `degraded_but_usable`, `multi_step_unproven`, or `surface_contract`
  - required fix or wording correction
  - proof file/test covering the claim

### Truth Classification Rules
- `reliable`
  - the main happy path is live-proven, or side-effect-safe controlled proof exists when a true live run would unnecessarily mutate the operator environment
  - surfaced wording matches reality
  - degraded paths, if any, are truthful and tested
- `partial`
  - the capability is usable or truthfully surfaced, but it is not yet ready to be described as dependable
  - every `partial` label should also declare a subtype
- `partial.environment_blocked`
  - logic-path repairs are in place, but a runtime prerequisite is still missing on the active machine/runtime
- `partial.degraded_but_usable`
  - the capability provides real user value, but quality or fidelity can degrade under known bounded conditions
- `partial.multi_step_unproven`
  - the first supported user journey is proven, but broader chained or conversational use is not yet proven
- `partial.surface_contract`
  - the backend/core path exists, but surfaced wording, buttons, or widget behavior still overpromise or hide important truth
- `broken`
  - the capability is surfaced as available but does not currently complete a truthful usable path
- `design_only`
  - the capability exists as planning/design material only and should not be surfaced as active runtime behavior
- `misstated`
  - runtime/docs/UI wording makes a materially false claim relative to the current implementation

### Phase-6 Slice Operating Rule
- one proven break per pass
- one repair scope per pass
- one focused proof bundle per pass
- one freeze note per capability before moving on

### Proof Bundle Requirement
Every capability slice should end with:
- one live-path proof
- or one controlled side-effect-safe proof when a true live run would unnecessarily mutate the operator environment
- one focused regression bundle
- one freeze note in this checklist
- one current classification line with subtype when applicable

### Freeze Note Template
Every repaired capability freeze note should record:
- status
- subtype when status is `partial`
- first supported user journey
- repaired truth gaps
- proof bundle
- remaining limitation
- what would promote the capability to `reliable`

### First Supported User Journey
This means the narrowest user flow that Nova currently supports truthfully.
It should be live-proven when safe, or side-effect-safe controlled proof when a true live run would unnecessarily mutate the operator environment.
It is the baseline journey to preserve while later slices extend behavior.

### Priority Audit Targets
- `response_verification` (`31`)
- `intelligence_brief` (`50`)
- `screen_capture` (`58`)
- `screen_analysis` (`59`)
- `explain_anything` (`60`)
- `memory_governance` (`61`)
- trust review / recent runtime activity surface in `nova_backend/static/dashboard.js`

### Implementation Tasks
- verify every capability shown in runtime docs is reachable from `GovernorMediator`
- verify every routed capability reaches the correct executor or runtime surface
- verify every surfaced dashboard widget corresponds to a truthful runtime state
- flag any UI text that implies production reliability where the feature is only partial
- explicitly downgrade wording before adding new integrations if the feature is not dependable yet

### Grounded Code Paths
- explain routing regexes and capability IDs live in `nova_backend/src/governor/governor_mediator.py`
- explain executor lives in `nova_backend/src/executors/explain_anything_executor.py`
- screen executors live in `nova_backend/src/executors/screen_capture_executor.py` and `nova_backend/src/executors/screen_analysis_executor.py`
- verification executor lives in `nova_backend/src/executors/response_verification_executor.py`
- brief/news logic currently flows through `nova_backend/src/executors/news_intelligence_executor.py`, `nova_backend/src/rendering/intelligence_brief_renderer.py`, and dashboard parsing in `nova_backend/static/dashboard.js`

### Definition Of Done
- every surfaced capability has a truth-matrix row
- every row has a classification and proof reference
- no user-facing claim remains unclassified

### Current Active Capability Freeze Matrix (2026-03-18)
| ID | Capability | Status | Current proof basis |
| --- | --- | --- | --- |
| 16 | `governed_web_search` | `partial.multi_step_unproven` | live follow-up proof plus search/report regression coverage |
| 17 | `open_website` | `reliable` | live preview path plus `nova_backend/tests/phase45/test_brain_server_website_preview.py` and `nova_backend/tests/executors/test_webpage_launch_executor.py` |
| 18 | `speak_text` | `reliable` | controlled routing/executor proof in `nova_backend/tests/test_governor_mediator_tts.py` and `nova_backend/tests/executors/test_tts_executor.py` |
| 19 | `volume_up_down` | `reliable` | controlled executor proof in `nova_backend/tests/executors/test_local_control_executors.py` |
| 20 | `media_play_pause` | `reliable` | controlled executor proof in `nova_backend/tests/executors/test_local_control_executors.py` |
| 21 | `brightness_control` | `reliable` | controlled executor proof in `nova_backend/tests/executors/test_local_control_executors.py` |
| 22 | `open_file_folder` | `reliable` | controlled executor proof in `nova_backend/tests/executors/test_open_folder_executor.py` and `nova_backend/tests/test_open_folder_executor.py` |
| 31 | `response_verification` | `reliable` | live verification WebSocket proof plus executor/governor regressions |
| 32 | `os_diagnostics` | `reliable` | live `system status` sweep plus `nova_backend/tests/executors/test_local_control_executors.py` |
| 48 | `multi_source_reporting` | `reliable` | live `research <query>` proof plus search/report regression coverage |
| 49 | `headline_summary` | `reliable` | live `summarize headline 1` proof plus `nova_backend/tests/executors/test_news_intelligence_executor.py` |
| 50 | `intelligence_brief` | `partial.degraded_but_usable` | live cold-session brief/news proof plus brief widget regression coverage |
| 51 | `topic_memory_map` | `reliable` | live `show topic memory map` proof plus story/memory regression coverage |
| 52 | `story_tracker_update` | `reliable` | live `track story <topic>` proof plus `nova_backend/tests/executors/test_story_tracker_executor.py` |
| 53 | `story_tracker_view` | `reliable` | live `show story <topic>` proof plus `nova_backend/tests/executors/test_story_tracker_executor.py` |
| 54 | `analysis_document` | `partial.degraded_but_usable` | live truthful create-doc degradation proof plus executor/governor regressions |
| 55 | `weather_snapshot` | `reliable` | live weather proof plus `nova_backend/tests/executors/test_info_snapshot_executor.py` |
| 56 | `news_snapshot` | `reliable` | live news proof plus `nova_backend/tests/executors/test_info_snapshot_executor.py` |
| 57 | `calendar_snapshot` | `partial.environment_blocked` | live truthful not-connected proof plus `nova_backend/tests/executors/test_info_snapshot_executor.py` |
| 58 | `screen_capture` | `partial.environment_blocked` | live missing-dependency proof plus `nova_backend/tests/phase45/test_screen_capture_executor.py` and governance capture coverage |
| 59 | `screen_analysis` | `partial.environment_blocked` | live missing-dependency proof plus `nova_backend/tests/executors/test_explain_anything_executor.py` and screen-analysis/capture coverage |
| 60 | `explain_anything` | `partial.environment_blocked` | live explain-flow proof plus routing, executor, trust, and screen-capture regressions |
| 61 | `memory_governance` | `reliable` | live `memory overview` proof plus `nova_backend/tests/phase5/test_memory_governance_executor.py` and dashboard memory widget coverage |

## Workstream 2 - Trust Loop Completion

### Goal
Make Nova visibly explain:
- what it did
- why it was allowed
- what changed
- what was blocked

### Current Grounded Surfaces
- trust panel state and rendering already exist in `nova_backend/static/dashboard.js`
- trust panel containers already exist in `nova_backend/static/index.html`
- system-status trust shape is already covered by `nova_backend/tests/phase45/test_dashboard_trust_review_widget.py`
- system-status contract already expects trust data in `nova_backend/tests/phase45/test_system_status_reporting_contract.py`

### Implementation Tasks
- define a canonical Recent Actions payload shape for dashboard and system-status consumers
- extend trust review payloads to include:
  - capability ID/name
  - action summary
  - allow/block reason
  - external effect
  - reversibility
  - request/ledger correlation
  - timestamp
- make blocked actions visible in the same calm trust surface instead of disappearing into logs
- ensure trust panel language stays factual and non-persuasive

### ActionResult Normalization Tasks
- inventory all executor return shapes
- align them to one canonical ActionResult contract
- ensure every governed result provides:
  - `user_message`
  - `speakable_text`
  - `structured_data`
  - `risk_level`
  - `external_effect`
  - `reversible`
  - audit/ledger correlation
- document any legacy result shims required during migration

### Canonical ActionResult Contract

#### Required Runtime Fields
- `success`
  - boolean execution outcome
- `status`
  - normalized lifecycle-facing status string
  - allowed values in this phase: `completed`, `failed`, `refused`
- `user_message`
  - final user-facing text
- `speakable_text`
  - TTS-safe version of the response
- `structured_data`
  - machine-readable payload dictionary
- `risk_level`
  - current normalized values: `low`, `moderate`, `high`, `critical`
- `external_effect`
  - whether the action changed something outside the bounded runtime response path
- `reversible`
  - whether the action can be reasonably undone
- `request_id`
  - request correlation id carried across the governed path
- `capability_id`
  - governed capability id that produced the result

#### Optional Runtime Fields
- `authority_class`
  - present when capability-topology truth is available
- `ledger_ref`
  - present when a deterministic ledger reference is available at the emitting layer
- `outcome_reason`
  - normalized cause/detail field for failure, refusal, or bounded degraded outcome

#### Ownership Rules
- executors should primarily supply:
  - success/failure intent
  - user-facing message
  - speakable text when executor-specific shaping is needed
  - structured payload
  - outcome-specific reason/details
  - explicit overrides for `risk_level`, `external_effect`, `reversible`, or `authority_class` when the executor has truth the Governor cannot infer safely
- Governor should centrally stamp or normalize wherever possible:
  - `request_id`
  - `capability_id`
  - `status`
  - default `risk_level`
  - default `external_effect`
  - default `reversible`
  - topology-backed `authority_class` when available
- trust/recent-activity surfaces may derive `ledger_ref` from the append-only ledger until the ledger writer itself becomes the canonical source for that field

#### Legacy Normalization Rules
- legacy `message` should normalize to `user_message`
- legacy `data` should normalize into `structured_data` unless it already contains an explicit nested `structured_data`
- missing `speakable_text` should default to a TTS-safe version of `user_message`
- missing `status` should normalize from:
  - `success=True` -> `completed`
  - `success=False` + refusal/policy block -> `refused`
  - other `success=False` -> `failed`
- missing `outcome_reason` should normalize from executor-supplied failure/refusal text when that text is the most truthful available cause
- legacy consumers may continue reading `message` and `data` during migration, but all new boundary logic should read the normalized contract

### ActionResult Migration Checklist
- lock the canonical contract in `nova_backend/src/actions/action_result.py`
- add one normalization helper so ActionResult can expose the canonical shape without requiring every executor to migrate at once
- normalize the Governor boundary in `nova_backend/src/governor/governor.py`
  - stamp `request_id`
  - stamp `capability_id`
  - normalize `status`
  - attach topology-backed authority metadata when available
- migrate first-wave governed executors:
  - `response_verification_executor.py`
  - `news_intelligence_executor.py`
  - `multi_source_reporting_executor.py`
  - `analysis_document_executor.py`
  - `explain_anything_executor.py`
  - `screen_capture_executor.py`
  - `screen_analysis_executor.py`
- migrate main consumers:
  - `brain_server.py`
  - trust/recent-activity reducer in `os_diagnostics_executor.py`
- preserve backward compatibility during migration:
  - keep `message` / `data` aliases usable
  - prefer canonical reads in new logic
- expand release-gate coverage before calling the refactor complete:
  - `tests/test_governor_execution_timeout.py`
  - `tests/phase45/test_brain_server_trust_status.py`
  - `tests/phase45/test_system_status_reporting_contract.py`
  - `tests/executors/test_response_verification_executor.py`
  - `tests/executors/test_news_intelligence_executor.py`
  - `tests/executors/test_explain_anything_executor.py`
  - `tests/test_runtime_auditor.py`

Current migration state as of 2026-03-19:
- completed:
  - canonical ActionResult contract locked in docs and `action_result.py`
  - Governor result stamping normalized in `governor.py`
  - first governed executor wave migrated:
    - `response_verification_executor.py`
    - `news_intelligence_executor.py`
    - `multi_source_reporting_executor.py`
    - `analysis_document_executor.py`
  - explain/screen executor wave migrated:
    - `explain_anything_executor.py`
    - `screen_capture_executor.py`
    - `screen_analysis_executor.py`
  - main governed consumer path in `brain_server.py` now prefers canonical `user_message` and `structured_data`
  - trust/recent-activity normalization now prefers canonical status and outcome metadata in `os_diagnostics_executor.py`
  - active-capability authority metadata parity enforcement added:
    - `registry.json` now carries explicit `authority_class`, `requires_confirmation`, `reversible`, and `external_effect` fields for the active runtime set
    - `CapabilityRegistry` now fails closed if an active capability is missing that authority metadata
    - `CapabilityTopology` now consumes registry authority truth and fails closed on parity drift
    - runtime-auditor governance rows now prefer explicit registry authority metadata over legacy heuristics when available
- next:
  - remove remaining legacy read fallbacks after broader executor coverage is complete

### Ledger Lifecycle Tasks
- verify each governed action produces:
  1. `INTENT_RECEIVED`
  2. `ACTION_VALIDATED`
  3. `EXECUTION_STARTED`
  4. `EXECUTION_COMPLETED` or `EXECUTION_FAILED`
- identify current event-name variants and map them to the canonical lifecycle
- add failing tests where lifecycle steps are missing or inconsistent

### Trust Metadata Tasks
- add or normalize authority metadata so trust surfaces can render truthful summaries
- keep registry truth and capability-topology truth aligned rather than splitting authority semantics across hardcoded files

### Current Phase-6 Freeze State (2026-03-19)
- surface: `trust_review_recent_actions`
- status: `reliable`
- first supported user journey:
  - successful governed action -> `trust_status` payload -> Recent Activity row with outcome, `Why`, `Effect`, `Request`, and `Ledger`
  - blocked governed action -> `trust_status` payload -> Recent Activity row marked as needing attention with the same trust metadata surfaced truthfully
- repaired and verified:
  - unsuccessful ledger-backed actions no longer render as `Action completed` in the trust review reducer
  - Recent Activity rows now carry explicit outcome labels so success and issue states are distinguishable at a glance
  - the dashboard trust panel now surfaces the outcome visibly instead of relying only on generic title text
  - failed action rows now carry a direct per-row `Why` reason from the governed result message instead of forcing the trust panel to infer cause indirectly
  - successful governed action rows now also surface explicit safe-case effect metadata instead of leaving `Effect` blank when the action had no external effect and remained reversible
  - request correlation is now surfaced directly from ledger-backed `request_id` values when the originating event includes one
  - each trust row now carries a deterministic ledger line reference so Recent Activity items can be correlated back to the append-only ledger without inventing a synthetic event id
  - governed action rows now carry explicit allow reasoning from authority metadata when the Governor has that data, so the trust surface can explain why a completed action was allowed instead of only why a failed action was blocked
- proof bundle:
  - live in-process WebSocket proof for `fact check The moon has a thick atmosphere like Earth`
  - focused regression coverage in:
    - `nova_backend/tests/test_governor_execution_timeout.py`
    - `nova_backend/tests/executors/test_local_control_executors.py`
    - `nova_backend/tests/phase45/test_dashboard_trust_review_widget.py`
    - `nova_backend/tests/phase45/test_brain_server_trust_status.py`
    - `nova_backend/tests/phase45/test_system_status_reporting_contract.py`
- current boundary:
  - the reliable claim applies to governed Recent Activity rows backed by the trust-status/reducer path; other runtime event summaries still remain event-type-specific rather than a fully universal action schema

### Definition Of Done
- Recent Actions is present and informative
- blocked and completed actions are both visible
- ActionResult shape is normalized or explicitly shimmed
- ledger lifecycle is complete for every governed action path under audit

## Workstream 3 - Reliability Repairs

### Goal
Repair currently surfaced features whose real-world reliability is below their claimed state.

### 3A. Explain Anything Reliability

#### Files
- `nova_backend/src/governor/governor_mediator.py`
- `nova_backend/src/executors/explain_anything_executor.py`
- `nova_backend/src/executors/screen_capture_executor.py`
- `nova_backend/src/executors/screen_analysis_executor.py`
- `nova_backend/src/perception/explain_anything.py`
- `nova_backend/src/context/context_snapshot_service.py`
- `nova_backend/static/dashboard.js`

#### Tests To Use Or Extend
- `nova_backend/tests/executors/test_explain_anything_executor.py`
- `nova_backend/tests/governance/test_screen_capture_ledger_events.py`
- `nova_backend/tests/governance/test_screen_capture_requires_invocation.py`
- `nova_backend/tests/phase45/test_explain_anything_router.py`
- `nova_backend/tests/phase45/test_screen_capture_executor.py`

#### Tasks
- trace a real invocation from regex match through executor selection and widget rendering
- verify invocation-source gating is not blocking legitimate routes unexpectedly
- verify context snapshot capture is present and useful when screen or page context exists
- verify failure states are surfaced clearly to the user instead of collapsing into generic failure text
- add one realistic end-to-end regression test that matches the real user prompt patterns: `what am I looking at?`, `explain this`, `view screen`

#### Current Phase-6 Freeze State (2026-03-18)
- capability `60`
- status: `partial`
- subtype: `partial.environment_blocked`
- first supported user journey:
  - `what am I looking at` -> capability `60` routing -> explain pipeline -> truthful environment-blocked capture response when `pyautogui` is missing
- repaired and verified:
  - prompt routing now covers common real prompts including `what am I looking at` and `view screen`
  - explicit screen-intent fallback now reaches the screen-analysis path even when context capture is empty
  - trust-review refresh now updates after explain actions
  - screen-capture failures now surface the real missing-dependency reason instead of a generic region-capture failure
- proof bundle:
  - live in-process WebSocket pass for `what am I looking at`
  - focused regression coverage in:
    - `nova_backend/tests/test_governor_mediator_phase4_capabilities.py`
    - `nova_backend/tests/executors/test_explain_anything_executor.py`
    - `nova_backend/tests/phase45/test_explain_anything_router.py`
    - `nova_backend/tests/phase45/test_screen_capture_executor.py`
    - `nova_backend/tests/phase45/test_brain_server_trust_status.py`
- remaining limitation:
  - live capture remains blocked on this runtime until `pyautogui` is available
- promote to `reliable` when:
  - the capture dependency is available
  - a real screen/OCR pass is live-proven on this machine/runtime
  - the current truthful degraded path remains intact for future blocked runtimes

### 3B. Intelligence Brief Reliability

#### Files
- `nova_backend/src/executors/news_intelligence_executor.py`
- `nova_backend/src/rendering/intelligence_brief_renderer.py`
- `nova_backend/static/dashboard.js`
- any brief-loading path in `nova_backend/src/brain_server.py`

#### Tests To Use Or Extend
- `nova_backend/tests/evaluation/test_intelligence_brief_quality.py`
- `nova_backend/tests/rendering/test_intelligence_brief_renderer.py`
- `nova_backend/tests/executors/test_news_intelligence_executor.py`

#### Current Phase-6 Freeze State (2026-03-18)
- capability `50`
- status: `partial`
- subtype: `partial.degraded_but_usable`
- first supported user journey:
  - `daily brief` on a cold session -> structured brief surface with truthful status and visible payoff
- repaired and verified:
  - entrypoint truth
  - backend degradation behavior for source-grounded briefing
  - brief widget/sidebar truth
  - visual wording/readability pass on the news-page brief surface
- proof bundle:
  - live cold-session runtime pass for `daily brief`
  - live cold-session runtime pass for `today's news`
  - focused regression coverage in:
    - `nova_backend/tests/executors/test_news_intelligence_executor.py`
    - `nova_backend/tests/phase45/test_dashboard_brief_shortcuts.py`
    - `nova_backend/tests/phase45/test_dashboard_intelligence_brief_widget.py`
  - browser-facing visual pass on the news page after widget integration
- remaining limitation:
  - source-grounded synthesis can still degrade when model inference is blocked, but it now does so truthfully and visibly with placeholder/omitted counts
- promote to `reliable` when:
  - source-grounded synthesis is live-proven under normal model availability
  - the grounded and degraded surfaces remain visually and structurally aligned

#### Tasks
- verify the brief loads consistently from the underlying snapshot/news path
- verify the returned brief text matches the dashboard parser expectations
- verify follow-up commands remain usable after the brief is shown
- add regression coverage for the specific failure mode the user reported: brief exists but is not working as well in actual use

### 3C. Response Verification Visibility

#### Files
- `nova_backend/src/executors/response_verification_executor.py`
- `nova_backend/static/dashboard.js`

#### Tests To Use Or Extend
- `nova_backend/tests/executors/test_response_verification_executor.py`

#### Tasks
- verify capability `31` is not merely connected internally but produces visible, understandable output
- verify the trust surface reflects verification results when relevant

#### Current Phase-6 Freeze State (2026-03-18)
- capability `31`
- status: `reliable`
- first supported user journey:
  - `fact check <claim>` -> verification pipeline -> live structured report in chat with claim-reliability framing and follow-up actions
- repaired and verified:
  - unavailable DeepSeek placeholder output no longer surfaces as a successful verification report
  - incomplete verification output is now rejected instead of being presented as a real fact-check result
  - claim reliability is now separated from report confidence, so `Accuracy: Low / Confidence: High` no longer surfaces as reassuring summary text
  - inline issue/correction sections now count truthfully even when the model does not use bullet lists
  - the governed runtime path now gives capability `31` the extended execution budget required for cold-start local-model verification
- proof bundle:
  - live in-process WebSocket proof for `fact check The moon has a thick atmosphere like Earth.`
  - live executor proof for both false-claim and true-claim samples
  - focused regression coverage in:
    - `nova_backend/tests/executors/test_response_verification_executor.py`
    - `nova_backend/tests/test_governor_execution_timeout.py`
    - `nova_backend/tests/test_brain_server_session_cleanup.py`
- remaining limitation:
  - verification remains chat-surfaced rather than having a dedicated standalone widget, but the surfaced contract is now truthful and usable

### 3D. Web Search and Conversation Follow-Through

#### Files
- `nova_backend/src/executors/web_search_executor.py`
- `nova_backend/src/executors/multi_source_reporting_executor.py`
- `nova_backend/src/governor/governor_mediator.py`
- `nova_backend/static/dashboard.js`

#### Tests To Use Or Extend
- `nova_backend/tests/executors/test_web_search_executor.py`
- `nova_backend/tests/executors/test_multi_source_reporting_executor.py`
- `nova_backend/tests/phase45/test_dashboard_search_widget_followups.py`
- `nova_backend/tests/test_governor_mediator_phase4_capabilities.py`

#### Current Phase-6 Freeze State (2026-03-19)
- capability `16`
- status: `reliable`
- first supported user journey:
  - `search for <query>` -> `research <query>`
  - `search for <query>` -> `create an intelligence brief on <query>`
  - `search for <query>` -> `analyze source reliability for <query>`
- repaired and verified:
  - search follow-up prompts are now self-contained and route to supported capabilities instead of promising unsupported search-result memory
  - search widget buttons now use supported topic-level prompts
  - search-origin follow-up into capability `48` now preserves a coherent search widget contract instead of collapsing into bare result links
  - `analyze source reliability for <query>` now preserves the original topic query and surfaces a dedicated `source_reliability` focus instead of turning the full phrase into a fresh search topic
  - `research <query>` now completes within the governed budget because optional model-enrichment steps use bounded timeouts and skip the second model attempt when the first one is already unavailable
- proof bundle:
  - live in-process WebSocket proof for:
    - `search for semiconductor policy updates` -> `research semiconductor policy updates`
    - `search for semiconductor policy updates` -> `create an intelligence brief on semiconductor policy updates`
    - `search for semiconductor policy updates` -> `analyze source reliability for semiconductor policy updates`
  - focused regression coverage in:
    - `nova_backend/tests/executors/test_web_search_executor.py`
    - `nova_backend/tests/executors/test_multi_source_reporting_executor.py`
    - `nova_backend/tests/phase45/test_dashboard_search_widget_followups.py`
    - `nova_backend/tests/test_governor_mediator_phase4_capabilities.py`
- remaining limitation:
  - broader open-ended search conversation beyond the surfaced first-step follow-up family remains outside the current frozen support claim

#### Additional Phase-6 Freeze State (2026-03-19)
- capability `48`
- status: `reliable`
- first supported user journey:
  - `research <query>` -> structured intelligence report with coherent search widget continuity
- repaired and verified:
  - report-mode follow-through preserves `query`, `provider`, `summary`, `result_count`, and `source_pages_read` instead of collapsing into a bare result list
  - source-reliability follow-through keeps the original topic query and explicit report focus
  - optional analyst-note and counter-analysis model enrichment now use bounded timeouts and truthful deterministic fallback instead of consuming the whole governor budget
- proof bundle:
  - live in-process WebSocket proof for `research semiconductor policy updates`
  - focused regression coverage in:
    - `nova_backend/tests/executors/test_multi_source_reporting_executor.py`
    - `nova_backend/tests/executors/test_web_search_executor.py`
    - `nova_backend/tests/phase45/test_dashboard_search_widget_followups.py`

### 3E. Analysis Document Reliability

#### Files
- `nova_backend/src/executors/analysis_document_executor.py`
- `nova_backend/static/dashboard.js`

#### Tests To Use Or Extend
- `nova_backend/tests/executors/test_analysis_document_executor.py`

#### Current Phase-6 Freeze State (2026-03-18)
- capability `54`
- status: `partial`
- subtype: `partial.degraded_but_usable`
- first supported user journey:
  - `create analysis report on <topic>` -> analysis-document pipeline -> truthful incomplete-document failure when the local model cannot complete the required structure in this runtime
- repaired and verified:
  - unavailable structured-analysis placeholder output no longer gets written as a successful analysis document
  - incomplete title-only or structurally thin outputs no longer get saved as finished documents
  - create-doc prompting now uses a stricter no-blank-line contract that is compatible with the local-model stop-token behavior
  - single-line section output now parses correctly into structured sections when the model does complete the contract
  - section explain fallback now reuses grounded section text instead of surfacing unavailable-model placeholder text
  - capability `54` now has a governed extended execution budget for long-form local-model synthesis instead of failing inside the generic boundary
- proof bundle:
  - live in-process WebSocket proof for `create analysis report on AI geopolitics`
  - live executor proof for `create analysis report on AI geopolitics`
  - focused regression coverage in:
    - `nova_backend/tests/executors/test_analysis_document_executor.py`
    - `nova_backend/tests/test_governor_execution_timeout.py`
    - `nova_backend/tests/conversation/test_deepseek_bridge.py`
- remaining limitation:
  - live create-document generation is still not dependable on this local model/runtime: the path now fails truthfully instead of saving a fake report, but the model still often returns incomplete document structure
- promote to `reliable` when:
  - create-document and explain-section flows are both live-proven with real structured analysis
  - the strict document contract produces full structured reports consistently enough that Nova is not relying on incomplete-document refusal as the normal outcome

### 3F. Basic Conversation And Personality Tone Alignment

#### Files
- `nova_backend/src/skills/general_chat.py`
- `nova_backend/src/personality/interface_agent.py`
- `nova_backend/src/brain_server.py`

#### Tests To Use Or Extend
- `nova_backend/tests/conversation/test_general_chat_tone.py`
- `nova_backend/tests/conversation/test_personality_interface_agent.py`
- `nova_backend/tests/phase45/test_brain_server_tone_commands.py`

#### Current Phase-6 Freeze State (2026-03-19)
- surface `general_chat` and tone-profile controls
- status: `reliable`
- first supported user journey:
  - `tone set concise` -> `what is a gpu?` -> short direct answer
  - `tone set detailed` -> `what is a gpu?` -> fuller answer without duplicated summary framing
- repaired and verified:
  - explicit tone selection now changes the actual general-chat prompt contract, token budget, and length shaping instead of acting as a presentation-only label
  - the core general-chat contract no longer instructs a dated `butler-like courtesy` style and is now aligned with Nova's calm, grounded, collaborative voice
  - detailed tone now improves dense structured output readability in the personality presentation layer by separating known section headers cleanly
  - tone commands now accept the normal trailing punctuation introduced by Nova's own input normalization path
  - the brain-server skill path no longer double-formats general-chat replies, so detailed answers do not surface duplicated `Summary:` blocks
- proof bundle:
  - live in-process WebSocket proof for `tone set concise` -> `what is a gpu?`
  - live in-process WebSocket proof for `tone set detailed` -> `what is a gpu?`
  - focused regression coverage in:
    - `nova_backend/tests/conversation/test_general_chat_tone.py`
    - `nova_backend/tests/conversation/test_personality_interface_agent.py`
    - `nova_backend/tests/phase45/test_brain_server_tone_commands.py`
- current boundary:
  - tone profiles are now dependable for the basic conversation path, but they do not yet retune every governed capability response contract outside `general_chat`

### 3G. Remaining Stable And Environment-Blocked Freeze States

The remaining active capabilities were validated in this pass through the freeze matrix, the focused regression bundle, and the live runtime sweep where side effects were safe to observe.

#### Reliable In Current Scope
- capability `17` `open_website`
  - first supported user journey: `search for <query>` -> `preview source 1` -> `website_preview` widget
  - note: preview now bypasses the confirmation gate correctly; actual open still requires confirmation when planned
- capability `18` `speak_text`
  - first supported user journey: explicit TTS request routed through governed speech output
  - note: classified from controlled routing/executor proof because replaying live audio would mutate the operator runtime without improving truth discovery
- capability `19` `volume_up_down`
  - first supported user journey: explicit volume command -> governed local control executor
- capability `20` `media_play_pause`
  - first supported user journey: explicit media command -> governed local control executor
- capability `21` `brightness_control`
  - first supported user journey: explicit brightness command -> governed local control executor
- capability `22` `open_file_folder`
  - first supported user journey: explicit preset-folder or explicit-path request -> governed open-path executor
- capability `32` `os_diagnostics`
  - first supported user journey: `system status` -> truthful diagnostics payload and trust review refresh
- capability `49` `headline_summary`
  - first supported user journey: `summarize headline 1` -> grounded headline summary
- capability `51` `topic_memory_map`
  - first supported user journey: `show topic memory map` -> structured topic-memory summary
- capability `52` `story_tracker_update`
  - first supported user journey: `track story <topic>` -> tracker snapshot persisted and surfaced truthfully
- capability `53` `story_tracker_view`
  - first supported user journey: `show story <topic>` -> stored story snapshot rendered truthfully
- capability `55` `weather_snapshot`
  - first supported user journey: `weather` -> truthful weather widget and summary
- capability `56` `news_snapshot`
  - first supported user journey: `news` -> headline snapshot widget and follow-up surface
- capability `61` `memory_governance`
  - first supported user journey: `memory overview` -> governed memory widget with truthful counts and links

#### Partial In Current Scope Because Runtime Prerequisites Are Missing
- capability `57` `calendar_snapshot`
  - status: `partial.environment_blocked`
  - first supported user journey: `calendar` -> truthful `Not connected.` response and widget state
- capability `58` `screen_capture`
  - status: `partial.environment_blocked`
  - first supported user journey: `take a screenshot` -> truthful missing-dependency response when `pyautogui` is unavailable
- capability `59` `screen_analysis`
  - status: `partial.environment_blocked`
  - first supported user journey: `analyze screen` -> truthful missing-dependency response through the screen-analysis path when `pyautogui` is unavailable

### Definition Of Done
- explain-anything works reliably for the common real prompts
- intelligence brief is dependable and rendered correctly
- response verification produces visible user payoff
- partial features are either repaired or honestly relabeled

## Workstream 4 - Governance Hardening

### Goal
Prevent future integrations from creating second authority paths or silently drifting away from runtime truth.

### Boundary Files
- `nova_backend/src/governor/network_mediator.py`
- `nova_backend/src/llm/llm_gateway.py`
- `nova_backend/src/llm/model_network_mediator.py`
- `nova_backend/src/governor/governor.py`
- `nova_backend/src/governor/governor_mediator.py`

### Existing Tests To Preserve And Extend
- `nova_backend/tests/adversarial/test_governor_bypass.py`
- `nova_backend/tests/adversarial/test_no_direct_network_imports_outside_network_mediator.py`
- `nova_backend/tests/governance/test_no_direct_ollama_usage.py`
- `nova_backend/tests/governance/test_network_governance_boundaries.py`
- `nova_backend/tests/governance/test_model_network_mediator_thread_safety.py`
- `nova_backend/tests/test_runtime_auditor.py`

### Implementation Tasks
- add or tighten tests that fail when new direct LLM call sites appear outside the approved gateway
- add or tighten tests that fail when new direct network call sites appear outside the approved mediated path
- verify capability registry, runtime docs, and surfaced dashboard claims stay in parity
- extend runtime-auditor checks where needed so capability and trust drift is caught automatically
- add one release-gate checklist run for Phase-6 closure:
  - targeted executor tests
  - trust-panel tests
  - governance boundary tests
  - runtime-auditor tests

### Suggested Verification Commands
- `pytest nova_backend/tests/executors/test_explain_anything_executor.py`
- `pytest nova_backend/tests/executors/test_response_verification_executor.py`
- `pytest nova_backend/tests/executors/test_news_intelligence_executor.py`
- `pytest nova_backend/tests/rendering/test_intelligence_brief_renderer.py`
- `pytest nova_backend/tests/phase45/test_dashboard_trust_review_widget.py`
- `pytest nova_backend/tests/governance/test_screen_capture_requires_invocation.py`
- `pytest nova_backend/tests/adversarial/test_governor_bypass.py`
- `pytest nova_backend/tests/adversarial/test_no_direct_network_imports_outside_network_mediator.py`
- `pytest nova_backend/tests/governance/test_no_direct_ollama_usage.py`
- `pytest nova_backend/tests/test_runtime_auditor.py`

### Definition Of Done
- no direct network bypasses
- no direct LLM bypasses
- runtime truth parity checks are green
- Phase-6 closure packet has concrete evidence instead of design-only intent

## Exit Gate
Phase 6 should not hand off to Phase 7 until:
- Workstreams 1 through 4 are complete or explicitly deferred with truthful wording
- explain-anything and brief are either reliable or clearly relabeled
- trust review and Recent Actions tell the truth about recent behavior
- capability metadata is strong enough to support future external reasoning and execution planning
- the governance regression suite is green

## Related Inputs
- `docs/design/Phase 6/PHASE_6_SOVEREIGNTY_ALIGNMENT_AND_TRUST_LOOP_PLAN.md`
- `docs/design/NOVA_SOVEREIGNTY_PLATFORM_PHASE_REALIGNMENT_2026-03-18.md`
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/design/Phase 8/node design.txt`
