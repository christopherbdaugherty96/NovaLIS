# NOVA

Nova is a governed home assistant and personal intelligence workspace.

It is designed to help people think, research, understand screens and files, continue real work, and preserve useful context without turning into a hidden autonomous agent.

Core rule:

`Intelligence may expand. Authority may not expand without explicit unlock.`

## What Nova Is

Nova is meant to feel like:
- a calm home assistant on your computer
- a calm intelligence layer on your computer
- a workspace for understanding information
- a system that can continue project context across sessions
- a governed assistant that stays inspectable and interruptible

Nova helps with:
- answer-first web research
- news headlines, summaries, and deeper story follow-up
- weather, calendar, and daily brief surfaces
- screen capture and screen explanation on explicit request
- file and folder opening through governed local routes
- ongoing thread continuity and governed memory
- read-only second-opinion review
- bounded local computer help

Nova is not meant to be:
- a hidden always-on agent
- a silent background automation loop
- an unbounded browser bot
- a system that expands its own authority without explicit approval

## What Is Live Today

According to the current runtime authority docs, Nova currently includes:
- governed web search
- answer and response verification
- multi-source reporting
- headline summary and intelligence brief flows
- topic/story tracking surfaces
- analysis documents
- weather, news, and calendar snapshots
- screen capture and screen analysis
- explain-anything routing
- governed memory controls
- external reasoning review
- active dashboard, voice, and websocket surfaces
- shipped user profile and connection-card setup surfaces
- guided onboarding and readiness flow
- structured morning brief delivery across chat and OpenClaw
- visible OpenClaw active-run state
- setup-aware "what can you do right now?" capability guidance
- richer calendar guidance for today, tomorrow, and upcoming views

Nova also has an OpenClaw home-agent foundation live as a bounded operator surface:
- manual briefing templates
- delivery controls
- explicit settings-gated scheduling
- strict preflight and rate-limited task reporting

What is not broadly live yet:
- full governed envelope execution
- broad autonomous browser/action control
- full connector-rich calendar integration
- pause/resume and fuller visible run controls across the broader execution layer

For exact runtime truth, always defer to:

- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`

## Why Nova Is Different

Nova's main differentiator is not raw automation breadth.

It is the separation between intelligence and authority.

Nova is being built so that it can:
- reason more deeply
- remember more usefully
- explain more clearly
- help more fluidly

without silently becoming more empowered.

That separation runs through the project:
- Governor-mediated execution
- capability registry control
- enforced network mediation
- append-only ledger logging
- explicit memory controls
- visible trust and settings surfaces

## Start Here

If you want the fastest path to understanding the project, use this order:

1. `docs/reference/HUMAN_GUIDES/README.md`
2. `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
3. `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
4. `docs/canonical/CANONICAL_DOCUMENT_MAP.md`
5. `REPO_MAP.md`

That gives you:
- the plain-language explanation first
- the live runtime truth second
- the governance layer after that
- the codebase map last

## Documentation Map

Nova's documentation is intentionally split by role.

### Human guides
- `docs/reference/HUMAN_GUIDES/`
- plain-language onboarding and product understanding

### Runtime truth
- `docs/current_runtime/`
- generated, runtime-aligned authority and implementation truth

### Proof packets
- `docs/PROOFS/`
- implementation and validation evidence

### Design docs
- `docs/design/`
- future direction, backlog, architecture packets, and planning docs

### Tracked automations
- `automations/`
- tracked project-owned Codex automation definitions and memory snapshots
- lets GitHub carry the same automation prompt/config history that exists in the local Codex setup

### Canonical governance
- `docs/canonical/`
- constitutional and governance source material

If any design or explanatory doc conflicts with runtime truth, runtime truth wins.

## Repository Orientation

Main repository surfaces:
- `nova_backend/src/`
- `nova_backend/tests/`
- `nova_backend/static/`
- `Nova-Frontend-Dashboard/` (maintained mirror copy; `nova_backend/static/` is the runtime-served canonical frontend)
- `nova_backend/src/data/nova_state/` (local runtime state such as connections, settings, memory, and OpenClaw state)
- `docs/`

If you are reviewing the backend first, a strong starting order is:

1. `nova_backend/src/brain_server.py`
2. `nova_backend/src/governor/`
3. `nova_backend/src/conversation/`
4. `nova_backend/src/openclaw/`
5. `nova_backend/src/working_context/`
6. `nova_backend/src/memory/`

If you are reviewing the user experience first, start with:

1. `nova_backend/static/index.html`
2. `nova_backend/static/dashboard-config.js`
3. `nova_backend/static/dashboard-workspace.js`
4. `nova_backend/static/dashboard-control-center.js`
5. `nova_backend/static/dashboard-chat-news.js`
6. `nova_backend/static/dashboard.js`
7. `nova_backend/static/style.phase1.css`
8. `nova_backend/static/dashboard-surfaces.css`
9. `nova_backend/static/orb.js`

## Current Product Direction

Nova is moving toward a stronger home-assistant operator model:
- a helpful home-assistant presence first
- outcome-first interaction
- better project continuity
- answer-first research
- more fluid non-technical UX
- governed reach expansion
- visible operator surfaces instead of hidden autonomy

The current product truth is:

- Governor = law
- Nova = presence

That means Nova should feel calm, personal, and easy to use, while the strict governance stays underneath rather than dominating the user experience.

The project is intentionally trying to expand usefulness without abandoning its trust model.

That means the roadmap favors:
- governed connectors
- visible operator mode
- bounded proactive automation
- clearer approval surfaces

instead of:
- unsafe plugin sprawl
- silent authority expansion
- background self-directed behavior

## Safety Posture

Nova is built around a few non-negotiable rules:
- no hidden autonomy
- no silent authority expansion
- no ungoverned network path
- no direct execution from cognitive reasoning alone
- no silent persistence for important memory or action surfaces
- no background execution outside explicit bounded carve-outs

Nova is strongest when it is:
- clear
- reviewable
- trustworthy
- helpful to non-technical users

## Current Best Reading Paths

### If you want the plain-English product story
- `docs/reference/HUMAN_GUIDES/README.md`

### If you want the exact live runtime state
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`

### If you want the future roadmap and backlog
- `docs/design/README.md`

### If you want the current product truth for where Nova is headed
- `docs/design/Phase 11/NOVA_HOME_ASSISTANT_PRODUCT_TRUTH_2026-04-02.md`

### If you want the most grounded current-status and next-step roadmap
- `docs/design/Phase 6/NOVA_GROUNDED_CURRENT_STATUS_AND_NEXT_ROADMAP_2026-04-02.md`

### If you want the codebase map
- `REPO_MAP.md`

## Short Version

Nova is currently best understood as:
- a calm local-first home assistant on your computer
- a governed intelligence workspace
- a read-heavy research, explanation, and continuity system
- a narrow but real operator surface through OpenClaw

Nova is not trying to be "an agent that can do everything."

It is trying to become a governed workspace that helps people:
- understand what is going on
- keep moving on real work
- carry useful context forward
- use bounded intelligence without losing control
