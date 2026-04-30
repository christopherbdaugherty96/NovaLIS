# Brain Implementation Roadmap

No fake deadlines.

This roadmap phases the Brain from design to runtime behavior without widening execution authority.

## Current Status Snapshot

Done:

- Brain architecture docs exist.
- Brain runtime architecture doc exists.
- Read-only `EnvironmentRequest` schema scaffold exists.
- Task Clarifier is implemented for tested ambiguity/boundary prompts.
- Brain live-test proof exists under `docs/demo_proof/brain_live_test/`.

Still not done:

- full Task Environment Router
- live Capability Contract lookup
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

Status: design/schema only.

Goal: create static contracts for the highest-priority capabilities:

- Cap 16 governed web search
- Cap 64 send email draft
- Cap 65 Shopify intelligence report
- Cap 63 OpenClaw execute

Deliverables:

- docs or data contracts
- tests that blocked actions are represented correctly
- no duplicate hardcoded capability truth where contract lookup should be used

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

---

## Phase 12 — OpenClaw Environment Planning

Status: future.

Goal: add plan-time OpenClaw environment requests before any browser execution work.

Rules:

- OpenClaw is an environment, not the Brain.
- Isolated browser should remain distinct from personal browser session.
- No OpenClaw execution should occur from planning alone.

---

## Phase 13 — Project Contexts and Suggestion Buffer

Status: future.

Goal: add project-specific context, rejected-plan memory, and governed suggestions.

Rules:

- suggestions do not execute
- suggestions do not authorize actions
- project context is not permission
- memory can influence understanding but not execution authority

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

## Recommended Next Step

Fix Cap 16 search reliability before building Dry Run / Plan Preview or broader Brain runtime modules.
