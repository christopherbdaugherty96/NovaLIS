# OpenAI Agent Operating Model
Date: 2026-03-27
Status: Current design truth for Nova's local-first OpenAI lane

## Purpose
This document defines how OpenAI should fit inside Nova as a governed, local-first helper lane.

It is not permission for Nova to become cloud-first.
It is not permission for OpenClaw to become an unmetered autonomous runtime.
It is the operating model for using OpenAI deliberately, sparingly, and visibly.

## Core Principle
Nova should remain:
- local-first
- explicit
- budgeted
- reviewable
- user-sovereign

OpenAI should be treated as:
- an optional metered reasoning lane
- a hard-task coding lane
- a synthesis lane for difficult planning and debugging work

OpenAI should not be treated as:
- the default runtime for everyday requests
- a hidden background worker
- an unmetered control plane
- direct execution authority

## The Three-Layer Model
The intended product shape is:

1. Nova
- visible voice
- trust layer
- settings and budget surface
- operator explanations

2. OpenClaw
- bounded worker inside Nova
- governed task runner
- template execution, delivery, and scheduling
- never the final user-facing voice

3. OpenAI
- optional metered model/provider lane
- used only when local and open-source routes are not the right fit
- always visible in Settings, Trust, and usage reporting

## What OpenAI Should Be Used For
OpenAI is a good fit for:
- multi-file coding help
- hard debugging passes
- architecture synthesis
- long-form plan consolidation
- difficult research synthesis
- cross-document reasoning after local retrieval narrows the context

OpenAI is not the preferred default for:
- weather
- calendar snapshots
- RSS/news fetches
- deterministic project state reads
- local file routing
- governed memory list/overview
- simple classification that can be done locally

## Routing Ladder
Nova should route work in this order:

1. Deterministic local tool
- no model
- no paid provider

2. Local model
- short local summary
- extraction
- classification
- low-cost chat support

3. OpenAI metered lane
- only when explicitly enabled
- only when routing policy allows it
- only when a task materially benefits from it

The intended heuristic is:
- fetch locally
- compress locally when possible
- summarize once
- meter everything

## Supported Product Modes
The current runtime should think in these modes:

### Local-first (recommended)
- local tools first
- local models second
- OpenAI only when explicitly invoked or when a later governed fallback policy allows it

### Explicit OpenAI only
- OpenAI should be used only when the user deliberately chooses that lane
- useful for coding sessions and hard project work

### Budgeted fallback
- still local-first
- allows OpenAI to act as a metered fallback for hard tasks
- only valid once budget and visibility controls are in place

## OpenAI Use Cases In Nova
### Coding mode
Use OpenAI for:
- patch planning
- refactor planning
- test-gap analysis
- hard integration debugging
- phase closeout summaries

Do not use OpenAI for:
- simple repo grep
- file listing
- basic deterministic edits
- routine status checks

### Project mode
Use OpenAI for:
- turning many docs into one plan
- reconciling competing design packets
- explaining tradeoffs
- tightening implementation sequences

### Market research mode
Use OpenAI for:
- research synthesis
- scenario comparison
- summarizing structured market data

Do not let OpenAI become:
- unchecked live trading authority
- hidden order-routing logic
- a silent risk engine

## Required Product Truth
Whenever OpenAI is used, Nova should be able to say:
- why it was used
- which model was used
- what route selected it
- how many tokens were used
- whether the token counts are estimated or exact
- what the current budget state is

## Current Runtime Baseline
This operating model is grounded to the current runtime seams:

- runtime settings:
  - `nova_backend/src/settings/runtime_settings_store.py`
- provider usage tracking:
  - `nova_backend/src/usage/provider_usage_store.py`
- Settings API:
  - `nova_backend/src/api/settings_api.py`
- diagnostics and Trust surfaces:
  - `nova_backend/src/executors/os_diagnostics_executor.py`
- OpenClaw setup visibility:
  - `nova_backend/src/api/openclaw_agent_api.py`

This means the repo now has a place to express:
- local-first routing preference
- OpenAI enable/pause state
- preferred OpenAI model
- metered token budget
- warning threshold
- recent provider usage visibility

## Non-Negotiable Invariants
OpenAI inside Nova must not violate:

1. Local-first remains the default.
2. OpenAI is optional, not assumed.
3. OpenAI use must be budgeted.
4. OpenAI use must be visible after every call.
5. OpenAI output never becomes execution authority by itself.
6. OpenAI must not silently widen OpenClaw authority.
7. OpenAI should not be used for deterministic fetch work.
8. If a cheaper local route is good enough, use it first.

## Recommended Near-Term Product Shape
Short term:
- keep OpenAI as a metered coding/reasoning lane
- keep OpenClaw narrow and governed
- keep Nova as the face

Medium term:
- let OpenAI help with hard project completion work
- let OpenAI support bounded action previews
- keep final execution behind Nova governance

Later:
- allow richer OpenAI-assisted operator workflows
- only after budget controls, review surfaces, and envelope controls are stronger

## What This Document Does Not Authorize
This document does not authorize:
- always-on OpenAI automation
- hidden background reasoning loops
- autonomous live trading
- silent cloud dependence
- replacing Nova's local-first identity with provider-first behavior
