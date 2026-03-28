# Phase 7 Document Map
Updated: 2026-03-28
Status: Current design map with Phase-7 runtime now complete in the governed external-reasoning lane
Purpose: Separate the near-term Phase-7 external-reasoning plan from older autonomy-presence exploration documents

## Current implemented Phase-7 runtime on `main`
The following Phase-7 product slices are now live in runtime/proof:
- answer-first governed web search with sources on demand
- inline news summaries on the News page
- cleaner user-facing news category language
- explicit governed external reasoning capability for same-thread second-opinion review
- same-session review followthrough and one-command review-plus-final-answer flow
- provider transparency in Trust and Settings
- actionable setup-mode and governed runtime-permission controls in Settings
- advisory-only explanation of the reasoning lane
- stronger local TTS renderer preference before fallback

Current proof packet:
- `docs/PROOFS/Phase-7/PHASE_7_PROOF_PACKET_INDEX.md`

Current dedicated verification package:
- `nova_backend/tests/phase7/`

## Canonical Phase-7 Planning Core
- `docs/design/Phase 7/PHASE_7_GOVERNED_EXTERNAL_REASONING_PLAN.md`

This is the current next-step Phase-7 plan for adding a governed external reasoning provider without collapsing Nova's intelligence-authority boundary.

Current bounded Phase-7 companion packet:
- `docs/design/Phase 7/PHASE_7_DEEPSEEK_SECOND_OPINION_PLAN.md`

Current provider usage and budget visibility companion packet:
- `docs/design/Phase 7/PHASE_7_PROVIDER_USAGE_AND_BUDGET_VISIBILITY_PLAN_2026-03-26.md`

Current Phase-7 news-reasoning companion input:
- `docs/design/NOVA_NEWS_EXPERIENCE_AND_REASONING_PLAN_2026-03-21.md`

Current Phase-7 web-search reasoning companion input:
- `docs/design/NOVA_WEBSEARCH_ANSWER_AND_REASONING_PLAN_2026-03-21.md`

Current Phase-7 crypto reasoning companion input:
- `docs/design/NOVA_GOVERNED_CRYPTO_CONNECTOR_AND_TRADING_PLAN_2026-03-21.md`

Current governed intelligence execution direction companion input:
- `docs/design/NOVA_GOVERNED_INTELLIGENCE_EXECUTION_DIRECTION_2026-03-21.md`

This companion packet captures one specific product shape inside that same phase:
- DeepSeek as a governed second-opinion reasoning source inside the same Nova chat box
- Nova remaining the primary voice
- no new execution authority

The usage-visibility packet should be read this way in Phase 7:
- provider usage visibility belongs to trust, not just billing
- estimated token awareness is acceptable before exact provider billing is available
- Settings and Trust should surface usage state honestly
- this does not authorize hidden paid-provider usage

The news reasoning packet should be read this way in Phase 7:
- current product-track items in that packet stay in the current UI/product lane
- Phase-7-relevant items are the later reasoning-quality extensions:
  - stronger long-form article synthesis when the local model is weak
  - more nuanced cross-source reasoning
  - optional governed second-opinion review of a news summary
  - harder ambiguity handling on complex current-events questions
- it does not authorize execution or broad autonomy

The web-search reasoning packet should be read this way in Phase 7:
- the first answer-first product slice is now live on `main`
- remaining current product-track items in that packet stay in the current search/UI lane
- Phase-7-relevant items are the later reasoning-quality extensions:
  - stronger provider-backed long-form synthesis for difficult web questions
  - deeper multi-source reasoning and contradiction handling
  - optional governed second-opinion review of a search answer
  - harder ambiguity handling on contested or complex topics
- it does not authorize execution or broad autonomy

The crypto connector and trading packet should be read this way in Phase 7:
- current product-track items in that packet stay in the public-data and product lane
- Phase-7-relevant items are the later reasoning-quality extensions:
  - stronger crypto market synthesis
  - better cross-source crypto news reasoning
  - optional second-opinion review of crypto research
- it does not authorize live trading

The governed intelligence execution direction packet should be read this way in Phase 7:
- Phase-7-relevant items are the governed multi-model intelligence layers:
  - external reasoning as bounded intelligence input
  - verification or fact-check paths later
  - stronger structured intelligence for harder research/search/news questions
  - cost-aware reasoning routing that still preserves the intelligence-authority boundary
- it does not authorize action autonomy

## Phase-7 Completion Note
Phase 7 is now complete in the current repo in the bounded sense defined by the canonical plan:
- governed text-only external reasoning is active
- explicit same-thread second-opinion review is active
- provider and route transparency are active
- the reasoning lane remains advisory only

Later work may still deepen quality, but that belongs to product refinement after Phase 7, not to the definition of whether Phase 7 exists at runtime.

Interpretation note:
- the late remote-bridge and manual home-agent slices are real runtime work
- they should be read as adjacent late-Phase-7 / pre-Phase-8 foundations, not as a redefinition of the canonical Phase-7 core

## Adjacent / Historical Phase-7-Era Research
- the older Phase-7 architecture document in this folder
- the older intelligence-capacity thesis document in this folder
- the remaining constitutional, presence, and autonomy essays in this folder

These documents remain valuable research inputs, but they should not be read as the current implementation order for the next Phase-7 package.
Many of them describe broader presence and background-cognition ideas that are beyond the immediate governed external-reasoning track.

## Cross-Phase Inputs
- `docs/design/NOVA_SOVEREIGNTY_PLATFORM_PHASE_REALIGNMENT_2026-03-18.md`
- `docs/design/NOVA_CONVERSATIONAL_COMPETITIVENESS_ROADMAP_2026-03-21.md`
- `docs/design/NOVA_GOVERNED_INTELLIGENCE_EXECUTION_DIRECTION_2026-03-21.md`
- `docs/design/NOVA_NEXT_LEVEL_ROBUST_AGENT_ROADMAP_2026-03-21.md`
- `docs/design/NOVA_CONTINUOUS_AGENT_OS_VISION_AND_TRUST_ROADMAP_2026-03-21.md`
- `docs/design/Phase 6/PHASE_6_SOVEREIGNTY_ALIGNMENT_AND_TRUST_LOOP_PLAN.md`
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`

## Interpretation Rule
When reading the Phase-7 folder:
- use the governed external reasoning plan first
- use the older autonomy/presence docs as exploratory future context only
- do not treat older Phase-7 autonomy language as runtime authorization
