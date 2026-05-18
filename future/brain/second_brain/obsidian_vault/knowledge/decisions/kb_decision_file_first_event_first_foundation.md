---
id: kb_decision_file_first_event_first_foundation
schema_version: 1
title: "Use File-First Knowledge With Append-Only Events"
entry_type: decision
status: promoted
authority_label: promoted_knowledge
created_at: "2026-05-18T00:00:00Z"
updated_at: "2026-05-18T00:00:00Z"
source_refs:
  - "future/brain/SECOND_BRAIN_FOUNDATION.md"
content_hash: "sha256:3333333333333333333333333333333333333333333333333333333333333333"
review_state: approved
reviewed_by: "planning_scaffold"
reviewed_at: "2026-05-18T00:00:00Z"
confidence: high
project_scope: "NovaLIS"
tags:
  - decision
  - file-first
relationships:
  - type: derived_from
    target: kb_research_second_brain_robustness_example
    confidence: high
    source_ref: "future/brain/SECOND_BRAIN_FOUNDATION.md"
  - type: supports
    target: kb_concept_non_authorizing_memory
    confidence: high
    source_ref: "future/brain/SECOND_BRAIN_FOUNDATION.md"
supersedes: []
superseded_by: []
ledger_refs: []
non_authorizing: true
---

# Use File-First Knowledge With Append-Only Events

## Decision

Use Markdown/Obsidian notes as the durable second-brain knowledge source, with machine indexes as rebuildable projections and knowledge events as append-only operation history.

## Boundaries

This decision does not authorize runtime implementation. It defines the future design direction only.
