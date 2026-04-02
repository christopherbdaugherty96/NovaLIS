# Phase 9 Governed Node Plan
Date: 2026-03-18
Status: Planning packet only; runtime not authorized
Scope: Nova as a local governed node and sovereignty-platform control plane across devices

## Purpose
This document relocates the source spec's platform-scale roadmap into the correct future phase.

Phase 9 is where Nova becomes more than a single-device runtime surface.
It becomes a governed node that can serve multiple clients without losing user sovereignty.

## Phase-9 Goal
Create a product shape where:
- Nova runs as a local governed node
- multiple devices can route through the same governed intelligence and execution plane
- the user experiences one trust model across desktop, voice, and mobile-adjacent surfaces
- providers can change without changing the daily authority model

## Dependencies
Phase 9 assumes the following are already solid:
- Phase 6 trust alignment and contract hardening
- Phase 7 governed external reasoning
- Phase 8 governed external execution
- strong recent-actions and trust-review surfaces
- installability and update discipline from the broader Phase-6 productization track

## Core Design Themes

### 1. Node Identity
Nova should present as a governed node, not a hidden cloud service.
That means:
- local control remains primary
- sovereignty language is reflected in setup and settings
- users can see what providers and executors are connected

### 2. Unified Governor Spine
Even with multiple clients, the authority model does not fork.
All clients still converge on one Governor spine for:
- validation
- confirmation
- execution bounds
- audit logging
- trust review

### 3. Cross-Device Trust Consistency
A request from desktop, voice, or another allowed client should preserve the same meaning for:
- what is read-only
- what needs confirmation
- what changed
- what was blocked and why

### 4. Provider and Executor Swapability
Daily experience should not collapse if the reasoning provider or executor changes.
That means Nova's user-facing contract stays stable while provider adapters remain replaceable.

### 5. Sovereign Cost and Packaging Discipline
Platform direction should continue the existing Phase-6 appliance and packaging thinking:
- local-first deployment
- explicit external-service configuration
- calm update surfaces
- inspectable provider costs and dependencies

### 6. Governed Capability Growth
Phase 9 may eventually introduce a tightly bounded coordinator pattern where Nova can help identify capability gaps without granting itself authority to change runtime behavior on its own.

In that future model:
- Nova may recognize and describe a missing capability or workflow gap
- Nova may propose a bounded implementation plan in plain language
- Nova may delegate code generation, analysis, or review subtasks to external reasoning providers or execution tools such as Claude or OpenClaw
- every delegated step remains auditable and reviewable
- the user remains the final governor of whether a proposed capability is accepted, implemented, or activated

The governing rule is:
- Nova may coordinate capability growth proposals
- Nova may not silently expand its own authority

This means:
- no autonomous capability installation
- no hidden mutation of active authority surfaces
- no external model or executor becomes authoritative by suggestion alone
- all proposed changes must remain human-reviewed, explicitly approved, and consistent with mutation-control boundaries

This pattern belongs after the earlier phases are stable because it depends on:
- Phase 7 governed external reasoning containment
- Phase 8 governed external execution isolation
- Phase 9 and later mutation-control rules for reviewability, rollback, and user sovereignty

The intended product shape is:
- Nova acts as a coordinator
- external tools may help generate or review candidate changes
- the user remains the governor of what Nova is capable of doing

## Non-Goals
Phase 9 is not permission for:
- hidden always-on autonomy
- background execution without prior policy design and explicit unlock
- cloud-first authority outsourcing
- silent data egress
- self-authorized capability expansion

## Suggested Implementation Order
1. complete Phases 6 through 8
2. define the node/client trust contract
3. define authenticated client routing through the same Governor spine
4. expose unified trust-review and Recent Actions across clients
5. package provider/executor configuration as explicit node settings
6. add node health, update, and dependency visibility surfaces

## Exit Criteria
Phase 9 is ready only when:
- multi-client routing preserves one Governor authority model
- users can inspect connected providers and executors clearly
- trust and Recent Actions surfaces remain coherent across entry points
- provider swaps do not change the authority semantics presented to the user

## Related Inputs
- `docs/design/Phase 6/NOVA_SOVEREIGNTY_PLATFORM_PHASE_REALIGNMENT_2026-03-18.md`
- `docs/design/Phase 7/PHASE_7_GOVERNED_EXTERNAL_REASONING_PLAN.md`
- `docs/design/Phase 8/PHASE_8_OPENCLAW_GOVERNED_EXECUTION_PLAN.md`
- the autonomy and mutation control design document in this folder
