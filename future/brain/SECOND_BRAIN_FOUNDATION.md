# Second Brain Foundation

Status: future planning / not runtime truth.

This document defines the safe foundation for a future Nova second brain.

It is intentionally scoped before implementation. It does not add runtime behavior, capability authority, dashboard execution, or autonomous memory.

Detailed draft schemas and contracts live under:

```text
future/brain/second_brain/
```

The end-to-end Obsidian vault scaffold lives under:

```text
future/brain/second_brain/obsidian_vault/
```

The scaffold includes a manifest and operator runbooks, but it remains future planning only.

The future implementation handoff blueprint lives under:

```text
future/brain/second_brain/implementation_blueprint/
```

---

## Core Rule

```text
The second brain can remember, retrieve, relate, and propose.
It cannot authorize.
```

Memory and knowledge are context. They are not permission.

Execution still requires:

```text
GovernorMediator
-> Governor
-> CapabilityRegistry
-> ExecuteBoundary
-> Executor
-> Ledger / receipt
```

---

## Truth Hierarchy

The second brain must preserve this hierarchy:

```text
1. Runtime code / generated runtime docs / tests
2. Ledger receipts for execution proof
3. Reviewed second-brain knowledge entries
4. Candidate / generated knowledge entries
5. Raw captured sources
6. Visual/dashboard interpretations
```

Obsidian / Markdown can be a knowledge source.

It must not become execution proof or runtime truth.

---

## Folder Model

Recommended vault subtree:

```text
second_brain/
  raw/
    inbox/
    assets/
  knowledge/
    research/
    decisions/
    patterns/
    conversations/
    references/
    capability_logs/
  entities/
    people/
    projects/
    tools/
    capabilities/
  concepts/
  synthesis/
  proposals/
  logs/
  templates/
  indexes/
```

Rules:

- `raw/` stores source material.
- `knowledge/` stores reviewed or reviewable notes.
- `synthesis/` stores generated analysis and must default to candidate status.
- `proposals/` stores suggested writes/promotions.
- `logs/` stores second-brain operation logs, not execution receipts.
- `indexes/` may store human-readable generated indexes; machine indexes remain rebuildable.

---

## Knowledge Entry Schema

Every second-brain note should carry YAML frontmatter with these fields:

Schema draft:

```text
future/brain/second_brain/knowledge_entry.schema.json
```

```yaml
---
id: kb_...
schema_version: 1
title: ""
entry_type: research
status: candidate
authority_label: candidate_knowledge
created_at: "2026-05-18T00:00:00Z"
updated_at: "2026-05-18T00:00:00Z"
source_refs: []
content_hash: "sha256:..."
review_state: unreviewed
reviewed_by: ""
reviewed_at: ""
confidence: medium
project_scope: ""
tags: []
relationships: []
supersedes: []
superseded_by: []
ledger_refs: []
non_authorizing: true
---
```

Allowed `entry_type` values:

```text
research
decision
pattern
conversation
reference
capability_log
entity
concept
synthesis
proposal
```

Allowed `status` values:

```text
captured
candidate
reviewed
promoted
rejected
superseded
archived
```

Allowed `authority_label` values:

```text
raw_source
candidate_knowledge
reviewed_knowledge
promoted_knowledge
runtime_truth_reference
ledger_receipt_reference
```

`non_authorizing: true` is mandatory.

---

## Relationship Schema

Relationships should be typed.

Schema draft:

```text
future/brain/second_brain/knowledge_relationship.schema.json
```

Example:

```yaml
relationships:
  - type: supports
    target: kb_decision_approval_gate
    confidence: high
    source_ref: receipt_...
```

Allowed relationship types:

```text
supports
contradicts
supersedes
derived_from
implements
blocks
depends_on
proves
cites
relates_to
```

Important boundary:

```text
proves = points to proof evidence or ledger references
authorizes = not allowed as a relationship type
```

Knowledge may cite proof. It may not become proof authority.

---

## Event Schema

Every material knowledge operation should be represented as an idempotent event:

Schema draft:

```text
future/brain/second_brain/knowledge_event.schema.json
```

```json
{
  "event_id": "kbevt_...",
  "seq": 1,
  "schema_version": 1,
  "occurred_at": "2026-05-18T00:00:00Z",
  "event_type": "knowledge.proposed",
  "subject_type": "entry",
  "entity_id": "kb_...",
  "entity_version": 1,
  "idempotency_key": "...",
  "source": "manual",
  "actor": "nova",
  "authority_label": "candidate_knowledge",
  "receipt_ref": "",
  "payload_hash": ""
}
```

Event types:

```text
knowledge.captured
knowledge.proposed
knowledge.reviewed
knowledge.promoted
knowledge.rejected
knowledge.superseded
knowledge.tombstoned
knowledge.archived
knowledge.index_rebuilt
knowledge.search_performed
knowledge.graph_snapshot_created
```

Search/read events are optional for local privacy, but if surfaced to the dashboard they must be non-authorizing and bounded.

---

## Index Contract

The machine index is disposable.

The event store is not disposable. Knowledge events are append-only operation history and must not be erased, regenerated, or resequenced by `rebuild_index()`.

Required index behavior:

```text
rebuild_index() walks markdown files and regenerates all tables
content_hash detects changed notes
missing frontmatter fails closed into health warnings
deleted notes produce tombstones or stale index cleanup
relationships are validated against known IDs
source_refs are validated when local
index output is deterministic
```

Recommended tables:

```text
knowledge_entries
knowledge_relationships
knowledge_sources
knowledge_tombstones
knowledge_chunks
knowledge_embeddings
knowledge_health_findings
```

Append-only event storage is separate from the disposable projection tables.

Search should begin with FTS. Embeddings may be added later using local models.

---

## Read Surface

Safe first tools:

```text
knowledge.search
knowledge.get_note
knowledge.get_graph
knowledge.get_neighbors
knowledge.find_paths
knowledge.health
knowledge.export_snapshot
```

These are read-only.

Proposal-only tools:

```text
knowledge.propose_entry
knowledge.propose_relationship
knowledge.propose_promotion
knowledge.propose_tombstone
```

These create proposals, not promoted knowledge.

Promotion and tombstone review requests should carry expected entity versions and content hashes so stale reviews fail closed under concurrent agent activity.

---

## Health / Lint Checks

The first implementation should include a health report:

Contract draft:

```text
future/brain/second_brain/health_check_contract.md
```

```text
missing required frontmatter
duplicate IDs
broken wikilinks
relationships with missing targets
source refs with missing files
promoted entries without review metadata
generated synthesis marked as promoted
non_authorizing missing or false
capability logs implying permission
stale entries with no reviewed successor
index drift
orphan notes
sensitive data findings
event scope/subject mismatch
stale review targets
tombstones missing prior hash or reason
```

Health checks should be safe to run often and should not modify files unless a future reviewed repair mode is explicitly approved.

---

## Living Dashboard Graph

The living dashboard graph is a visualization of second-brain events and graph state.

It is not the second brain itself.

The intended experience is that the graph looks alive:

```text
soft neuron-like nodes
synaptic relationship edges
electric pulses traveling along edges
subtle idle breathing glow
bounded bursts for search, save, review, conflict, and reasoning activity
```

This alive visual layer is presentation only. It must not imply approval, execution permission, certification, lock status, runtime truth, or ledger proof.

Contract draft:

```text
future/brain/second_brain/living_dashboard_visual_contract.md
```

Recommended mapping:

```text
knowledge entry -> neuron node
relationship -> synaptic edge
knowledge event -> visual intention
event seq -> replay checkpoint
```

Entry colors:

```text
research -> blue
decision -> gold
pattern -> green
conversation -> purple
reference -> white
capability_log -> red/orange
```

Animation states:

```text
idle breathing glow with sparse ambient pulses
search pulse radiating toward ranked matches
new knowledge flash with edge arcs to linked entries
review / promotion glow
reasoning cascade across active subgraph
conflict warning pulse between contradicting nodes
stale / superseded dimming
critical health warning pulse
```

Robustness requirements:

```text
sequence-numbered WebSocket events
last_seq replay on reconnect
idempotent frontend event application
priority queue of visual intentions
animation budget
per-node effect throttle
per-edge effect throttle
frustum/visibility culling
instanced rendering or THREE.Points for scale
per-instance category color and pulse attributes
single selective bloom pipeline
```

Do not implement this before the graph snapshot and event feed exist.

---

## Promotion Path

Before this becomes runtime:

```text
1. Create reviewed priority lock.
2. Add schemas.
3. Add tests for non-authorizing invariants.
4. Add lint / health report.
5. Add deterministic rebuildable index.
6. Add read-only query surface.
7. Add event feed / replay.
8. Add proposal-only writes.
9. Add dashboard visualization.
10. Regenerate runtime docs only after code exists.
```

---

## Non-Goals

```text
no autonomous mutation
no hidden learning
no execution authority
no external writes
no browser/computer-use expansion
no OpenClaw expansion
no approval inferred from notes
no receipt replacement
no dashboard surface treated as authority
```

---

## Current Status

Planning only.

Do not claim Nova has a live second brain until implementation, tests, receipts/health output, and generated runtime truth support that claim.
