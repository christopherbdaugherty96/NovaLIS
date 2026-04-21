# Documentation and Phase System
Updated: 2026-04-20

## Purpose
This guide explains how Nova's documentation system is organized and how phases fit into the project.

## Why Nova Has So Many Document Types
Nova uses different document types because not all documentation is trying to do the same job.

Some docs explain.
Some prove.
Some define design intent.
Some record runtime truth.
Some record governance law.

## Main Documentation Layers

### Human guides
These explain the project in normal language.
They are for understanding, onboarding, and everyday orientation.

### Runtime truth docs
These describe what is live in the actual runtime.
They are the operational authority surface for current behavior.

### Active roadmap docs
These describe what is being worked on now, what is blocked, and what comes next.
They are the authority surface for active execution priority, not runtime architecture.

### Proof packets
These are evidence bundles showing what was implemented and verified.
They are especially important around phase closures and implementation slices.

### Design docs
These describe intended architecture, future plans, phase ideas, and proposed systems.
They are useful but not automatically proof that a feature is live.

### Canonical governance docs
These define the highest-level governance and constitutional ideas behind Nova.

### Historical status docs
These preserve what Nova looked like at an earlier checkpoint.
They can still be useful, but they are not the authority surface for current truth.

## Why Phases Matter
Phases are how Nova organizes large architectural steps over time.

Examples:
- Phase 4: governed execution foundation
- Phase 4.2: cognitive/reporting depth
- Phase 4.5: perception and UX refinement
- Phase 5: continuity, governed memory, tone controls, scheduling, and opt-in pattern review
- Phase 6: review-oriented delegated-policy, trust-loop, executor-gate, and capability-topology package before any broad trigger runtime

## What A Phase Means In Practice
A phase is not just a label.
It usually means:
- a new capability surface
- a new governance boundary or rule set
- new proof and verification work
- new runtime behavior

## Why Current Runtime Matters More Than Old Docs
Some older docs reflect earlier moments in the project.
That is normal in a system that evolves.

When you need to know what is true now, runtime truth wins.
When you need to know what is active now, the active roadmap wins.
That is why the current runtime docs, active roadmap docs, and proof packets matter so much.

For current execution priority, the important live surfaces are:
- `4-15-26 NEW ROADMAP/Now.md`
- `docs/capability_verification/STATUS.md`

For future or long-range work, the important planning surfaces are:
- `4-15-26 NEW ROADMAP/MasterRoadMap.md`
- `4-15-26 NEW ROADMAP/BackLog.md`
- `docs/future/`

For the current repository state, Phase 5 is a good example of this layering:
- the design docs define intent and boundaries
- the proof packet shows what was implemented and ratified
- the runtime docs explain what is live now

Phase 6 now shows a closed mixed pattern:
- the design docs define the lawful delegated-policy model, executor gate, topology, and trust-loop rules
- the proof packet records the validator/store foundation, policy review center, and completion handoff
- the runtime docs describe a complete review-oriented delegated-policy package, while still not claiming live delegated trigger runtime

Phase 6 also now has an endgame productization layer in design docs:
- desktop packaging
- update delivery
- API/service compliance
- early-launch legal and business readiness

Those are still planning/docs surfaces, not live runtime truth.

## The Best Reading Order For Most People
1. human guides
2. active roadmap docs
3. runtime truth docs
4. proof packets
5. design docs and future docs
6. canonical governance docs when deeper theory is needed

## Short Version
Nova's documentation system is layered on purpose.

The right question is not just:
- where is the doc?

It is also:
- what kind of doc is it?
- is it explanatory, active, live, historical, proof-oriented, or design-oriented?

That distinction keeps the project easier to understand.
