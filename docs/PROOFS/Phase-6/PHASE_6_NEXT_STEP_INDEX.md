# Phase-6 Next-Step Index
Updated: 2026-03-14
Status: Planned next-step packet only
Purpose: Index of Phase-6 planning artifacts that describe the next implementation slice without claiming live runtime status.

## Important Status Note
Nothing in this folder should be read as proof of active runtime behavior unless a future runtime slice is implemented and verified.

Current runtime truth still lives in:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- `docs/PROOFS/Phase-6/PHASE_6_PROOF_PACKET_INDEX.md`

Implemented Phase-6-era runtime slices already include:
- `PHASE_6_POLICY_VALIDATOR_FOUNDATION_RUNTIME_SLICE_2026-03-13.md`
- `PHASE_6_POLICY_EXECUTOR_GATE_RUNTIME_SLICE_2026-03-13.md`
- `PHASE_6_OPERATOR_HEALTH_SURFACE_RUNTIME_SLICE_2026-03-13.md`
- `PHASE_6_LIVE_CAPABILITY_DISCOVERY_SURFACE_RUNTIME_SLICE_2026-03-13.md`
- `PHASE_6_TRUST_REVIEW_SURFACE_RUNTIME_SLICE_2026-03-13.md`
- `PHASE_6_DASHBOARD_REFINEMENT_MEMORY_AND_NEWS_RUNTIME_SLICE_2026-03-14.md`
- `PHASE_6_POLICY_REVIEW_CENTER_RUNTIME_SLICE_2026-03-26.md`

## Core Planning References
- the corrected Phase-6 roadmap document in `docs/design/Phase 6/`
- `docs/design/Phase 6/PHASE_6_DOCUMENT_MAP.md`
- `docs/PROOFS/Phase-5/PHASE_5_CLOSED_ACT_2026-03-13.md`
- `docs/PROOFS/Phase-6/PHASE_6_DEFERRED_FROM_PHASE_5_2026-03-13.md`

## Current Planned Artifacts
1. `docs/design/Phase 6/ATOMIC_POLICY_LANGUAGE_AND_POLICY_ENVELOPE_SPEC.md`
   - First core Phase-6 design spec for one-trigger, one-action delegated policies
   - Defines the minimum lawful policy model before validator or trigger-monitor work begins
2. `PHASE_6_POLICY_VALIDATOR_FOUNDATION_RUNTIME_SLICE_2026-03-13.md`
   - First real Phase-6 runtime foundation slice
   - Adds Governor-side policy validation and disabled draft storage without enabling trigger execution
3. `docs/design/Phase 6/PHASE_6_POLICY_EXECUTOR_GATE_SPEC.md`
   - Defines the required Governor-side execution gate between delegated policy and actual capability execution
   - Clarifies why trigger runtime must not arrive before a lawful execution path exists
   - Includes dry-run / simulation guidance for safe policy debugging before broad enablement
4. `docs/design/Phase 6/PHASE_6_CAPABILITY_TOPOLOGY_SYSTEM_SPEC.md`
   - Defines the authority-class and delegation-classification model for Nova's growing capability surface
   - Keeps delegated policy rules legible, scalable, and audit-friendly
   - Adds the authority-class hierarchy needed for safe delegated-policy boundaries
5. `docs/design/Phase 6/PHASE_6_POLICY_SIMULATION_SURFACE_SPEC.md`
   - Defines Nova's first delegated-policy trust surface through dry-run inspection
   - Standardizes simulation result format, safety indicators, and review flow before broad enablement
   - The core simulation contract is now implemented in the current runtime, but broader surface/UI expansion is still planned
6. `PHASE_6_PROJECT_WIDE_NEXT_STEPS_2026-03-13.md`
   - Recommended whole-project priority order after Phase-5 closure
   - Keeps Phase-6 core work, product hardening, installability, operator health, and productization in the right sequence
7. `PHASE_6_DEFERRED_FROM_PHASE_5_2026-03-13.md`
   - Records tracks intentionally not added to the closed Phase-5 package
   - Clarifies that those tracks are planning inputs, not active runtime truth
   - Keeps the Phase-5 closure boundary clean while Phase-6 core is defined
8. `docs/design/Phase 6/PHASE_6_PRODUCT_SURFACES_SPEC.md`
   - Defines the three surfaces that make Nova feel like a real product:
   - operator health, daily utility, and trust / review
9. `docs/design/Phase 6/PHASE_6_PROGRESSIVE_SCREEN_INTELLIGENCE_PRODUCT_SPEC.md`
   - Signature product-direction spec for Nova's `what is this?` interaction
   - Defines cursor-first, section-next, page-last expansion as the preferred model
10. `docs/design/Phase 6/PHASE_6_LOCAL_AI_APPLIANCE_AND_PRODUCT_DIRECTION.md`
   - Local AI appliance / Nova Hub direction for the Phase-6 era
   - Frames installability, sellability, and product packaging around Nova's architecture
11. `docs/design/Phase 6/PHASE_6_ENDGAME_PRODUCTIZATION_ROADMAP.md`
   - End-of-Phase-6 productization roadmap for packaging, updates, launch readiness, and distribution
   - Treats desktop packaging and launch preparation as a Phase-6-era product track, not runtime truth
12. `docs/design/Phase 6/PHASE_6_DESKTOP_APP_PACKAGING_AND_DISTRIBUTION_SPEC.md`
   - Recommended local desktop app path, packaging options, and first distribution channels
13. `docs/design/Phase 6/PHASE_6_UPDATE_AND_COMPONENT_DELIVERY_SPEC.md`
   - Documents the recommended early update flow and component-delivery model
14. `docs/design/Phase 6/PHASE_6_API_CONFIGURATION_AND_EXTERNAL_SERVICE_COMPLIANCE_SPEC.md`
   - Clarifies that Nova's API architecture can largely stay intact while productizing config, attribution, and external-service compliance
15. `docs/design/Phase 6/PHASE_6_EARLY_LAUNCH_LEGAL_AND_BUSINESS_READINESS.md`
   - Records the minimum early-launch legal packet, company-formation triggers, and state/federal verification reminders
16. `PHASE_6_PORCUPINE_WAKE_WORD_RUNTIME_PLAN.md`
   - Governance-safe plan for adding a local Porcupine wake-word gate
   - Explicitly non-authorizing
   - Adjacent convenience/input track, not the delegated-autonomy core

## Interpretation Rule
Use this folder to understand what may come next.
Do not use it to claim that any Phase-6 feature is already live.
