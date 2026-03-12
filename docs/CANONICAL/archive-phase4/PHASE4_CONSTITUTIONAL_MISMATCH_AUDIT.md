> STATUS (2026-03-12): HISTORICAL PHASE-4 ARTIFACT
> This file is retained for traceability and historical audit context.
> For current canonical runtime truth, use:
> - docs/current_runtime/CURRENT_RUNTIME_STATE.md
> - docs/PROOFS/Phase-5/PHASE_5_PROOF_PACKET_INDEX.md
> - docs/canonical/CANONICAL_DOCUMENT_MAP.md
# Nova Phase-4 Constitutional Mismatch Audit + Unified Runtime Spec v1.0

## SECTION 1 â€” MISMATCH REPORT

### [A. Governor Layer]
File: `nova_backend/src/brain_server.py`  
Line: 288-298  
Violation: The runtime executes `skill.handle(...)` directly in the WebSocket loop when no governed invocation is detected, creating a parallel execution path outside the Governor choke point.  
Invariant Broken: (2) All execution routes through a single Governor choke point; (3) No direct executor calls outside Governor; (15) No silent execution.  
Severity: Critical

### [A. Governor Layer]
File: `nova_backend/src/skill_registry.py`  
Line: 25-35, 38-62  
Violation: Skills are instantiated and invoked directly by the registry path without capability registry checks, phase gate checks, or `ActionRequest` creation.  
Invariant Broken: (1) Intelligenceâ€“Authority Split is absolute; (2) single Governor choke point; (3) no direct execution path outside Governor.  
Severity: Critical

### [B. Ledger Layer]
File: `nova_backend/src/brain_server.py`  
Line: 288-356  
Violation: Skill execution (including network-backed skills and Deep Thought path) occurs with no `ACTION_ATTEMPTED` or `ACTION_COMPLETED` events; those events are only emitted by Governor execution path.  
Invariant Broken: (6) Ledger logs ACTION_ATTEMPTED before execution; (15) No silent execution.  
Severity: Critical

### [B. Ledger Layer]
File: `nova_backend/src/ledger/writer.py`  
Line: 21-25  
Violation: `event_type` is accepted as an unconstrained argument and no allowlist is enforced at write boundary, so canonical event names are not hard-locked at ledger boundary.  
Invariant Broken: Hardcoded canonical event taxonomy requirement in audit brief.  
Severity: Major

### [C. Network Layer]
File: `nova_backend/src/llm/llm_manager.py`  
Line: 10, 62, 87-91, 257-260  
Violation: Direct `requests` session/network calls exist outside `NetworkMediator`.  
Invariant Broken: (5) Network calls must route through NetworkMediator; network-layer rule â€œNo direct HTTP usage outside NetworkMediator.â€  
Severity: Critical

### [C. Network Layer]
File: `nova_backend/src/llm/llm_manager_vlock.py`  
Line: 16, 68, and direct session HTTP call sites in this module  
Violation: Direct `requests` usage exists outside `NetworkMediator`.  
Invariant Broken: (5) Network calls must route through NetworkMediator.  
Severity: Critical

### [C. Network Layer]
File: `nova_backend/src/governor/network_mediator.py`  
Line: 195-206  
Violation: Module-level singleton explicitly documents and enables non-governed callers (â€œbypass Governor routing intentionallyâ€) via `capability_id=None`.  
Invariant Broken: (2) single Governor choke point; no bypass path.  
Severity: Critical

### [D. Skills Layer]
File: `nova_backend/src/skills/weather.py` + `nova_backend/src/services/weather_service.py`  
Line: `weather.py` 17, 23-24; `weather_service.py` 7, 49-58  
Violation: Skill path performs outbound network access from skill runtime via service call instead of Governor action mediation.  
Invariant Broken: Skills must not perform network requests directly; all execution through Governor.  
Severity: Critical

### [D. Skills Layer]
File: `nova_backend/src/skills/news.py` + `nova_backend/src/tools/rss_fetch.py`  
Line: `news.py` 12, 38-41, 60-65; `rss_fetch.py` 6, 25-34  
Violation: News skill performs live network retrieval in skill path (RSS fetch) without Governor action mediation.  
Invariant Broken: Skills do not touch network directly; all execution via Governor; no fallback retrieval outside governed tools.  
Severity: Critical

### [D. Skills Layer]
File: `nova_backend/src/skills/general_chat.py`  
Line: 194-202  
Violation: Skill can invoke Deep Thought (`self.deepseek.process`) from skill layer based on policy, i.e., skill-initiated escalation path.  
Invariant Broken: Skills do not escalate automatically; skills do not initiate authority-bearing operations.  
Severity: Critical

### [E. Deep Thought Integration]
File: `nova_backend/src/conversation/escalation_policy.py` + `nova_backend/src/skills/general_chat.py`  
Line: `escalation_policy.py` 17-35; `general_chat.py` 174-205  
Violation: Escalation policy returns `ALLOW` automatically, causing automatic Deep Thought invocation without explicit user invocation.  
Invariant Broken: (11) Deep Thought advisory only; no automatic escalation.  
Severity: Critical

### [E. Deep Thought Integration]
File: `nova_backend/src/conversation/prompts.py`  
Line: 1-13  
Violation: Deep Thought request path injects internal system prompt and recent context into composed prompt; this is hidden augmentation rather than minimal pass-through wrapper.  
Invariant Broken: Deep Thought verification requirement â€œNo prompt augmentation / no hidden system context injection.â€  
Severity: Major

### [F. TTS (Capability 18)]
File: `nova_backend/src/brain_server.py`  
Line: 256-262, 339-343, 355-356  
Violation: TTS is auto-invoked for voice channel responses (`governor.handle_governed_invocation(18, ...)`) without explicit user TTS invocation each turn.  
Invariant Broken: (12) TTS invocation-bound only; no automatic speech execution.  
Severity: Major

### [G. STT Pipeline]
No constitutional mismatches found.

### [H. UI Layer]
No constitutional mismatches found.

### [I. Hidden Flags / Authority Expansion]
File: `nova_backend/src/audio_manager.py`  
Line: 47-56  
Violation: Background worker loop is started via `loop.create_task(self._worker())` and runs continuously.  
Invariant Broken: (9) No background reasoning threads; hidden/background execution surface prohibition in audit brief.  
Severity: Major

File: `nova_backend/src/governor/network_mediator.py`  
Line: 198-206  
Violation: Explicitly documented bypass route for skill/tool callers outside Governor authority boundary.  
Invariant Broken: no bypass/backdoor capability paths.  
Severity: Critical

---

## SECTION 2 â€” Unified Nova Runtime Spec v1.0 (As-Implemented)

### 1) Governor Spine
- Runtime has a Governor class that owns execution boundary, single-action queue, capability registry, network mediator, and ledger (lazy-loaded). (`governor.py`)
- Governed entrypoint is `Governor.handle_governed_invocation(capability_id, params)`.
- Governed route validates capability, phase gate, queue, logs `ACTION_ATTEMPTED`, creates immutable `ActionRequest`, routes to executor, then logs `ACTION_COMPLETED` best-effort.
- **As-implemented divergence:** non-governed skill path still exists in `brain_server.py` and runs outside Governor.

### 2) Capability Registry
- Registry source is `src/config/registry.json` with schema_version `1.0`, phase `4`.
- `CapabilityRegistry` fail-closes on missing/malformed schema or phase mismatch.
- Enabled gate requires both `status == "active"` and `enabled == true`.

### 3) Skills Contract (Runtime Reality)
- Skills are registered in fixed deterministic order: `SystemSkill`, `WeatherSkill`, `NewsSkill`, fallback `GeneralChatSkill`.
- Skills return `SkillResult` structure with message/data/widget payload fields.
- **As-implemented authority scope:** weather/news/deep thought paths perform network-backed operations in skills layer via non-governed routing.
- Skill routing is deterministic iteration order; no dynamic plugin loader detected.

### 4) Execution Flow
- WebSocket input â†’ mediator parse.
- If explicit governed invocation found (`search`, `open`, `speak` patterns), runtime routes through Governor.
- Else runtime executes skill path directly in WebSocket handler.
- Result is sent to UI; voice channel can auto-trigger TTS governed invocation.

### 5) Ledger Contract
- Ledger is append-only JSONL at `src/data/ledger.jsonl`.
- Each write flushes + `os.fsync`.
- Governor path writes `ACTION_ATTEMPTED` pre-execution and `ACTION_COMPLETED` post-execution (best-effort).
- Network mediator logs `EXTERNAL_NETWORK_CALL` and `NETWORK_CALL_FAILED`.
- Ledger write failure raises `LedgerWriteFailed`.
- **As-implemented gap:** skill-path execution is not wrapped by attempted/completed action events.

### 6) Network Contract
- `NetworkMediator.request(...)` enforces scheme checks, localhost/private-IP blocking for literals, rate limiting, timeout, and ledger logging.
- Governed web search executor uses Governor-owned mediator instance.
- A module singleton `network_mediator` is also exposed for non-governed skill/tool callers (`capability_id=None`).
- **As-implemented gap:** additional direct `requests` use exists in LLM manager modules.

### 7) Deep Thought Contract
- Deep Thought path implemented via `DeepSeekBridge.process(...)` calling DeepSeek API through `network_mediator` singleton.
- Escalation decision = heuristics + policy (`ALLOW`/`DENY`/`ASK_USER`).
- On `ALLOW`, deep analysis runs and response passes through safety + formatter.
- Thought metadata stored in TTL in-memory `ThoughtStore` for UI retrieval.
- **As-implemented gaps:** automatic escalation exists; prompt/context augmentation exists.

### 8) TTS Contract
- Capability 18 executor uses local `pyttsx3` and speaks supplied `text`.
- If no text provided, returns governed failure.
- Brain server auto-fills text for explicit `speak that` command using last response.
- **As-implemented gap:** voice-channel auto-speak invokes capability 18 automatically after many responses.

### 9) STT Contract
- STT endpoint `/stt/transcribe` accepts uploaded audio bytes.
- Pipeline: ffmpeg conversion (local subprocess) â†’ Vosk local transcription.
- Returns text only, no direct action execution.
- No wake-word activation path detected in router/engine.

### 10) UI Constitutional Rules (Runtime Reality)
- UI uses websocket event stream; chat append behavior preserves chronology by append order.
- No explicit predictive prefetch logic detected.
- Deep-thought visibility is user-initiated via â€œâ“˜ Show reasoningâ€ fetch (`get_thought`).

### 11) Orb Rule
- Active UI orb in static frontend is image + CSS status text; no reasoning-state coupling logic found in JS for orb semantics.
- Legacy canvas orb script exists but current `index.html` uses image orb asset.

### 12) Phase Gate Enforcement
- Global phase gate constant `GOVERNED_ACTIONS_ENABLED=True` checked in Governor before action execution.
- Capability-level enabled/status checked in registry.
- Queue enforces single pending governed action.
- **As-implemented gap:** non-governed skill path is unaffected by this phase gate.

### 13) ActionResult Schema
- Fields: `success`, `message`, optional `data`, optional `request_id`.
- Governance metadata defaults: `risk_level`, `authority_class`, `external_effect`, `reversible`.
- Factory helpers: `ok`, `failure`, `refusal`; `user_message` alias to `message`.

### 14) Authority Class Hierarchy
- Represented in `ActionResult.authority_class` as string categories:
  - `read_only`
  - `local_effect`
  - `network_outbound`
  - `persistent_change`
- Runtime currently relies on defaults in most current executor returns.

### 15) Failure Model (Fail-Closed)
- Governed path denies on registry errors, disabled capabilities, queue contention, and ledger-write failure before request creation.
- Network mediator raises explicit error on validation/network failures and logs failures.
- STT returns empty string on failure instead of crashing endpoint.
- **As-implemented limitation:** some `ACTION_COMPLETED` logs are best-effort swallow on ledger failure.

### 16) Intelligenceâ€“Authority Split
- Governed capabilities enforce request/result boundary.
- Conversational/skill logic remains separate from ActionRequest model.
- **As-implemented gap:** skill path still has live network behavior and Deep Thought invocation, weakening strict split.

### 17) No-Autonomy Guarantee
- No autonomous scheduler/orchestration engine detected in current active runtime modules.
- Session-scoped processing is request-driven.
- **As-implemented caveat:** background audio worker task exists in `audio_manager.py`.

### 18) Online Boundary Model
- Governed online path: capability 16 â†’ web search executor â†’ network mediator.
- Non-governed online paths also exist (weather/news/deepseek via mediator singleton, and direct requests in LLM managers).
- Network logs are produced at mediator boundary for mediator-routed calls.

### 19) Audit Surface Map
- Governor core: `governor.py`, `governor_mediator.py`, `execute_boundary.py`, `single_action_queue.py`, `capability_registry.py`
- Actions: `action_request.py`, `action_result.py`
- Ledger: `ledger/writer.py`
- Network: `governor/network_mediator.py`, plus direct network modules (`llm_manager*.py`)
- Skills/runtime routing: `brain_server.py`, `skill_registry.py`, `skills/*`, `services/weather_service.py`, `tools/rss_fetch.py`
- Deep Thought: `conversation/{complexity_heuristics.py, escalation_policy.py, deepseek_bridge.py, prompts.py}`
- TTS/STT: `executors/tts_executor.py`, `routers/stt.py`, `services/stt_engine.py`, `audio_manager.py`
- UI: `static/index.html`, `static/dashboard.js`, `static/orb.js`

---

### Audit Conclusion
Nova is **not constitutionally clean** against the provided Phase-4 invariants. The most significant drifts are:
1. A parallel non-governed skill execution path.
2. Network-capable skill operations outside Governor mediation.
3. Automatic Deep Thought escalation and prompt/context augmentation.
4. Automatic TTS invocation for voice responses.

