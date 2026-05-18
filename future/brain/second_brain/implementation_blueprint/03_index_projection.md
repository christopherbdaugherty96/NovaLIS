# Slice 3 - Deterministic Index Projection

Status: future implementation blueprint / not runtime truth.

## Goal

Build a deterministic, rebuildable machine projection from Markdown files.

## Suggested Runtime Files

```text
nova_backend/src/second_brain/index_store.py
nova_backend/tests/second_brain/test_index_store.py
```

## Projection Tables

```text
knowledge_entries
knowledge_relationships
knowledge_sources
knowledge_tombstones
knowledge_health_findings
knowledge_entries_fts
```

## Separate Append-Only Store

```text
knowledge_events
```

`knowledge_events` is not disposable projection state. `rebuild_index()` must not erase, regenerate, or resequence historical event rows.

## Determinism Rule

```text
same files + same config -> same projection rows + same health findings
```

## Required Tests

```text
deterministic rebuild
deleted note produces cleanup or tombstone
event store survives rebuild
content hash drift detected
invalid frontmatter creates health finding
broken relationships create health finding
source Markdown is not mutated
```
