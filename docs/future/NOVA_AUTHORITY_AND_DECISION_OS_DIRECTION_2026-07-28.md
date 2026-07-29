# Nova Authority and Decision OS — Long-Term Direction

Status: long-term strategic compass; non-authorizing.

This document describes the direction in which evidence-earned Nova work should accumulate.
It does not select the next lane, change current ordering, activate a priority lock, expand a
capability, or claim that the described future exists in runtime.

Current ordering remains in `NOVA_MASTER_ROADMAP_2026-07-05.md`. Current runtime existence
remains defined by code and generated runtime truth. Lane scope remains defined by reviewed
priority locks. Owner approval remains the source of activation.

## North Star

> Nova is a local-first personal authority and decision operating system. It builds an
> evidence-backed understanding of what matters, prepares the next best action, routes work
> among approved intelligence providers, and permits execution only through explicit,
> inspectable, revocable authority — with proof of what actually changed.

Nova does not need to be the smartest model. Models and specialist agents may be replaceable
reasoning providers. Nova's durable role is to govern:

- what context may reach which provider;
- what is fact, reasoning, inference, proposal, decision, or permission;
- which capability may handle an exact action;
- when approval is authentic and still valid;
- what executed and what external effect occurred;
- whether the promised outcome was verified;
- what may be learned without silently expanding authority.

This is a local control-plane thesis for the models, agents, tools, and data sources the owner
chooses to place behind Nova. It is not a claim that external AI vendors will adopt Nova as a
universal industry standard.

## Five Layers, Ordered by Blast Radius

The order is part of the safety architecture. Later layers must not be used to bypass the
boundaries of earlier ones.

### 1. Awareness

Nova maintains an evidence-backed view of what changed, what matters, what is stale, and what
remains uncertain across the owner's day, household, projects, and businesses.

Every consequential item should preserve source, freshness, confidence, and epistemic class.
Awareness is information, not authority.

### 2. Decision Intelligence

Nova identifies:

- the decision actually pending;
- the highest-value uncertainty;
- missing or stale evidence;
- relevant alternatives and constraints;
- likely consequences;
- the safest useful next step.

The objective is not to answer the most prompts. It is to help the owner make the next better
decision.

Because useful decision intelligence may exceed available local inference hardware, this layer
includes governed hybrid-compute routing. "Local-first" means local authority, not a promise
that every inference runs locally. Any provider route must make visible:

- what context would leave the machine;
- which provider would receive it;
- why that provider is needed;
- what redaction or minimization was applied;
- whether the route is local-only, cloud-allowed, ask-first, or blocked.

Privacy-aware model routing is therefore a governed capability boundary, not a hidden
implementation detail.

### 3. Prepared Reality

Nova turns messy context into prepared-but-unexecuted next moves:

- drafts;
- checklists;
- meeting and decision packets;
- proposed schedule changes;
- business recommendations;
- content packages;
- forms;
- recovery options;
- bounded workflow previews.

> Nova already did the thinking and preparation, but it waits exactly where the owner's
> authority matters.

Prepared Reality is both the defining experience and the commercial bridge for governed AI.
Governance creates friction if the user must repeatedly do the preparation themselves. Nova
should complete the safe 95 percent so the authority-bearing 5 percent can be reviewed in one
informed glance.

Preparation remains non-executing. A prepared action is not approval.

### 4. Governed Execution

Every effectful action requires a declared capability and a verified authority path. The target
model is:

- exact-action-bound approval;
- session and actor binding;
- expiry;
- single use;
- replay refusal;
- parameter-change invalidation;
- bounded execution;
- truthful timeout and unknown-outcome handling;
- independent effect and receipt outcomes;
- visible proof of what changed.

No materially stronger external-action surface should be stacked on a caller-supplied
confirmation Boolean. The authorization-integrity lane remains the prerequisite hardening
direction for future effectful expansion; this document does not activate it.

Authority is earned per action class, never inferred from Nova appearing generally intelligent.

### 5. Outcome Learning

Nova may retain an inspectable decision chain:

```text
situation
-> evidence
-> alternatives
-> recommendation
-> owner decision
-> approved action
-> verified effect
-> observed outcome
-> lesson
```

Hard invariant:

> Learning may change what Nova proposes and how confidently it proposes it. Learning may
> never change what requires approval, how approval is obtained, which permissions exist, or
> which authority boundary applies.

Repeated past approval is not present permission. Memory is context, not authority. No learning
system may promote itself, unlock a capability, lower a risk class, or silently widen execution.

## Intended Product Loop

```text
notice
-> establish current truth
-> identify the important uncertainty
-> recommend
-> simulate where useful
-> prepare
-> obtain exact-action approval
-> execute through a bounded capability
-> verify the effect
-> issue a receipt
-> learn from the outcome without expanding authority
```

The mature experience should feel Jarvis-like at the interface while remaining governed and
inspectable underneath.

## Evidence-Backed World and Decision Model

Long-term context should distinguish:

- observations;
- sourced facts;
- reported forecasts;
- deterministic reasoning;
- model inference;
- preferences;
- commitments;
- owner decisions;
- permissions;
- execution receipts;
- outcomes.

Each important item should be inspectable for source, time, confidence, contradiction, and
authority tier. Nova should eventually be able to answer:

> What does the owner currently believe, what evidence supports it, what remains unresolved,
> what decision is pending, and what is Nova permitted to do about it?

This should be built as thin evidence-earned vertical slices, not as an attempt to model the
owner's entire life in one internal phase.

## Realistic Control-Plane and Commercial Scope

Nova may become the authority plane for owner-selected:

- local and approved cloud models;
- specialist reasoning agents;
- OpenClaw and other bounded execution environments;
- household integrations;
- creator and small-business workflows;
- MCP-style tools and data sources;
- local-machine capabilities.

A portable governance SDK or protocol is a possible later extraction only after Nova proves
the model inside its own product. It is not an assumption about third-party vendor adoption and
is not an opening product strategy.

The most credible commercial progression is:

```text
personal Nova
-> household coordination
-> creator and small-business operations
-> governed multi-user delegation
-> reusable governance infrastructure
```

The household and small-business wedge becomes valuable when multiple people, agents, or
workflows can act and the questions "who approved what?" and "what actually changed?" carry
real consequences.

## Feature Warrant — Required Before a Future Lane Opens

The evidence rule must be an artifact, not a remembered intention. Before a future product or
capability lane opens, its reviewed scope should include a compact feature warrant answering:

1. What observed problem earned this lane?
2. What uncertainty does it eliminate?
3. Does it improve awareness, decision, preparation, authority, or proof?
4. What is the smallest useful vertical slice?
5. Does it introduce or enlarge an external effect?
6. Is the authorization primitive strong enough for that effect?
7. What evidence will prove the change helped?
8. Which repeated app-open, failure, or user burden should decline?
9. Is this improving Nova, or merely increasing its conceptual completeness?

The warrant must cite the observation, defect, proof, or owner decision that earned the lane.
It does not itself authorize implementation: normal ordering, scope-lock, owner-activation, and
review rules still apply.

This requirement should reuse Nova's existing priority-lock/review machinery if implemented.
It must not become a new sprawling governance-document layer.

## Strategic Non-Goals

Nova should not become:

- a larger generic chatbot;
- an unrestricted computer-use agent;
- a hidden autonomous agent swarm;
- a connector collection without a decision thesis;
- a personality wrapper around third-party automation;
- a system that infers permission from repeated behavior;
- a universal protocol dependent on vendor adoption;
- an attempt to build every underlying model and tool;
- a conceptual cathedral built ahead of observed usefulness.

## Relationship to the Existing Roadmap

This direction synthesizes existing roadmap concepts rather than authorizing a new lane:

- H13 world model / Second Brain;
- H20 sensitive-data and provider routing;
- H23 Prepared Reality;
- H25 temporal recall;
- H28 deterministic what-if simulation;
- H31 governed tool boundary;
- the authorization-integrity priority lock;
- the existing awareness -> decision -> approved action -> observation -> learning loop.

The roadmap remains evidence-driven:

```text
The morning determines the next stone.
The authority-and-decision OS thesis determines the direction in which the stones accumulate.
The feature warrant prevents laying stones no observed need earned.
```

## Present Boundary

This document changes no current action:

- one post-#312 real-use/product-acceptance morning remains the next product input;
- the owner then selects the next evidence-ranked product lane;
- authorization integrity remains independently activatable in parallel priority;
- continuity consolidation and document-lifecycle work remain separate owner decisions;
- no new capability, connector, external write, scheduler, OpenClaw expansion, autonomous
  execution, learning authority, or cloud-data route is authorized here.
