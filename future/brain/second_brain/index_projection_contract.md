# Second Brain Index Projection Contract

Status: future planning / not runtime truth.

The second-brain machine index is a projection of Markdown files. It is disposable and must be rebuildable.

Knowledge events are different: they are append-only operation history. They are not part of the disposable projection and must not be erased by index rebuilds.

---

## Core Rule

```text
Markdown is the knowledge source.
The index is acceleration and validation.
```

If the database and Markdown disagree, the Markdown files win unless health checks prove the files are invalid.

---

## Required Rebuild Behavior

Future `rebuild_index()` behavior:

```text
1. Walk configured second-brain vault roots.
2. Parse Markdown frontmatter.
3. Validate entries against knowledge_entry.schema.json.
4. Parse wikilinks and typed relationships.
5. Compute content hashes.
6. Rebuild all projection tables in a transaction.
7. Emit a health report.
8. Emit a new append-only knowledge.index_rebuilt event through the event store.
```

Rebuild must be deterministic:

```text
same files + same content -> same index rows + same health findings
```

---

## Suggested Tables

```sql
knowledge_entries(
  id text primary key,
  path text not null unique,
  title text not null,
  entry_type text not null,
  status text not null,
  authority_label text not null,
  review_state text not null,
  confidence text not null,
  project_scope text not null,
  created_at text not null,
  updated_at text not null,
  content_hash text not null,
  non_authorizing integer not null check(non_authorizing = 1),
  body_text text not null
);

knowledge_tombstones(
  id text primary key,
  former_path text not null default '',
  deleted_at text not null,
  deleted_by text not null,
  previous_content_hash text not null default '',
  reason text not null default ''
);

knowledge_relationships(
  source_id text not null,
  target_id text not null,
  relationship_type text not null,
  confidence text not null,
  source_ref text not null default '',
  note text not null default '',
  primary key(source_id, target_id, relationship_type, source_ref)
);

knowledge_sources(
  entry_id text not null,
  source_ref text not null,
  source_type text not null,
  source_hash text not null default '',
  primary key(entry_id, source_ref)
);
```

Append-only event store, not a disposable projection table:

```sql
knowledge_events(
  event_id text primary key,
  seq integer not null unique,
  event_type text not null,
  subject_type text not null,
  entity_id text not null default '',
  entity_version integer not null default 0,
  scope_id text not null default '',
  idempotency_key text not null unique,
  occurred_at text not null,
  authority_label text not null,
  payload_hash text not null
);
```

`rebuild_index()` must not delete, resequence, or regenerate historical event rows.

Projection health table:

```sql

knowledge_health_findings(
  finding_id text primary key,
  severity text not null,
  code text not null,
  path text not null default '',
  entry_id text not null default '',
  message text not null
);
```

FTS table:

```sql
knowledge_entries_fts(
  title,
  body_text,
  content='knowledge_entries',
  content_rowid='rowid'
);
```

Vector / embedding storage is optional and should be added after FTS and relationship traversal work.

---

## Drift Detection

The projection should detect:

```text
file changed since indexed
file missing after indexed
file tombstoned
index row missing for valid note
relationship target missing
schema version mismatch
frontmatter invalid
event sequence gap
```

Event store drift should be reported separately from projection drift. A projection rebuild can fix projection drift; it cannot rewrite history to fix event drift.

---

## Privacy Boundary

Index rows may contain local note text.

Do not send second-brain note text to cloud services unless a future Model Router / privacy setting explicitly allows it.

Local embeddings are preferred for the first semantic layer.

Sensitive-data lifecycle:

```text
scan before indexing body text
do not embed notes with critical sensitive-data findings
block export for notes with unresolved secret/private-key findings
quarantine or exclude unsafe raw files from projections
redact derived snapshots when allowed instead of leaking raw content
purge or rebuild derived chunks/embeddings after redaction
record redaction/quarantine findings in health output
```

---

## Concurrency

Event `seq` allocation must be atomic.

Future implementation should allocate sequence numbers inside the event-store write transaction, protected by SQLite write locking or an equivalent single-writer lock.

Do not allocate sequence numbers by reading `max(seq)` in userland without a transaction.

---

## Tombstone Semantics

Deleted or removed notes should not silently disappear from operational history.

Future implementation should preserve:

```text
entry id
former path
previous content_hash
deleted_at
deleted_by
deletion reason
superseding entry id when applicable
```

Tombstones are not execution receipts. They exist to keep graph/history recovery deterministic and to prevent stale links from quietly retargeting.
