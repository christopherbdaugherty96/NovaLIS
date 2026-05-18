# Slice 4 - Read-Only Query Surface

Status: future implementation blueprint / not runtime truth.

## Goal

Expose read-only query functions over the projection.

## Suggested Runtime Files

```text
nova_backend/src/second_brain/query.py
nova_backend/tests/second_brain/test_query.py
```

## Operations

```text
knowledge.search
knowledge.get_note
knowledge.get_graph
knowledge.get_neighbors
knowledge.find_paths
knowledge.health
knowledge.export_snapshot
```

## Required Response Metadata

```text
non_authorizing
projection_version
max_seq
health_state
warnings
truncated
omitted_count
redaction_applied
```

## Must Not Do

```text
mutate vault files
emit proposal writes
call Executor
call OpenClaw
grant approval
send external requests
```
