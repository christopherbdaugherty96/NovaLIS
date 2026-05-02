# Future Docs Guide

**Purpose:** Explain what future documents are for, how much authority they carry, and how they relate to Nova's live project state.

## Short Version

The `docs/future/` folder preserves direction.
It does not define current truth.

Use these sources in order of authority:
1. Running code
2. Generated runtime truth docs
3. Active TODO / current sprint docs
4. Future planning docs
5. Historical archives

## Canonical Future Direction

- `ROADMAP.md` — primary future direction and phased expansion path.
- `NOVA_AGENT_STACK_RECOMMENDATIONS.md` — future governed agent-stack architecture direction.

## Brain, Memory, Learning, Routine, and Agent Stack Planning

These docs define future architecture direction. They are not live runtime capability claims:

- `BRAIN_HUMAN_GUIDE.md` - human-readable Brain planning guide.
- `BRAIN_MEMORY_HUMAN_GUIDE.md` - Brain + Memory integration planning guide.
- `NOVA_AGENT_STACK_RECOMMENDATIONS.md` - governed agent stack recommendations based on external agent/orchestration stack review.
- `CONTEXT_PACK_SPEC.md` - planned bounded bridge between Memory/Learning/Search/Project state and Brain.
- `LEARNING_LAYER_SPEC.md` - planned governed adaptation layer.
- `ROUTINE_LAYER_SPEC.md` - planned routine/workflow orchestration layer.
- `DAILY_BRIEF_ROUTINE_SPEC.md` - Daily Brief as Routine Layer surface, not Brain.
- `GUARD_SYSTEM_SPEC.md` - planned Brain/Mode/Context/Routine/Memory/Learning/OpenClaw guard layers.
- `TRACE_AND_OBSERVABILITY_SPEC.md` - planned safe trace and observability surfaces.

## Optional Workflow Planning

These docs preserve possible workflow directions. They are not live runtime
capability claims:

- `AURALIS_WEBSITE_COWORKER_WORKFLOW.md` - future Auralis website-production coworker workflow.
- `AURALIS_LEAD_CONSOLE_V1.md` - future Auralis lead workflow planning surface.
- `auralis_mock_leads/README.md` - fictional mock lead fixtures for planning-only Auralis workflow tests.
- `../tools/youtubelis.md` - pointer to the planning-only YouTubeLIS tool folder.
- `GOOGLE_CONNECTOR_IMPLEMENTATION_ROADMAP.md` - future Google read/context connector roadmap; no runtime connector claim.
- `../design/Phase 6/FREE_FIRST_COST_GOVERNANCE_FIRST_STEPS_2026-04-30.md` - free-first cost posture implementation plan; not runtime enforcement.

## What Belongs Here

Use this folder for:
- long-term vision
- optional expansions
- connector ideas
- future UX concepts
- strategic bets
- experiments not yet committed to build now

## What Does Not Belong Here

Avoid treating this folder as:
- live feature proof
- implementation status
- current sprint authority
- release promises

Examples:
- Brain, Memory, Learning, Context Pack, Routine Layer, Guard, and Trace docs in this folder are future architecture direction until code, tests, generated runtime truth, and proof artifacts agree.
- Daily Brief routine docs describe intended future framing; current runtime behavior must still be checked against code and generated docs.
- Google connector docs are future read/context direction only; no Google OAuth, Gmail, Calendar, Drive, or Gmail-send runtime connector exists until runtime truth proves it.
- Auralis docs are future production discipline workflows only; they do not grant publish, deploy, domain, DNS, or client-send authority.
- YouTubeLIS docs are planning-only tool-folder material; they do not grant upload, publish, account, or background automation authority.
- Free-first docs are design policy until registry metadata, generator output, tests, and UI/proof paths make cost posture runtime-visible.

## Why This Matters

Good future planning is useful.
Confusing future plans with current reality damages trust.

Nova should preserve ambition while staying honest about what exists now.
