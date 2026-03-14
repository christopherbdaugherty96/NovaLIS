# Phase-6 Project-Wide Next Steps
Date: 2026-03-13
Status: Planning note only
Scope: Recommended next-step order for Nova as a whole after Phase-5 closure

## Purpose
This document records the smartest next implementation order for Nova as a whole.

It is not only a Phase-6 sequencing note.
It also accounts for:
- Phase-5 stability
- product trust
- installability
- operator legibility
- the difference between core delegated-autonomy work and adjacent convenience work

## Starting Point
Nova now has a closed Phase-5 trust-facing package.

That means the current runtime already includes:
- governed memory
- session-scoped thread continuity plus durable memory bridge
- memory inspectability
- manual tone controls
- explicit scheduling with policy controls
- opt-in pattern review

This creates a new project-wide question:

What should come next if the goal is not just more capability, but a stronger product and a safer platform?

## Recommended Order

### 1. Phase-5 Stability Freeze and UX Hardening
Purpose:
- treat the closed Phase-5 package as a stable product layer

Priority work:
- make `Nova what is this?` the strongest explain-anything interaction
- prefer cursor-first screen understanding, with section/page expansion only when needed
- tighten scheduling UI
- improve pattern-review explanations
- unify memory/thread/tone/schedule status into a calmer settings or health surface
- keep proofs, runtime docs, and human guides current

Why first:
- Nova already has a believable daily-use layer
- trust and polish now matter more than another burst of new surfaces
- the point-and-explain loop is the highest-value product hardening target inside the current explain stack

### 2. Governor Policy Validator
Purpose:
- start real Phase-6 implementation at the lawful authority boundary

Priority work:
- policy schema validator
- policy-capable allowlist checks
- envelope validation
- explicit block reasons
- disabled-by-default stored policy objects

Why second:
- no delegated-trigger runtime should exist until the Governor can validate one atomic policy action safely

### 3. One End-to-End Delegated Atomic-Policy Slice
Purpose:
- prove the delegated-policy model in one small real runtime slice

Priority work:
- one trigger class
- one allowed atomic action class
- one envelope model
- one audit trail
- one emergency-stop path

Recommended style:
- keep it time-based or similarly deterministic
- keep it read-only or very low risk
- avoid orchestration, chaining, or durable-state mutation

Why third:
- one truthful slice is more valuable than a wide but blurry autonomy system

### 4. Installability and Startup Hardening
Purpose:
- reduce the gap between Nova as an internal architecture and Nova as real software

Priority work:
- one-click or greatly simplified install path
- clearer missing-dependency diagnostics
- first-run environment validation
- startup readiness checks
- explicit status for model, network, microphone, and runtime locks
- packaging assumptions that could later support a local AI appliance or hub

Why fourth:
- install friction is now one of the biggest blockers to Nova feeling real outside the current workspace

### 5. Unified Operator Health Surface
Purpose:
- make Nova's moving parts legible to operators and reviewers

Priority work:
- phase/build visibility
- model readiness
- network readiness
- memory status
- tone status
- schedule policy status
- pattern-review opt-in status
- future wake-word status when that exists

Why fifth:
- Nova is now complex enough that health needs a first-class surface, not scattered hints

### 6. Wake Word as an Adjacent Convenience Layer
Purpose:
- improve everyday UX without confusing it with delegated autonomy

Priority work:
- Porcupine-based local wake gate
- short listening window
- non-authorizing design
- clean status visibility and kill switch

Why sixth:
- wake word helps delight and flow
- but it should not outrank the policy validator, installability, or operator health work

### 7. Local AI Appliance / Nova Hub Productization Direction
Purpose:
- keep the hardware/product direction coherent without letting it distort the core software roadmap

Priority work:
- define the simplest local-AI node story
- keep the message centered on local + governed AI
- package screen explanation, research, and computer help as the core value loop

Why seventh:
- the appliance direction becomes believable only after the software experience, installability, and health surfaces are strong enough

### 8. Broader Phase-6 Policy UI and Trigger Expansion
Purpose:
- expand delegated-policy usability after the lawful core is proven

Priority work:
- better policy authoring UX
- more trigger classes
- richer policy inspection surfaces
- stronger blocked/allowed explanations

Why eighth:
- expansion should happen after the first policy slice proves the model and after the product is easier to run

## Explicit Non-Priorities Right Now
The following are not the smartest immediate next moves for the whole project:
- second-orb exploration
- self-hosted search-index work
- reopening deferred identity/preferences by default
- broader adaptive tone evolution
- anything that behaves like hidden autonomy

These may matter later, but they should not outrank the core policy substrate, installability, or operator health work.

## Relationship to the Core Phase-6 Roadmap
The corrected Phase-6 roadmap still defines the constitutional implementation order:
1. Phase-5 boundary
2. atomic policy model
3. Governor policy validator
4. trigger-only monitoring
5. transparency and control
6. constitutional verification

This project-wide roadmap adds a product and platform lens on top of that order.

In practice, it means:
- Phase-6 core should begin with the Governor validator path
- while Nova as a whole should also invest in polish, installability, and health visibility
- and keep progressive screen intelligence as the signature product-surface track

## Best Single Summary
The smartest next move for Nova as a whole is:

build the Governor policy validator next, while freezing and hardening the Phase-5 product layer.

That combination improves both:
- Nova as a lawful platform
- Nova as a usable product

## Interpretation Rule
Use this document to guide project-wide prioritization.

Do not use it to claim that any new Phase-6 runtime behavior is already live.
