# Nova Gemma 4 Local Brain Strategy

Date:
- 2026-04-02

Status:
- active design guidance

Scope:
- Gemma 4 grounding
- local-brain role in Nova
- hybrid routing posture
- current hardware reality check
- routing and UX implications
- rollout guidance

Authority note:
- this is design guidance, not runtime truth
- live runtime status still belongs to `docs/current_runtime/`

## Why This Packet Exists

Gemma matters to Nova, but it should not be treated as:
- Nova's whole identity
- a replacement for governance
- proof that Nova should become "all local everything"

The right question is:

`How should Gemma 4 fit into Nova's local-first governed intelligence architecture?`

## Grounded Facts

As of 2026-04-02:
- Google officially ships a `Gemma 4` family
- Google positions it as the latest Gemma generation
- official variants include:
  - `E2B`
  - `E4B`
  - `A4B`
  - `31B`
- Google's official Gemma materials describe Gemma 4 as Apache 2.0 licensed

Source references for future verification:
- `https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/`
- `https://ai.google.dev/gemma/docs/releases`
- `https://ai.google.dev/gemma/docs/get_started`

Important grounding note:
- "Gemma matters" does not mean "Gemma alone solves Nova"
- a stronger local model does not replace governance, connector breadth, or operator design
- model strategy should stay subordinate to Nova's constitutional structure

## What Gemma Should Mean For Nova

Gemma should be treated as:

`a candidate local brain layer for Nova`

Not:
- Nova's execution layer
- Nova's trust model
- Nova's autonomy system
- Nova's whole routing policy

Nova's enduring structure remains:
- `Nova = presence + governance + orchestration`
- `local model = daily intelligence lane`
- `external model = bounded deep-reasoning lane`
- `nodes and tools = execution surfaces`

## Why Gemma 4 Matters Specifically

Gemma 4 matters because it strengthens the local-first side of Nova's identity.

That gives Nova a better path toward:
- private daily assistance
- lower marginal cost
- less dependence on cloud availability
- faster routine interaction
- a more believable "home assistant" feel

It is especially relevant for Nova because Nova is not trying to become:
- a cloud-first chatbot
- an API reseller shell
- a generic wrapper around someone else's hosted brain

Nova is trying to become:

`a governed personal intelligence system that can live locally first and widen outward only when justified`

## Best Architectural Role

Gemma 4 belongs in Nova's `Core Mind` lane.

That means Gemma should help with:
- everyday conversation
- summaries
- drafts
- screen explanation
- form-help reasoning
- lightweight planning
- general local assistance
- read-only project analysis and coding-plan drafts for Nova's future local code-operator lane

It should not be treated as the same thing as:
- the Governor
- OpenClaw
- browser automation
- connector execution
- policy enforcement

## Role Separation

The clearest Nova model is:

### Gemma 4

Purpose:
- local cognition
- fast drafting
- default conversation
- everyday assistant reasoning

### External reasoning providers

Purpose:
- deeper review
- harder synthesis
- heavier analysis
- bounded second-opinion support

### Governor

Purpose:
- permission law
- risk classification
- policy boundary
- execution authorization

### Execution nodes

Purpose:
- perform actions in the world
- browser control
- OS control
- external APIs
- OpenClaw task execution

This separation is critical because it prevents a common mistake:

`confusing better reasoning with safe execution`

## Strongest Nova Move

The smartest move is not:
- "replace everything with Gemma"
- "use APIs for everything"
- "keep adding providers without one settled model policy"

The strongest move is:

`local-first governed hybrid`

That means:
1. local model for everyday work
2. governed cloud lane for harder reasoning
3. one execution law regardless of which model answered

## Best User-Facing Framing

Nova should not explain this to users as:
- "choose your LLM backend"
- "pick your provider strategy"
- "switch between model tiers"

The user-friendly framing should be:
- `Local by default`
- `Stronger review when needed`
- `You stay in control`

That keeps the product understandable for non-technical users while preserving the real architecture underneath.

## Decision Policy

Gemma 4 should be preferred when the task is:
- private
- everyday
- short to medium length
- latency-sensitive
- inexpensive to keep local
- low-risk if the answer is imperfect

External reasoning should be preferred when the task is:
- unusually complex
- high context length
- multi-source and research-heavy
- high-stakes enough to justify stronger review
- explicitly requested by the user

Execution should never be chosen based only on the model.

Execution should always depend on:
- capability approval
- task envelope
- risk tier
- budget
- interruptibility

## Workload Examples

### Good Gemma-first tasks

- "Summarize this page"
- "Help me draft this email"
- "Explain what I'm looking at"
- "Turn my notes into a cleaner outline"
- "Help me fill this form"
- "Give me the next three steps"
- "Summarize this repo"
- "Review this project and suggest the safest next cleanup"

### Good external-review tasks

- "Compare three approaches and argue the tradeoffs"
- "Do a deeper research-backed analysis"
- "Sanity-check this important reasoning"
- "Review this architecture for failure modes"

### Tasks where the model choice is secondary to governance

- "Sign into this site for me"
- "Send this email"
- "Buy this domain"
- "Place this trade"
- "Run this workflow end to end"

For these, the real boundary is not "which model thought about it."
The real boundary is "what is Nova allowed to execute."

## OpenClaw Relationship

Gemma and OpenClaw solve different problems.

Gemma:
- local reasoning
- drafting
- screen interpretation
- fast assistant cognition

OpenClaw:
- bounded execution node
- worker/task runtime
- governed action surface under Nova

So the clean relationship is:

`Gemma thinks locally`

`OpenClaw executes under Nova's law`

And more fully:

- Gemma helps Nova interpret and prepare
- OpenClaw helps Nova perform bounded task work
- the Governor decides whether performance is allowed at all
- the ledger records what happened

## Token and Cost Grounding

Using Gemma locally is not automatically "better" in every way, but it is often better for:
- privacy
- predictable marginal cost
- low-latency everyday use
- offline or weak-network operation

Using external providers is still useful for:
- deeper reasoning
- harder synthesis
- longer chains
- more demanding research or review tasks

So the real Nova advantage is not:

`local only`

It is:

`local + external + governed execution`

## Cost Strategy

The right cost strategy for Nova is:

1. keep everyday usage local where quality is sufficient
2. reserve cloud cost for moments where it clearly buys better outcomes
3. make that external usage visible, bounded, and explainable

That makes Nova economically stronger in the long run than either:
- pure API dependence
- unrealistic local-only ideology

## Hardware Reality Check For This Machine

Current machine guidance already documented elsewhere in the repo suggests:
- integrated GPU
- limited RAM headroom
- realistic small-model expectations

That means Nova should not be designed around:
- large local frontier-model assumptions
- heavy always-on large-model orchestration on this machine

The practical rule is:

`choose the strongest local model that remains smooth enough for daily use`

## Hardware Tiers

Gemma planning should be hardware-aware.

### Lower-end local machines

Characteristics:
- integrated GPU
- limited RAM
- lower thermal headroom

Best posture:
- smaller local model
- fast response over maximal capability
- external escalation when needed

### Mid-range local machines

Characteristics:
- more RAM
- stronger consumer GPU
- better multitasking headroom

Best posture:
- more capable local default
- broader local usage before escalation
- better multimodal responsiveness

### Higher-end local systems

Characteristics:
- large RAM
- dedicated GPU
- stronger sustained inference

Best posture:
- stronger local-first default
- less frequent need to escalate
- more room for richer local screen and workflow reasoning

The important architectural rule is:

`Nova's structure should scale across hardware tiers without changing its constitutional boundaries`

## Recommended Nova Posture

For this machine and current Nova state:

1. Keep a lightweight local daily assistant lane.
2. Evaluate small Gemma-family variants only if they stay responsive.
3. Keep governed external reasoning for harder tasks.
4. Keep execution governance completely model-agnostic.

This preserves:
- local-first identity
- cost discipline
- user trust
- future flexibility

## Best Current Recommendation For This Repo

For the current Nova codebase and this machine class:

1. keep the local-first architecture truth
2. keep the provider router/governed fallback cleanup as the real next code step
3. evaluate Gemma-family local candidates only within that unified routing model
4. do not let model excitement distract from connector and execution gaps

That means the strongest move is still:
- unify routing
- finish Phase 4.5 and Phase 8 practical usefulness
- then strengthen the local brain inside that architecture

## Rollout Order

The clean implementation order is:

### 1. Routing truth first

- one routing vocabulary
- one provider router
- one explanation surface for why local or external was used

### 2. Local-brain evaluation second

- benchmark Gemma candidate variants on real Nova tasks
- compare speed, quality, and stability against the current local defaults
- prefer consistency over benchmark vanity

### 3. UX explanation third

- make "local by default" visible in Settings and Trust surfaces
- make "stronger review used" understandable when escalation happens
- avoid raw model jargon as the primary UX

### 4. Ongoing refinement later

- tune prompts and routing thresholds
- re-evaluate local candidates as hardware or runtime improves
- keep external usage bounded by policy and budget

## Evaluation Criteria

Gemma should be judged by Nova-relevant criteria, not generic hype.

Evaluate:
- responsiveness
- summary quality
- instruction-following reliability
- screen-explanation usefulness
- draft quality
- stability over repeated daily use
- acceptable resource usage on target hardware

Do not evaluate only by:
- parameter count
- leaderboard excitement
- marketing claims

## Failure Modes To Avoid

Common traps:
- choosing a model that feels impressive but is too slow for daily use
- overfitting the architecture to one model family
- confusing "works locally" with "works well for Nova"
- exposing too much provider/model jargon in the product surface
- letting model-routing complexity leak into user trust

## Product Truth

The user should feel:
- Nova is here
- Nova is fast enough
- Nova is private by default
- Nova becomes stronger when needed
- Nova stays governed either way

That is a better user truth than:
- which parameter size ran
- which provider won the routing contest
- whether Gemma or something else answered

## What Not To Do

Do not turn Gemma into:
- a marketing shortcut
- a replacement for Nova's architecture
- an excuse to skip provider-routing cleanup
- proof that Nova is now "Jarvis" by model choice alone

Nova becomes powerful through:
- orchestration
- visibility
- bounded execution
- trust-preserving capability growth

Not through any one model name.

## Practical Interpretation

The best grounded sentence is:

`Gemma 4 should be part of Nova's local brain layer, not Nova's whole identity.`

An even stronger Nova-specific version is:

`Gemma 4 can strengthen Nova's local mind, but Nova's real power still comes from governed orchestration, visible execution, and trust-preserving control.`

## Recommended Reading Pair

Read this alongside:
- `docs/design/Phase 6/NOVA_LOCAL_FIRST_INTELLIGENCE_ARCHITECTURE_AND_MODEL_ROUTING_TODO_2026-04-02.md`
- `docs/design/Phase 9/NOVA_GOVERNED_MASS_NODE_OPERATOR_SYSTEM_2026-04-02.md`

Use this packet to keep model strategy grounded while Nova expands its governed node and operator surfaces.
