# Nova — Master Roadmap
Updated: 2026-04-03
Status: Living document
Purpose: Keep one honest prioritized backlog that reflects what is already shipped, what is next, and what should stay future work

This is the single planning backlog for work that still remains.
It should not re-list already shipped slices as if they are still untouched.

---

## How To Read This

- `P0` — do next
- `P1` — do soon after P0
- `P2` — important, but not blocking the current product line
- `P3` — future expansion

Status tags:
- `[ ]` not started
- `[~]` in progress or partially landed
- `[x]` shipped baseline

Runtime truth still wins over this design packet.

---

## Grounded Current Position

Nova is currently:
- Phase 7 complete in the bounded reasoning sense
- Phase 8 active, with meaningful usefulness and operator-foundation work already landed
- Phase 4.5 still partial, but now mostly in manual polish territory instead of missing major UI systems

Recently shipped:
- `[x]` user profile surface and governed identity-memory write
- `[x]` connection cards with save/test/disconnect/reset flows
- `[x]` improved intro/setup onboarding flow
- `[x]` structured morning brief across chat and OpenClaw
- `[x]` connection-aware starter usefulness cards
- `[x]` visible OpenClaw active run state on Home and Agent surfaces

That means the current next work is not “start from zero.”
It is:
- close the last Phase-4.5 polish gap
- finish Phase-8 usefulness through real connectors
- then close Phase 8 properly before Phase-9 intelligence expansion becomes the main code focus

---

## Corrected Execution Order

```
Stage 1 — Phase 4.5 closeout
  manual polish, live-device validation, final setup/readiness cleanup

Stage 2 — Phase 8 usefulness
  real calendar integration, stronger daily-assistant usefulness

Stage 3 — Phase 8 closure
  envelope execution, pause/resume, richer run controls

Stage 4 — Phase 9 intelligence
  DeepSeek tier, provider routing, memory-tier evolution
```

Phase 9 should not become the main implementation track until Stage 3 is more complete.

---

## P0 — Finish The Current Product Foundation

### 0.1 — Last Phase-4.5 Closeout Work
Design docs:
- `docs/design/Phase 4.5/NOVA_CONNECTIONS_SETUP_UI_REDESIGN.md`
- `docs/design/Phase 4.5/NOVA_USER_FRIENDLINESS_TODO_2026-04-02.md`

- `[x]` profile baseline shipped
- `[x]` connection-card baseline shipped
- `[x]` intro/setup baseline shipped
- `[ ]` run a real manual UX pass across Intro, Home, Agent, Settings, live-help, and voice
- `[ ]` validate local TTS confidence on real hardware
- `[ ]` tighten any remaining setup/readiness copy that still feels diagnostic instead of assistant-like

### 0.2 — Finish Phase-8 Usefulness
Design docs:
- `docs/design/Phase 8/PHASE_8_DOCUMENT_MAP.md`
- `docs/design/Phase 8/NOVA_OPENCLAW_HOME_AGENT_MASTER_REFERENCE_2026-03-27.md`

- `[x]` structured morning brief baseline shipped
- `[x]` connection-aware home usefulness starters shipped
- `[ ]` real calendar integration beyond the current ICS-backed snapshot baseline
- `[ ]` better in-chat answer to “what can you do right now?” based on live setup state
- `[ ]` continue improving daily assistant quality without widening authority

### 0.3 — Finish Phase-8 Closure
Design docs:
- `docs/design/Phase 8/PHASE_8_OPENCLAW_CANONICAL_GOVERNED_AUTOMATION_SPEC_2026-03-25.md`
- `docs/design/Phase 8/PHASE_8_OPENCLAW_GOVERNED_EXECUTION_PLAN.md`
- `docs/design/Phase 8/NOVA_PHASE_8_USER_OPERABILITY_AND_RUN_SYSTEM_AUDIT_2026-04-05.md`

- `[x]` visible run-state baseline shipped
- `[ ]` pause / resume controls for governed runs
- `[ ]` richer interruption, failure, and stop-state UX
- `[ ]` full envelope execution foundations with explicit budgets and previews
- `[ ]` shared run visibility across the intended Nova surfaces
- `[ ]` first-class run object and clearer run timeline across the main operator surfaces
- `[ ]` stronger checkpoint UX for meaningful outward-facing outcomes
- `[ ]` lower-noise focus mode so one active task dominates instead of competing with every panel
- `[ ]` WebSocket hardening for heartbeat, reconnect debounce, and single-connection stability

---

## P1 — Memory, Automation, And Personalization Follow-Through

### 1.1 — Memory Tier Evolution
Design doc:
- `docs/design/phase 5/NOVA_MEMORY_TIERS_DESIGN.md`

- `[ ]` rolling-memory purge behavior
- `[ ]` permanent-memory promotion UX
- `[ ]` inspectable memory-tier surfaces that stay easy to understand
- `[ ]` keep all memory evolution explicit and governed

### 1.2 — User-Created Automations
Design doc:
- `docs/design/Phase 8.5/NOVA_AUTOMATIONS_DESIGN.md`

- `[ ]` custom template creation
- `[ ]` extended recurrence options
- `[ ]` RSS / research digest template
- `[ ]` keep all automation widening inside explicit settings and visible surfaces

### 1.3 — Preference Learning First
Design doc:
- `docs/design/phase 5/NOVA_GOVERNED_LEARNING_LADDER_2026-04-02.md`

- `[ ]` tone and response-style preference learning
- `[ ]` summary-shape preference learning
- `[ ]` editable and resettable learned preferences
- `[ ]` no hidden initiative or silent workflow creation

---

## P2 — Connector And Communication Expansion

### 2.1 — Email And Calendar Workflows
Design docs:
- `docs/design/Phase 8.5/NOVA_AUTOMATIONS_DESIGN.md`
- `docs/design/Phase 11/NOVA_IDEA_TO_WORKFLOW_OPERATOR_MODEL_TODO_2026-04-02.md`

- `[ ]` email connector implementation
- `[ ]` meeting-prep workflow
- `[ ]` document ingest / file-watch workflow
- `[ ]` job application and communication operator flows

### 2.2 — Better Everyday Operator Workflows
Design docs:
- `docs/design/Phase 8/NOVA_GOVERNED_VISIBLE_OPERATOR_MODE_TODO_2026-04-02.md`
- `docs/design/Phase 11/NOVA_INTERACTION_MODEL_V1_STRICT_ON_RISK_SOFT_ON_FLOW_2026-04-02.md`

- `[ ]` safer form-fill assistance
- `[ ]` sign-in assistance with hard credential boundaries
- `[ ]` “handle this for me” low-risk workflow shaping
- `[ ]` one-checkpoint-per-meaningful-outcome behavior

---

## P2 — Trading And Financial Assistant Work

### 2.3 — Trading Connector Direction
Design docs:
- `docs/design/Phase 11/NOVA_TRADING_CONNECTOR_DESIGN.md`
- `docs/design/Phase 8/TRADING_MODE_GUARDRAILS_2026-03-27.md`

- `[ ]` connector base classes and budget store
- `[ ]` paper-trading-first path
- `[ ]` portfolio / watchlist / market-research surfaces
- `[ ]` no live autonomous trading until much later guarded phases

### 2.4 — Personal Finance Intelligence
Design docs:
- `docs/design/Phase 11/NOVA_HOME_ASSISTANT_PRODUCT_TRUTH_2026-04-02.md`
- `docs/design/Phase 11/NOVA_IDEA_TO_WORKFLOW_OPERATOR_MODEL_TODO_2026-04-02.md`

- `[ ]` spending insight
- `[ ]` subscription detection
- `[ ]` budgeting suggestions
- `[ ]` keep this in the analysis/help lane before any transaction flow

---

## P3 — Phase-9 Intelligence Work

### 3.1 — DeepSeek V3 As Tier-2 Provider
Design docs:
- `docs/design/Phase 9/NOVA_AGENT_NODE_ARCHITECTURE_2026-04-01.md`
- `docs/design/Phase 6/NOVA_LOCAL_FIRST_INTELLIGENCE_ARCHITECTURE_AND_MODEL_ROUTING_TODO_2026-04-02.md`

- `[ ]` add DeepSeek base URL and API-key support
- `[ ]` add provider pricing / budget visibility
- `[ ]` keep Nova local-first by default

### 3.2 — Provider Routing In Conversation
- `[x]` conversation router exists
- `[x]` complexity heuristics exist
- `[ ]` route primary responses across local / DeepSeek / OpenAI tiers
- `[ ]` keep routing visible, bounded, and budget-aware

### 3.3 — Memory And Continuity Coherence
- `[ ]` stronger memory coherence across surfaces
- `[ ]` later workflow-habit learning after preference learning is stable
- `[ ]` bounded proactive learning only after scheduler and routines are earned

---

## P3 — Node / Mass-Node / Operator Expansion

Design docs:
- `docs/design/Phase 9/NOVA_GOVERNED_MASS_NODE_OPERATOR_SYSTEM_2026-04-02.md`
- `docs/design/Phase 9/PHASE_9_GOVERNED_NODE_PLAN.md`

- `[ ]` webhook trigger path
- `[ ]` multi-node protocol and trust handshake
- `[ ]` bounded cross-node execution
- `[ ]` keep Nova as the governing layer, not just another worker

---

## Open Questions

- `[ ]` When should rolling memories be suggested for permanent promotion?
- `[ ]` Should calendar remain ICS-first until a stronger official connector is earned?
- `[ ]` How much of “what can you do?” should be dynamic in chat versus Home surfaces?
- `[ ]` When should Phase 4.5 be declared fully closed in runtime docs?
- `[ ]` What is the exact minimum Phase-8 closure bar before Phase-9 provider routing becomes the main focus?

---

## Design Doc Index

| Doc | Topic |
| --- | --- |
| `NOVA_AGENT_NODE_ARCHITECTURE_2026-04-01.md` | intelligence tiers, provider routing, node roadmap |
| `NOVA_CONNECTIONS_SETUP_UI_REDESIGN.md` | setup page, profile, connection cards |
| `NOVA_MEMORY_TIERS_DESIGN.md` | rolling memory, permanent memory, purge logic |
| `NOVA_AUTOMATIONS_DESIGN.md` | templates, triggers, digest, email triage, file watch |
| `NOVA_TRADING_CONNECTOR_DESIGN.md` | governed trading connector direction |
| `NOVA_GROUNDED_CURRENT_STATUS_AND_NEXT_ROADMAP_2026-04-02.md` | current grounded ordering and phase truth |
