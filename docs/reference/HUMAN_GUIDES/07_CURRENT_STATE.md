# Current State
Updated: 2026-03-14

## Where Nova Is Today
Nova is no longer just a design project.
It has a real working runtime.

At a high level, the current state is:
- Phase 4 governance spine is active
- Phase 4.2 cognitive/reporting layer is active
- Phase 4.5 perception and UX surfaces are active
- Phase 5 trust-facing runtime package is active and formally closed for the current repository state

That means Nova already has:
- governed execution
- bounded local actions
- research and reporting
- screen explanation
- session-scoped thread continuity
- governed memory
- governed memory overview and inspectability surface
- manual response-style controls with inspectable tone settings
- user-directed scheduling for daily briefs and reminders, with quiet-hours and rate-limit controls
- opt-in pattern review for continuity work
- Operator Health Surface with a System Reason panel
- a live "What Nova Can Do Right Now" panel driven from the currently enabled capability surface
- a Home-page Trust Panel that now shows recent ledger-backed activity and current blocked conditions
- a cleaner dashboard header with dropdown workspace and control menus
- a simplified Home page with fewer, higher-value cards
- a dedicated Memory page for governed-memory review
- a stronger News page with source-grounded briefing, topic search, and article-summary actions
- broader political channels including left, center, and right views
- improved deep-analysis routing and orthogonal-review presentation
- dashboard support for all of the above

## What Feels Mature Already
These parts are already meaningfully real:
- governed search and reporting
- story summaries and intelligence briefs
- system status and local computer help
- Home-page operator health and reason visibility
- Home-page live capability discovery based on the active governed capability set
- Home-page trust review backed by recent ledger activity
- Home-page launch and personal-layer summary surfaces
- screenshot capture and screen explanation
- session-scoped project thread continuity
- thread health, blocker, and decision surfaces
- governed memory and thread-linked memory
- durable memory review through `memory overview` and the dedicated Memory page
- manual tone settings through the response-style surface
- explicit scheduled updates through the Home-page schedule surface
- explicit pattern review through the Home-page pattern queue
- source-grounded news brief and per-article summary flows

## What Is Still Maturing
These parts are active but still evolving:
- richer browser context
- more polished explain-anything flows
- more premium dashboard interactions
- stronger everyday workflows around thread and memory use
- clearer natural-language guidance around the live capability panel and command phrasing
- broader tone-calibration evolution beyond the current manual, inspectable controls
- richer scheduling polish and longer-range daily workflow surfaces beyond the current explicit policy controls
- deeper pattern heuristics and better proposal explanations

## What Is Planned But Not Fully Live Yet
Some highly important ideas are still planned or partially scaffolded rather than fully live.
The clearest example right now is wake word.

Wake word is part of Nova's design direction, but it is not yet the right way to describe today's runtime.

A careful plain-language description of the current system is:
- voice input exists
- voice output exists
- wake word is planned

The next planned wake-word step is documented here:
- `docs/PROOFS/Phase-6/PHASE_6_PORCUPINE_WAKE_WORD_RUNTIME_PLAN.md`

Phase-6 planning has started at the design level, and the first foundation code now exists too.

The first core Phase-6 design artifact now exists here:
- `docs/design/Phase 6/ATOMIC_POLICY_LANGUAGE_AND_POLICY_ENVELOPE_SPEC.md`

That document defines the smallest lawful delegated-policy model:
- one trigger
- one atomic action
- one bounded envelope

The first implemented runtime foundation slice is documented here:
- `docs/PROOFS/Phase-6/PHASE_6_POLICY_VALIDATOR_FOUNDATION_RUNTIME_SLICE_2026-03-13.md`
- `docs/PROOFS/Phase-6/PHASE_6_POLICY_EXECUTOR_GATE_RUNTIME_SLICE_2026-03-13.md`

What exists now:
- Governor-side policy validation
- disabled-by-default policy drafts
- capability topology metadata for delegated-policy review
- explicit policy inspection, simulation, and one-shot review-run commands
- Governor-routed manual delegated review for safe low-authority policies

What does not exist yet:
- trigger monitoring
- delegated trigger execution
- background autonomous action

The broader project-wide next-step order is documented here:
- `docs/PROOFS/Phase-6/PHASE_6_PROJECT_WIDE_NEXT_STEPS_2026-03-13.md`

That roadmap keeps the smartest order clear:
- harden the Phase-5 product layer
- deepen delegated-policy visibility and simulation surfaces
- improve installability and operator trust surfaces
- widen trigger runtime only after the manual review path is proven
- improve operator health and installability before widening the system further

The next two core Phase-6 architecture specs now exist here:
- `docs/design/Phase 6/PHASE_6_POLICY_EXECUTOR_GATE_SPEC.md`
- `docs/design/Phase 6/PHASE_6_CAPABILITY_TOPOLOGY_SYSTEM_SPEC.md`

The first trust-facing delegated-policy review surface is now documented here:
- `docs/design/Phase 6/PHASE_6_POLICY_SIMULATION_SURFACE_SPEC.md`

The first product-facing Phase-6-era visibility slice is now documented here:
- `docs/PROOFS/Phase-6/PHASE_6_OPERATOR_HEALTH_SURFACE_RUNTIME_SLICE_2026-03-13.md`

The signature product-direction screen-help spec is documented here:
- `docs/design/Phase 6/PHASE_6_PROGRESSIVE_SCREEN_INTELLIGENCE_PRODUCT_SPEC.md`

The longer-range local appliance / Nova Hub direction is documented here:
- `docs/design/Phase 6/PHASE_6_LOCAL_AI_APPLIANCE_AND_PRODUCT_DIRECTION.md`

The end-of-Phase-6 productization and launch-readiness planning set is now documented here:
- `docs/design/Phase 6/PHASE_6_ENDGAME_PRODUCTIZATION_ROADMAP.md`
- `docs/design/Phase 6/PHASE_6_DESKTOP_APP_PACKAGING_AND_DISTRIBUTION_SPEC.md`
- `docs/design/Phase 6/PHASE_6_UPDATE_AND_COMPONENT_DELIVERY_SPEC.md`
- `docs/design/Phase 6/PHASE_6_API_CONFIGURATION_AND_EXTERNAL_SERVICE_COMPLIANCE_SPEC.md`
- `docs/design/Phase 6/PHASE_6_EARLY_LAUNCH_LEGAL_AND_BUSINESS_READINESS.md`

The three product surfaces that would make Nova feel much more like a real daily-use system are documented here:
- `docs/design/Phase 6/PHASE_6_PRODUCT_SURFACES_SPEC.md`

What those endgame docs do not mean:
- Nova is not already shipping as a desktop app
- Nova does not already have a live auto-update system
- Nova is not already legally/commercially launched

They mean:
- the productization path is now documented clearly enough to follow once the Phase-6 platform is ready

## What Makes The Current State Special
Nova already combines things that usually live in separate products:
- governed local action
- research and multi-source reporting
- screen explanation
- session-scoped thread continuity plus durable governed memory
- explicit memory
- calm user-directed scheduling
- opt-in pattern review

That combination is unusual.

## The Best Honest Description Right Now
If someone asked what Nova is today, a strong honest answer would be:

Nova is a governed personal intelligence workspace that can research, explain, help with your computer, follow ongoing project threads in the current session, preserve explicit memory across sessions, schedule calm user-directed updates, and surface opt-in review patterns without giving up user control.

## If You Need The Official Runtime Truth
Use:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
