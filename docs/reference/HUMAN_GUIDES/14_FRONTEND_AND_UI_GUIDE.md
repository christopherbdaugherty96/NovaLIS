# Frontend and UI Guide
Updated: 2026-04-10

## Purpose
This guide explains Nova's frontend in plain language.

## What The Frontend Is For
The frontend is the visible layer of Nova.
It is where users actually experience the system.

Its job is to:
- show responses clearly
- surface widgets and thread views
- make follow-up actions easy
- provide calm presence through the orb
- display system and continuity state without becoming an authority surface
- make trust, workspace, memory, and onboarding legible to non-technical users

## Main Runtime Frontend Files
The runtime-served frontend lives in:
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard-config.js`
- `nova_backend/static/dashboard-workspace.js`
- `nova_backend/static/dashboard-control-center.js`
- `nova_backend/static/dashboard-chat-news.js`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/orb.js`
- `nova_backend/static/style.phase1.css`
- `nova_backend/static/dashboard-surfaces.css`

There is also a maintained mirror copy in:
- `Nova-Frontend-Dashboard/`

Current repo rule:
- `nova_backend/static/` is the runtime-served canonical frontend
- `Nova-Frontend-Dashboard/` is a maintained mirror and should stay matched
- if `scripts/check_frontend_mirror_sync.py` fails, fix the mirror drift immediately

Current planning references for frontend cleanup and productization:
- `docs/design/Phase 4.5/NOVA_FRONTEND_FOUNDATION_AND_USABILITY_ROADMAP_2026-04-10.md`
- `docs/design/Phase 4.5/NOVA_USABILITY_NEXT_STEPS_ROADMAP_2026-04-10.md`
- `docs/design/Phase 6/NOVA_SYSTEM_AUDIT_AND_PRODUCTIZATION_GAPS_2026-04-10.md`

There is now also a product-facing landing preview at:
- `nova_backend/static/landing.html`

## What Each Main File Does

### `index.html`
The main shell of the dashboard page.
It now defines the major user-facing views:
- Chat
- News
- Intro
- Home
- Agent
- Workspace
- Policies
- Memory
- Trust
- Settings

### `dashboard.js`
The most important frontend logic file.
It handles things like:
- websocket interaction
- rendering chat and widgets
- thread map and thread detail behavior
- trust and system-status surfaces
- persistent navigation and header page/runtime status
- reasoning transparency surfaces
- remote bridge and connection-status surfaces
- policy review rendering
- memory review and item actions
- memory recency review and lineage visibility
- workspace-board rendering
- structure-map rendering
- intro and settings rendering
- setup-readiness rendering for first-run and settings flows
- home-agent operator rendering
- first-run guidance
- follow-up actions

### `dashboard-config.js`
Shared static frontend config for:
- API and websocket base wiring
- page labels and navigation metadata
- quick-action sets by page
- command suggestions and help examples
- command-discovery groupings

This file exists to shrink the main dashboard surface without changing runtime behavior.

### `dashboard-workspace.js`
Shared Home and Workspace surface logic for:
- continuity helpers and thread resume actions
- workspace refresh requests
- thread map and thread detail rendering
- Workspace Home, Workspace Board, structure-map, operational-context, and assistive-notice rendering

This file exists to peel the workspace-facing product surfaces out of the main dashboard runtime.

### `dashboard-control-center.js`
Shared control-center logic for:
- policy review and policy readiness surfaces
- tone, schedule, and pattern-review surfaces
- operator health, capability visibility, and Trust Center rendering
- Home Agent delivery, run-state, and template surfaces
- runtime Settings rendering and settings-update helpers

This file exists to peel the operational review and settings product surfaces out of the main dashboard runtime.

### `dashboard-chat-news.js`
Shared interaction logic for:
- chat rendering and chat-adjacent helpers
- news, weather, and search surfaces
- modal interactions and startup/help flows
- cross-surface UI actions that are product-facing but not part of the control-center or workspace modules

This file exists to peel the conversational and discovery-heavy UI surfaces out of the main dashboard runtime.

### `orb.js`
The orb presence layer.
It is meant to create a sense of calm presence, not a hidden semantic signal.

### `style.phase1.css`
The base styling layer for the dashboard shell, orb, accessibility, and responsive behavior.
The separate landing-preview page uses its own embedded product-preview styling.

### `dashboard-surfaces.css`
The product-surface styling layer for:
- Home and Workspace pages
- Agent, Trust, Policy, Memory, and Settings pages
- chat, news, weather, search, and modal interaction surfaces

This file exists to reduce cross-surface CSS coupling and make page-level UI work easier to maintain.

## What The Frontend Shows Today
The frontend can present:
- chat output
- search widgets
- weather/news/calendar widgets
- system status
- persistent page navigation and header context
- Workspace Home on the Home page
- a dedicated Workspace page
- a dedicated Agent page
- a dedicated Policies page
- a dedicated Trust page
- a dedicated Introduction page
- a separate landing-preview page
- a dedicated Settings page
- a live setup-readiness checklist on Intro and Settings
- thread map and thread detail
- continuity and memory actions
- follow-up prompts
- screen/perception results
- a first-run guide for non-technical users
- startup-help copy for users who are stuck on `Connecting`
- a stronger first-run magic-moment prompt centered on `explain this`
- a clearer text-bearing thinking bar while Nova is working
- visible push-to-talk state changes
- timeout-backed snapshot fallbacks with a direct calendar-to-Settings action
- inline confirmation before state-changing memory actions are sent
- a dedicated Recent memory action on the Memory page

More specifically, the current dashboard can now show:
- Home-page Workspace Home
- Home-page launch area that now stays clearly primary over review surfaces
- Home-page Workspace Home that now favors one focus lane, fewer resume cards, and quieter support actions
- Home-page capability review as the main secondary lane instead of multiple competing admin-style panels
- Home-page Workspace Home operational-context section
- Home-page Workspace Home assistive-notices section
- Home-page and Trust-page assistive notice cards with dismiss and mark-resolved controls
- Memory Center list and item detail
- Memory Center recent-memory access and richer supersede-lineage detail for edited items
- top-level navigation between Chat, Home, News, Workspace, Memory, Policies, Trust, Settings, and Intro
- top-level navigation between Chat, Home, News, Agent, Workspace, Memory, Policies, Trust, Settings, and Intro
- header page context and runtime connection state
- News-page in-card summaries
- bounded second-opinion controls
- assistant chat summary cards for bottom-line, main-gap, and best-correction signals
- Workspace page project board
- Workspace page selected-project drill-down and recent decisions
- Structure Map for local-project visualization with structured graph output
- Trust page recent governed actions, blocked conditions, drill-down, and capability visibility
- Trust page operational-context panel with refresh/reset controls
- Trust page assistive-notices panel with refresh and direct Settings path
- Trust page assistive-notices panel now also shows when notices are cooling down or already handled
- Trust page now includes a handled-notices review list for the current continuity window
- Trust page reasoning-transparency section with provider, route, mode, authority, and last outcome
- Trust page language that now leads with user questions: what happened, what was blocked, what left the device, and what needs attention
- Policy Review Center draft overview, selected-draft detail, simulation review, and one-shot manual run review
- Intro page setup-readiness checklist with direct connection-status and Home actions
- Intro page setup flow that now keeps the main first steps tighter and more obviously optional where appropriate
- Intro page that now removes most duplicate explainer sections in favor of guided setup plus first useful action
- Settings page setup-mode selection, runtime permission controls, reasoning transparency, and voice confidence review
- Settings page setup checklist with current next-step guidance for the active device/runtime
- Settings page local-first AI routing controls, optional OpenAI lane visibility, and metered budget controls
- Settings page assistive-noticing mode controls
- Settings page provider, connection, bridge-status, and settings-history review
- Settings page connection guidance that now distinguishes what is configurable today from what still remains manual setup
- Trust page remote-bridge review
- Agent page runtime cards, template availability state, delivery-mode controls, per-template schedule controls, ready-for-review inbox state, and recent run history
- Agent page setup/readiness review for the local summarizer, weather, calendar, remote bridge, and scheduler so the user can see what is optional versus currently ready
- Agent page narrow scheduled briefing controls that stay visible and pausable instead of acting like hidden automation
- Agent page schedule metadata that now surfaces quiet-hours and rate-limit hold reasons when policy suppresses a due scheduled run
- Agent page summary language that now frames OpenClaw as Nova's visible worker layer rather than an autonomous system
- richer long-form report rendering for `INTELLIGENCE BRIEF` and `DETAILED STORY ANALYSIS` surfaces, with the lead takeaway visible earlier in the chat card

## What The Frontend Is Not Supposed To Become
Nova's frontend is not supposed to become a hidden authority layer.
That means it should not silently decide to:
- execute actions on its own
- create hidden background loops
- signal internal reasoning in misleading ways
- become a disguised autonomous agent surface

Its role is to make Nova legible and usable.

## Why The Frontend Matters So Much
Many systems become impressive in code but weak in real use.
The frontend is where Nova starts to feel like:
- a workspace
- a continuity system
- a trust-preserving daily tool
- a calm intelligence layer

The newer Workspace, Agent, Trust, Policies, Memory, Intro, Settings, and first-run surfaces are especially important because they make Nova feel less like a command console and more like a product a normal person can return to every day.

Current note:
- the low-risk Phase 4.5 usability pass is now effectively complete
- the stronger within-frontend structural simplification pass has also landed
- any future redesign question is now about whether to go beyond the current static frontend architecture
