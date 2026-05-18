# Second Brain API / MCP Contract

Status: future planning / not runtime truth.

This document defines the future read-first API surface for Nova's second brain.

It does not add any current API route, MCP tool, or runtime behavior.

---

## Core Boundary

```text
Read APIs may retrieve context.
Proposal APIs may draft knowledge changes.
No second-brain API may execute external actions.
No second-brain API may grant approval.
```

---

## Read-Only Operations

### `knowledge.search`

Purpose: retrieve relevant knowledge entries.

Request:

```json
{
  "query": "approval gate status",
  "project_scope": "NovaLIS",
  "entry_types": ["decision", "research"],
  "statuses": ["reviewed", "promoted"],
  "limit": 10,
  "include_candidates": false
}
```

Response:

```json
{
  "results": [
    {
      "id": "kb_...",
      "title": "Approval gate wiring status",
      "entry_type": "decision",
      "status": "promoted",
      "authority_label": "promoted_knowledge",
      "score": 0.92,
      "why_selected": "FTS match + relationship proximity",
      "warnings": []
    }
  ],
  "warnings": [],
  "non_authorizing": true
}
```

### `knowledge.get_note`

Purpose: retrieve a single note by ID.

Request:

```json
{
  "id": "kb_..."
}
```

Response must include:

```text
frontmatter
body
relationships
source_refs
health_warnings
non_authorizing
```

### `knowledge.get_graph`

Purpose: return a bounded graph snapshot.

Request:

```json
{
  "project_scope": "NovaLIS",
  "entry_types": [],
  "statuses": ["reviewed", "promoted"],
  "limit_nodes": 500,
  "limit_edges": 1000
}
```

Response shape is defined in:

```text
future/brain/second_brain/living_dashboard_visual_contract.md
```

Every graph response should report boundedness and freshness:

```text
projection_version
max_seq
truncated
omitted_node_count
omitted_edge_count
sampling_strategy
redaction_applied
health_state
warnings
```

### `knowledge.get_neighbors`

Purpose: get local graph neighborhood around a note.

Request:

```json
{
  "id": "kb_...",
  "hops": 2,
  "relationship_types": ["supports", "contradicts", "depends_on"],
  "limit_nodes": 100
}
```

### `knowledge.find_paths`

Purpose: find paths between two notes.

Request:

```json
{
  "source_id": "kb_...",
  "target_id": "kb_...",
  "max_hops": 4
}
```

### `knowledge.health`

Purpose: return second-brain health findings.

Response shape is defined in:

```text
future/brain/second_brain/health_check_contract.md
```

### `knowledge.export_snapshot`

Purpose: produce a bounded, read-only snapshot for agent context or backup.

Request:

```json
{
  "project_scope": "NovaLIS",
  "include_body": false,
  "include_candidates": false,
  "limit": 1000,
  "redaction_mode": "strict"
}
```

Response metadata must include:

```text
projection_version
generated_from_hash
max_seq
truncated
omitted_count
redaction_applied
blocked_by_health_findings
non_authorizing
```

---

## Proposal-Only Operations

### `knowledge.propose_entry`

Purpose: create a candidate entry proposal.

This must not create promoted knowledge.

The first implementation should write proposal artifacts only under `proposals/` or an equivalent review queue. Promotion is the only path into curated `knowledge/` or `status: promoted`.

Request:

```json
{
  "title": "Second brain event replay design",
  "entry_type": "proposal",
  "project_scope": "NovaLIS",
  "body": "Proposal body...",
  "source_refs": [],
  "relationships": [],
  "idempotency_key": "..."
}
```

Response:

```json
{
  "proposal_id": "kb_...",
  "status": "candidate",
  "stored_under": "proposals/",
  "review_state": "unreviewed",
  "non_authorizing": true
}
```

### `knowledge.propose_relationship`

Purpose: create a candidate relationship proposal.

Request:

```json
{
  "source_id": "kb_...",
  "expected_source_version": 1,
  "expected_source_content_hash": "sha256:...",
  "idempotency_key": "...",
  "relationship": {
    "type": "supports",
    "target": "kb_...",
    "confidence": "medium"
  }
}
```

### `knowledge.propose_promotion`

Purpose: request review/promotion of a candidate note.

This creates a review item. It does not promote the entry by itself.

Request:

```json
{
  "id": "kb_...",
  "expected_entity_version": 1,
  "expected_content_hash": "sha256:...",
  "reviewer_id": "user",
  "review_lease_id": "review_...",
  "reason": "Source-backed and relevant to active project."
}
```

Promotion must fail closed if the entity version or content hash changed after review began. The caller should receive a `stale_review_target` or `review_lease_conflict` error and create a new review item.

### `knowledge.propose_tombstone`

Purpose: request deletion/tombstoning of a candidate or curated entry.

This creates a review item. It does not erase event history.

Request:

```json
{
  "id": "kb_...",
  "expected_entity_version": 1,
  "expected_content_hash": "sha256:...",
  "reason": "Superseded by newer reviewed entry.",
  "superseded_by": "kb_..."
}
```

---

## Blocked Operations

The second-brain API must not expose:

```text
knowledge.execute
knowledge.approve_action
knowledge.enable_capability
knowledge.run_openclaw
knowledge.send
knowledge.publish
knowledge.buy
knowledge.change_account
knowledge.write_external
```

---

## Error Contract

Errors should be explicit and non-authorizing:

```json
{
  "error": {
    "code": "candidate_excluded",
    "message": "Candidate knowledge was excluded by request settings.",
    "recoverable": true
  },
  "non_authorizing": true
}
```

---

## ContextPack Integration

Second-brain retrieval may feed future context assembly only as labeled context items:

```text
source_label: second_brain
authority_label: candidate_knowledge / reviewed_knowledge / promoted_knowledge
why_selected: explicit ranking explanation
```

Context assembly must preserve candidate labels and stale/conflict warnings.
