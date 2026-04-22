# NOVA Runtime Capability Reference
Updated: 2026-04-21
Status: Active
Scope: Human-readable explanation of the current runtime capability surface

## Purpose
This document explains what Nova can do in plain language.

Use it together with:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md` for active-status truth
- `docs/current_runtime/RUNTIME_FINGERPRINT.md` for runtime fingerprinting
- `docs/PROOFS/` for phase closure and implementation evidence

Interpretation rule:
- `CURRENT_RUNTIME_STATE.md` answers "is this active right now?"
- this document answers "what does it do?"

## Capability Types
- Governed capability: a registry-backed capability ID routed through `GovernorMediator -> Governor -> ExecuteBoundary -> Executor`
- Supporting runtime surface: active runtime behavior without its own capability ID
- Design-stage surface: documented intent that is not yet a live governed runtime capability

## Active Governed Capabilities

| ID | Name | Category | Phase | What it does | Typical prompts | Runtime effect |
| --- | --- | --- | --- | --- | --- | --- |
| 16 | `governed_web_search` | Research | 4 | Searches current web sources through the governed network path, can read a few source pages, and returns a results widget with suggested follow-ups. | `search for...`, `look up...`, `research...` | Read-only network |
| 17 | `open_website` | Navigation | 4 | Opens a requested website, source URL, or article page in the default browser. Can preview before opening. | `open source 2`, `open reuters`, `preview source 1` | Local browser launch |
| 18 | `speak_text` | Voice output | 4 | Reads text aloud through the local offline TTS path after speech-safe formatting removes raw links and system tokens. The runtime now prefers the stronger local renderer before fallback. | `speak that`, `read that`, `say it` | Local audio output |
| 19 | `volume_up_down` | Local control | 4 | Raises, lowers, mutes, unmutes, or sets system volume on the local device. | `volume up`, `mute`, `set volume to 40` | Local OS effect |
| 20 | `media_play_pause` | Local control | 4 | Starts, pauses, or resumes local media playback through platform-specific media controls. | `play`, `pause`, `resume` | Local OS effect |
| 21 | `brightness_control` | Local control | 4 | Raises, lowers, or sets display brightness using platform-supported controls. | `brightness up`, `set brightness to 65` | Local OS effect |
| 22 | `open_file_folder` | Local navigation | 4 | Opens allowed folders or explicit file/folder paths inside Nova's approved path roots. | `open downloads`, `open file C:\\...` | Local OS effect |
| 31 | `response_verification` | Analysis safety | 4.2 | Verifies text or a prior answer for likely issues, corrections, and confidence without authorizing any action. | `verify this`, `fact check...`, `double check...` | Read-only analysis |
| 32 | `os_diagnostics` | System insight | 4 | Reports system health, CPU, memory, disk, network-interface status, model readiness, and active capability count. | `system status`, `system check` | Read-only local inspection |
| 48 | `multi_source_reporting` | Intelligence | 4.2 | Builds a structured multi-source report with findings, source credibility, counter-analysis, and decomposed confidence signals. | `research local AI sovereignty`, `analyze current robotics market` | Read-only network + analysis |
| 49 | `headline_summary` | News intelligence | 4.2 | Summarizes selected headlines, compares headlines, and can read the linked story page when asked for `story #x` details. | `summarize headline 2`, `more on story 1`, `compare headlines 1 and 3` | Read-only analysis |
| 50 | `intelligence_brief` | News intelligence | 4.2 | Builds a compact daily or topic brief from current headlines, clusters related stories, and supports brief-level follow-up actions. | `daily brief`, `intelligence brief`, `news brief` | Read-only analysis |
| 51 | `topic_memory_map` | News intelligence | 4.2 | Shows a topic map of recurring themes in the latest headline set so users can see what the news cycle is clustering around. | `topic map`, `show topic memory map` | Read-only analysis |
| 52 | `story_tracker_update` | Ongoing research | 4.2 | Starts tracking a story, refreshes tracked stories, links related stories, and stores new snapshots for comparison over time. | `track story ...`, `update story ...`, `link story A to B` | Local workspace write |
| 53 | `story_tracker_view` | Ongoing research | 4.2 | Shows tracked story timelines, comparisons, and relationship views for already tracked topics. | `show story ...`, `compare story ...`, `show relationship graph` | Read-only local inspection |
| 54 | `analysis_document` | Long-form analysis | 4.2 | Creates session-scoped analysis documents, lists them, summarizes them, and explains specific sections. | `create analysis report on...`, `list analysis docs`, `explain section 2 of doc 1` | Read-only session artifact |
| 55 | `weather_snapshot` | Snapshot widget | 4.5 | Loads a weather snapshot and widget with a short summary and suggested next actions. | `weather`, `weather update`, `forecast` | Read-only network |
| 56 | `news_snapshot` | Snapshot widget | 4.5 | Loads the current news widget and headline cache used by follow-up summary and story commands. | `news`, `latest news`, `headlines` | Read-only network |
| 57 | `calendar_snapshot` | Snapshot widget | 4.5 | Loads a calendar/agenda snapshot for the current session with a compact summary and follow-up prompts. | `calendar`, `agenda`, `today's schedule` | Read-only local/service inspection |
| 58 | `screen_capture` | Perception | 4.5 | Captures a bounded region around the cursor at request time, along with context snapshot metadata, for later explanation. | `take a screenshot`, `capture the screen` | Read-only perception |
| 59 | `screen_analysis` | Perception | 4.5 | Runs OCR plus visual analysis on an explicit screen capture and returns "what I found" with suggested next steps. | `analyze this screen`, `explain this screen` | Read-only perception + analysis |
| 60 | `explain_anything` | Perception | 4.5 | Routes an explicit "what is this?" request to the best read-only explainer path: current screen, current page, or selected file. | `explain this`, `what is this?`, `which one should I download?` | Read-only perception + analysis |
| 61 | `memory_governance` | Governed persistence | 5 | Saves, lists, shows, locks, defers, unlocks, deletes, or supersedes explicit memory items, including thread-linked memory. | `memory save ...`, `memory list`, `memory show ...`, `memory lock ...` | Persistent local write |
| 62 | `external_reasoning_review` | Governed reasoning | 7 | Gives Nova a same-thread governed second-opinion lane that can critique or strengthen an answer without gaining any execution authority. Trust and Settings surfaces explain the provider, route, and advisory boundary when it is used. | `second opinion`, `deepseek second opinion`, `review this answer` | Read-only analysis |
| 63 | `openclaw_execute` | Governed automation | 8 | Runs a named read-only OpenClaw template through a bounded template lane with explicit envelope preview, budget meters, and result delivery. Depending on the template, the run may stay local or use governed network reads. Phase 9 adds goal-based execution via the thinking loop. | `run morning brief`, `daily brief`, `run project snapshot` | Governed read-only execution |
| 64 | `send_email_draft` | External communication | 9 | Composes an email draft and opens it in the system mail client via a mailto: URI. The user must click Send manually — Nova never transmits. Confirmation-gated; the first external-effect capability. Requires a configured mail client. | `draft an email to...`, `email Alex about...`, `send email draft` | External effect — confirmation-gated, user sends |
| 65 | `shopify_intelligence_report` | Store intelligence | 9 | Fetches a read-only snapshot of Shopify store metrics via the registered HttpShopifyConnector: order count, revenue, product status, and inventory levels for a configurable period. Routed through NetworkMediator (cap 65 scope). Requires NOVA_SHOPIFY_SHOP_DOMAIN and NOVA_SHOPIFY_ACCESS_TOKEN env vars. | `shopify report`, `how's my store doing`, `shopify stats today`, `show my shopify orders` | Tier 1 read-only network |

## Capability Notes By Category

### Research and intelligence
- Capabilities `16`, `48`, `49`, `50`, `51`, and `62` are Nova's current information and reasoning layer.
- `49` is no longer headline-only. Commands like `more on story 2` or `summary of story #2` are designed to read the linked article page and summarize that page when the URL is available.
- `62` is advisory-only. It stays in the same thread, surfaces provider transparency, and cannot widen Nova's authority or trigger actions.
- `52` and `53` support longer-running story tracking instead of one-shot summaries.
- `54` keeps analysis documents session-scoped unless the user explicitly saves them elsewhere.

### Local device and navigation
- Capabilities `17`, `19`, `20`, `21`, and `22` create local effects, but they remain invocation-bound and Governor-mediated.
- `22` is path-limited. Nova only opens files/folders inside approved user roots such as home, Documents, Downloads, Desktop, and Pictures.
- `32` is read-only and is the operator-facing health/status surface.

### Perception and explain mode
- `58`, `59`, and `60` are active runtime capabilities.
- They are request-time only. There is no background screen watching or hidden capture loop.
- They use context snapshot signals to improve explanations, but they do not gain execution authority from that context.

### Governed memory
- `61` is the first active Phase-5 governed persistence slice.
- It is explicit, inspectable, reversible where appropriate, and tied to ledger events.
- Thread-linked memory is supported through the project continuity workflow.

### OpenClaw intelligence layer (Phase 9)
- The OpenClaw agent intelligence layer adds goal-based execution on top of the Phase 8 template pipeline.
- A 10-tool dynamic registry (`src/openclaw/tool_registry.py`) exposes skills and executor-backed tools to an iterative thinking loop (`src/openclaw/thinking_loop.py`).
- The thinking loop uses LLM-guided reasoning to select tools, generate parameters, evaluate results, and produce synthesized natural-language answers.
- Executor-backed mutation tools (volume, brightness, media, webpage, screen capture) route through the Governor via `ExecutorSkillAdapter`.
- Execution memory tracks per-tool reliability and speed for optimal ordering.
- Error recovery uses configurable retry with backoff and circuit-breaker patterns.
- The current default template inventory includes `morning_brief`, `evening_digest`, `market_watch`, `project_snapshot`, and the not-yet-connected `inbox_check`.
- `project_snapshot` is the current read-only local project-analysis slice. It uses bounded local file reads rather than governed outbound network access.

### Self-awareness
- Nova has a dynamic self-awareness block (`src/identity/nova_self_awareness.py`) injected into every system prompt.
- It gives the LLM real-time knowledge of Nova's active capabilities, tools, connected services, and runtime status.
- This means Nova can accurately answer "what can you do?" from live system state, not a static description.

### LLM and personality
- Default local model: Gemma 4 (`gemma4:e4b`) with 32K context window.
- Personality: warm, direct, lightly witty — "a capable, thoughtful friend, not a corporate assistant."
- System prompt hierarchy: `system_prompt.py` (single source of truth) → `general_chat.py BASE_CONTRACT` (rich conversational prompt) → self-awareness block + memory context (dynamic per-request).

## Active Supporting Runtime Surfaces (No Separate Capability ID)

| Surface | Status | What it does | Notes |
| --- | --- | --- | --- |
| STT transcription | Active | Converts push-to-talk audio into text through local ffmpeg + Vosk and routes the transcript into the normal chat path. | Voice input surface, not a governed capability ID |
| Interface personality agent | Active | Cleans presentation tone, strips unsafe authority-style phrasing, and keeps output readable without changing execution authority. | Presentation-only layer |
| Tone controls | Active | Stores a global response style, per-domain overrides, recent tone-change history, and reset controls through the dashboard and chat commands. | Manual, inspectable, and non-authorizing |
| Working Context Engine | Active | Maintains session-scoped task context such as active app, active URL, last relevant object, and recent relevant turns. | Non-persistent by default |
| Project continuity threads | Active | Tracks ongoing work by thread with blocker, health, latest decision, memory count, and detail panel support. | Session-scoped workspace continuity surface; durable cross-session continuity comes from governed memory |
| Thread-memory bridge | Active | Lets users explicitly save thread snapshots and decisions into governed memory and list memory by thread. | Built on capability `61` |
| Notification scheduling | Active | Manages explicit schedules, quiet hours, rate limits, due-item delivery checks, and dismiss/cancel/reschedule flows. | User-directed, policy-bound, and inspectable |
| Pattern review | Active | Maintains an opt-in advisory review queue for recurring blockers, decision gaps, and related continuity patterns. | No auto-apply and no background review loop |
| Atomic policy draft foundation | Active | Validates and stores disabled-by-default one-trigger / one-action policy drafts and exposes explicit draft commands. | Phase-6 foundation surface only; no trigger runtime |
| Policy executor gate | Active | Simulates delegated policies and permits one-shot manual review runs for safe low-authority policies through the Governor. | Manual review only; no background execution |
| Capability topology | Active | Classifies governed capabilities by authority class, delegation class, reversibility, and policy delegatability. | Internal governance surface used by the executor gate |
| Policy Review Center | Active | Gives users a dedicated Policies page for draft inspection, simulation review, and one-shot manual run results. | Product surface only; trigger runtime remains disabled |
| Dashboard widgets and detail panels | Active | Displays weather, news, calendar, system status, thread map, thread detail, structure-map graph output, and follow-up actions in the UI. | UI surface only |
| Introduction and Settings pages | Active | Gives non-technical users a first-run explanation of Nova plus explicit setup-mode, accessibility, and voice-confidence controls. | Product surface only; does not grant execution authority |
| Orb presence layer | Active | Provides calm visual presence only. It does not signal hidden state, reasoning depth, or execution readiness. | Non-authoritative |
| Context snapshot service | Active | Captures active-window, browser, cursor, and system signals at request time for perception flows. | Internal read-only surface |

## Design-Stage or Planned Surfaces

| Surface | Status | What it is | Why it is not listed as active runtime |
| --- | --- | --- | --- |
| Wake word listener (`Hey Nova`) | Design-stage | Proposed local-only voice activator that would wake Nova and then hand off to STT. | Design docs and an optional dependency path exist, but there is no active wake-word runtime module in the current capability registry or voice package |
| Deeper browser context adapters | Partial/design-stage | Richer active-tab, selection, and browser-state capture for explain flows. | Current runtime uses bounded context snapshot signals; richer browser integration is not yet a separate active runtime surface |

## Wake Word Clarification
Wake word is important enough to call out directly because it is easy to confuse with active voice support.

Current truth:
- Voice transcription is active.
- Text-to-speech capability is active, with stronger renderer preference now in code.
- Voice status and voice check product surfaces are active.
- Real-device spoken output still deserves local validation.
- Wake word is documented and planned.
- Wake word is not part of the default dependency install.
- Wake word is not yet a live governed capability or active runtime surface in the current registry.

Relevant design reference:
- `docs/design/Phase 4.5/NOVA_WAKE_WORD_SCREEN_CONTEXT_IMPLEMENTATION.md`

## Recommended Reading Order
1. `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
2. `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
3. `docs/current_runtime/RUNTIME_FINGERPRINT.md`
4. `docs/PROOFS/Phase-4/`
5. `docs/PROOFS/Phase-4.5/`
6. `docs/PROOFS/Phase-5/`
7. `docs/PROOFS/Phase-6/`
8. `docs/PROOFS/Phase-6/PHASE_6_PROOF_PACKET_INDEX.md`

## Maintenance Rule
When a capability or surface changes:
1. Update runtime code and tests first.
2. Regenerate runtime truth artifacts as needed.
3. Update this reference in the same change set so the descriptions stay aligned with the live system.
