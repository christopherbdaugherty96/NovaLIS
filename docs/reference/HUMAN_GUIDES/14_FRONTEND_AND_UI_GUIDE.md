# Frontend and UI Guide
Updated: 2026-03-26

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
- `nova_backend/static/dashboard.js`
- `nova_backend/static/orb.js`
- `nova_backend/static/style.phase1.css`

There is also a mirrored copy in:
- `Nova-Frontend-Dashboard/`

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
- reasoning transparency surfaces
- remote bridge and connection-status surfaces
- policy review rendering
- memory review and item actions
- workspace-board rendering
- structure-map rendering
- intro and settings rendering
- first-run guidance
- follow-up actions

### `orb.js`
The orb presence layer.
It is meant to create a sense of calm presence, not a hidden semantic signal.

### `style.phase1.css`
The main styling layer for the dashboard and orb surface.
It now also styles the dedicated Workspace, Trust, Intro, and Settings pages and the first-run guide.
The separate landing-preview page uses its own embedded product-preview styling.

## What The Frontend Shows Today
The frontend can present:
- chat output
- search widgets
- weather/news/calendar widgets
- system status
- Workspace Home on the Home page
- a dedicated Workspace page
- a dedicated Policies page
- a dedicated Trust page
- a dedicated Introduction page
- a separate landing-preview page
- a dedicated Settings page
- thread map and thread detail
- continuity and memory actions
- follow-up prompts
- screen/perception results
- a first-run guide for non-technical users
- a stronger first-run magic-moment prompt centered on `explain this`

More specifically, the current dashboard can now show:
- Home-page operator health
- Home-page trust review
- Home-page Workspace Home
- Memory Center list and item detail
- News-page in-card summaries
- bounded second-opinion controls
- Workspace page project board
- Workspace page selected-project drill-down and recent decisions
- Structure Map for local-project visualization with structured graph output
- Trust page recent governed actions, blocked conditions, drill-down, and capability visibility
- Trust page reasoning-transparency section with provider, route, mode, authority, and last outcome
- Policy Review Center draft overview, selected-draft detail, simulation review, and one-shot manual run review
- Settings page setup-mode selection, runtime permission controls, reasoning transparency, and voice confidence review
- Settings page provider, connection, bridge-status, and settings-history review
- Trust page remote-bridge review

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

The newer Workspace, Trust, Policies, Memory, Intro, Settings, and first-run surfaces are especially important because they make Nova feel less like a command console and more like a product a normal person can return to every day.
