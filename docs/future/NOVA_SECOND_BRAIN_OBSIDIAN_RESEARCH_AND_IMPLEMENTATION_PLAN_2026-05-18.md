# Nova Second Brain / Obsidian Research And Implementation Plan - 2026-05-18

Status: future planning / not runtime truth.

This document records the GitHub research pass for a Nova second brain, plus the improvement plan it implies.

It does not authorize implementation, capability expansion, dashboard redesign, autonomous execution, external writes, or runtime behavior changes. Current generated runtime docs and code remain authoritative.

---

## Core Position

Nova's second brain should be:

```text
file-first Obsidian / Markdown knowledge layer
-> deterministic rebuildable local index
-> read-only MCP / REST query surface
-> review-gated proposal and promotion flow
-> optional dashboard visualization after data/events exist
```

It should not be:

```text
self-authorizing memory
autonomous vault mutation
hidden learning
execution authority
replacement for the ledger
runtime truth
```

Permanent rule:

```text
Knowledge helps Nova reason.
Governance still decides.
Execution still requires Governor / CapabilityRegistry / ExecuteBoundary / receipts.
```

---

## Research Sources

| Project | Relevant Pattern | Nova Takeaway |
| --- | --- | --- |
| [NicholasSpisak/second-brain](https://github.com/NicholasSpisak/second-brain) | `raw/ -> wiki/ -> index/log` LLM Wiki structure; setup / ingest / query / lint skills | Use raw source separation, maintained wiki pages, operation log, and a vault health command. |
| [kytmanov/obsidian-llm-wiki-local](https://github.com/kytmanov/obsidian-llm-wiki-local) | Local Ollama-first wiki compiler; draft rejection and retry loop | Keep ingestion local-first and reviewable; rejection should teach future compiles. |
| [obra/knowledge-graph](https://github.com/obra/knowledge-graph) | SQLite, FTS5, local embeddings, graph traversal, PageRank, community detection, MCP | Use graph analytics and local index projections, not ad hoc file search. |
| [sspaeti/obsidian-note-taking-assistant](https://github.com/sspaeti/obsidian-note-taking-assistant) | DuckDB/VSS, backlinks, hidden semantic connections, graph-boosted search | Combine lexical, semantic, and graph ranking. |
| [Epistates/turbovault](https://github.com/epistates/turbovault) | Obsidian-flavored Markdown parser, multi-vault support, atomic writes, MCP tools | Treat Markdown parsing, frontmatter, wikilinks, and atomic writes as first-class concerns. |
| [aaronsb/obsidian-mcp-plugin](https://github.com/aaronsb/obsidian-mcp-plugin) | MCP access to vault graph through semantic operations | Expose graph-aware read tools instead of raw file-only access. |
| [eugeniughelbur/obsidian-second-brain](https://github.com/eugeniughelbur/obsidian-second-brain) | Rich command vocabulary: save, ingest, synthesize, reconcile, export, daily, task, decision | Useful command taxonomy, but Nova should review-gate and avoid autonomous rewrite behavior. |
| [huytieu/COG-second-brain](https://github.com/huytieu/COG-second-brain) | Agent-facing Markdown conventions and Git-backed vault operation | Keep agent instructions explicit and version-controlled. |
| [voidashi/obsidian-vault-template](https://github.com/voidashi/obsidian-vault-template) | Controlled hierarchy, properties/tags, MOCs, templates, Dataview-friendly organization | Avoid folder sprawl; use properties and typed MOCs. |
| [vieiraae/obsidian-sidekick](https://github.com/vieiraae/obsidian-sidekick) | AI sidekick can run tools and modify files from Obsidian | Cautionary example: powerful in-vault tools need Nova governance and receipts. |

---

## Borrowed Patterns To Adopt

### 1. Source / Knowledge Separation

Use separate folders for source material, curated knowledge, generated synthesis, and logs:

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

Raw source notes should be immutable or append-only where possible. Curated knowledge can be edited after review. Generated synthesis starts as candidate/proposed knowledge, not promoted truth.

### 2. File-First Truth

Markdown files and YAML frontmatter are the durable knowledge source.

SQLite, DuckDB, FTS, vector indexes, graph projections, and dashboard snapshots are derived projections. They must be rebuildable from files.

Knowledge events are different. They are append-only operation history and must not be erased, regenerated, or resequenced by index rebuilds.

### 3. Review-Gated Promotion

Use a lifecycle:

```text
captured
-> candidate
-> reviewed
-> promoted
-> superseded / archived / rejected
```

Rejected knowledge is not junk. It should preserve the rejection reason so Nova avoids repeating bad summaries, unsafe plans, or stale conclusions.

### 4. Typed Relationships

Use typed relationships instead of generic links:

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

This is especially important for Nova because "proves", "implements", and "authorizes" must never be blurred. A note can cite or summarize a receipt, but the ledger remains proof authority.

### 5. Graph-Aware Search

Queries should combine:

```text
FTS / keyword score
semantic similarity
relationship distance
recency / freshness
authority label
review status
project scope
source reliability
```

Use reciprocal rank fusion or a similarly inspectable combiner. Avoid opaque "closest vector wins" behavior for governance-sensitive answers.

### 6. Vault Health / Lint

Add a second-brain health command before visualization:

```text
broken wikilinks
duplicate IDs
missing required frontmatter
orphan notes
unreviewed generated synthesis
stale claims
index drift
notes without source references
relationships pointing to missing nodes
promoted entries without review metadata
capability logs implying authority
```

### 7. MCP / REST Read Surface

Expose graph-aware, read-only query tools first:

```text
knowledge.search
knowledge.get_note
knowledge.get_graph
knowledge.get_neighbors
knowledge.find_paths
knowledge.health
knowledge.export_snapshot
```

Write-like operations should begin as proposal-only:

```text
knowledge.propose_entry
knowledge.propose_relationship
knowledge.propose_promotion
```

No second-brain write should imply execution authority.

---

## Nova-Specific Robustness Requirements

### Required Knowledge Entry Fields

Every knowledge entry should carry:

```text
id
schema_version
title
entry_type
status
authority_label
created_at
updated_at
source_refs
content_hash
review_state
reviewed_by
reviewed_at
confidence
project_scope
tags
relationships
supersedes
superseded_by
ledger_refs
non_authorizing
```

`non_authorizing: true` should be mandatory for second-brain entries.

### Event Model

Every material change should emit or record an idempotent knowledge event:

```text
event_id
seq
schema_version
occurred_at
event_type
subject_type
entity_id
entity_version
scope_id
idempotency_key
source
actor
authority_label
receipt_ref
payload_hash
```

Entity-scoped events use `entity_id` and `entity_version`. Vault, index, search, and snapshot events use `scope_id` so the event store does not need fake note IDs.

The future dashboard visualization should subscribe to these events, not mutate knowledge directly.

### Index Contract

The indexer must support:

```text
full rebuild
incremental update
content hash drift detection
tombstones / deleted note handling
frontmatter validation
relationship validation
source reference validation
deterministic output
separate append-only event history
```

Sensitive-data handling must happen before export, embeddings, or cloud routing:

```text
scan raw and curated notes before indexing body text
block embeddings/export for secrets, private keys, env files, or credential-like values
redact or omit sensitive content in snapshots
purge/rebuild derived chunks and embeddings after redaction
report quarantine/redaction state through health findings
```

---

## Living Brain Dashboard Direction

The dashboard idea is strong, but it should be phase-gated behind the data and event layer.

The target aesthetic is explicitly alive, like a neural system responding to Nova's knowledge activity:

```text
soft glowing neuron nodes
synaptic relationship edges
electric pulses traveling along edges
subtle idle breathing
bounded bursts for searches, saves, reviews, conflicts, and reasoning cascades
```

This is visual feedback only. Glow, centrality, pulse intensity, or animation frequency must never imply approval, execution authority, capability certification, lock status, runtime truth, or ledger proof.

Recommended visual model:

```text
each knowledge entry = glowing neuron node
each relationship / backlink = synaptic edge
knowledge events = visual intentions
event sequence = replayable animation feed
```

Entry colors:

| Entry type | Color |
| --- | --- |
| Research | Blue |
| Decisions | Gold |
| Patterns | Green |
| Conversations | Purple |
| References | White |
| Capability logs | Red / orange |

Animation states:

```text
idle: low ambient glow and sparse pulses
search: pulses radiate from query node to matches
new knowledge: new node flash plus edge arcs to linked entries
review / promotion: warm sustained glow that decays into normal state
reasoning: short-lived cascade across relevant subgraph
conflict: contained warning pulse between contradicting nodes
stale knowledge: dimmed / cool pulse
critical health: visible warning pulse without effect spam
```

Robust visual rules:

```text
visual events are interpretations of raw knowledge events
frontend replay must be idempotent
events use sequence numbers
reconnect sends last_seq and receives missed events / snapshot
high-cost effects are throttled
nodes use instanced rendering / shader attributes
edges use lightweight pulse trails or shader uniforms
category color and pulse state are per-instance attributes
bloom is selective, not doubled with fake glow
large graphs degrade to clustered / sampled view
visual overload degrades gracefully before frame rate collapses
```

Library recommendation:

```text
3d-force-graph for vanilla JS graph rendering
Three.js ShaderMaterial or Points for large node sets
single selective bloom pipeline for special events
```

Do not build the living view as the first runtime slice. Build the event/index layer first, then render real data.

---

## Phased Build Plan

### Phase 0 - Priority Lock / Scope

Create a reviewed second-brain priority lock before runtime implementation.

Allowed:

```text
docs
schemas
tests
read-only index prototypes
non-authorizing lint / validation
```

Blocked until separately authorized:

```text
dashboard runtime implementation
new execution capabilities
external writes
scheduled autonomous mutation
OpenClaw expansion
browser/computer-use expansion
```

### Phase 1 - Schema And Lint

Implement schemas and validation before storage behavior:

```text
KnowledgeEntry schema
KnowledgeRelationship schema
KnowledgeEvent schema
frontmatter validator
vault health report
tests for authority boundary fields
```

### Phase 2 - File-First Index

Implement deterministic index:

```text
vault walker
frontmatter parser
wikilink parser
relationship parser
SQLite / DuckDB projection
rebuild_index()
drift report
```

### Phase 3 - Retrieval

Implement read-only search:

```text
FTS search
relationship traversal
graph-neighbor query
RRF ranking
optional local embeddings
ContextPack integration
```

### Phase 4 - Event Feed

Implement idempotent knowledge events:

```text
monotonic seq
event replay buffer
snapshot endpoint
last_seq reconnect flow
typed events
tests for duplicate replay
```

### Phase 5 - Proposal-Only Writes

Implement safe write proposals:

```text
propose_entry
propose_relationship
propose_promotion
review queue
rejection records
receipt / ledger linkage
```

### Phase 6 - Living Brain Visualization

Implement dashboard visualization after real graph/event data exists:

```text
graph snapshot
WebSocket event subscription
priority visual-intention queue
animation budget
instanced rendering
visibility culling
boundedness/redaction metadata
desktop/mobile visual QA
```

---

## Acceptance Criteria Before Runtime Claim

Nova cannot claim a live second brain until:

```text
code exists
tests exist
runtime path is non-authorizing
knowledge cannot grant execution authority
index is rebuildable from markdown
lint catches broken links / schema drift
read APIs are bounded and inspectable
write path is proposal/review-gated
events are idempotent and replayable
event history survives index rebuilds
snapshots/export report truncation and redaction
stale proposal reviews fail closed
generated runtime docs reflect the feature
current docs distinguish implemented vs planned behavior
```

Draft schemas and contracts for this plan live in:

```text
future/brain/second_brain/
```

The complete future Obsidian vault scaffold lives in:

```text
future/brain/second_brain/obsidian_vault/
```

The scaffold includes `VAULT_MANIFEST.md` and operator runbooks for capture/review/promotion, health/lint, and the future living graph.

---

## Current Recommendation

Do not start with the 3D dashboard.

Start with:

```text
1. second-brain priority lock
2. schema / frontmatter contract
3. health/lint command
4. deterministic index rebuild
5. read-only search / graph APIs
6. event ledger
7. proposal-only writes
8. living graph visualization
```

That sequence gives Nova a more powerful brain without weakening its strongest differentiator: governed local-first execution with visible authority boundaries.
