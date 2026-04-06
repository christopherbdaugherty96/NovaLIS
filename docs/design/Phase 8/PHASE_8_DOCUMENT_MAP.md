# Phase 8 Document Map
Updated: 2026-04-05
Status: Current design map
Purpose: Keep the canonical OpenClaw direction, supporting execution plan, and raw source notes clearly separated

## Current implemented Phase-8 runtime on `main`
The following Phase-8 foundation slices are now live in runtime/proof:
- manual OpenClaw home-agent foundation
- manual briefing templates with operator-visible delivery controls
- persistent delivery inbox and Agent page review surface
- structured morning brief delivery across chat and OpenClaw scheduled/manual surfaces
- connection-aware Home / starter usefulness surface for briefing, schedule, weather, news, and research entry points
- setup-aware "what can you do right now?" capability guidance tied to live connections and active-run truth
- richer calendar guidance for today, tomorrow, and upcoming views
- visible active run state for OpenClaw manual runs across the Agent page and Home delivery surface
- stage-aware active run progress for collection, summarization, and delivery
- strict manual preflight before home-agent runs
- explicit envelope preview with scoped hostnames and declared budgets
- measured narrow-lane run usage surfaced in active-run and recent-run history
- narrow scheduled briefing runtime behind explicit settings control
- local-first metered OpenAI fallback for narrow task reports
- bounded assistive noticing with rate limiting, handled state, and Trust review

Current proof packet:
- `docs/PROOFS/Phase-8/PHASE_8_PROOF_PACKET_INDEX.md`
- latest full design review refresh: `docs/PROOFS/Phase-8/PHASE_8_FULL_DESIGN_REVIEW_AND_RUNTIME_ALIGNMENT_2026-03-28.md`

Current dedicated verification package:
- `nova_backend/tests/phase8/`

## Read This First
- `docs/design/Phase 8/NOVA_OPENCLAW_HOME_AGENT_MASTER_REFERENCE_2026-03-27.md`
- `docs/design/Phase 8/NOVA_SYSTEM_MAP_CURRENT_AND_FUTURE_2026-03-27.md`

This is the current repo-grounded Phase-8 reference.
Read it first when you need to know:
- what is live now
- what is only a manual foundation
- what is still deferred
- how Nova and OpenClaw are currently divided in product terms

## Canonical Phase-8 Governed Automation Spec
- `docs/design/Phase 8/PHASE_8_OPENCLAW_CANONICAL_GOVERNED_AUTOMATION_SPEC_2026-03-25.md`

This is the formal canonical design truth for how OpenClaw should fit into Nova.
If there is tension about the eventual strict automation model, this document wins.

## Supporting Phase-8 Implementation Context
- `docs/design/Phase 8/PHASE_8_OPENCLAW_GOVERNED_EXECUTION_PLAN.md`
- `docs/design/Phase 8/PHASE_8_OPENCLAW_HOME_AGENT_AND_PERSONALITY_LAYER_PLAN_2026-03-26.md`
- `docs/design/Phase 8/PHASE_8_ADVANCED_GOVERNOR_LAYER_ARCHITECTURE_2026-03-27.md`
- `docs/design/Phase 8/OPENAI_AGENT_OPERATING_MODEL_2026-03-27.md`
- `docs/design/Phase 8/OPENAI_PROVIDER_ROUTING_AND_BUDGET_POLICY_2026-03-27.md`
- `docs/design/Phase 8/OPENAI_USAGE_VISIBILITY_SPEC_2026-03-27.md`
- `docs/design/Phase 8/TRADING_MODE_GUARDRAILS_2026-03-27.md`
- `docs/design/Phase 8/NOVA_GOVERNED_CRYPTO_CONNECTOR_AND_TRADING_PLAN_2026-03-21.md`
- `docs/design/Phase 8/NOVA_GOVERNED_REACH_EXPANSION_AND_OPENCLAW_COMPARISON_2026-04-02.md`
- `docs/design/Phase 8/NOVA_GOVERNED_VISIBLE_OPERATOR_MODE_TODO_2026-04-02.md`
- `docs/design/Phase 8/NOVA_OPENCLAW_END_TO_END_EXPANSION_MASTER_TODO_2026-04-02.md`
- `docs/design/Phase 8/NOVA_PHASE_8_USER_OPERABILITY_AND_RUN_SYSTEM_AUDIT_2026-04-05.md`

This remains useful as a narrower implementation-planning packet.
It should now be read as supporting context beneath the canonical Phase-8 spec above.

The home-agent and personality-layer plan adds the practical product interpretation:
- Nova remains the visible voice and trust layer
- OpenClaw becomes the silent worker inside Nova's boundary system
- low-token local execution should be earned through manual briefing foundations before broader automation is attempted

Together, the canonical spec and supporting plan now explicitly define OpenClaw this way:
- OpenClaw may be a bounded autonomous worker
- Nova remains the governing law, watcher, and intervention point
- OpenClaw is inside Nova's envelope and boundary system, never above it

The OpenAI documents define the metered-provider side of that same system:
- OpenAI is optional and budgeted
- Nova remains local-first by default
- token and cost awareness are part of the trust model
- trading research can arrive earlier than live autonomous trading

The system-map document is the fastest plain-language bridge between the repo and the product model:
- current system diagram
- future target system diagram
- current end-to-end flow
- future end-to-end target

The advanced governor-layer packet defines the future trust-monitoring and anomaly-detection architecture:
- device trust
- trust scoring
- anomaly detection
- dynamic policy suggestions
- stronger zero-trust interpretation for external systems

The crypto and trading packets should be read as a tightly bounded side-track inside Phase 8:
- market research and read-only connector work can arrive earlier
- paper-trading and approval-gated execution are later
- live autonomous trading is not authorized by the existence of these packets

The reach-expansion, visible-operator, and end-to-end expansion packets are future backlog companions:
- they explain how Nova can widen governed reach without copying unsafe OpenClaw breadth
- they are roadmap-shaping packets, not proof that broader browser or connector execution is already live

The user-operability audit should be read as the product-clarity companion for the same backlog:
- it focuses on the gap between a powerful operator system and a usable operator product
- it argues that run visibility, focus, checkpoint UX, and failure clarity are still core Phase-8 concerns
- it should shape the remaining run-system work, not be treated as a separate cosmetic-only note
- it also proposes a concrete first-class run object, a three-mode UI contract, and proof implications for future Phase-8 validation

The visible-operator packet should now also be read alongside:
- `docs/design/Phase 11/NOVA_INTERACTION_MODEL_V1_STRICT_ON_RISK_SOFT_ON_FLOW_2026-04-02.md`

That interaction doctrine matters here because:
- Phase 8 should stay strict in law while becoming friendlier in flow
- visible operator work should bundle low-risk actions instead of prompting constantly
- checkpoints should land on meaningful outcomes, not every micro-step
- hard governance should stay concentrated at real risk boundaries

## Raw Source Inputs Preserved
- `docs/design/Phase 8/openclaw.txt`
- `docs/design/Phase 8/node design.txt`

These notes remain valuable because they capture the originating product and hardening intent.
They are preserved as source material, but they are not the final authority over the formal canonical spec.

Read them this way:
- `openclaw.txt` preserves the harder execution and containment intuition behind the worker model
- `node design.txt` preserves the user-facing "explain what I am looking at" product instinct that later feeds screen-help and visible-operator work

## Phase-8 Shipping Line
Current live Phase-8 truth is narrower than the full canonical shipping line.

Live now:
- manual OpenClaw home-agent foundation
- manual briefing templates
- narrow scheduled briefing lane behind explicit settings control
- delivery-mode controls
- operator-facing Agent page
- structured morning brief presentation
- visible active run state
- stage-aware active run progress
- explicit envelope preview and narrow-lane usage visibility
- connection-aware home/operator starter surfaces
- setup-aware capability discoverability in chat and UI
- Nova-owned task-result presentation

Full canonical Phase-8-safe scope still includes:
- Strict mode only
- TaskEnvelope v1
- normalization layer
- Governor Interceptor
- ExecuteBoundary hardening
- Data Minimization Engine
- NetworkMediator
- proposal-only OpenClaw adapter
- operator surfaces such as action preview, recent actions, status, stop, and failure visibility

Phase 8 should not be read as authorization for:
- broad Envelope mode without explicit budgets
- silent supervisory execution
- hidden background automation loops

## Cross-Phase Inputs
- `docs/design/Phase 5/PHASE_5_MEMORY_REMEMBRANCE_AND_ASSISTIVE_NOTICING_ARCHITECTURE_2026-03-27.md`
- `docs/design/Phase 6/NOVA_SOVEREIGNTY_PLATFORM_PHASE_REALIGNMENT_2026-03-18.md`
- `docs/design/Phase 7/NOVA_CONVERSATIONAL_COMPETITIVENESS_ROADMAP_2026-03-21.md`
- `docs/design/Phase 7/NOVA_GOVERNED_INTELLIGENCE_EXECUTION_DIRECTION_2026-03-21.md`
- `docs/design/Phase 9/NOVA_NEXT_LEVEL_ROBUST_AGENT_ROADMAP_2026-03-21.md`
- `docs/design/Phase 9/NOVA_CONTINUOUS_AGENT_OS_VISION_AND_TRUST_ROADMAP_2026-03-21.md`
- `docs/design/Phase 5/NOVA_CROSS_SYSTEM_MEMORY_AND_GOVERNED_AWARENESS_DIRECTION_2026-03-27.md`
- `docs/design/Phase 7/NOVA_NEWS_EXPERIENCE_AND_REASONING_PLAN_2026-03-21.md`
- `docs/design/Phase 7/NOVA_WEBSEARCH_ANSWER_AND_REASONING_PLAN_2026-03-21.md`
- `docs/design/Phase 8/NOVA_GOVERNED_CRYPTO_CONNECTOR_AND_TRADING_PLAN_2026-03-21.md`
- `docs/design/Phase 6/PHASE_6_SOVEREIGNTY_ALIGNMENT_AND_TRUST_LOOP_PLAN.md`
- `docs/design/Phase 7/PHASE_7_GOVERNED_EXTERNAL_REASONING_PLAN.md`
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`

## Phase-8 Boundary For News, Search, And Reasoning Work
The news and web-search packets are primarily current product-track and Phase-7 reasoning documents.

In Phase 8, read them with this boundary:
- news remains read-only
- web search remains read-only
- reasoning output can support action previews
- reasoning output never becomes execution authority or approval authority

The memory / remembrance / assistive-noticing packet matters here because:
- user personal memory remains a Phase-5 governed memory concern
- operational remembrance becomes trust-visible in later layers
- assistive noticing and suggestive help should be treated as bounded later-phase behavior, not backported into Phase-5 runtime by accident

The cross-system memory / governed-awareness direction packet matters here because:
- it explains why Phase 8 is not just "more agent power"
- it frames Nova as stateful across the environment, not only inside one repo
- it reinforces that awareness should widen before autonomous authority does

The first live assistive-noticing slice should be read that way too:
- bounded visible notices are now live
- the current slice is suggestion-only
- Home, Trust, Settings, and explicit command review are the intended surfaces
- policy-bound assist actions remain later work

The same interpretation applies to broader agent-roadmap packets:
- read-only connectors can arrive earlier
- write-capable connectors, app control, and action-capable schedules belong here
- continuously-on usefulness never removes approval requirements for real-world effect

## Hand-off To Later Phases
Read the canonical OpenClaw spec this way across phases:
- Phase 8: strict governed execution foundations
- Phase 9: bounded Envelope mode with explicit budgets and stronger run controls
- Phase 10 and later: supervisory quietness only under reviewable control

## Interpretation Rule
When reading the Phase-8 folder:
- use the master reference first for repo-grounded current truth
- use the canonical governed automation spec next for the eventual strict automation model
- use the governed execution plan second
- use the home-agent and personality-layer plan as the practical product-direction companion
- use the Phase-8.5 scheduler packet in `docs/design/Phase 8.5/` for the shipped narrow scheduler and the remaining proactive-delivery guardrails
- use `openclaw.txt` and `node design.txt` as preserved raw source inputs
- do not treat the existence of a Phase-8 folder as proof that the full canonical Phase-8 automation model is live in runtime
