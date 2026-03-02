# NovaLIS Master Capability Matrix
**Date:** 2026-03-02  
**Scope:** Runtime behavior currently reachable from `nova_backend/src/` plus declared registry/design intent.  
**Purpose:** Single operator-facing map of **allowed today** vs **planned later** with trigger rules, code paths, dependencies, and failure modes.

---

## 1) Executive Snapshot

NovaLIS currently exposes **three** governed action capabilities in active runtime (IDs **16**, **17**, and **18**), plus deterministic non-governed conversational/utility skills (system/weather/news/general chat and STT ingress). All other listed Phase-4+ capability IDs are present in registry metadata but disabled and unimplemented in the active execution router.

---

## 2) Capability Status Legend

- **Allowed Today (Active):** Reachable and enabled in runtime code paths.
- **Allowed Today (Read-only/Utility):** Reachable skill or service path; does not use governed action execution.
- **Planned Later (Declared):** Present as metadata or design declaration; not executable now.
- **Blocked:** Explicitly disabled by registry or phase gate, or no execution router branch.

---

## 3) Master Matrix — Allowed Today vs Planned Later

| Domain | Capability | ID | Trigger / Entry | Runtime Path | External Effect | Status Today | Planned Later Notes |
|---|---|---:|---|---|---|---|---|
| Governed Action | Governed Web Search | 16 | `search ...`, `search for ...`, `look up ...`, `research ...` (+ one-shot clarification) | `GovernorMediator.parse_governed_invocation` → `Governor.handle_governed_invocation` → `Governor._execute` → `WebSearchExecutor` | HTTP GET to DuckDuckGo IA API through `NetworkMediator`; returns chat + `search` widget | **Allowed Today (Active)** | Can be expanded with retry/result shaping without authority model change |
| Governed Action | Open Preset Website | 17 | `open <name>` | `GovernorMediator` → `Governor` → `WebpageLaunchExecutor` | Opens preset URL via `webbrowser.open`; logs `WEBPAGE_LAUNCH` | **Allowed Today (Active)** | Preset list can be expanded cautiously |
| Governed Action | Speak Text (TTS) | 18 | `speak that`, `read that`, `say it` (manual invocation); auto-triggered after successful governed action on voice channel | `GovernorMediator.parse_governed_invocation` → `Governor.handle_governed_invocation` → `Governor._execute` → `tts_executor.execute_tts` | Local offline TTS via `pyttsx3` (lazy-loaded); no network effect | **Allowed Today (Active)** | Engine can be swapped (e.g. Piper) without authority model change |
| Governed Action | Volume Up/Down | 19 | No live parser mapping | Registry only (disabled); no `_execute` branch | None | **Blocked** | Declared in registry for future phase |
| Governed Action | Media Play/Pause | 20 | No live parser mapping | Registry only (disabled); no `_execute` branch | None | **Blocked** | Declared in registry for future phase |
| Governed Action | Brightness Control | 21 | No live parser mapping | Registry only (disabled); no `_execute` branch | None | **Blocked** | Declared in registry for future phase |
| Governed Action | Open File/Folder | 22 | No live parser mapping | Registry only (disabled); no `_execute` branch | None | **Blocked** | Declared in registry for future phase; `risk_level: confirm` |
| Governed Action | OS Diagnostics | 32 | No live parser mapping | Registry only (disabled); no `_execute` branch | None | **Blocked** | Declared in registry for future phase |
| Governed Action | Multi-source Reporting | 48 | No live parser mapping | Registry only (disabled); no `_execute` branch | None | **Blocked** | Declared in registry for future phase |
| Utility Command | Stop Speech | n/a | WebSocket text exactly `stop` | `brain_server.py` fast path | Stops speech state | **Allowed Today (Read-only/Utility)** | Stable deterministic control |
| Utility Command | Repeat Last Speech | n/a | WebSocket text exactly `repeat` | `brain_server.py` fast path | Replays last spoken text | **Allowed Today (Read-only/Utility)** | Stable deterministic control |
| Utility Command | Record Correction | n/a | Prefix `Correction:` | `brain_server.py` fast path → `record_correction` | Writes correction record | **Allowed Today (Read-only/Utility)** | Can evolve storage schema without changing invocation model |
| Skill | System Skill | n/a | token match (`system`, `status`, `uptime`, `time`, `date`) | `SkillRegistry` → `SystemSkill` | Local system/time metadata only | **Allowed Today (Read-only/Utility)** | No governed action required |
| Skill | Weather Skill | n/a | contains `weather` | `SkillRegistry` → `WeatherSkill` → `WeatherService` | HTTP weather lookup via `NetworkMediator`; weather widget | **Allowed Today (Read-only/Utility)** | Depends on `WEATHER_API_KEY` |
| Skill | News Skill | n/a | contains `news`/`headlines` | `SkillRegistry` → `NewsSkill` | RSS/news fetch + fallback, widget output | **Allowed Today (Read-only/Utility)** | Source quality/availability can vary |
| Skill | General Chat | n/a | fallback after deterministic skill routing | `SkillRegistry` → `GeneralChatSkill` | Local ollama text generation (`phi3:mini`) when available | **Allowed Today (Read-only/Utility)** | Optional dependency; fail-soft if unavailable |
| Inbound IO | STT Transcription | n/a | `POST /stt/transcribe` | `stt` router → `transcribe_bytes` (ffmpeg + Vosk) | Returns transcript text only | **Allowed Today (Read-only/Utility)** | Local model/toolchain availability required |

---

## 4) Active Governed Capability Details

### 4.1 Capability 16 — Governed Web Search

- **Parser Contract:** literal invocation patterns + one-strike clarification.
- **Authority Chain:** capability lookup, enabled check, phase gate, queue check, ledger attempt, immutable request, executor route.
- **Network Surface:** DuckDuckGo Instant Answer API through `NetworkMediator` only.
- **User Output:** chat summary and separate `search` widget payload.
- **Failure Modes:** network failure, mediator rejection, empty query, rate limit, capability disabled, phase gate off.

### 4.2 Capability 17 — Open Preset Website

- **Parser Contract:** `open <word>` where `<word>` maps to static preset keys.
- **Authority Chain:** same Governor gate sequence as cap 16.
- **Execution Surface:** local browser launch via Python `webbrowser` module.
- **User Output:** confirmation message with resolved URL.
- **Failure Modes:** unknown preset key; browser launch exception.

### 4.3 Capability 18 — Speak Text (Governed TTS)

- **Parser Contract:** explicit manual triggers (`speak that`, `read that`, `say it`) parsed in `GovernorMediator.parse_governed_invocation`; also auto-triggered after successful governed action when session channel is voice.
- **Authority Chain:** same Governor gate sequence as cap 16 (registry lookup → enabled check → phase gate → queue check → ledger `ACTION_ATTEMPTED` → `ActionRequest` creation → `_execute` routing).
- **Execution Surface:** `tts_executor.execute_tts()` → `TTSEngine.speak()` via lazy-loaded `pyttsx3`. Entirely local, offline, no network effect.
- **User Output:** `ActionResult` with `success=True`, empty message. No mutation of `last_response` state.
- **Failure Modes:** empty text input; TTS engine initialization failure; engine busy (stopped and restarted).
- **Non-Autonomy Guarantee:** TTS does not trigger in background, on idle, from escalation reasoning, or from internal planning. `brain_server.py` is verified (adversarial tests) to never call `handle_governed_invocation(18, ...)` or `execute_tts()` directly.
- **Test Coverage:** `tests/executors/test_tts_executor.py` (unit), `tests/test_governor_mediator_tts.py` (parser), `tests/adversarial/test_tts_spine_integrity.py` (authority boundary), `tests/governance/test_tts_invocation_bound.py` (non-autonomy).
- **Authority Proof:** `docs/PROOFS/Phase-4/TTS_SPINE_AUTHORITY_PROOF.md`.

---

## 5) Governed Capability IDs Present But Not Active

### 5.1 Why they are not active today

A capability can be non-active for any of these reasons:

1. **Disabled in registry** (`enabled: false`).
2. **No parser path** in `GovernorMediator` to emit invocation for that ID.
3. **No executor route** branch in `Governor._execute`.

IDs 19/20/21/22/32/48 currently meet all three conditions: disabled in registry, no parser mapping, and no executor branch in active runtime.

---

## 6) Guardrails and Enforcement Surfaces

- **Phase gate:** `GOVERNED_ACTIONS_ENABLED` controls global governed execution allowance.
- **Single-action boundary:** `SingleActionQueue` enforces one pending governed action at a time.
- **Network mediation:** scheme/host/IP validation + rate limiting + ledger logging.
- **WebSocket hardening:** max 4096-byte input and JSON parse guard before processing.
- **Session hygiene:** mediated clarification state is cleared on WebSocket disconnect.
- **TTS concurrency guard:** `TTSEngine` stops any active speech before starting new output; `_playback_lock` prevents overlapping renders.

---

## 7) Frontend / UX Reachability Map

- Dashboard opens WebSocket `/ws` and proactively requests `weather` and `news` on connect.
- Chat input and STT transcript both converge to one canonical ingestion path (`injectUserText` → WebSocket send).
- STT push-to-talk posts recorded audio to `/stt/transcribe` and sends transcript back through same chat path.

---

## 8) Dependencies and Operational Preconditions

### Required for full "Allowed Today" experience

- Backend runtime with FastAPI and websocket support.
- `requests` for network-mediated outbound calls.
- `WEATHER_API_KEY` for weather responses.
- Local Vosk model files for STT.
- `ffmpeg` on PATH (or bundled under `nova_backend/tools/ffmpeg/.../ffmpeg.exe`) for STT conversion.
- Optional: local `ollama` + `phi3:mini` model for General Chat skill.
- `pyttsx3` for capability 18 TTS engine (lazy-loaded on first invocation).

---

## 9) Planned-Later Expansion Checklist (per capability)

Use this checklist before marking any new capability as "Allowed Today (Active)" in this document:

1. Registry entry exists and is **enabled** intentionally.
2. `GovernorMediator` has deterministic explicit trigger mapping.
3. `Governor._execute` has explicit branch and bounded executor.
4. All outbound network calls go through `NetworkMediator`.
5. Ledger event sequence includes attempt/completion (and relevant capability-specific events).
6. Concurrency and fail-closed tests are added/updated in `nova_backend/tests`.
7. Frontend behavior is explicit and user-initiated only.
8. This master matrix is updated in the same change set.

### 9.1 Capability 18 — Expansion Checklist Verification

| Step | Status | Evidence |
|------|--------|----------|
| 1. Registry enabled | ✅ | `registry.json` ID 18 `enabled: true` |
| 2. GovernorMediator trigger | ✅ | `speak that`, `read that`, `say it` parsed to `Invocation(capability_id=18)` |
| 3. Governor._execute branch | ✅ | `elif req.capability_id == 18:` routes to `execute_tts` |
| 4. NetworkMediator for outbound | ✅ N/A | No network calls; purely local TTS engine |
| 5. Ledger attempt/completion | ✅ | `ACTION_ATTEMPTED` + `ACTION_COMPLETED` logged by Governor gate sequence |
| 6. Tests | ✅ | Unit, parser, adversarial, governance tests all present and passing |
| 7. Frontend user-initiated only | ✅ | No auto-invocation from frontend; adversarial test confirms |
| 8. Matrix updated | ✅ | This document (2026-03-02 update) |

---

## 10) Change Control for this Document

Whenever runtime capability behavior changes, update at minimum:

- Section 1 executive snapshot,
- Section 3 master matrix,
- Section 4/5 active vs non-active capability details,
- Section 9 expansion checklist status.

This document should remain implementation-binding and descriptive of what is mechanically reachable now.

### 10.1 Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2026-02-25 | Initial version | Baseline capability inventory |
| 2026-03-02 | Added Capability 18 (Speak Text) as Active | Cap 18 was enabled in registry and routed in Governor._execute as of PHASE_4_FREEZE amendment (2026-02-26) but this document was not updated in that change set. Corrected ID assignments: Open File/Folder is ID 22, not 18. Updated Sections 1, 3, 4, 5, 6, 8, 9. |

---

## 11) Cross-Reference: Phase-4/Phase-7 Design-to-Code Audit

For a full comparison between design corpus claims (Phase 4, 4.2, 4.5, 7) and active runtime reachability, see:

- `docs/canonical/NOVA_PHASE4_PHASE7_CODE_COMPARISON.md`

Use that document when validating whether a design concept is currently implemented versus roadmap-only.