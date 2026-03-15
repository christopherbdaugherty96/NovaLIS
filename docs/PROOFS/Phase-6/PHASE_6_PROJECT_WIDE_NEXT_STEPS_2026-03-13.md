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

The strongest product threshold for Nova is when three surfaces exist together:
- Operator Health Surface
- Daily Utility Surface
- Trust / Review Surface

## Starting Point
Nova now has a closed Phase-5 trust-facing package.

That means the current runtime already includes:
- governed memory
- session-scoped thread continuity plus durable memory bridge
- memory inspectability
- manual tone controls
- explicit scheduling with policy controls
- opt-in pattern review
- policy executor-gate review foundations with simulation and one-shot manual runs

The earlier Phase-6 foundation steps are no longer just planned:
- policy validator: implemented
- draft policy store: implemented
- policy executor gate: implemented
- capability topology: implemented

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

This stage should also begin shaping the Daily Utility Surface:
- morning brief
- explain this
- research this
- summarize this document
- continue my project

### 2. Delegated-Policy Visibility and Review Surface
Purpose:
- make the new executor-gate path visible, understandable, and usable in everyday Nova workflows

Priority work:
- delegated policies panel
- simulation/result rendering in dashboard trust surfaces
- visible blocked-policy reasons
- manual review-run controls
- policy readiness indicators and summaries

Why second:
- executor-gate and topology foundations now exist, so the next high-value move is turning them into an inspectable user-facing control plane before any trigger runtime expands

### 3. One End-to-End Delegated Atomic-Policy Slice
Purpose:
- prove the delegated-policy model in one small real runtime slice

Priority work:
- one trigger class
- one allowed atomic action class
- one envelope model
- one audit trail
- one emergency-stop path

Why third:
- keep it time-based or similarly deterministic
- keep it read-only or very low risk
- avoid orchestration, chaining, or durable-state mutation

Why third:
- one truthful slice is more valuable than a wide but blurry autonomy system

### 4. Unified Operator Health Surface
Purpose:
- make Nova's moving parts legible to operators and reviewers

Priority work:
- phase/build visibility
- Governor status
- capability count or governed-surface summary
- policy draft / policy status visibility
- model readiness
- network mediator readiness
- ledger status
- future microphone / wake status when relevant

Why fourth:
- Nova is now complex enough that trust improves when health is visible in one place instead of scattered across surfaces

This is the first of the three key product surfaces:
- Operator Health Surface

### 5. Installability and Startup Hardening
Purpose:
- reduce the gap between Nova as an internal architecture and Nova as real software

Priority work:
- one-click or greatly simplified install path
- clearer missing-dependency diagnostics
- first-run environment validation
- startup readiness checks
- explicit status for model, network, microphone, and runtime locks
- packaging assumptions that could later support a local AI appliance or hub

Why fifth:
- install friction is now one of the biggest blockers to Nova feeling real outside the current workspace

### 6. Desktop Packaging and Distribution
Purpose:
- turn Nova from a local runtime into installable software

Priority work:
- desktop shell or executable packaging path
- installer assets
- GitHub Releases distribution path
- download-website readiness

Why sixth:
- once installability is strong enough, packaging becomes the bridge from internal system to real product

### 7. Update Delivery and External-Service Readiness
Purpose:
- make Nova maintainable and launchable as software used by other people

Priority work:
- simple update path
- stable config and key handling
- API attribution and service-compliance review
- model-license review

Why seventh:
- installation without maintainable updates and external-service readiness will not hold up under real users

### 8. Early-Launch Legal and Business Readiness
Purpose:
- prepare the minimum non-runtime packet needed for an honest alpha or beta launch

Priority work:
- terms
- privacy
- third-party licenses
- software-license position
- security contact
- company-formation trigger rules

Why eighth:
- this is where Nova stops being only a project and becomes something that can be distributed responsibly

### 9. Wake Word as an Adjacent Convenience Layer
Purpose:
- improve everyday UX without confusing it with delegated autonomy

Priority work:
- Porcupine-based local wake gate
- short listening window
- non-authorizing design
- clean status visibility and kill switch

Why ninth:
- wake word helps delight and flow
- but it should not outrank the executor gate, topology, installability, or operator health work

### 10. Local AI Appliance / Nova Hub Productization Direction
Purpose:
- keep the hardware/product direction coherent without letting it distort the core software roadmap

Priority work:
- define the simplest local-AI node story
- keep the message centered on local + governed AI
- package screen explanation, research, and computer help as the core value loop

Why tenth:
- the appliance direction becomes believable only after the software experience, installability, and health surfaces are strong enough

### 11. Broader Phase-6 Policy UI and Trigger Expansion
Purpose:
- expand delegated-policy usability after the lawful core is proven

Priority work:
- better policy authoring UX
- more trigger classes
- richer policy inspection surfaces
- stronger blocked/allowed explanations

Why eleventh:
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
4. policy executor gate
5. capability topology
6. trigger-only monitoring
7. transparency and control
8. constitutional verification

This project-wide roadmap adds a product and platform lens on top of that order.

In practice, it means:
- Phase-6 core should continue with policy visibility and one truthful trigger slice before broad trigger expansion
- while Nova as a whole should also invest in polish, installability, and health visibility
- and keep progressive screen intelligence as the signature product-surface track

The three product surfaces are documented here:
- `docs/design/Phase 6/PHASE_6_PRODUCT_SURFACES_SPEC.md`

## Best Single Summary
The smartest next move for Nova as a whole is:

turn the new delegated-policy review path into a visible, trustworthy surface while freezing and hardening the Phase-5 product layer.

That combination improves both:
- Nova as a lawful platform
- Nova as a usable product

## Interpretation Rule
Use this document to guide project-wide prioritization.

Do not use it to claim that any new Phase-6 runtime behavior is already live.
