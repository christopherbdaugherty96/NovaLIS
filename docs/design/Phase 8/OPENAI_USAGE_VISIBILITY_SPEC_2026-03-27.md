# OpenAI Usage Visibility Spec
Date: 2026-03-27
Status: Current visibility baseline

## Purpose
If Nova uses a metered provider, the user should know:
- that it happened
- why it happened
- how much it used
- what the budget state is

Usage visibility is not polish.
For Nova, it is part of the trust model.

## Required Event Fields
For each metered provider event, Nova should store:
- timestamp
- provider
- route
- analysis profile
- model label
- request id
- estimated input tokens
- estimated output tokens
- estimated total tokens
- exact input tokens when available
- exact output tokens when available
- exact total tokens when available
- usage measurement type (`estimated` or `exact`)
- estimated cost when available

## Daily Aggregate Fields
Nova should also keep a daily snapshot with:
- event count
- estimated input/output/total tokens
- exact input/output/total tokens when available
- estimated cost total when available
- budget tokens
- warning threshold tokens
- remaining budget tokens
- budget state
- budget state label
- last event timestamp

## User-Facing Wording
Preferred wording:
- `No paid provider used`
- `Used OpenAI reasoning`
- `Estimated cost this turn: $0.02`
- `Budget low`
- `Budget reached`
- `OpenAI paused by budget limit`

Avoid:
- vague technical labels with no meaning
- hidden token counts
- silent cost accumulation

## Current Measurement Truth
The current runtime should be honest about measurement quality:

### Estimated
Used when:
- exact provider usage is not returned
- Nova has to infer usage from prompt/response size

### Exact
Used when:
- provider returns actual token counts

### Cost
If true billing is not available yet:
- say cost is estimated
- do not imply invoice-accurate billing

## Surface Requirements
### Settings
Show:
- routing mode
- whether metered OpenAI is enabled or paused
- preferred model
- daily metered budget
- warning threshold
- current budget state

### Trust Center
Show:
- usage summary
- token totals today
- budget state
- cost visibility quality
- last metered use

### OpenClaw / Agent Page
Show:
- whether OpenAI is configured as an optional lane
- whether it is enabled
- whether the current home-agent setup can use it

## Current Runtime Mapping
This visibility spec is currently mapped to:
- `nova_backend/src/usage/provider_usage_store.py`
- `nova_backend/src/executors/os_diagnostics_executor.py`
- `nova_backend/src/api/settings_api.py`
- `nova_backend/src/api/openclaw_agent_api.py`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/index.html`

## Current Honest Limits
The current runtime still has limits:
- billing is not invoice-accurate
- exact token reporting depends on provider support
- not every metered route is live yet
- OpenAI remains an optional lane, not the default runtime

## Design Rules
1. Visibility must survive a page refresh.
2. Visibility must not depend on the user knowing a hidden command.
3. Visibility must remain understandable to a non-technical user.
4. Visibility should distinguish local work from paid provider work.
5. Visibility should say when no paid provider was used.

## Future Enhancements
1. per-turn usage cards in chat
2. per-provider history filtering
3. invoice-style daily/weekly summaries
4. budget limit enforcement events in the ledger
5. provider-specific model cost tables
