---
id: kb_research_second_brain_robustness_example
schema_version: 1
title: "Second Brain Robustness Requirements"
entry_type: research
status: promoted
authority_label: promoted_knowledge
created_at: "2026-05-18T00:00:00Z"
updated_at: "2026-05-18T00:00:00Z"
source_refs:
  - "docs/future/NOVA_SECOND_BRAIN_OBSIDIAN_RESEARCH_AND_IMPLEMENTATION_PLAN_2026-05-18.md"
content_hash: "sha256:2222222222222222222222222222222222222222222222222222222222222222"
review_state: approved
reviewed_by: "planning_scaffold"
reviewed_at: "2026-05-18T00:00:00Z"
confidence: high
project_scope: "NovaLIS"
tags:
  - second-brain
  - robustness
relationships:
  - type: supports
    target: kb_decision_file_first_event_first_foundation
    confidence: high
    source_ref: "docs/future/NOVA_SECOND_BRAIN_OBSIDIAN_RESEARCH_AND_IMPLEMENTATION_PLAN_2026-05-18.md"
supersedes: []
superseded_by: []
ledger_refs: []
non_authorizing: true
---

# Second Brain Robustness Requirements

Nova's second brain should be file-first, review-gated, event-backed, and non-authorizing.

## Key Requirements

- Markdown is the durable knowledge source.
- SQLite/vector/graph indexes are rebuildable projections.
- Knowledge events are append-only operation history.
- Proposal promotion must fail closed on stale version/hash.
- Sensitive data blocks export, embedding, and cloud routing until reviewed.
- The living dashboard is visibility only.
