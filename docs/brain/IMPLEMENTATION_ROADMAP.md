# Brain Implementation Roadmap

No fake deadlines.

This roadmap phases the Brain from design to runtime behavior without widening execution authority.

## Current Status Snapshot

Done:

- Brain architecture docs exist.
- Brain runtime architecture doc exists.
- Read-only `EnvironmentRequest` schema scaffold exists.
- Task Clarifier is implemented for tested ambiguity/boundary prompts.
- Static Capability Contract catalog exists for Cap 16, Cap 64, Cap 65, and Cap 63.
- Brain live-test proof exists under `docs/demo_proof/brain_live_test/`.

Still not done:

- full Task Environment Router
- live Capability Contract lookup
- Capability Contract use by runtime routing/Governor
- Dry Run / Plan Preview API
- Brain Trace UI
- project context engine
- suggestion buffer runtime
- full OpenClaw environment planning
- Context Assembler
- Model Router / Tier Manager
- Intention Parser / structured output validation
- Tool / Function Calling Bridge
- Search Synthesis module
- Sandbox Boundary Enforcer
- Persona / Identity Filter

Active P1 blocker:

- Cap 16 search reliability / CPU-budget handling for current-information prompts.

---

## Capability Expansion Guardrails (Not an Active Phase)

This section is intentionally separated from the implementation phases.
It does not define current work or upcoming milestones.

This section does not define the next work to execute.

It defines the conditions that must be true *before* NovaLIS expands its capability surface at any future point.

Current priority remains unchanged (see Active P1 blocker and phases above).

These guardrails exist to prevent premature expansion that would weaken governance, traceability, or system integrity.

This is a system constraint, not a build sequence.
It must not be interpreted as an ordered task list.

Capability expansion is only permitted when ALL of the following system conditions are already true:

```text
1. Capability contracts are used in planning.
2. Environment requests validate against known authority tiers.
3. Dry Run / Plan Preview exists for higher-authority tasks.
4. Trust Flow or equivalent approval surface exists.
5. Run lifecycle states are enforced.
6. Receipts are consistent.
7. Context assembly is bounded and explicit.
8. GovernorMediator / CapabilityRegistry / ExecuteBoundary remain the only execution path.
```

Allowed before this is complete:

- read-only reliability work
- low-risk diagnostics
- contract/schema work
- dry-run planning
- tests
- UI/receipt visibility

Avoid before this is complete:

- new account-write capabilities
- publishing workflows
- purchases
- real financial execution
- broad OpenClaw automation
- autonomous scheduled execution
- new desktop actions that cannot produce receipts

Rule:

> Every new capability must prove the governance system works; it must not become a shortcut around it.

This section is intentionally non-actionable in the current phase and must not influence task prioritization.

---

## Future Planning Package

The long-term Brain planning package now lives under:

```text
future/brain/
```

This package is not runtime truth and is not a new implemented Brain phase. It is source material for future phases already listed in this roadmap.

Current future Brain planning docs include:

```text
future/brain/README.md
future/brain/ARCHITECTURE_MAP.md
future/brain/PROMOTION_PATH.md
future/brain/CONTEXT_ASSEMBLER.md
future/brain/SIGNAL_REGISTRY.md
future/brain/RUN_LIFECYCLE.md
future/brain/TRUST_INTEGRATION.md
future/brain/RECEIPT_TO_MEMORY.md
future/brain/DOMAIN_PERMISSION_PROFILES.md
future/brain/FINAL_POLISH_RULES.md
```

Related domain planning remains source-of-truth in:

```text
future/governed_desktop_runs/
future/market_sandbox/
future/youtubelis/
```

Do not treat these future docs as implemented runtime behavior. Their purpose is to keep the future Brain architecture coherent while current work remains focused on Cap 16 reliability, capability contracts, dry-run planning, and traceable governance.

Mapping to existing roadmap phases:

| Future planning area | Roadmap phase it informs | Notes |
| --- | --- | --- |
| Context assembly rules | Phase 5 — Context Assembler | Defines future context boundaries, freshness, conflicts, and exclusion rules. |
| Signal registry | Phase 13 — Project Contexts and Suggestion Buffer | Defines controlled triggers without granting execution authority. |
| Trust integration / Trust Flow | Phase 9 — Dry Run / Plan Preview and Phase 11 — Brain Trace UI | Defines the visible user-facing bridge from plan to approval to receipt. |
| Run lifecycle | Phase 8 — Sandbox Boundary Enforcer and Phase 12 — OpenClaw Environment Planning | Defines lifecycle states, retry limits, terminal states, and stop conditions. |
| Receipt-to-memory policy | Phase 13 — Project Contexts and Suggestion Buffer | Defines when receipts may become memory or learning records. |
| Domain permission profiles | Phase 6 — Intention Parser and Phase 8 — Sandbox Boundary Enforcer | Defines cross-domain risk classification inputs. |
| Final polish rules | Runtime Constraint section | Captures universal non-overlap rules: no hidden authority, no silent learning, no receipt-free behavior. |

---

## Implementation Status

| Phase | Status | Code | Tests | Runtime integration |
|-------|--------|------|-------|---------------------|
| 0 — Governor Spine Proof | ✅ | dry-run examples in `docs/demo_proof/` | — | — |
| 1 — Task Clarifier | ✅ | `src/brain/task_clarifier.py` | `tests/brain/test_task_clarifier.py` | `session_router.py` → `session_handler.py` |
| 2 — Environment Catalog | ✅ | `EnvironmentType` / `AuthorityTier` enums | `test_environment_request.py` | none |
| 3 — Capability Contracts | ✅ | `CapabilityContract` dataclass | `test_environment_request.py` | none |
| 4 — Dry Run / Plan Preview | ⚠️ partial | `BrainDryRun`, `task_to_environment_request()` | `test_environment_request.py` | none (builder exists, no routing wired) |
| 5 — Brain Trace UI | ⚠️ schema only | `BrainTraceEvent` dataclass | `test_environment_request.py` | none |
| 6 — Cap 16 Reliability Integration | ❌ | — | — | — |
| 7 — OpenClaw Environment Planning | ❌ | — | — | — |
| 8 — Project Contexts / Suggestion Buffer | ❌ | — | — | — |

Capability Contracts status note: the shared `CapabilityContract` dataclass exists, and a static catalog now exists in `src/brain/capability_contracts.py` for Cap 16, Cap 64, Cap 65, and Cap 63. Runtime contract lookup is not wired into the full Task Environment Router or Governor path yet.

## Phase 0 — Governor Spine Proof

Status: partially satisfied by existing governance/proof work and Brain dry-run examples.

Goal: prove the Brain can ask for permission and be denied without bypassing the Governor.

Deliverables:

- dry-run examples that reach Governor Gate but do not execute
- blocked examples with fallback ladders
- proof that no execution capability is added by Brain planning

---

## Phase 1 — Task Clarifier

Status: first live slice implemented.

Goal: prove Nova can detect ambiguity and ask the minimum useful question before planning.

Implemented prompt classes include:

- missing city/service area for contractor/outreach prompts
- missing recipient for incomplete email drafts
- personal account/account-write boundary
- ambiguous browser/OpenClaw/personal-browser requests
- Shopify read-only/write boundary
- memory authority boundary

Remaining work:

- expand prompt coverage only when proof shows gaps
- avoid broad, fragile pattern matching
- keep clarifier deterministic unless a later governed classifier is designed

---

## Phase 2 — Cap 16 Reliability Integration

Status: active P1.

Goal: make current-information prompts reliable enough for Brain planning.

Expected behavior:

- successful search returns source-backed answer
- partial search returns partial source-backed answer
- weak/no evidence is stated honestly
- budget/token failure returns a bounded failure with retry/narrowing guidance
- current-fact prompts do not fall back to stale confident memory

---

## Phase 3 — Capability Contracts

Status: schema/scaffold plus static catalog.

Current truth:

- `CapabilityContract` dataclass exists as Brain schema.
- Static contracts exist for the highest-priority capabilities:
  - Cap 16 governed web search
  - Cap 64 send email draft
  - Cap 65 Shopify intelligence report
  - Cap 63 OpenClaw execute
- Runtime routing/Governor lookup is not live yet.

Goal: use static contracts as the next authority vocabulary for:

- Cap 16 governed web search
- Cap 64 send email draft
- Cap 65 Shopify intelligence report
- Cap 63 OpenClaw execute

Deliverables:

- static contract catalog
- tests that blocked actions are represented correctly
- no duplicate hardcoded capability truth where contract lookup should be used

Remaining work:

- wire contracts into a future EnvironmentRequest/Dry Run builder
- keep Governor as the execution authority
- do not treat static contracts as permission to execute

---

## Phase 4 — Environment Catalog Validation

Status: design only.

Goal: prove task plans validate against known environments and authority tiers.

Deliverables:

- schema/data file for environments
- tests for valid/invalid environment requests
- consistency with `ENVIRONMENT_CATALOG.md`

---

## Phase 5 — Context Assembler

Status: future.

Goal: retrieve only the context needed for the current task.

Inputs may include:

- current conversation
- project memory
- user preferences
- recent decisions
- recent receipts
- active routines
- open loops
- runtime truth docs
- capability contracts
- proof packages

Rules:

- context can improve understanding
- context cannot authorize action
- sensitive context should not be sent to cloud/deep reasoning lanes without governed approval
- future planning details live in `future/brain/CONTEXT_ASSEMBLER.md` and must not be treated as implemented behavior

---

## Phase 6 — Intention Parser / Structured Output Validation

Status: future.

Goal: ensure model-suggested routes are validated before they can reach tool/capability paths.

Deliverables:

- structured intent schema
- strict parser/validator
- malformed-intent fallback to clarification
- tests for invalid, unsafe, and incomplete intent payloads

Rules:

- the model may suggest intent
- deterministic code validates intent
- malformed output should not be guessed into action
- future domain permission profile inputs live in `future/brain/DOMAIN_PERMISSION_PROFILES.md`

---

## Phase 7 — Search Synthesis Module

Status: future.

Goal: turn raw search results into structured evidence before final response synthesis.

Deliverables:

- claims
- source URLs
- known/unclear fields
- confidence/uncertainty notes
- partial-results behavior
- weak/no-evidence behavior

This phase supports Cap 16 reliability and future Brain dry runs.

---

## Phase 8 — Sandbox Boundary Enforcer

Status: future.

Goal: enforce the boundary between internal cognition and real-world actions in code.

Inside sandbox:

- reason
- summarize
- draft
- plan
- retrieve memory
- prepare dry runs
- suggest next steps

Outside sandbox:

- send
- buy
- publish
- submit
- delete
- edit account
- write Shopify
- run OpenClaw
- change calendar
- modify files
- trigger external services

Rules:

- outside-sandbox actions require capability checks
- confirmations and receipts must remain visible
- the Sandbox Boundary Enforcer must not bypass the Governor
- future run lifecycle, auto-approval, and final-polish constraints live in `future/brain/RUN_LIFECYCLE.md`, `future/governed_desktop_runs/AUTO_APPROVAL_POLICY.md`, and `future/brain/FINAL_POLISH_RULES.md`

---

## Phase 9 — Dry Run / Plan Preview

Status: future.

Goal: generate non-executing plan previews for multi-step or higher-authority tasks.

Deliverables:

- structured dry-run payloads
- planned steps
- environments
- capability contracts
- confirmation points
- expected proof
- fallback ladder
- what Nova will not do

This phase should come after Task Clarifier, Cap 16 reliability, and initial Capability Contracts.

Future Trust Flow / Trust Integration planning lives in `docs/product/TRUST_FLOW.md` and `future/brain/TRUST_INTEGRATION.md`.

---

## Phase 10 — Persona / Identity Filter

Status: future.

Goal: ensure final responses preserve Nova's honest identity, boundary language, and user-facing clarity.

Deliverables:

- boundary phrase library
- current-capability honesty checks
- no-overclaim wording tests
- optional small-model style pass later

Rules:

- Persona improves communication
- Persona does not authorize action

---

## Phase 11 — Brain Trace UI

Status: future.

Goal: render operational trace metadata without exposing hidden chain-of-thought.

Trace should show:

- task
- clarification status
- environments
- authority
- capability
- confirmation
- proof
- fallback

Future trust-card and receipt visibility details should align with `docs/product/TRUST_FLOW.md` and `future/brain/TRUST_INTEGRATION.md`.

---

## Phase 12 — OpenClaw Environment Planning

Status: future.

Goal: add plan-time OpenClaw environment requests before any browser execution work.

Rules:

- OpenClaw is an environment, not the Brain.
- Isolated browser should remain distinct from personal browser session.
- No OpenClaw execution should occur from planning alone.
- governed desktop planning details live in `future/governed_desktop_runs/` and are not runtime truth until implemented

---

## Phase 13 — Project Contexts and Suggestion Buffer

Status: future.

Goal: add project-specific context, rejected-plan memory, and governed suggestions.

Rules:

- suggestions do not execute
- suggestions do not authorize actions
- project context is not permission
- memory can influence understanding but not execution authority
- receipt-to-memory and signal-registry planning lives in `future/brain/RECEIPT_TO_MEMORY.md` and `future/brain/SIGNAL_REGISTRY.md`

---

## Phase 14 — Model Router / Tier Manager

Status: future.

Goal: choose between deterministic answer, local small model, local medium model, and optional cloud/deep reasoning lane.

Rules:

- model routing is a privacy/governance decision, not only optimization
- sensitive local context must not be sent to cloud/deep reasoning without approved settings or explicit confirmation
- user should be able to choose privacy tiers such as `never_cloud` or `ask_before_cloud`

Model Router can be designed early, but it should not distract from Cap 16 reliability and Capability Contracts.

---

## Phase 15 — Obsidian Presence Mirror

Status: future.

Goal: mirror Nova's activity, files in use, proof, receipts, and open loops into a controlled Obsidian presence folder.

Rules:

- Obsidian is a mirror, not authority
- no approval should be inferred from notes
- writes should be constrained to a configured `Nova_Presence/` folder
- ledger remains proof authority

---

## Runtime Constraint

Each phase must preserve:

- Governor authority
- capability registry boundaries
- receipt/proof discipline
- no hidden execution
- no conceptual docs treated as implemented runtime truth
- no hidden authority, no silent learning, no receipt-free behavior

## Recommended Next Step

Fix Cap 16 search reliability before building Dry Run / Plan Preview, broader Brain runtime modules, or new medium/high-risk capabilities.
