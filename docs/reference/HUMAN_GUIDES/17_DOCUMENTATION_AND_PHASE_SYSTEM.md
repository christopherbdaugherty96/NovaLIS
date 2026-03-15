# Documentation and Phase System
Updated: 2026-03-13

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

### Proof packets
These are evidence bundles showing what was implemented and verified.
They are especially important around phase closures and implementation slices.

### Design docs
These describe intended architecture, future plans, phase ideas, and proposed systems.
They are useful but not automatically proof that a feature is live.

### Canonical governance docs
These define the highest-level governance and constitutional ideas behind Nova.

## Why Phases Matter
Phases are how Nova organizes large architectural steps over time.

Examples:
- Phase 4: governed execution foundation
- Phase 4.2: cognitive/reporting depth
- Phase 4.5: perception and UX refinement
- Phase 5: continuity, governed memory, tone controls, scheduling, and opt-in pattern review
- Phase 6: delegated-policy planning, beginning with atomic policy language, Governor-side policy validation, a policy executor gate, and capability topology before any broad trigger runtime

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
That is why the current runtime docs and proof packets matter so much.

For the current repository state, Phase 5 is a good example of this layering:
- the design docs define intent and boundaries
- the proof packet shows what was implemented and ratified
- the runtime docs explain what is live now

Phase 6 currently shows the opposite pattern:
- the design docs now define the first lawful policy model plus the next core execution layers
- the proof packet records next-step planning, implemented validator/store foundation, executor-gate review slice, and Phase-5 deferrals
- the runtime docs now describe manual delegated review surfaces, but still do not claim live delegated trigger runtime

Phase 6 also now has an endgame productization layer in design docs:
- desktop packaging
- update delivery
- API/service compliance
- early-launch legal and business readiness

Those are still planning/docs surfaces, not live runtime truth.

## The Best Reading Order For Most People
1. human guides
2. runtime truth docs
3. proof packets
4. design docs
5. canonical governance docs when deeper theory is needed

## Short Version
Nova's documentation system is layered on purpose.

The right question is not just:
- where is the doc?

It is also:
- what kind of doc is it?
- is it explanatory, live, historical, proof-oriented, or design-oriented?

That distinction keeps the project easier to understand.
