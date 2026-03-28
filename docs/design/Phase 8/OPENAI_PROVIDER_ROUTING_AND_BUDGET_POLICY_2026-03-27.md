# OpenAI Provider Routing and Budget Policy
Date: 2026-03-27
Status: Current policy baseline

## Purpose
This document defines how Nova should decide when OpenAI is allowed to be used, and how that use should be budgeted.

## Default Position
Nova is local-first.

That means:
- local tools first
- local models second
- OpenAI third

If a task can be completed well without a metered provider, Nova should not use one.

## Metered Provider Permission
The OpenAI lane should remain separately pausable through runtime settings.

Recommended runtime permission:
- `metered_openai_enabled`

Default:
- paused

Meaning:
- OpenAI can be configured without becoming active by default
- the user can keep credentials present while still keeping the metered lane paused

## Routing Modes
### `local_first`
Recommended default.

Behavior:
- deterministic local execution first
- local model lane next
- OpenAI only when explicitly invoked or when a later governed fallback policy allows it

### `explicit_openai`
Behavior:
- OpenAI should only run when the user explicitly chooses or requests that lane
- useful for coding sessions and hard project work

### `budgeted_fallback`
Behavior:
- local-first still applies
- OpenAI can be used as a metered fallback for hard tasks
- only valid when visibility and budget controls are working

## Recommended OpenAI Model Defaults
The metered default should bias toward lower cost first.

Recommended preference order:

1. `gpt-5-mini`
- default coding and planning lane
- lower token burn
- best first-choice metered model

2. `gpt-5.1-codex`
- code-focused alternative for coding-heavy work

3. `gpt-5.4`
- reserved for harder architecture/debugging passes
- better quality, higher expected cost

## Budget Policy
Recommended starting daily metered budget:
- `4,000` tokens/day

Recommended warning threshold:
- `80%`

Meaning:
- warn before exhaustion
- make low-budget state visible early
- avoid surprise overages

Suggested future presets:
- light: `4,000`
- normal: `12,000`
- heavy project push: `25,000`

## Budget Rules
1. Metered budget applies only to metered providers.
2. Local tool work does not count against metered budget.
3. Local model work does not count against metered budget.
4. If budget is exhausted, OpenAI should pause automatically unless a future explicit override exists.
5. Budget state should be shown in Trust, Settings, and provider usage surfaces.

## Routing Guidance By Task Type
### Always local-first
- weather
- calendar
- RSS/news fetch
- file scans
- test runs
- local repo structure reads
- governed memory overview/list

### Usually local-first, metered only when needed
- summarizing a long repo state
- reconciling many design documents
- difficult debugging
- implementation sequencing

### Metered lane can be justified
- hard coding agent work
- multi-file refactor planning
- architecture review
- research synthesis with many inputs

## Batch Rule
Non-urgent metered tasks should prefer batch/offline handling when a future implementation supports it.

Examples:
- nightly doc reconciliation
- large repo audit packets
- low-priority research summarization

## Guardrails
OpenAI routing should never:
- bypass Nova permissions
- bypass OpenClaw strict preflight
- bypass ledger and usage reporting
- become the default for trivial requests

## Current Runtime Mapping
The current runtime now has places for this policy:

- runtime settings store:
  - `nova_backend/src/settings/runtime_settings_store.py`
- settings API:
  - `nova_backend/src/api/settings_api.py`
- diagnostics / Trust:
  - `nova_backend/src/executors/os_diagnostics_executor.py`
- OpenClaw readiness surface:
  - `nova_backend/src/api/openclaw_agent_api.py`
- provider usage tracking:
  - `nova_backend/src/usage/provider_usage_store.py`

## Next Tightening Steps
1. add true per-provider cost estimation tables for supported OpenAI models
2. add request-class routing rules instead of global-only routing modes
3. add automatic pause on budget exhaustion
4. add provider-specific rate limiting for scheduled/agent work
