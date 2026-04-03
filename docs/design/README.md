# Design Documentation Index

Read this first:
- `docs/design/DESIGN_AUTHORITY.md`

## Purpose

`docs/design/` is the design-intent layer for Nova.

It contains:
- future architecture direction
- phase roadmaps
- product-shaping packets
- backlog notes
- historical design material

It does not define live runtime behavior.

For runtime truth, always defer to:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- verified proof packets in `docs/PROOFS/`

## Root-Level Rule

The top level of `docs/design/` is now intentionally minimal.

Only these root files should remain:
- `docs/design/README.md`
- `docs/design/DESIGN_AUTHORITY.md`

Everything else should live inside:
- a phase folder
- `IDEAS/`
- `archive/`
- `archive(phase 4)/`

## Current Phase Layout

### 2026-04-02 Session Design Docs (now in phase folders)

- `docs/design/Phase 9/NOVA_MASTER_ROADMAP_2026-04-02.md` — master prioritized backlog P0–P3
- `docs/design/Phase 9/NOVA_AGENT_NODE_ARCHITECTURE_2026-04-01.md` — intelligence tiers, provider routing
- `docs/design/Phase 4.5/NOVA_CONNECTIONS_SETUP_UI_REDESIGN.md` — profile setup, connection cards
- `docs/design/phase 5/NOVA_MEMORY_TIERS_DESIGN.md` — rolling + permanent memory tiers
- `docs/design/Phase 8.5/NOVA_AUTOMATIONS_DESIGN.md` — templates, triggers, RSS, email triage, file watch
- `docs/design/Phase 11/NOVA_TRADING_CONNECTOR_DESIGN.md` — governed auto-trading, Alpaca, cap 64

### Phase 3.5
Path:
- `docs/design/Phase 3.5/`

Focus:
- sealed governance foundations
- fast governance architecture
- deferred explainability patterns
- repository authority correction references

Start with:
- `docs/design/Phase 3.5/PHASE_3_5_DOCUMENT_MAP.md`

### Phase 4
Path:
- `docs/design/Phase 4/`

Focus:
- core identity
- deep thought / DeepSeek framing
- early conversational mode and constitutional framing

Start with:
- `docs/design/Phase 4/PHASE_4_DOCUMENT_MAP.md`

### Phase 4.2
Path:
- `docs/design/Phase 4.2/`

Focus:
- orthogonal cognition stack
- presence doctrine
- runtime-alignment notes for the cognition layer

Start with:
- `docs/design/Phase 4.2/PHASE_4_2_DOCUMENT_MAP.md`

### Phase 4.5
Path:
- `docs/design/Phase 4.5/`

Focus:
- UI and orb direction
- speech and input naturalness
- assistant utility audits
- user-facing experience improvements
- structure-map and visual explainer work

Key moved packets:
- `docs/design/Phase 4.5/NOVA_USER_EXPERIENCE_IMPROVEMENT_PLAN_2026-03-26.md`
- `docs/design/Phase 4.5/NOVA_USER_FRIENDLINESS_TODO_2026-04-02.md`
- `docs/design/Phase 4.5/NOVA_STYLE_LAYER_PLAN_2026-03-20.md`

Start with:
- `docs/design/Phase 4.5/PHASE_4_5_DOCUMENT_MAP.md`

### Phase 5
Path:
- `docs/design/phase 5/`

Focus:
- memory governance
- remembrance
- working context
- tone and assistive noticing
- continuity and governed awareness
- preference learning as the first bounded learning layer

Start with:
- `docs/design/phase 5/PHASE_5_DOCUMENT_MAP.md`

### Phase 6
Path:
- `docs/design/Phase 6/`

Focus:
- trust loop completion
- policy executor and simulation surfaces
- capability topology
- productization and packaging
- repo audit and remediation
- sovereignty-alignment realignment
- local-first intelligence architecture and provider-routing consolidation

Key moved packets:
- `docs/design/Phase 6/NOVA_SOVEREIGNTY_PLATFORM_PHASE_REALIGNMENT_2026-03-18.md`
- `docs/design/Phase 6/NOVA_CORRECTED_REPO_AUDIT_AND_REMEDIATION_2026-03-26.md`
- `docs/design/Phase 6/NOVA_AUDIT_TODO_2026-03-28.md`
- `docs/design/Phase 6/NOVA_CURRENT_PHASE_GROUNDING_AND_FIRST_PRIORITY_TODO_2026-04-02.md`

Start with:
- `docs/design/Phase 6/PHASE_6_DOCUMENT_MAP.md`

### Phase 7
Path:
- `docs/design/Phase 7/`

Focus:
- governed external reasoning
- second-opinion flows
- conversational competitiveness
- web-search and news reasoning improvements
- silent-governor conversational behavior

Key moved packets:
- `docs/design/Phase 7/CONVERSATIONAL_CORE_PHASE_PLAN_2026-03-19.md`
- `docs/design/Phase 7/NOVA_WEBSEARCH_ANSWER_AND_REASONING_PLAN_2026-03-21.md`
- `docs/design/Phase 7/NOVA_NEWS_EXPERIENCE_AND_REASONING_PLAN_2026-03-21.md`

Start with:
- `docs/design/Phase 7/PHASE_7_DOCUMENT_MAP.md`

### Phase 8
Path:
- `docs/design/Phase 8/`

Focus:
- governed execution
- OpenClaw home-agent architecture
- OpenAI provider routing for bounded task-report flows
- visible operator expansion direction
- execution widening under trust controls
- trading guardrails and crypto connector planning

Key moved packets:
- `docs/design/Phase 8/NOVA_GOVERNED_VISIBLE_OPERATOR_MODE_TODO_2026-04-02.md`
- `docs/design/Phase 8/NOVA_GOVERNED_REACH_EXPANSION_AND_OPENCLAW_COMPARISON_2026-04-02.md`
- `docs/design/Phase 8/NOVA_OPENCLAW_END_TO_END_EXPANSION_MASTER_TODO_2026-04-02.md`

Start with:
- `docs/design/Phase 8/PHASE_8_DOCUMENT_MAP.md`

### Phase 8.5
Path:
- `docs/design/Phase 8.5/`

Focus:
- scheduler and proactive delivery direction
- bounded proactive behavior under explicit settings control
- later bounded proactive learning after earlier trust and usability layers are earned

Start with:
- `docs/design/Phase 8.5/PHASE_8_5_DOCUMENT_MAP.md`

### Phase 9
Path:
- `docs/design/Phase 9/`

Focus:
- governed node architecture
- multi-system coherence
- more continuous agent-system vision under trust constraints
- governed capability-growth proposals under explicit human approval

Key moved packets:
- `docs/design/Phase 9/NOVA_CONTINUOUS_AGENT_OS_VISION_AND_TRUST_ROADMAP_2026-03-21.md`
- `docs/design/Phase 9/NOVA_NEXT_LEVEL_ROBUST_AGENT_ROADMAP_2026-03-21.md`

Start with:
- `docs/design/Phase 9/PHASE_9_DOCUMENT_MAP.md`

### Phase 10
Path:
- `docs/design/Phase 10/`

Focus:
- long-horizon autonomy and mutation-control direction
- reviewable adaptation and stronger containment-proof thinking

Note:
- this phase is intentionally thin and is fed mostly by earlier-phase inputs plus adjacent Phase-9 autonomy theory

Start with:
- `docs/design/Phase 10/PHASE_10_DOCUMENT_MAP.md`

### Phase 11
Path:
- `docs/design/Phase 11/`

Focus:
- future operator-model expansion
- home-assistant product truth and experience shaping
- governed creator and business lanes
- self-development mode
- future naming/product-lane direction

Interpretation:
- read the home-assistant product truth first
- read the idea-to-workflow operator model second
- treat the remaining packets as future-lane expansions under that calmer core identity

Key moved packets:
- `docs/design/Phase 11/NOVA_HOME_ASSISTANT_PRODUCT_TRUTH_2026-04-02.md`
- `docs/design/Phase 11/NOVA_IDEA_TO_WORKFLOW_OPERATOR_MODEL_TODO_2026-04-02.md`

Start with:
- `docs/design/Phase 11/PHASE_11_DOCUMENT_MAP.md`

## Special Folders

### IDEAS
Path:
- `docs/design/IDEAS/`

Use for:
- raw idea capture
- not-yet-phased concepts

### archive
Path:
- `docs/design/archive/`

Use for:
- superseded design artifacts
- deprecated packets no longer treated as current
- archived redundant placeholder files that no longer need to clutter active phase folders

### archive(phase 4)
Path:
- `docs/design/archive(phase 4)/`

Use for:
- legacy Phase 4 material preserved separately from the newer consolidated archive

## Recommended Reading Order

If you want the fastest useful orientation:

1. `docs/design/DESIGN_AUTHORITY.md`
2. relevant phase document map
3. the phase packet you care about
4. compare against `docs/current_runtime/CURRENT_RUNTIME_STATE.md`

Every active phase folder should now be entered through its document map first.

## Short Version

Use `docs/design/` for:
- intended direction
- phase planning
- backlog notes

Use runtime docs for:
- what Nova can actually do today
