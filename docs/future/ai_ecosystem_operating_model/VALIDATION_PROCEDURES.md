# Validation Procedures

Status: Draft validation procedure
Date: 2026-06-08
Source: User-directed build prompt
Reason: Define reviewable tests for the operating model

## Scope

These procedures validate the docs-only operating package and its alignment with
current repo boundaries. They do not claim live runtime proof.

## Test 1: Source Ranking Enforcement

Objective:
Verify that the package ranks runtime truth above drafts.

Procedure:
Review `AI_ECOSYSTEM_OPERATING_RULES.md` and `CURRENT_TRUTH.md` for explicit
Tier 0 through Tier 4 ranking and lower-tier override prohibition.

Expected result:
The package states that lower tiers may never override higher tiers.

Actual result:
Recorded in `VALIDATION_REPORT_2026-06-08.md`.

Pass/fail:
Recorded in `VALIDATION_REPORT_2026-06-08.md`.

Evidence:
File references and search output.

## Test 2: Authority Separation

Objective:
Verify explicit separation between context, truth, authority, and execution.

Procedure:
Search package files for all four definitions and verify that no document
claims Obsidian or AI output can authorize execution.

Expected result:
All four terms are defined and Obsidian is context-only.

Actual result:
Recorded in `VALIDATION_REPORT_2026-06-08.md`.

Pass/fail:
Recorded in `VALIDATION_REPORT_2026-06-08.md`.

Evidence:
File references and search output.

## Test 3: Priority Enforcement

Objective:
Verify that the package does not override `.agent_context/current_priority.md`.

Procedure:
Read `.agent_context/current_priority.md` and confirm the package states its
`ACTIVE_PRIORITY.md` is draft/package-scoped only.

Expected result:
The package preserves Second Brain Slice 1 as the accepted implementation lane.

Actual result:
Recorded in `VALIDATION_REPORT_2026-06-08.md`.

Pass/fail:
Recorded in `VALIDATION_REPORT_2026-06-08.md`.

Evidence:
File references.

## Test 4: Handoff Generation

Objective:
Verify the operating rules define a session handoff format.

Procedure:
Review `AI_ECOSYSTEM_OPERATING_RULES.md` for required handoff fields.

Expected result:
The file lists changed files, commands run, tests, evidence, limits, and next
action.

Actual result:
Recorded in `VALIDATION_REPORT_2026-06-08.md`.

Pass/fail:
Recorded in `VALIDATION_REPORT_2026-06-08.md`.

Evidence:
File references.

## Test 5: Conflict Resolution

Objective:
Verify that the package defines conflict resolution rules.

Procedure:
Review `AI_ECOSYSTEM_OPERATING_RULES.md` for the required precedence order.

Expected result:
Runtime truth wins, current accepted scope wins, reviewed documents beat drafts,
decision logs beat AI chat output, and drafts never override accepted truth.

Actual result:
Recorded in `VALIDATION_REPORT_2026-06-08.md`.

Pass/fail:
Recorded in `VALIDATION_REPORT_2026-06-08.md`.

Evidence:
File references.

## Test 6: Stale Document Handling

Objective:
Verify that stale documents are handled with traceability.

Procedure:
Review `AI_ECOSYSTEM_OPERATING_RULES.md` for stale-document policy.

Expected result:
Stale documents must be marked, supersession should be recorded, and nothing is
deleted without traceability.

Actual result:
Recorded in `VALIDATION_REPORT_2026-06-08.md`.

Pass/fail:
Recorded in `VALIDATION_REPORT_2026-06-08.md`.

Evidence:
File references.

## Test 7: Update Workflow

Objective:
Verify that AI-generated updates remain proposals until reviewed.

Procedure:
Review `AI_ECOSYSTEM_OPERATING_RULES.md` for update protocol and approval
requirements.

Expected result:
AI may propose updates but may not silently modify accepted truth.

Actual result:
Recorded in `VALIDATION_REPORT_2026-06-08.md`.

Pass/fail:
Recorded in `VALIDATION_REPORT_2026-06-08.md`.

Evidence:
File references.

## Test 8: Review Workflow

Objective:
Verify human-review checkpoints are documented.

Procedure:
Review approval requirements and branch/PR rules.

Expected result:
Human review is required before priority changes, truth promotion, capability
changes, runtime changes, certification claims, or merges.

Actual result:
Recorded in `VALIDATION_REPORT_2026-06-08.md`.

Pass/fail:
Recorded in `VALIDATION_REPORT_2026-06-08.md`.

Evidence:
File references.
