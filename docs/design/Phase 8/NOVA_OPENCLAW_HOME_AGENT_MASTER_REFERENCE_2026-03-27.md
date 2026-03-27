# Nova + OpenClaw Home Agent — Master Reference
**Date:** 2026-03-27
**Status:** Current design truth + implementation baseline

---

## Section 1 — Document Purpose and Authority

This is the master reference for the Nova + OpenClaw home agent and personality direction. It captures the complete picture: what is live today, what is designed but not yet built, what is explicitly deferred, and what is future-only.

This document supersedes scattered notes from prior planning sessions. It defers to `PHASE_8_OPENCLAW_CANONICAL_GOVERNED_AUTOMATION_SPEC_2026-03-25.md` for execution governance details — that document wins any conflict on governance invariants, capability registration, and GovernorMediator wiring.

**Cross-references:**
- Canonical governance spec: `docs/design/Phase 8/PHASE_8_OPENCLAW_CANONICAL_GOVERNED_AUTOMATION_SPEC_2026-03-25.md`
- Execution plan: `docs/design/Phase 8/PHASE_8_OPENCLAW_GOVERNED_EXECUTION_PLAN.md`
- Implementation plan (predecessor): `docs/design/Phase 8/PHASE_8_OPENCLAW_HOME_AGENT_AND_PERSONALITY_LAYER_PLAN_2026-03-26.md`
- Phase 8 folder navigation: `docs/design/Phase 8/PHASE_8_DOCUMENT_MAP.md`
- Runtime state (auto-generated, may lag): `docs/current_runtime/CURRENT_RUNTIME_STATE.md`

---

## Section 2 — The Full Two-Layer Model

Nova is the personality face. OpenClaw is the silent background worker. The user never interacts with OpenClaw directly — they always talk to Nova.

```
TOP LAYER: NOVA (personality agent, user-facing)
  - Warm, calm, direct presence
  - Speaks like a trusted household intelligence
  - Owns all results — user always talks to Nova, never to a task runner
  - Temperature: 0.68 balanced, 0.75 conversational, 0.55 task_report
  - System prompt updated to reflect personality-forward identity

BOTTOM LAYER: OPENCLAW (silent worker, never user-facing)
  - Runs tasks under TaskEnvelope governance
  - Reports results back to Nova's personality bridge
  - Nova presents results as its own output
  - User never sees "task runner completed" language
```

### How a run flows

1. User triggers a named envelope (or, in Phase 8.5+, the scheduler triggers it automatically)
2. OpenClaw agent runner picks up the envelope
3. Runner calls data APIs sequentially — weather, news, calendar, system — zero LLM tokens at this stage
4. Runner calls the local LLM exactly once at the end with all collected data
5. Raw result passes through `agent_personality_bridge.py`
6. Nova's personality bridge formats the output in Nova's voice
7. Nova presents the result — the word "OpenClaw" or "task runner" never appears

---

## Section 3 — What Is Live Today (as of 2026-03-27)

Everything in this section was implemented in the Phase 8.0 foundation implementation pass.

### Backend — `nova_backend/src/openclaw/` (new module)

| File | What it does |
|---|---|
| `__init__.py` | Module init. Exports `OPENCLAW_MODULE_VERSION = "0.1.0"`. |
| `task_envelope.py` | `TaskEnvelope` dataclass: `id`, `title`, `tools_allowed`, `max_steps`, `max_duration_s`, `created_at`, `status` (pending / running / complete / stopped / failed), `triggered_by` (schedule / user / bridge), `result_text`. |
| `agent_runtime_store.py` | In-memory store for active and recent envelopes. Methods: `register`, `update_status`, `get_active`, `get_recent`, `stop_all`, `stop_by_id`. Thread-safe. Keeps last 50 completed runs. |
| `agent_personality_bridge.py` | Formats OpenClaw task results through Nova's voice. Voice templates per envelope type: `morning_brief`, `evening_digest`, `inbox_check`, `task_run`, `default`. Method: `format_for_nova(envelope, raw_result) -> str`. Nova presents this — never the raw task output. |
| `agent_runner.py` | `OpenClawAgentRunner`. Manual execution only (scheduler explicitly deferred to Phase 8.5). Runs envelope: calls existing weather / news / calendar skills (zero LLM), then calls LLM once at end to summarize. Respects tool allowlist from envelope. Returns structured result dict. |

### Backend — `nova_backend/src/api/openclaw_agent_api.py` (new API)

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/openclaw/agent/status` | GET | Returns agent runtime status: active envelopes, last run time, module version, feature flags. |
| `/api/openclaw/agent/run` | POST | Manually trigger a named envelope. Token-gated (same token as bridge). Body: `{"envelope": "morning_brief"}`. Returns result through personality bridge. |
| `/api/openclaw/agent/stop` | POST | Stop a running envelope by id, or stop all active envelopes. |
| `/api/openclaw/agent/recent` | GET | Returns last N completed envelope runs with timestamps and summaries. |

### Backend — Modified Files

| File | Change |
|---|---|
| `nova_backend/src/nova_config.py` | Updated `SYSTEM_PROMPT`: Nova is now personality-forward — warm, calm, direct, owns results. Added `conversational` profile (temp 0.75, 512 tokens) and `task_report` profile (temp 0.55, 384 tokens) to `COMMUNICATION_PROFILES`. |
| `nova_backend/src/personality/interface_agent.py` | Added `present_agent_result(task_title, result_text) -> str` method. Nova presents task results through its voice, never surfacing OpenClaw as the source. |
| `nova_backend/src/personality/conversation_personality_agent.py` | Added `present_agent_result` passthrough. |
| `nova_backend/src/settings/runtime_settings_store.py` | Added `home_agent_enabled` permission (default false, user-controlled). Controls whether the agent API endpoint accepts run requests. |
| `nova_backend/src/executors/os_diagnostics_executor.py` | Added `_agent_status_details()` method. Returns agent module version, whether enabled, last run time. Surfaces in Trust Center diagnostics. |
| `nova_backend/src/brain_server.py` | Registered `openclaw_agent_api` router. Agent status wired into startup diagnostics. |

### Frontend

| File | Change |
|---|---|
| `nova_backend/static/index.html` | Added `page-agent` page div with: active envelope status, recent runs list, manual run trigger buttons for `morning_brief` / `evening_digest` / `inbox_check`, stop button, schedule status (displays "scheduler not yet active" — honest). |
| `nova_backend/static/dashboard.js` | Added `showAgentPage()`, `renderAgentStatus()`, `renderRecentAgentRuns()`, agent nav link in primary nav strip, `triggerAgentRun(envelopeName)`, `stopAgentRun()`. |
| `nova_backend/static/style.phase1.css` | Added `.agent-page-grid`, `.agent-run-row`, `.agent-status-chip` styles consistent with existing design language. |

### Tests Added

| Test file | Coverage |
|---|---|
| `nova_backend/tests/openclaw/test_agent_runtime_store.py` | Store register / update / stop / recent behavior. |
| `nova_backend/tests/openclaw/test_agent_runner.py` | Manual run, tool dispatch, LLM call once at end, error handling. |
| `nova_backend/tests/conversation/test_openclaw_agent_personality_bridge.py` | `format_for_nova` voice templates, no task-runner language in output. |
| `nova_backend/tests/test_openclaw_agent_api.py` | Status endpoint, run endpoint (token auth, envelope validation, `home_agent_enabled` gate), stop endpoint, recent endpoint. |
| `nova_backend/tests/test_runtime_settings_api.py` | `home_agent_enabled` permission present and defaults false. |
| `nova_backend/tests/executors/test_os_diagnostics_openclaw_agent.py` | Agent status details returned by diagnostics. |

---

## Section 4 — What Is Explicitly NOT Live (Design-Only, Deferred)

These items are designed but not yet built. Do not treat them as live.

| Item | Status | Deferred To |
|---|---|---|
| APScheduler / cron-based scheduling | NOT LIVE | Phase 8.5 |
| Proactive push notifications (Option C quiet mode) | NOT LIVE | Phase 8.5 |
| Home Assistant REST integration | NOT LIVE | Phase 9 |
| MQTT broker integration | NOT LIVE | Phase 9 |
| IMAP email reader | NOT LIVE | Phase 9 |
| Vikunja task manager integration | NOT LIVE | Phase 9 |
| Capability ID 63 (`openclaw_execute`) | NOT REGISTERED | Phase 8 full |
| GovernorInterceptor (Phase 8 spec) | NOT BUILT | Phase 8 full |
| DataMinimizationEngine | NOT BUILT | Phase 8 full |
| ExecuteBoundary hardening for agent | NOT BUILT | Phase 8 full |
| TaskEnvelope in GovernorMediator path | NOT WIRED | Phase 8 full |
| OpenClawAdapter (proposals model) | NOT BUILT | Phase 8 full |
| Broad Envelope mode | NOT AUTHORIZED | Phase 9 |
| Silent supervisory execution | NOT AUTHORIZED | Phase 10+ |

---

## Section 5 — The Free/Open-Source API Stack

Every free API that powers or will power home agent tools. No paid dependencies.

### Currently Usable (Phase 8 — skills already exist)

| Tool | API | Endpoint | Cost | Auth | Notes |
|---|---|---|---|---|---|
| Weather | Open-Meteo | `https://api.open-meteo.com/v1/forecast` | Free forever | None | No API key. JSON response. Replaces any OpenWeatherMap dependency. |
| Calendar | ICS file (CalendarSkill) | Local `.ics` file | Free | None | Export from Google / Outlook / Apple. Already in Nova. |
| News | RSS feedparser | Any RSS URL | Free | None | BBC, AP, Reuters, Hacker News. Already in Nova's news skill. |
| System status | `psutil` (local) | Python library | Free | None | Already in Nova. |

### Phase 9 — New Integrations

| Tool | API | Endpoint | Cost | Auth | Notes |
|---|---|---|---|---|---|
| Tasks | Vikunja | `https://your-vikunja/api/v1/tasks` | Free, self-host | API token | Best self-hosted task manager. Full REST API. |
| Home control | Home Assistant | `http://homeassistant.local:8123/api/services/...` | Free, self-host | Long-lived token | POST to control lights, locks, switches. |
| Home control (alt) | MQTT + Mosquitto | Local broker | Free, self-host | Optional | OpenClaw publishes to broker. Devices subscribe. |
| Email read | Python `imaplib` | IMAP (standard) | Free | IMAP credentials | Read-only. Nova never writes to mailbox. |
| Email (self-hosted) | Mailu or Mailcow | REST API | Free, self-host | Token | Full self-hosted mail server option. |
| Web search | SearXNG | `http://your-searxng/search?q=...&format=json` | Free, self-host | None | Best option. No tracking. |
| Web search (alt) | DuckDuckGo Instant Answer | `https://api.duckduckgo.com/?q=...&format=json` | Free | None | Limited but instant. No key required. |

### CalDAV — Self-Hosted Calendar Options

| Option | Tool | Notes |
|---|---|---|
| Lightweight | Radicale | Self-host CalDAV. Python-based. Very simple. |
| Full suite | Nextcloud Calendar | If already running Nextcloud. CalDAV + REST. |

---

## Section 6 — Model Routing Strategy (Token Efficiency)

The design principle is **data first, summarize once**. The LLM is called exactly once per envelope run, after all data APIs have been queried.

```
For any agent task:
  1. Call all data APIs first (0 LLM tokens)
  2. Call LLM exactly ONCE at the end with all collected data
  3. Instruction: "Summarize this data in Nova's voice. 2-4 sentences. Direct and calm."
  4. Pass result through personality bridge
  5. Nova presents it
```

### Per-task LLM budget

| Task | LLM calls | Approximate tokens |
|---|---|---|
| `morning_brief` | 1 | ~250 tokens |
| `evening_digest` | 1 | ~200 tokens |
| `inbox_check` | 1 per batch of 10 emails | ~300 tokens |
| Calendar summary | 1 (optional) | ~80 tokens — may be skipped if structured data is enough |
| Home command | 0 | Deterministic — no LLM |
| Weather check | 0 | Deterministic — no LLM |

### Model assignments

| Use | Model | Why |
|---|---|---|
| Nova conversational chat | `gemma2:2b` (primary) | Better natural language quality |
| Agent task summarization | `phi3:mini` (dedicated) | Fast, structured output, great tool calling, 1.3B |
| Classification micro-tasks | `qwen2.5:0.5b` (optional future) | Ultra-fast yes/no decisions |

---

## Section 7 — Governance Invariants That Must Never Change

These are non-negotiable for all home agent work. Any change to these requires a formal design document update.

1. **Every execution must be associated with an active TaskEnvelope.** No default execution context.
2. **OpenClaw never talks to the user directly.** All results go through Nova's personality bridge.
3. **The scheduler (when added) lives only in `src/openclaw/agent_scheduler.py`.** That path is explicitly excluded from `test_no_background_screen_monitoring.py`.
4. **`home_agent_enabled` permission is the gate.** If false, all agent run requests are rejected at the API layer.
5. **No silent supervisory execution.** Every run is visible in the agent page and ledger.
6. **Nova's voice owns all results.** The words "OpenClaw", "task runner", "agent completed" must never appear in user-facing output.
7. **All outbound HTTP goes through NetworkMediator.** Agent tools are no exception.
8. **Local LLM only for summarization.** No cloud API calls from agent tools.

---

## Section 8 — Option C Delivery Mode (Confirmed Product Direction)

The confirmed delivery model is task-type-aware. Different task types reach the user in different ways.

| Task type | Delivery method | Behavior |
|---|---|---|
| Scheduled quiet tasks (weather update, inbox check) | Widget / notification push | User sees it on next dashboard open. No chat message. |
| Named daily briefs (`morning_brief`, `evening_digest`) | Chat message from Nova | Nova sends a proactive chat message. Feels like a check-in. |
| Manual user-triggered runs | Inline chat response | Nova responds in the chat like any other message. |
| Background failures | Quiet error chip in agent page | No interruption. Visible on agent page only. |

**Current state:** Option A (widget push only) is the starting implementation. Scheduled push is not live yet. Option C full behavior — proactive chat messages from the scheduler — arrives in Phase 8.5.

---

## Section 9 — Phase Roadmap for Home Agent

| Phase | What ships | Scheduler? | LLM calls per run | Status |
|---|---|---|---|---|
| **8.0 Foundation** (NOW) | TaskEnvelope, AgentRuntimeStore, personality bridge, manual run API, agent page UI, `home_agent_enabled` setting | Manual only | 1 | IMPLEMENTED |
| **8.5 Scheduler** | APScheduler in `src/openclaw/agent_scheduler.py`, morning_brief + evening_digest schedules, Option C proactive chat messages, rate limiting | Yes — cron | 1 | NEXT |
| **8 Full** | GovernorInterceptor, DataMinimizationEngine, ExecuteBoundary hardening, capability ID 63, TaskEnvelope wired into GovernorMediator | Yes | 1 | PLANNED |
| **9** | Home Assistant, MQTT, IMAP email, Vikunja, Broad Envelope mode with explicit budgets | Yes | 1 | PLANNED |
| **10+** | Supervisory quietness, deeper household automation, user-reviewable autonomous run history | Yes | 1 max | FUTURE |

---

## Section 10 — What Is Still Missing As A Product (Gap Analysis)

Every user-visible gap, stated honestly.

| Gap | Impact | Phase |
|---|---|---|
| No scheduling yet — agent doesn't run proactively | Home agent feels manual, not autonomous | 8.5 |
| No Home Assistant integration — can't control home devices | Core "home agent" promise not yet fulfilled | 9 |
| No email reading — can't triage inbox proactively | Major daily value missing | 9 |
| No task manager integration — tasks are static JSON only | Task management feels disconnected | 9 |
| Bridge scope block is prefix-only | Paraphrased effectful requests may pass through | 8 full |
| `invocation_source: "openclaw_bridge"` field is inert | Bridge call type not differentiated in ledger | 8 full |
| No rate limiting on bridge or agent API | Token-holding caller could flood Nova | 8.5 |
| No session context across bridge calls | Bridge is single-turn only | Phase 9 |
| Agent page shows "scheduler not active" — feels incomplete | Trust issue for new users | 8.5 |
| Nova voice allowlist not fully protecting short phrases | "Got it." / "Done." could still be stripped | Should fix now |
| `CURRENT_RUNTIME_STATE.md` does not reflect Phase 8 foundation | Runtime doc is stale | Update when regenerated |

---

## Section 11 — Cross-Reference Map (Where Every Piece Lives)

### Design Documents

| Document | Purpose |
|---|---|
| `docs/design/Phase 8/PHASE_8_OPENCLAW_CANONICAL_GOVERNED_AUTOMATION_SPEC_2026-03-25.md` | Canonical governance spec. Wins all conflicts. |
| `docs/design/Phase 8/PHASE_8_OPENCLAW_GOVERNED_EXECUTION_PLAN.md` | Supporting execution sequence |
| `docs/design/Phase 8/PHASE_8_OPENCLAW_HOME_AGENT_AND_PERSONALITY_LAYER_PLAN_2026-03-26.md` | Implementation plan that preceded this document |
| `docs/design/Phase 8/NOVA_OPENCLAW_HOME_AGENT_MASTER_REFERENCE_2026-03-27.md` | **THIS DOCUMENT** — master truth |
| `docs/design/Phase 8/PHASE_8_DOCUMENT_MAP.md` | Phase 8 folder navigation guide |
| `docs/current_runtime/CURRENT_RUNTIME_STATE.md` | Live runtime state (auto-generated — will need regeneration) |

### Runtime Code

| Path | Purpose |
|---|---|
| `nova_backend/src/openclaw/` | Home agent module (new) |
| `nova_backend/src/api/openclaw_agent_api.py` | Agent HTTP API (new) |
| `nova_backend/src/api/bridge_api.py` | Original read-only bridge (existing) |
| `nova_backend/src/personality/interface_agent.py` | Nova voice layer (updated) |
| `nova_backend/src/nova_config.py` | System prompt + comm profiles (updated) |
| `nova_backend/src/settings/runtime_settings_store.py` | `home_agent_enabled` permission (updated) |
| `nova_backend/src/executors/os_diagnostics_executor.py` | Agent diagnostics in Trust Center (updated) |

### Tests

| Path | Coverage |
|---|---|
| `nova_backend/tests/openclaw/test_agent_runtime_store.py` | Store behavior |
| `nova_backend/tests/openclaw/test_agent_runner.py` | Runner execution |
| `nova_backend/tests/conversation/test_openclaw_agent_personality_bridge.py` | Voice bridge |
| `nova_backend/tests/test_openclaw_agent_api.py` | API endpoints |
| `nova_backend/tests/executors/test_os_diagnostics_openclaw_agent.py` | Diagnostics |
| `nova_backend/tests/test_openclaw_bridge_api.py` | Original bridge (unchanged) |
| `nova_backend/tests/governance/test_no_background_screen_monitoring.py` | Must exclude `src/openclaw/` from scheduler scan |

---

## Section 12 — The Next Three Things (Ordered By Value)

After this document is written, the next concrete work items in order:

### 1. Add `src/openclaw/` exclusion to `test_no_background_screen_monitoring.py`

This governance test currently scans for background execution patterns. The future scheduler in `src/openclaw/agent_scheduler.py` is an authorized exception — it is the designated and only allowed location for scheduled execution in this codebase. Explicitly carve out the `src/openclaw/` directory with a comment explaining why it is allowed there. Without this change, Phase 8.5 scheduler code will trigger a false governance failure.

### 2. Add Phase 8.5 design packet

Create `docs/design/Phase 8/PHASE_8_5_SCHEDULER_AND_PROACTIVE_DELIVERY_PLAN.md` before writing any scheduler code. This document should cover: APScheduler integration approach, the Option C full delivery mode, rate limiting design, and the `morning_brief` / `evening_digest` schedule definitions (times, retry policy, failure handling).

### 3. Regenerate `CURRENT_RUNTIME_STATE.md`

The runtime state document predates the Phase 8 foundation work. Run `scripts/generate_runtime_docs.py` to update it. The new document should reflect: the `src/openclaw/` module, the new API routes, the `home_agent_enabled` permission, and the new test surface.
