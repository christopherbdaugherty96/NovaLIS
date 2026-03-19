# Phase 6 Sovereignty Alignment and Trust Loop Plan
Date: 2026-03-18
Status: Planning packet only; runtime not authorized
Scope: Pre-integration alignment work required before any external reasoning provider or external executor is added

## Purpose
This document captures the parts of the sovereignty-platform spec that belong in Phase 6 instead of later integration phases.

Phase 6 is the right place for the work that makes future integrations safe, truthful, and debuggable.
Without this layer, Claude or OpenClaw integration would multiply drift and make failures harder to interpret.

Concrete execution packet:
- `docs/design/Phase 6/PHASE_6_ENGINEERING_CHECKLIST_2026-03-18.md`

## Current Grounded Starting Point
The current repo already has:
- active runtime truth docs and runtime-auditor surfaces
- a live capability registry with active capabilities through `61`
- active perception capabilities `58`, `59`, and `60`
- active memory-governance capability `61`
- an existing mediated `llm_gateway`
- Phase-6 foundation surfaces for policy drafts, executor gate simulation, and capability topology in runtime references

The current repo also has unresolved practical truth gaps:
- explain-anything is currently `partial.environment_blocked`: routing and truthful failure reporting are repaired, but live capture is blocked by a runtime dependency on this machine
- intelligence brief is currently `partial.degraded_but_usable`: entrypoint truth, degradation behavior, surfaced widget/sidebar state, and visual wording are aligned, but source-grounded quality can still degrade under blocked model conditions
- governed web search is now `reliable`: surfaced follow-up prompts are truthful, and the promised first-step follow-up family (`research`, `create an intelligence brief`, `analyze source reliability`) has live in-process proof without contextual drift
- response verification is now `reliable`: live governed verification, truthful degraded handling, and surfaced claim-reliability framing are aligned
- analysis document generation is currently `partial.degraded_but_usable`: fake successful documents are gone, but live create-doc synthesis still degrades into truthful incomplete-document refusal on this local model/runtime
- the basic conversation and tone-control surface is now `reliable`: `tone set concise` and `tone set detailed` work in normal chat, general-chat generation now honors those tone profiles, and the detailed path no longer double-formats long replies
- calendar, screen capture, and screen analysis are now sharply classified as environment-blocked rather than vaguely broken on this machine/runtime
- open-website preview, system status, research reporting, weather/news snapshots, story tracking, and memory overview now have frozen truthful first-journey proofs in the Phase-6 checklist
- local control, speech output, file/folder opening, and diagnostics now have explicit side-effect-safe proof coverage so they are no longer floating as implied unclassified runtime claims
- trust-facing payoff surfaces are now `reliable` for governed Recent Activity rows: Recent Activity distinguishes success vs issue states, surfaces `Why` and `Effect`, and exposes request/ledger correlation for the governed trust-status path without hiding the safe-case outcome
- the Phase-6 release-gate bundle is currently green: trust-panel regressions, runtime-auditor checks, governance-boundary tests, and the key explain/verify/brief executor suites all passed on March 19, 2026
- the main remaining Phase-6 blocker is now cross-cutting contract normalization: ActionResult shape and capability authority metadata are still not normalized enough for safe external-provider expansion

## What Moves Here From The Source Spec
The following source-spec themes belong in Phase 6:
- corrected execution-pipeline hardening
- four-event ledger completeness
- ActionResult normalization
- authority-class normalization
- capability audit and UI/runtime parity checks
- trust-review and Recent Actions payoff loop
- pre-integration fix list

## Phase-6 Operating Rule
Every capability slice should follow the same bounded loop:
- classify claimed state vs observed behavior
- identify the first proven break
- repair only that break
- run one focused proof bundle
- freeze the updated truth state before moving on

Proof bundle minimum:
- one live-path proof
- or one side-effect-safe controlled proof when a true live run would unnecessarily mutate the operator environment
- one focused regression bundle
- one freeze note in `docs/design/Phase 6/PHASE_6_ENGINEERING_CHECKLIST_2026-03-18.md`
- one final classification line with subtype when applicable

Partial status should always be sharpened with a subtype:
- `partial.environment_blocked`
- `partial.degraded_but_usable`
- `partial.multi_step_unproven`
- `partial.surface_contract`

## Phase-6 Objectives

### Objective 1 - Runtime Truth Alignment
Required work:
- remove remaining runtime/doc path drift before new integrations land
- treat `docs/current_runtime/CURRENT_RUNTIME_STATE.md` as authoritative for current state
- make design docs point to runtime truth instead of shadowing it

### Objective 2 - End-to-End Capability Audit
Required work:
- enumerate every capability presented in the UI
- verify prompt routing, Governor validation, executor invocation, returned output, and ledger results
- explicitly mark anything partial or misleading until it is truly working

Priority focus areas:
- `intelligence_brief`
- `response_verification`
- `screen_capture`
- `screen_analysis`
- `explain_anything`
- `memory_governance`

### Objective 3 - Explain and Brief Reliability
Required work:
- make the runtime behavior for "what is this?" match the active capability claims
- verify the screen/context routing path under real interaction, not just narrow tests
- tighten brief generation so the user-facing result is consistently useful and visible

Interpretation rule:
- this is not a new Phase 8 initiative
- it is Phase-6 truth-alignment work because the surfaces are already presented as active

### Objective 4 - Trust Loop Completion
Required work:
- add a Recent Actions surface with plain-language cause and outcome visibility
- improve Trust Review so users can see what Nova did, why it was allowed, and what external effect occurred
- make failures visible instead of disappearing into logs

This is the missing payoff loop the source spec correctly called out.
It should be solved before widening external execution.

### Objective 5 - Capability Metadata Hardening
Required work:
- extend capability metadata so every capability can declare authority class, reversibility, confirmation requirement, and external effect semantics in one governed place
- align capability-topology work with registry-facing truth instead of scattered hardcoded assumptions
- preserve current IDs and active behaviors while adding the richer metadata model

### Objective 6 - ActionResult and Ledger Contract Normalization
Required work:
- define one canonical ActionResult shape for all executors
- verify that every governed execution path returns user-safe text, speakable text, structured metadata, and audit correlation
- verify that every action produces a complete lifecycle in the ledger

Current next implementation move:
- lock the canonical ActionResult contract in the Phase-6 checklist
- normalize `action_result.py` and the Governor boundary first
- migrate the first governed executor wave and core consumers only after the boundary contract is stable

Current implementation state as of 2026-03-19:
- completed:
  - ActionResult contract locked in docs
  - `action_result.py` normalization spine added
  - Governor boundary now stamps shared result metadata centrally
  - first governed executor wave migrated:
    - response verification
    - news intelligence
    - multi-source reporting
    - analysis documents
  - explain/screen executor wave migrated:
    - explain anything
    - screen capture
    - screen analysis
  - main governed `brain_server.py` path now prefers canonical result reads
  - trust/recent-activity normalization now reads canonical status and outcome metadata first
  - active-capability authority metadata parity now enforced:
    - active registry entries carry explicit authority metadata
    - `CapabilityRegistry` fails closed on missing active-capability governance fields
    - `CapabilityTopology` fails closed on registry/topology parity drift
    - runtime-auditor governance rows now consume the explicit authority metadata when present
- next:
  - remove remaining legacy consumer fallbacks after broader executor migration is complete

Target lifecycle:
1. `INTENT_RECEIVED`
2. `ACTION_VALIDATED`
3. `EXECUTION_STARTED`
4. `EXECUTION_COMPLETED` or `EXECUTION_FAILED`

### Objective 7 - CI and Boundary Enforcement
Required work:
- strengthen checks against direct LLM calls outside the gateway path
- strengthen checks against direct network usage outside the approved mediated path
- fail closed when new code introduces a second authority path

## Explicit Out Of Scope For Phase 6
Do not treat these as Phase-6 deliverables:
- Anthropic API wiring
- OpenClaw execution wiring
- multi-device node routing
- general autonomy or background execution

Those belong to later phases after Phase-6 alignment closes.

## Exit Criteria
Phase 6 is ready to hand off only when all of the following are true:
- runtime docs and live behavior no longer disagree on major user-facing surfaces
- explain-anything and brief flows are verified in realistic use
- capability claims in UI and docs are operationally true
- trust-facing Recent Actions and review surfaces exist and are informative
- capability metadata can safely express future external-provider and executor classes
- ActionResult and ledger lifecycle checks are enforced consistently
- direct-network and direct-LLM bypass tests are green

## Related Inputs
- `docs/design/NOVA_SOVEREIGNTY_PLATFORM_PHASE_REALIGNMENT_2026-03-18.md`
- `docs/design/Phase 6/PHASE_6_ENGINEERING_CHECKLIST_2026-03-18.md`
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/design/Phase 6/PHASE_6_DOCUMENT_MAP.md`
- `docs/design/Phase 8/node design.txt`
