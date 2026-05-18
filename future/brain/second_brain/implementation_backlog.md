# Second Brain Implementation Backlog

Status: future planning / not runtime truth.

This backlog is intentionally ordered so Nova builds the durable foundation before the living dashboard.

---

## Slice 0 - Activate Priority Lock

```text
[ ] Review proposed priority lock.
[ ] Confirm it does not conflict with active approval-gate lock.
[ ] Decide whether first slice is docs/schema only or code/test.
```

---

## Slice 1 - Schema Validation

```text
[ ] Add schema loader.
[ ] Validate knowledge_entry.schema.json.
[ ] Validate knowledge_relationship.schema.json.
[ ] Validate knowledge_event.schema.json.
[ ] Add tests for non_authorizing true.
[ ] Add tests for blocked relationship type "authorizes".
[ ] Add tests for promoted-without-review failure.
[ ] Add tests for reviewed_at blank before review and strict date-time after promotion.
[ ] Add tests for entry-scoped and vault/index-scoped events.
```

Suggested write scope:

```text
nova_backend/src/second_brain/schemas.py
nova_backend/tests/second_brain/test_schemas.py
```

---

## Slice 2 - Markdown Parser / Health Report

```text
[ ] Parse YAML frontmatter.
[ ] Extract body text.
[ ] Extract wikilinks.
[ ] Validate required fields.
[ ] Produce health report.
[ ] Add no-mutation tests.
```

Suggested write scope:

```text
nova_backend/src/second_brain/markdown_parser.py
nova_backend/src/second_brain/health.py
nova_backend/tests/second_brain/test_health.py
```

---

## Slice 3 - Deterministic Index

```text
[ ] Add SQLite/DuckDB projection.
[ ] Implement rebuild_index().
[ ] Store entries, relationships, sources, tombstones, and health findings as projection data.
[ ] Keep knowledge_events in a separate append-only event store.
[ ] Add FTS table.
[ ] Add deterministic rebuild tests.
[ ] Add index drift tests.
[ ] Add tombstone drift/recovery tests.
```

Suggested write scope:

```text
nova_backend/src/second_brain/index_store.py
nova_backend/tests/second_brain/test_index_store.py
```

---

## Slice 4 - Read-Only Query Surface

```text
[ ] Implement search.
[ ] Implement get_note.
[ ] Implement get_graph.
[ ] Implement get_neighbors.
[ ] Implement find_paths.
[ ] Implement health query.
[ ] Include snapshot/export boundedness and redaction metadata.
[ ] Prove queries are read-only.
```

Suggested write scope:

```text
nova_backend/src/second_brain/query.py
nova_backend/tests/second_brain/test_query.py
```

---

## Slice 5 - ContextPack Integration

```text
[ ] Convert search results to ContextItem shape.
[ ] Preserve authority_label.
[ ] Preserve candidate/stale/conflict warnings.
[ ] Ensure retrieval remains planning-only.
```

Suggested write scope:

```text
nova_backend/src/brain/context_pack.py
nova_backend/src/second_brain/context_bridge.py
nova_backend/tests/second_brain/test_context_bridge.py
```

---

## Slice 6 - Event Feed

```text
[ ] Implement KnowledgeEvent store.
[ ] Add atomic monotonic sequence allocation.
[ ] Add replay from last_seq.
[ ] Add snapshot_required on gap.
[ ] Add slow-consumer and event-burst coalescing behavior.
[ ] Add duplicate idempotency tests.
```

Suggested write scope:

```text
nova_backend/src/second_brain/events.py
nova_backend/tests/second_brain/test_events.py
```

---

## Slice 7 - Proposal-Only Writes

```text
[ ] propose_entry creates candidate note/proposal.
[ ] propose_relationship creates candidate relationship proposal.
[ ] propose_promotion creates review item.
[ ] propose_tombstone creates deletion/tombstone review item.
[ ] promotion requires explicit review state.
[ ] promotion requires expected entity version and content hash.
[ ] stale review targets fail closed.
[ ] writes emit knowledge events.
[ ] no proposal path reaches execution.
```

Suggested write scope:

```text
nova_backend/src/second_brain/proposals.py
nova_backend/tests/second_brain/test_proposals.py
```

---

## Slice 8 - Living Dashboard Graph

Prerequisites:

```text
[ ] get_graph is implemented.
[ ] event replay is implemented.
[ ] dashboard receives sequence-numbered events.
[ ] performance budget is accepted.
```

Implementation:

```text
[ ] Add vanilla JS graph view.
[ ] Use 3d-force-graph / Three.js.
[ ] Render entries as glowing neuron nodes.
[ ] Render relationships as synaptic edges.
[ ] Add electric edge pulses for search/save/review activity.
[ ] Add subtle idle breathing glow.
[ ] Add bounded reasoning cascade visual.
[ ] Add visual intention queue.
[ ] Add animation budget.
[ ] Add per-node and per-edge effect cooldowns.
[ ] Add reconnect replay.
[ ] Add no-authority UI copy tests.
```

Suggested write scope:

```text
nova_backend/static/*
Nova-Frontend-Dashboard/*
nova_backend/tests/*dashboard*
```

Do not start this slice before data/event slices exist.
