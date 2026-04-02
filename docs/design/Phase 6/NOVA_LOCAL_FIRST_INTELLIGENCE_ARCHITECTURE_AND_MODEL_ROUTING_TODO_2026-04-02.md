# Nova Local-First Intelligence Architecture And Model Routing TODO

Date:
- 2026-04-02

Status:
- active design and implementation TODO

Scope:
- final intelligence structure
- local-first model strategy
- governed cloud fallback rules
- current hardware-grounded recommendation

Authority note:
- this is design and roadmap direction
- live runtime truth still belongs to `docs/current_runtime/`

## Why This Packet Exists

Nova should stop drifting between:
- local model language
- provider-routing language
- second-opinion language
- narrow OpenAI fallback language

The project needs one final intelligence structure.

The goal is not:
- "host every model locally"
- "push everything to APIs"
- "keep adding model paths without a final shape"

The goal is:
- one clear local-first Nova mind
- one governed review or fallback lane
- one execution law regardless of which model answered

## Grounded Current State

Current runtime truth already shows:
- Nova is local-first in spirit
- governed external reasoning is active
- a metered OpenAI fallback exists for a narrow OpenClaw task-report lane
- settings and docs still use mixed vocabulary for provider routing

Current local hardware reference for this machine:
- GPU: Intel Iris Xe Graphics
- RAM: about 8 GB physical memory

Current installed local models:
- `gemma2:2b`
- `phi3:mini`
- `gemma3:4b`
- `phi3.5:latest`

That means Nova should be designed for:
- efficient local-first reasoning
- realistic small-model daily use
- governed cloud escalation only when truly useful

It should not be designed around:
- large-model local fantasies this machine cannot carry comfortably
- cloud-first dependence

## Final Architecture Truth

Nova should use a three-layer intelligence structure.

### 1. Nova Core Mind

This is the everyday assistant mind.

Rules:
- local-first
- fast enough for ordinary use
- available by default
- cheapest and most private lane

Primary uses:
- everyday chat
- summaries
- memory guidance
- screen explanation
- continuity help
- planning
- daily assistant behavior

### 2. Nova Review Mind

This is the stronger reasoning lane.

Rules:
- external or cloud-backed when allowed
- explicit when possible
- bounded and visible
- advisory unless passed into governed execution paths

Primary uses:
- second opinions
- hard reasoning tasks
- quality fallback for difficult prompts
- heavier comparative analysis

### 3. Nova Action Law

This is not a separate model.

It is:
- Governor
- CapabilityRegistry
- ExecuteBoundary
- ledger
- bounded execution routes

Rule:
- intelligence may suggest
- only governed execution may act

This must stay true whether the answer came from:
- local model
- external provider
- narrow task-report fallback

## Core Product Rule

Nova should be:
- local-first for daily intelligence
- governed-cloud for higher-cost or higher-power review

Not:
- local-only ideology
- API-first dependence
- fragmented per-feature provider logic

## Smartest Move

The smartest move is not model expansion.

It is:
- unifying provider routing and model roles into one clear system

That creates:
- cleaner settings
- cleaner docs
- lower cost confusion
- better user trust
- easier future scaling

## Strongest Move

The strongest move is:
- make `local-first governed hybrid` the permanent Nova intelligence law

That gives Nova:
- strong product identity
- privacy advantage
- lower operating cost
- better home-assistant fit
- cloud power only when needed

This is stronger than:
- trying to self-host everything
- trying to be a cloud assistant with local branding

## Hardware-Grounded Model Recommendation

For this current machine, the strongest realistic local primary model is:
- `gemma3:4b`

Why:
- strongest installed local model that is still realistic for this device class
- better fit for a main local assistant than the smaller 2b-class options
- still within the practical ceiling of this hardware better than 8b+ ambitions

Recommended local stack on this device:
- primary local model: `gemma3:4b`
- fast fallback model: `phi3.5` or `phi3:mini`
- external heavy lane: governed cloud reasoning only when explicitly allowed

Do not design current Nova around:
- 8b+ as the default daily local model on this machine
- 70b-class local assumptions

## Final Routing Truth

Nova should expose one clean policy vocabulary.

Recommended routing modes:
- `local_only`
- `local_first`
- `explicit_external_only`

Recommended interpretation:
- `local_only`: Nova never uses external reasoning
- `local_first`: Nova uses local by default and only uses external reasoning through explicit second opinion or governed fallback rules
- `explicit_external_only`: external reasoning is allowed only when the user directly asks for it

Avoid keeping mixed language like:
- `MODEL_PROVIDER=auto`
- `routing_mode`
- "metered lane"
- provider terms that do not map cleanly to product behavior

## What Should Change In Code

### 1. Create one canonical provider router

Add or consolidate a single routing authority under:
- `nova_backend/src/providers/`

Likely new file:
- `provider_router.py`

This router should decide:
- when local is required
- when external is allowed
- whether the request is explicit review vs governed fallback
- whether budget permits external use
- what reason should be surfaced to the user and ledger

### 2. Stop scattering provider policy across settings and features

Current affected surfaces include:
- `nova_backend/src/api/settings_api.py`
- `nova_backend/src/providers/openai_responses_lane.py`
- `nova_backend/src/governor/governor.py`
- any runtime diagnostics or audit surfaces that surface provider state

Goal:
- one policy source of truth
- one explanation vocabulary

### 3. Make model roles explicit

Nova should clearly know:
- primary local model
- local fast fallback model
- external review provider
- narrow feature-specific fallback paths if any remain

This should be inspectable in:
- settings
- diagnostics
- runtime audit surfaces

### 4. Keep action law independent from model source

No matter which model answers:
- Governor rules do not soften
- capabilities do not widen
- execution authority does not grow

This needs to remain obvious in code and docs.

## What Should Change In Docs

### Runtime truth

Update:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`

Clarify:
- Nova is local-first by default
- external reasoning is bounded and visible
- APIs are a governed review or fallback lane, not the main brain

### Root orientation

Update:
- `README.md`
- `docs/README.md`

Add a short section for:
- local-first intelligence
- governed cloud fallback
- budgeted visibility

### Product and roadmap truth

Update:
- `docs/design/Phase 11/NOVA_HOME_ASSISTANT_PRODUCT_TRUTH_2026-04-02.md`
- `docs/design/Phase 6/NOVA_GROUNDED_CURRENT_STATUS_AND_NEXT_ROADMAP_2026-04-02.md`

Clarify:
- Nova should be hosted local-first where practical
- cloud is a bounded support lane
- connector usefulness comes before model sprawl

### Human guides

Update:
- `docs/reference/HUMAN_GUIDES/12_CODEBASE_TOUR.md`
- `docs/reference/HUMAN_GUIDES/14_FRONTEND_AND_UI_GUIDE.md`
- `docs/reference/HUMAN_GUIDES/16_TESTING_AND_VALIDATION.md`

Clarify:
- where provider routing lives
- how to test local-first and fallback behavior
- how settings map to actual runtime policy

## Final Build Order

### Stage 1 - Lock the architecture truth

Do:
- adopt `local-first governed hybrid` as the official Nova model strategy
- stop using mixed routing language across docs and code

### Stage 2 - Unify config and settings vocabulary

Do:
- replace transitional provider-policy wording with one stable routing vocabulary
- make the same wording appear in env/config, settings UI, diagnostics, and docs

### Stage 3 - Add the canonical provider router

Do:
- centralize all local vs external routing decisions
- return structured reasons for routing
- connect budget enforcement to the router

### Stage 4 - Promote the strongest realistic local model

Do:
- make `gemma3:4b` the default daily local primary on this machine class
- keep a smaller fast fallback available
- do not widen model size expectations beyond the hardware envelope

### Stage 5 - Clean up feature-specific routing drift

Do:
- review second opinion
- review OpenClaw task-report fallback
- review diagnostics/settings provider status
- remove per-surface one-off logic where a single router should decide

### Stage 6 - Update docs and user-facing explanations

Do:
- align runtime docs
- align README/docs entry points
- make settings explain local-first and cloud fallback in plain language

### Stage 7 - Only then expand connector usefulness

Do next after routing clarity:
- calendar
- Gmail
- tasks or notes

Rule:
- connector usefulness is a bigger product win than chasing model complexity prematurely

## What Should Not Be Done

Do not:
- try to host every model locally just because it sounds sovereign
- turn APIs into the main Nova brain
- keep multiple routing vocabularies alive
- design for model sizes this hardware cannot support as a daily default
- expand feature breadth before the intelligence structure is clear

## Short Version

The final Nova intelligence structure should be:

1. local-first daily mind
2. governed cloud review or fallback lane
3. one execution law regardless of model source

On this current machine, the best practical local primary is:
- `gemma3:4b`

The strongest overall move is:
- unify provider routing into one clean local-first hybrid architecture

