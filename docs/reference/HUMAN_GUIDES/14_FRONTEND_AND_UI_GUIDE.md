# Frontend and UI Guide
Updated: 2026-03-25

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

## Main Runtime Frontend Files
The runtime-served frontend lives in:
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/orb.js`
- `nova_backend/static/style.phase1.css`

There is also a mirrored copy in:
- `Nova-Frontend-Dashboard/`

## What Each Main File Does

### `index.html`
The main shell of the dashboard page.

### `dashboard.js`
The most important frontend logic file.
It handles things like:
- websocket interaction
- rendering chat and widgets
- thread map and thread detail behavior
- system status surfaces
- follow-up actions

### `orb.js`
The orb presence layer.
It is meant to create a sense of calm presence, not a hidden semantic signal.

### `style.phase1.css`
The main styling layer for the dashboard and orb surface.

## What The Frontend Shows Today
The frontend can present:
- chat output
- search widgets
- weather/news/calendar widgets
- system status
- a Workspace Home card on the Home page
- thread map and thread detail
- continuity/memory actions
- follow-up prompts
- screen/perception results

More specifically, the current dashboard can now show:
- Home-page operator health
- Home-page trust review
- Home-page Workspace Home
- Memory Center list and item detail
- News-page in-card summaries
- second-opinion and follow-up controls

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
- a calm intelligence layer

That is why the dashboard and thread surfaces matter so much.

The newer Workspace Home and Memory Center surfaces are especially important because they make Nova feel less like a command console and more like a place where ongoing work lives.
