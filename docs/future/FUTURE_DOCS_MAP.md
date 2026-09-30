# Future Docs Map

Purpose: let a reviewer tell, at a glance, what each `docs/future/` doc *is* — active, parked,
superseded, fixture, or design history — and where it belongs. This is a **classification
bridge**, not a promotion. Listing a doc here does not add it to any active lane.

## Authority

- Ordering authority for what comes next: `docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md`
  (lanes A–D + Horizon H1–H31). It does not use phase numbers.
- What is real today: generated `docs/current_runtime/CURRENT_RUNTIME_STATE.md`.
- Product identity: `docs/product/PRODUCT_DEFINITION.md` (converged 2026-07-07).
- **Uncited docs are reference until promoted.** By the roadmap's Supersession Note, anything in
  `docs/future/` not referenced by the roadmap is design reference, de-prioritized until a lane
  pulls it in. This map records that status; it does not change it.

## Path note — capital `docs/Future/` split (RESOLVED)

A pre-existing case split (introduced by commit `fd9ba33`) once tracked 45 of these files under
capital `docs/Future/` — invisible on Windows, two directories on case-sensitive checkouts.
**Resolved by PR #281 (2026-07-09, merge `152e366e`): all 45 paths normalized to lowercase.**
Every bare filename in this map now lives under `docs/future/`. (Historical docs and evidence
snapshots may still mention the old capital path; those references are history, not current
layout.)

## Status legend

- `active/cited` — already referenced by the roadmap, design tree, `INDEX`, or canonical layer.
- `roadmap-lane` — substrate for an active lane (A–D) but not yet individually cited.
- `horizon` — belongs to Horizon (H1–H31): not scheduled; graduates via the promotion ladder.
- `design-history` — design thinking for a built or partially-built area; a record, not a plan.
- `superseded` — replaced by a newer doc; kept for history; **do not promote**.
- `owner-paused` — under an explicit owner pause decision; **do not promote** without owner say-so.
- `fixture/reference` — templates, mock data, or coordination scaffolding; not a plan.

## Already integrated (the cited set)

~35 of the 115 top-level docs are already referenced by the roadmap / design / `INDEX` /
canonical layer and are **`active/cited`** — e.g. the current Google connector foundation
(`GOOGLE_READ_ONLY_CONNECTOR_FOUNDATION_2026-05-03.md`, `NOVA_GOOGLE_CONNECTOR_MODEL.md`), the
brain/learning/routine specs listed in `docs/future/README.md`, `GOVERNED_GOAL_CARDS_DESIGN.md`,
and `NOVA_BACKGROUND_REASONING_NOT_AUTOMATION_PLAN.md`. Private Auralis commercial planning is
outside the public-source boundary; see `../security/AURALIS_PUBLIC_BOUNDARY_2026-09-30.md`.
Those are not re-listed below. This map focuses on the **80 orphaned** top-level docs.

---

## Cluster 1 — Auralis / commerce (22 docs)

Cluster verdict: **SECOND BUSINESS.** The roadmap parks Auralis client-services at Horizon **H12**
and personal Auralis awareness at **Lane C** (C1 "Auralis Today" is shipped). Governed
commerce/operator execution here also collides with the roadmap's read-only awareness boundary
and Do-Not-Expand doctrine. **Do not promote into active lanes.** Merger work is under an owner
HARD PAUSE (2026-04-27).

| Doc | Status | Intended home |
| --- | --- | --- |
| Private Auralis commercial planning | owner-paused; private | Outside public Nova source; see `../security/AURALIS_PUBLIC_BOUNDARY_2026-09-30.md` |
| README_CREATIVE_COMMERCE_ORCHESTRATION.md | design-history | H12 |
| PORTFOLIO_PRIORITY_SWITCH_WEBSITE_LLC_2026-04-22.md | superseded | archive candidate |
| commerce_marketing_operator_decision.md | design-history | H12 (do not promote — read-only boundary) |
| governed_content_operator.md | design-history | H12 (do not promote — read-only boundary) |
| NOVA_SHOPIFY_GOVERNED_OPERATOR_DESIGN_2026-04-20.md | design-history | H12 (Shopify is read-only today) |
| NOVA_CREATOR_LED_SHOPIFY_POD_MODEL_2026-05-11.md | design-history | H12 |
| NOVA_ECOMMERCE_OPERATOR_END_STATE_PLAN_2026-04-30.md | design-history | H12 (end-state, not scheduled) |
| NOVA_GOVERNED_MEDIA_AND_ECOMMERCE_ENGINE.md | design-history | H12 |
| NOVA_MEDIA_ENGINE_SAFE_IMPLEMENTATION_ROADMAP.md | design-history | H12 |
| SHOPIFY_DROPSHIP_VIDEO_AD_WORKFLOW_GOAL.md | design-history | H12 |
| RJ_PRINT_GOVERNED_PRODUCTION_TICKET_PLAN.md | design-history | H12 |
| HYDROGEN_OXYGEN_STOREFRONT_BUILD_RULESET_2026-04-12.md | fixture/reference | Auralis build ruleset |
| BUSINESS_OPTIONS.md | design-history | H12 |

## Cluster 2 — Google / connectors (10 docs)

Cluster verdict: **Lane C substrate (personal awareness: Gmail / Tasks / Traffic).** The *current*
connector direction is the already-cited `GOOGLE_READ_ONLY_CONNECTOR_FOUNDATION_2026-05-03.md`;
these older April plans are superseded by it or are supporting reference.

| Doc | Status | Intended home |
| --- | --- | --- |
| NOVA_CONNECTOR_RISK_CLASSIFICATION_TABLE_2026-04-28.md | roadmap-lane | Lane C (connector risk reference) |
| NOVA_CONNECTOR_REGISTRY_PLAN_2026-04-27.md | roadmap-lane | Lane C (connector registry reference) |
| NOVA_MCP_GOVERNED_CONNECTOR_PLAN_2026-04-27.md | design-history | Lane C / Horizon MCP boundary (H31) |
| GOOGLE_CONNECTOR_IMPLEMENTATION_ROADMAP.md | superseded | by GOOGLE_READ_ONLY_CONNECTOR_FOUNDATION_2026-05-03 |
| GOOGLE_INTEGRATION_DESIGN_DOC.md | superseded | by GOOGLE_READ_ONLY_CONNECTOR_FOUNDATION_2026-05-03 |
| GOOGLE_WORKSPACE_CONNECTOR_PLAN.md | superseded | by GOOGLE_READ_ONLY_CONNECTOR_FOUNDATION_2026-05-03 |
| GOOGLE_CONNECT_EMAIL_OAUTH_FUTURE_2026-04-22.md | design-history | Lane C (Gmail OAuth) |
| NOVA_GOOGLE_ACCOUNT_AND_CONNECTOR_ONBOARDING_PLAN.md | design-history | Lane C (onboarding) |
| NOVA_GOOGLE_CONNECTOR_DIRECTION_FINAL_LOCK_2026-04-26.md | superseded | Apr-26 "final lock" (see Cluster 4) |
| NOVA_INTEGRATION_OPPORTUNITY_ROADMAP_2026-04-27.md | design-history | Lane C / D reference |

## Cluster 3 — Personality layer (8 docs)

Cluster verdict: **PARTIALLY IMPLEMENTED.** Runtime has `nova_backend/src/personality/` (two-layer
voice). These are design + audit history for a built area, not forward plans. Belongs to the
design layer, not the roadmap.

| Doc | Status | Intended home |
| --- | --- | --- |
| PERSONALITY_LAYER_ARCHITECTURE.md | design-history | design/personality |
| PERSONALITY_LAYER_IMPLEMENTATION_PLAN.md | design-history | design/personality |
| PERSONALITY_LAYER_DESIGN_PROMPT.md | design-history | design/personality |
| PERSONALITY_LAYER_GOVERNANCE_AUDIT_v2.md | design-history | design/personality (current audit) |
| PERSONALITY_LAYER_GOVERNANCE_AUDIT.md | superseded | by _v2 |
| PERSONALITY_IMPLEMENTATION_PLAN_AUDIT.md | design-history | design/personality |
| PERSONALITY_LIVE_WIRING_DESIGN_SCOPE.md | design-history | design/personality |
| PERSONALITY_PHASE_3_DESIGN_SCOPE.md | design-history | design/personality |

## Cluster 4 — April 2026 vision / decision "final locks" (17 docs)

Cluster verdict: **SUPERSEDED.** This is a dense set of 2026-04-26-era "final lock / decision
record / product vision" docs. They converged into `docs/product/PRODUCT_DEFINITION.md` (identity
converged 2026-07-07) and the July roadmap North Star. Multiple competing "final" direction docs
cannot all be current. **Do not promote; strong archive candidates.**

| Doc | Status |
| --- | --- |
| NOVA_FULL_STACK_DIRECTION_FINAL_LOCK_2026-04-26.md | superseded |
| NOVA_ROLE_BASED_ASSISTANT_DECISION_RECORD_2026-04-26.md | superseded |
| NOVA_ROLE_BASED_ASSISTANT_CORE_VISION.md | superseded |
| NOVA_SOLO_BUSINESS_ASSISTANT_DECISION_RECORD_2026-04-26.md | superseded |
| NOVA_SOLO_BUSINESS_ASSISTANT_PRODUCT_VISION.md | superseded |
| NOVA_SOLO_BUSINESS_ASSISTANT_IMPLEMENTATION_NOTES.md | superseded |
| NOVA_EVERYDAY_MODE_PRODUCT_VISION.md | superseded |
| NOVA_EVERYDAY_MODE_IMPLEMENTATION_NOTES.md | superseded |
| NOVA_EVERYDAY_MODE_REVIEW_SUMMARY_2026-04-26.md | superseded |
| NOVA_VOICE_FIRST_ASSISTANT_DIRECTION.md | superseded |
| NOVA_VOICE_FIRST_ELEVENLABS_FINAL_REVIEW_2026-04-26.md | superseded |
| NOVA_STRATEGIC_VISION.md | superseded |
| NOVA_MARKET_POSITION.md | superseded |
| ARCHITECTURAL_POSITIONING.md | superseded |
| REALISTIC_SCOPE_AND_PRIORITIES.md | superseded |
| NOVA_TWO_DOMAIN_DIRECTION_2026-05-11.md | superseded |
| NOVA_SESSION_REFERENCE_SUMMARY_2026-04-26.md | superseded |

## Cluster 5 — OpenClaw / autonomy / voice (12 docs)

Cluster verdict: **MIXED.** Autonomy/learning theory → Horizon (H1/H2). OpenClaw implementation →
design history for the built/partial Phase 8/9 OpenClaw runtime. Voice/ElevenLabs is queued, not
active (`docs/status/CURRENT_WORK_STATUS.md`).

| Doc | Status | Intended home |
| --- | --- | --- |
| NOVA_GOVERNED_AUTONOMY_DIRECTION_2026-05-11.md | horizon | H1/H2 earned autonomy |
| NOVA_GOVERNED_LEARNING_PLAN.md | horizon | H2 learning layer |
| openclaw_sovereign_governance.md | horizon | H1/H2 |
| NOVA_OPENCLAW_AUTOMATED_WORKFLOW_OPPORTUNITY_MAP_2026-04-27.md | horizon | H1 (shadow mode) |
| FUTURE_AGENT_ARCHITECTURE_BACKLOG.md | horizon | H-series agent backlog |
| NOVA_OPENCLAW_HANDS_LAYER_IMPLEMENTATION_PLAN.md | design-history | Phase 8/9 OpenClaw |
| NOVA_OPENCLAW_GOVERNANCE_HARDENING_2026-04-21.md | design-history | Phase 8/9 OpenClaw |
| OPENCLAW_INTEGRATION_DESIGN.md | design-history | Phase 8/9 OpenClaw |
| OPENCLAW_INTEGRATION_REVIEW.md | design-history | Phase 8/9 OpenClaw |
| NOVA_TASK_RUN_STATE_PLAN_2026-04-27.md | design-history | Phase 8 run-state |
| NOVA_ELEVENLABS_VOICE_INTEGRATION_PLAN.md | horizon | queued-not-active (voice) |
| NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md | superseded | Apr-26 voice cluster |

## Cluster 6 — Misc specs / infra (11 docs)

| Doc | Status | Intended home |
| --- | --- | --- |
| NOVA_PROVIDER_BUDGET_AND_USAGE_CONTROL_PLAN_2026-04-28.md | roadmap-lane | Lane B / cost governance |
| NOVA_REQUEST_UNDERSTANDING_CONTRACT.md | design-history | Brain / task understanding (partial) |
| NOVA_REQUEST_UNDERSTANDING_REVIEW_CARD_DONE_MEANS_2026-04-28.md | design-history | Brain / task understanding |
| NOVA_CONVERSATION_COHERENCE_LAYER_PLAN.md | design-history | Lane D coherence |
| NOVA_COHERENCE_MEMORY_BACKGROUND_ARCHITECTURE_ALIGNMENT.md | design-history | Lane D coherence |
| DIAMOND_PREVIEW_RELEASE_STANDARD_2026-04-23.md | design-history | Lane D preview standard |
| EMAIL_COORDINATION_BOARD.md | design-history | Lane C (email) |
| PHASE_2_DESIGN_SCOPE.md | design-history | design/personality phase 2 |
| repo_improvement_action_plan.md | design-history | Lane B robustness reference |
| NOVA_SOCIAL_CONTENT_OPERATOR_DESIGN_2026-04-21.md | design-history | H12 (do not promote — read-only boundary) |
| NOVA_EVERYDAY_TASK_SERVICE_EXPANSION_2026-04-26.md | superseded | Apr-26 everyday-mode cluster |

## Subfolders and non-doc files

| Path | Status | Note |
| --- | --- | --- |
| ai_ecosystem_operating_model/ (11 md, vault template) | fixture/reference | labeled reference by the roadmap Supersession Note |
| auralis_mock_leads/ (*.json) | fixture/reference | mock lead test data, not a plan |
| auralis_digital/SOCIAL_CONTENT_WORKFLOW_PACK.md | owner-paused | Auralis second business |
| FarFuture/PORTFOLIO_OPERATING_MODEL_2026-04-22.md | horizon | portfolio operating model |
| active_screen_command_layer/README.md | horizon | screen-command surface (future) |
---

## Archive candidates (do not move without a separate reviewed pass)

The clearest candidates for a future archival pass are the **17 superseded April-2026 vision /
decision "final lock" docs** in Cluster 4, plus the individually-marked `superseded` rows above
(older Google connector plans, personality audit v1, PORTFOLIO_PRIORITY_SWITCH, the Apr-26 voice
and everyday-task docs). Moving files is intentionally **out of scope** for this map — it is a
separate, reviewed pass. This map only makes the candidates legible.
