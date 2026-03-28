# Nova + OpenClaw Home Agent — Master Reference
Updated: 2026-03-28
Status: Current design truth + runtime-aligned implementation baseline
Purpose: Hold the single most useful, current, and repo-grounded picture of how Nova and OpenClaw fit together today

## 1. Document Purpose And Authority
This is the master reference for the Nova + OpenClaw home-agent direction.

It exists to answer four questions clearly:
- what is live in runtime now
- what is only a manual foundation
- what is still design-only
- what rules must not be broken as the system grows

Authority order for Phase 8 should be read this way:
1. `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
2. `docs/PROOFS/`
3. `docs/design/Phase 8/NOVA_OPENCLAW_HOME_AGENT_MASTER_REFERENCE_2026-03-27.md`
4. `docs/design/Phase 8/PHASE_8_OPENCLAW_CANONICAL_GOVERNED_AUTOMATION_SPEC_2026-03-25.md`
5. `docs/design/Phase 8/PHASE_8_OPENCLAW_HOME_AGENT_AND_PERSONALITY_LAYER_PLAN_2026-03-26.md`
6. preserved raw notes

Conflict rule:
- runtime truth wins for statements about what is live
- the canonical governed automation spec wins for statements about the eventual strict Phase-8 execution model
- this document is the bridge between those two truths

## 2. The Two-Layer Model
Nova is the visible layer.
OpenClaw is the worker layer inside Nova.

The correct product reading is:
- Nova is the face, voice, trust layer, and explanation surface
- OpenClaw is the bounded worker substrate for task-style runs
- OpenAI is an optional metered lane inside Nova, not a replacement for Nova's local-first identity
- the user talks to Nova, not to OpenClaw
- OpenClaw results are presented through Nova's voice
- OpenClaw is inside Nova governance, never above it

Current practical flow:
1. the user opens the Agent page or triggers a manual template
2. Nova calls the OpenClaw home-agent API
3. the runner gathers structured inputs first
4. one local summary pass may happen at the end
5. the personality bridge rewrites the result into Nova's voice
6. Nova presents the result in chat, widget, or both depending on delivery mode

## 3. What Is Live Today
The following is live in the current repo state.

### Runtime module
`nova_backend/src/openclaw/`

Files and roles:
- `__init__.py`
  - package marker for the OpenClaw home-agent foundation
- `task_envelope.py`
  - small envelope object built from named templates
  - currently used for manual run framing, not broad execution authority
- `agent_runtime_store.py`
  - persistent local operator store
  - holds built-in templates, delivery preferences, and recent runs
- `agent_personality_bridge.py`
  - forces worker results back through Nova-owned presentation
- `agent_runner.py`
  - manual low-token briefing runner
  - currently supports named briefing-style collection, local-first summary behavior, and a narrow metered OpenAI fallback for task reports
- `strict_preflight.py`
  - strict manual-foundation preflight gate
  - validates allowed tools, max steps, max duration, and allowed trigger source before the runner starts
- `agent_scheduler.py`
  - narrow local scheduler for named briefing templates only
  - stays behind explicit runtime settings control and does not widen general execution authority

### Local API surface
`nova_backend/src/api/openclaw_agent_api.py`

Live endpoints:
- `GET /api/openclaw/agent/status`
  - returns agent snapshot, bridge status, connection state, settings snapshot, and setup/readiness detail for the live home-agent surface
- `POST /api/openclaw/agent/templates/{template_id}/delivery`
  - updates template delivery mode
- `POST /api/openclaw/agent/templates/{template_id}/schedule`
  - updates per-template schedule state for schedule-ready templates
- `POST /api/openclaw/agent/templates/{template_id}/run`
  - runs a manual template if `home_agent_enabled` is on

Important runtime truth:
- this is a local operator surface, not the remote token-gated OpenClaw bridge
- the remote token-gated bridge remains `src/api/bridge_api.py`
- the manual home-agent foundation is a separate surface from the remote bridge

### Live templates
The runtime store currently ships with:
- `morning_brief`
  - manual run available
  - named briefing
  - hybrid delivery by default
  - schedule-ready
- `evening_digest`
  - manual run available
  - named briefing
  - hybrid delivery by default
  - schedule-ready
- `inbox_check`
  - visible but not runnable yet
  - future quiet-review connector path
- `market_watch`
  - manual run available
  - read-only market research only
  - no buy, sell, or broker authority

### Live UI surfaces
Frontend pages and controls are live in:
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/style.phase1.css`

What the user can do now:
- open the Agent page
- inspect setup and readiness for local model, weather, calendar, remote bridge, and scheduler inputs
- inspect template readiness
- run `morning_brief`
- run `evening_digest`
- change delivery mode
- enable or pause schedule-ready templates
- inspect next-run state from the Agent page
- review pending surface deliveries from the Home page and Agent page
- dismiss finished surface deliveries after review
- inspect recent run history
- navigate to Settings or Trust from the Agent page

### Live settings and trust integration
- `home_agent_enabled` is a real runtime permission in `runtime_settings_store.py`
- `home_agent_scheduler_enabled` is a real runtime permission in `runtime_settings_store.py`
- `metered_openai_enabled` is a real runtime permission in `runtime_settings_store.py`
- OpenClaw home-agent status appears in diagnostics via `os_diagnostics_executor.py`
- local-first OpenAI routing, budget policy, and a narrow OpenClaw task-report fallback are live in diagnostics and settings
- strict manual preflight status appears in diagnostics and runtime truth
- the runtime auditor already recognizes the home-agent foundation as a live runtime system

### Live test coverage
Current repo-backed coverage includes:
- `nova_backend/tests/openclaw/test_agent_runtime_store.py`
- `nova_backend/tests/openclaw/test_agent_runner.py`
- `nova_backend/tests/openclaw/test_agent_scheduler.py`
- `nova_backend/tests/openclaw/test_task_envelope.py`
- `nova_backend/tests/conversation/test_openclaw_agent_personality_bridge.py`
- `nova_backend/tests/test_openclaw_agent_api.py`
- `nova_backend/tests/executors/test_os_diagnostics_openclaw_agent.py`
- `nova_backend/tests/test_runtime_auditor.py`

## 4. What Is Explicitly Not Live
These items are not live and should not be described as runtime behavior.

Not live:
- broad autonomous scheduling beyond the shipped narrow briefing scheduler
- full GovernorMediator TaskEnvelope execution path
- Data Minimization Engine from the canonical Phase-8 automation spec
- dedicated Governor Interceptor from the canonical Phase-8 automation spec
- capability ID `63` or any registered `openclaw_execute` capability
- broad envelope mode
- Home Assistant control
- MQTT control
- IMAP inbox connector
- Vikunja task connector
- multi-step autonomous worker supervision
- silent always-on household monitoring

Important wording rule:
- say `manual home-agent foundation`
- do not say `full Phase 8 automation is live`

## 5. Free-First Tooling Direction
The current and intended OpenClaw stack remains local-first and cost-conscious.

Already usable now:
- weather via Nova's existing weather skill path
- calendar via existing local ICS calendar path
- news via Nova's existing feed-based news path
- schedule context via local schedule store
- local LLM summarization for brief task reports

Planned free or self-hosted expansions:
- Open-Meteo for weather
- ICS / CalDAV / Nextcloud / Radicale for calendar
- RSS / SearXNG / DuckDuckGo Instant Answer for news and search
- Vikunja or local task store for tasks
- Home Assistant or MQTT for home control
- IMAP or self-hosted mail for inbox review

Guiding rule:
- fetch structured data first
- summarize once
- avoid repeated LLM loops

## 5.1 How OpenClaw Is Set Up Today
OpenClaw currently has two distinct runtime surfaces inside Nova.

### Remote bridge
Files:
- `nova_backend/src/api/bridge_api.py`

Purpose:
- token-gated remote ingress for read, review, and reasoning requests
- stateless stage-1 bridge
- explicitly blocked from widening into local device or durable-state actions

Current requirements:
- `remote_bridge_enabled` must be enabled in runtime settings
- `NOVA_OPENCLAW_BRIDGE_TOKEN` or `NOVA_BRIDGE_TOKEN` must be configured

Current guardrails:
- prefix-based scope blocking still exists
- capability-aware remote-safe blocking now exists on top of that
- local-context and local-effect capabilities stay in the local dashboard

### Local home-agent foundation
Files:
- `nova_backend/src/api/openclaw_agent_api.py`
- `nova_backend/src/openclaw/agent_runtime_store.py`
- `nova_backend/src/openclaw/agent_runner.py`
- `nova_backend/src/openclaw/strict_preflight.py`
- `nova_backend/src/openclaw/agent_scheduler.py`

Purpose:
- manual briefing runs
- narrow scheduled briefing runs
- operator-facing delivery and review

Current requirements:
- `home_agent_enabled` must be enabled
- local model access is preferred for summarization but is not a hard requirement for fallback summaries
- `WEATHER_API_KEY` improves weather completeness but is optional
- `NOVA_CALENDAR_ICS_PATH` enables calendar snapshots but is optional
- `home_agent_scheduler_enabled` must be enabled before timed runs start

Current operator truth:
- the Agent page now shows setup/readiness for the local summarizer, weather, calendar, remote bridge, and scheduler
- `morning_brief` and `evening_digest` are the current runnable templates
- `inbox_check` remains visible as a future connector-backed task

## 6. Token And Model Strategy
Current low-token strategy:
- the runner gathers data first
- the local LLM is only used for final summarization when needed
- Nova then presents the result in its own voice

That means:
- no LLM used as a raw data fetcher
- no repeated reprompt loop for each tool step
- no cloud-token dependency required for the manual foundation

Current practical model split:
- Nova chat keeps its normal conversational routing
- task-style home-agent reports use the `task_report` communication profile
- the OpenClaw runner estimates token use and records it in recent runs

Product rule:
- local free LLM use is acceptable
- Nova should still feel like the personality agent on the surface
- OpenClaw should stay invisible unless the user is inspecting the operator surface

## 7. Governance Invariants
These rules are non-negotiable.

1. Nova remains the visible voice.
2. OpenClaw stays inside Nova governance.
3. Manual home-agent runs are not proof of broad execution authority.
4. No background scheduler beyond the explicit narrow briefing scheduler carve-out is live until explicitly designed, implemented, and audited.
5. The home-agent surface must stay truthful about what is ready now versus planned later.
6. Worker results must go through Nova-owned presentation.
7. Outbound HTTP still belongs under Nova's governed network rules.
8. The existence of `src/openclaw/` does not authorize silent automation.

Current governance note:
- `test_no_background_screen_monitoring.py` now scans `src/openclaw/`
- that is correct for the current foundation stage because only the explicit narrow briefing scheduler carve-out is live
- any wider scheduler carve-out must remain explicit, narrow, and documented

## 8. Delivery Model
Current delivery behavior is already richer than a placeholder and now spans manual plus narrow scheduled delivery.

Live now:
- named briefing templates can use delivery modes
- delivery modes normalize to `widget`, `chat`, or `hybrid`
- current defaults:
  - `morning_brief` -> `hybrid`
  - `evening_digest` -> `hybrid`
  - `inbox_check` -> `widget`

Current truth:
- delivery modes control presentation channels for manual runs and the explicit narrow scheduled briefing lane
- they do not imply broad proactive background automation
- surface-first delivery now includes a persistent delivery inbox for widget/hybrid runs and scheduled deliveries

Longer-term desired model:
- named briefings can feel like Nova check-ins
- quiet review tasks stay surface-first
- failures remain inspectable instead of noisy

## 9. Phase Roadmap
The honest roadmap is:

### Phase 8 foundation
Live now:
- manual home-agent runtime store
- envelope-shaped manual task framing
- operator-facing Agent page
- delivery controls
- Nova-owned presentation bridge

### Phase 8.5
Live now:
- scheduler design packet
- narrow scheduled delivery behind explicit runtime settings control
- operator-visible schedule enable/pause and next-run visibility
- precise governance carve-out for the scheduler location

Still ahead inside the same lane:
- operator-visible rate limiting and quiet-hours suppression
- richer proactive notification UX beyond the current delivery inbox plus chat-surface model

### Full canonical Phase 8 execution
Still ahead:
- dedicated envelope-governed execution path
- stricter interception
- normalization and minimization layers
- wider operator surfaces for stopping, reviewing, and auditing action-level work

### Phase 9+
Later work:
- home connectors
- inbox connectors
- task manager connectors
- broader bounded worker usefulness under explicit budgets

## 10. Gap Analysis
The major remaining gaps are:
- no full strict Phase-8 execution substrate
  - impact: operator surface exists before full governed execution architecture
- no quiet-hours or rate-limit suppression for scheduled runs yet
  - impact: narrow scheduling is live, but the broader operator controls for suppression are still incomplete
- no richer proactive notification push beyond chat/inbox
  - impact: delivery is visible and timed now, but still intentionally narrow
- `inbox_check` is visible but not connected
  - impact: product promise is ahead of connector readiness
- no Home Assistant or MQTT connector
  - impact: not yet a real home-control worker
- no IMAP or task connector
  - impact: household utility remains briefing-first
- no full action-level stop/review surface for broader governed execution
  - impact: the narrow scheduler is inspectable, but the canonical Phase-8 operator model is still ahead

## 11. Cross-Reference Map
Most important files for this topic:

Design:
- `docs/design/Phase 8/PHASE_8_OPENCLAW_CANONICAL_GOVERNED_AUTOMATION_SPEC_2026-03-25.md`
- `docs/design/Phase 8/PHASE_8_OPENCLAW_HOME_AGENT_AND_PERSONALITY_LAYER_PLAN_2026-03-26.md`
- `docs/design/Phase 8/PHASE_8_5_SCHEDULER_AND_PROACTIVE_DELIVERY_PLAN_2026-03-27.md`
- `docs/design/Phase 8/PHASE_8_ADVANCED_GOVERNOR_LAYER_ARCHITECTURE_2026-03-27.md`
- `docs/design/Phase 8/OPENAI_AGENT_OPERATING_MODEL_2026-03-27.md`
- `docs/design/Phase 8/OPENAI_PROVIDER_ROUTING_AND_BUDGET_POLICY_2026-03-27.md`
- `docs/design/Phase 8/OPENAI_USAGE_VISIBILITY_SPEC_2026-03-27.md`
- `docs/design/Phase 8/TRADING_MODE_GUARDRAILS_2026-03-27.md`
- `docs/design/Phase 8/PHASE_8_DOCUMENT_MAP.md`

Runtime:
- `nova_backend/src/openclaw/task_envelope.py`
- `nova_backend/src/openclaw/agent_runtime_store.py`
- `nova_backend/src/openclaw/agent_personality_bridge.py`
- `nova_backend/src/openclaw/agent_runner.py`
- `nova_backend/src/openclaw/agent_scheduler.py`
- `nova_backend/src/api/openclaw_agent_api.py`
- `nova_backend/src/settings/runtime_settings_store.py`
- `nova_backend/src/executors/os_diagnostics_executor.py`
- `nova_backend/src/audit/runtime_auditor.py`

Frontend:
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/style.phase1.css`

Runtime truth:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- `docs/current_runtime/GOVERNANCE_MATRIX_TREE.md`

Proof:
- `docs/PROOFS/Phase-8/PHASE_8_PROOF_PACKET_INDEX.md`
- `docs/PROOFS/Phase-8/PHASE_8_MANUAL_FOUNDATION_AND_DELIVERY_INBOX_RUNTIME_SLICE_2026-03-27.md`
- `docs/PROOFS/Phase-8/PHASE_8_5_NARROW_SCHEDULER_RUNTIME_SLICE_2026-03-27.md`

Tests:
- `nova_backend/tests/openclaw/`
- `nova_backend/tests/test_openclaw_agent_api.py`
- `nova_backend/tests/test_runtime_auditor.py`
- `nova_backend/tests/governance/test_no_background_screen_monitoring.py`

## 12. The Next Three Things
The next highest-value follow-through is:

1. add an explicit Phase 8 row to runtime truth
   - done in this pass through the runtime auditor and regenerated runtime docs

2. keep the Phase 8 planning docs truthful
   - the home-agent and personality-layer packet must describe the live narrow scheduler honestly, not collapse it into “full automation”

3. finish the remaining narrow scheduler controls before widening anything
   - add quiet-hours and rate-limit suppression
   - keep the carve-out precise and auditable

Bottom line:
- Nova now has a real manual OpenClaw home-agent foundation
- that foundation improves the product today
- it does not mean the full canonical Phase-8 governed automation stack is complete
