# Brain Implementation Roadmap

No fake deadlines.

This roadmap phases the Brain from design to runtime scaffolding without widening execution authority.

## Phase 0 — Governor Spine Proof

Prove the brain can ask for permission and be denied.

Deliverable:

- dry-run examples that reach Governor Gate but do not execute
- blocked examples with fallback ladders

## Phase 1 — Task Clarifier

Prove Nova can detect ambiguity and ask the minimum useful question before planning.

Deliverable:

- clarification examples
- tests for missing city, missing recipient, missing product, ambiguous browser request

## Phase 2 — Environment Catalog Validation

Prove task plans validate against known environments and authority tiers.

Deliverable:

- schema/data file for environments
- tests for valid/invalid environment requests

## Phase 3 — Capability Contracts

Create static contracts for the highest-priority capabilities:

- Cap 16 governed web search
- Cap 64 send email draft
- Cap 65 Shopify intelligence report
- Cap 63 OpenClaw execute

Deliverable:

- docs or data contracts
- tests that blocked actions are represented correctly

## Phase 4 — Dry Run / Plan Preview

Generate non-executing plan previews for multi-step tasks.

Deliverable:

- structured dry-run payloads
- UI or API preview later

## Phase 5 — Brain Trace UI

Render operational trace metadata:

- task
- clarification status
- environments
- authority
- capability
- confirmation
- proof
- fallback

## Phase 6 — Cap 16 Reliability Integration

Tie current-information requests to the EnvironmentRequest model and Cap 16 proof harness.

Current active priority remains Cap 16 search reliability.

## Phase 7 — OpenClaw Environment Planning

Add plan-time OpenClaw environment requests before any browser execution work.

## Phase 8 — Project Contexts and Suggestion Buffer

Add project-specific context, rejected-plan memory, and governed suggestions.

## Runtime Constraint

Each phase must preserve:

- Governor authority
- capability registry boundaries
- receipt/proof discipline
- no hidden execution
- no conceptual docs treated as implemented runtime truth