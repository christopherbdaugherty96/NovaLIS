# Phase 7 Proof Packet Index
Updated: 2026-03-28
Status: Current proof index

## Current canonical Phase-7 completion packet
- `docs/PROOFS/Phase-7/PHASE_7_PRODUCT_FOUNDATION_RUNTIME_SLICE_2026-03-25.md`
- `docs/PROOFS/Phase-7/PHASE_7_COMPLETION_AND_REASONING_TRANSPARENCY_RUNTIME_SLICE_2026-03-26.md`
- `docs/PROOFS/Phase-7/PHASE_7_SETTINGS_RUNTIME_PERMISSIONS_SLICE_2026-03-26.md`
- `docs/PROOFS/Phase-7/PHASE_7_PRODUCT_ENTRY_AND_USAGE_VISIBILITY_RUNTIME_SLICE_2026-03-26.md`
- `docs/PROOFS/Phase-7/PHASE_7_DEDICATED_VERIFICATION_AND_PROOF_ALIGNMENT_2026-03-27.md`
- `docs/PROOFS/Phase-7/PHASE_7_CONVERSATION_VOICE_AND_SECOND_OPINION_PRESENTATION_REFINEMENT_2026-03-28.md`
- `docs/PROOFS/Phase-7/PHASE_7_REASONING_SURFACE_AND_LONG_FORM_PRESENTATION_REFINEMENT_2026-03-28.md`
- `docs/PROOFS/Phase-7/PHASE_7_REPORT_SURFACES_CHAT_SUMMARY_CARD_AND_VOICE_REFINEMENT_2026-03-28.md`
- `docs/PROOFS/Phase-7/PHASE_7_SAME_SESSION_REVIEW_FOLLOWTHROUGH_TRIAD_RUNTIME_SLICE_2026-03-28.md`
- `docs/PROOFS/Phase-7/PHASE_7_FULL_DESIGN_REVIEW_AND_RUNTIME_ALIGNMENT_2026-03-28.md`

## Adjacent late-Phase-7 / pre-Phase-8 access and foundation slices
- `docs/PROOFS/Phase-7/PHASE_7_GOVERNED_REMOTE_BRIDGE_RUNTIME_SLICE_2026-03-26.md`
- `docs/PROOFS/Phase-7/PHASE_7_RUNTIME_ROUTING_CLEANUP_2026-03-26.md`
- `docs/PROOFS/Phase-7/PHASE_7_RUNTIME_ENTRYPOINT_MODULARIZATION_2026-03-26.md`
- `docs/PROOFS/Phase-7/PHASE_7_FRONTEND_ORIENTATION_AND_FEEDBACK_RUNTIME_SLICE_2026-03-26.md`
- `docs/PROOFS/Phase-7/PHASE_7_OPENCLAW_HOME_AGENT_FOUNDATION_RUNTIME_SLICE_2026-03-26.md`

## Historical Note
The first bounded product-foundation slice remains:
- `docs/PROOFS/Phase-7/PHASE_7_PRODUCT_FOUNDATION_RUNTIME_SLICE_2026-03-25.md`

It is still part of the canonical packet above because answer-first search and news grounding remain part of the final Phase-7 story.

## Scope captured across the current packets
- answer-first governed web search responses with sources on demand
- inline news-card and category summaries on the News page
- cleaner user-facing news category language
- explicit governed external reasoning capability for same-thread second-opinion review
- same-session review followthrough and one-command review-plus-final-answer flow
- provider transparency in Trust and Settings
- actionable setup-mode and governed runtime-permission controls in Settings
- advisory-only explanation of the reasoning lane
- clearer second-opinion review summaries with bottom-line, main-gap, and best-correction signals
- calmer voice summaries for structured review output instead of reading the full audit scaffold aloud
- Trust and Settings reasoning panels that now expose bottom-line, main-gap, and best-correction review signals directly
- stronger executive-summary shaping for long-form general-chat, search, and news outputs
- report surfaces that now lead more consistently with an explicit bottom line in chat and voice
- reusable assistant chat summary cards for bottom-line, main-gap, and best-correction reporting signals
- same-session review followthrough so Nova can revise, summarize, or restore an answer from the bounded second-opinion lane
- explicit one-command review-plus-final-answer flow for the bounded second-opinion lane
- full Phase-7 design-folder review confirming the canonical bounded reading against the live repo
- TTS executor preference for the stronger local renderer before fallback
- a phase7 dedicated verification package for the bounded reasoning lane
- token-gated governed remote bridge for read/reasoning access
- Trust and Settings visibility for provider, connection, and bridge state
- a separate landing-preview page for product messaging review
- a stronger first-run magic-moment prompt centered on `explain this`
- a visible primary navigation strip across the major Nova pages
- an explicit header page-context and connection-status surface
- Intro-first first-run routing instead of dropping new users directly into Chat
- a stronger text-bearing thinking bar instead of a nearly invisible activity line
- clearer push-to-talk state feedback and safer inline memory action confirmation
- timeout-backed snapshot fallback states with a direct calendar-to-Settings funnel
- estimated governed reasoning-usage visibility in Trust and Settings
- bounded general-chat fallback isolated from the legacy skill registry path
- passive confirmation-gate logic removed from the live websocket runtime path
- focused API routers for app shell, audit, bridge, and runtime settings
- websocket session loop extracted into a dedicated runtime module
- Nova-owned personality tuning for calmer task-report delivery
- a dedicated Agent page with manual home-agent briefing templates
- delivery-mode controls for named briefings vs. quiet review work
- Trust and Settings visibility for the manual OpenClaw home-agent foundation

Interpretation note:
- the canonical Phase-7 core is still the bounded governed external-reasoning lane
- remote bridge and manual home-agent foundations are real adjacent slices, but they should not be read as redefining the Phase-7 finish line

## Read with
- `docs/design/Phase 7/PHASE_7_DOCUMENT_MAP.md`
- `docs/design/Phase 7/PHASE_7_DEEPSEEK_SECOND_OPINION_PLAN.md`
- `docs/design/Phase 7/PHASE_7_GOVERNED_EXTERNAL_REASONING_PLAN.md`
- `docs/design/NOVA_WEBSEARCH_ANSWER_AND_REASONING_PLAN_2026-03-21.md`
- `docs/design/NOVA_NEWS_EXPERIENCE_AND_REASONING_PLAN_2026-03-21.md`
- `docs/design/NOVA_TTS_REGRESSION_NOTE_2026-03-21.md`

## Verification Commands (Current)
Run these commands from `nova_backend/`.

- `python -m pytest tests\phase7 -q`
- `python -m pytest tests\executors\test_external_reasoning_executor.py tests\conversation\test_deepseek_bridge.py tests\conversation\test_provider_usage_store.py tests\test_runtime_settings_api.py tests\test_openclaw_bridge_api.py tests\test_runtime_auditor.py -q`
- `python -m pytest tests\executors\test_response_verification_executor.py tests\executors\test_external_reasoning_executor.py -q`
- `python -m pytest tests\phase45\test_brain_server_followups_and_voice.py::test_deepseek_button_builds_bounded_second_opinion_context tests\phase45\test_brain_server_followups_and_voice.py::test_second_opinion_followthrough_generates_nova_final_answer tests\phase45\test_brain_server_followups_and_voice.py::test_second_opinion_followthrough_can_summarize_gaps_and_restore_original_answer tests\phase45\test_brain_server_followups_and_voice.py::test_second_opinion_and_final_answer_runs_in_one_explicit_command -q`
- `python -m pytest tests\phase45\test_dashboard_phase7_chat_controls.py tests\phase45\test_dashboard_trust_center_widget.py tests\phase45\test_brain_server_trust_status.py tests\phase45\test_dashboard_onboarding_widget.py -q`
- `python -m py_compile src\audit\runtime_auditor.py src\conversation\review_followthrough.py src\executors\external_reasoning_executor.py src\usage\provider_usage_store.py`
- `python ..\scripts\generate_runtime_docs.py`
- `python ..\scripts\check_runtime_doc_drift.py`
- `python ..\scripts\check_frontend_mirror_sync.py`

## Latest Verification Snapshot (2026-03-28)
- phase7 dedicated verification package: `7 passed`
- external-reasoning / bridge / usage / trust-surface bundle: `33 passed`
- surrounding phase7 / bridge / news / timeout bundle: `45 passed`
- reasoning-surface / general-chat / web-search / news-presentation bundle: `75 passed`
- broader conversation / voice / second-opinion regression bundle: `18 passed`
- focused report-surface / voice refinement bundle: `22 passed`
- executor review-lane bundle: `10 passed`
- websocket review-followthrough subset: `4 passed`
- runtime documentation drift check: passed
- frontend mirror parity check: passed
