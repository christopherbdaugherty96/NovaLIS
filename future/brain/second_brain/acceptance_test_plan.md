# Second Brain Acceptance Test Plan

Status: future planning / not runtime truth.

These are the tests a future implementation should add before claiming any second-brain runtime behavior.

---

## Schema Tests

```text
valid knowledge entry passes
missing non_authorizing fails
non_authorizing false fails
promoted without approved review_state fails
promoted without reviewed_by fails
promoted without reviewed_at fails
candidate with blank reviewed_at passes
promoted without source_refs or ledger_refs fails
synthesis cannot be runtime_truth_reference
unknown relationship type fails
authorizes relationship type fails
proves relationship without source_ref or ledger_ref fails
invalid event seq fails
entry event without entity_id fails
index/search/snapshot event without scope_id fails
duplicate idempotency key fails
placeholder template IDs fail health checks
placeholder content hashes fail health checks
fixture hashes fail outside scaffold mode
```

---

## Index Tests

```text
rebuild_index is deterministic
valid markdown creates index rows
invalid frontmatter creates health finding
broken wikilink creates health finding
missing relationship target creates health finding
deleted note is removed or tombstoned
tombstone preserves previous content hash
tombstone preserves deletion reason
content hash changes after note edit
index does not mutate source markdown
event store is not erased by rebuild_index
```

---

## Retrieval Tests

```text
search is read-only
graph query is read-only
graph snapshot includes boundedness and freshness metadata
export snapshot includes redaction and omission metadata
candidate knowledge is labeled candidate in results
runtime truth references sort above candidate knowledge
stale promoted entry surfaces warning
conflicting entries surface warning
knowledge retrieval cannot call Executor
knowledge retrieval cannot call OpenClaw
```

---

## Event Tests

```text
events are monotonic by seq
seq allocation is atomic under concurrent writers
duplicate event_id is idempotent
duplicate idempotency_key is idempotent
sequence gap triggers snapshot_required
replay from last_seq returns only missed events
snapshot max_seq resumes stream correctly
slow clients get snapshot_required instead of unbounded replay
event bursts are coalesced without losing append-only history
domain events do not contain animation instructions
```

---

## Dashboard Contract Tests

```text
graph snapshot renders without mutating knowledge
idle state shows bounded ambient glow/pulses
search events create bounded electric edge pulses
new knowledge events flash the node and linked edges
reasoning cascade respects animation budget
duplicate replay does not double-trigger animation
large graph uses capped / sampled rendering
critical health finding appears as warning state
visual status never says authorized / certified / locked unless source truth says so
```

---

## Governance Tests

```text
second-brain note cannot grant approval
second-brain note cannot enable capability
second-brain note cannot satisfy approval gate
ledger remains proof authority
runtime generated docs remain runtime truth authority
proposal-only write does not promote without review
stale promotion target fails closed
review lease conflict fails closed
sensitive data findings block export/cloud routing
sensitive data findings block embeddings until reviewed/redacted
```
