# Proposed Priority Lock - Second Brain Foundation

Status: PROPOSED / not active.

Date: 2026-05-18

This is a proposed future priority lock for the Nova second-brain foundation.

It is not the active workstream and does not override:

```text
docs/status/ACTIVE_PRIORITY_LOCK_2026-05-15_APPROVAL_GATE_WIRING.md
.agent_context/current_priority.md
generated runtime truth
runtime code
tests
```

---

## Goal

Design and implement a file-first, non-authorizing second-brain foundation for Nova.

The second brain should improve retrieval, project memory, knowledge graph navigation, and future dashboard visualization without granting execution authority.

---

## Scope

Allowed first slice:

```text
KnowledgeEntry schema
KnowledgeRelationship schema
KnowledgeEvent schema
frontmatter validation
vault health / lint report
deterministic index rebuild from markdown
append-only event store boundary
read-only graph/search query surface
tests proving non-authorizing invariants
documentation and proof of boundaries
```

Later slices, only after first-slice proof:

```text
local embeddings
graph-boosted ranking
MCP read tools
proposal-only knowledge writes
event replay feed
living dashboard graph visualization
```

---

## Strict Non-Goals

```text
no new execution capability
no authority expansion
no autonomous vault mutation
no silent learning
no external writes
no OpenClaw expansion
no browser/computer-use expansion
no dashboard visualization before data/events exist
no approval inferred from memory or notes
no ledger replacement
no generated runtime claim before code/tests exist
```

---

## Required Boundaries

```text
knowledge is context, not permission
markdown is knowledge source, not execution proof
SQLite / DuckDB / vector indexes are rebuildable projections
knowledge events are append-only operation history, not disposable projection rows
ledger remains proof authority
generated runtime docs remain runtime truth authority
dashboard visualization remains visibility-only
all write paths start as proposal/review gated
```

---

## Required Output For First Active Slice

```text
1. Schema files or dataclasses exist for knowledge entries, relationships, and events.
2. Tests prove every knowledge entry is non-authorizing.
3. Health/lint command reports missing frontmatter, broken links, duplicate IDs, stale/unreviewed entries, and authority drift.
4. Index rebuild proves markdown files can regenerate the machine projection.
5. Index rebuild proves it does not erase, regenerate, or resequence append-only event history.
6. Read-only graph/search APIs do not mutate files and do not invoke execution capabilities.
7. Docs distinguish implemented runtime behavior from future dashboard/visualization plans.
```

---

## Acceptance Criteria

Before this lock can close:

```text
tests pass
index rebuild is deterministic
event history is append-only and separate from disposable projections
health report catches authority drift
knowledge retrieval feeds planning/context only
no second-brain path reaches Executor / OpenClaw / external writes
proposal promotion fails closed on stale version/hash
generated runtime docs are updated only after implementation exists
current docs do not overclaim
```

---

## Research Basis

See:

```text
docs/future/NOVA_SECOND_BRAIN_OBSIDIAN_RESEARCH_AND_IMPLEMENTATION_PLAN_2026-05-18.md
future/brain/SECOND_BRAIN_FOUNDATION.md
future/brain/second_brain/
```

Draft implementation contracts currently include:

```text
future/brain/second_brain/knowledge_entry.schema.json
future/brain/second_brain/knowledge_relationship.schema.json
future/brain/second_brain/knowledge_event.schema.json
future/brain/second_brain/index_projection_contract.md
future/brain/second_brain/event_replay_contract.md
future/brain/second_brain/api_contract.md
future/brain/second_brain/health_check_contract.md
future/brain/second_brain/living_dashboard_visual_contract.md
future/brain/second_brain/governance_threat_model.md
future/brain/second_brain/implementation_backlog.md
future/brain/second_brain/implementation_blueprint/
future/brain/second_brain/acceptance_test_plan.md
future/brain/second_brain/OBSIDIAN_VAULT_END_TO_END.md
future/brain/second_brain/obsidian_vault/
future/brain/second_brain/obsidian_vault/VAULT_MANIFEST.md
future/brain/second_brain/obsidian_vault/RUNBOOK_CAPTURE_REVIEW_PROMOTE.md
future/brain/second_brain/obsidian_vault/RUNBOOK_HEALTH_LINT.md
future/brain/second_brain/obsidian_vault/RUNBOOK_LIVING_GRAPH.md
future/brain/second_brain/templates/
```

---

## Sequencing Rule

```text
Data / schema / lint / index first.
Event replay second.
Proposal-only writes third.
Living dashboard graph last.
```

The living dashboard graph should use real graph snapshots and sequence-numbered knowledge events. It should not be prototyped as a runtime claim before the data layer exists.
