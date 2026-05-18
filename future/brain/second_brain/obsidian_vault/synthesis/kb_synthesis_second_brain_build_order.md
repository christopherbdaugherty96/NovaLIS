---
id: kb_synthesis_second_brain_build_order
schema_version: 1
title: "Second Brain Build Order"
entry_type: synthesis
status: candidate
authority_label: candidate_knowledge
created_at: "2026-05-18T00:00:00Z"
updated_at: "2026-05-18T00:00:00Z"
source_refs:
  - "future/brain/second_brain/implementation_backlog.md"
content_hash: "sha256:7777777777777777777777777777777777777777777777777777777777777777"
review_state: unreviewed
reviewed_by: ""
reviewed_at: ""
confidence: medium
project_scope: "NovaLIS"
tags:
  - synthesis
  - build-order
relationships:
  - type: supports
    target: kb_decision_file_first_event_first_foundation
    confidence: medium
    source_ref: "future/brain/second_brain/implementation_backlog.md"
supersedes: []
superseded_by: []
ledger_refs: []
non_authorizing: true
---

# Second Brain Build Order

## Synthesis

Build order should be:

```text
schema
health/lint
deterministic index
read-only query
append-only events
proposal-only writes
living graph
```

This is candidate synthesis until reviewed.
