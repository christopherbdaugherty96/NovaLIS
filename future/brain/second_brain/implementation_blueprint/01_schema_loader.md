# Slice 1 - Schema Loader

Status: future implementation blueprint / not runtime truth.

## Goal

Load and validate the schema files in:

```text
future/brain/second_brain/
```

## Suggested Runtime Files

```text
nova_backend/src/second_brain/__init__.py
nova_backend/src/second_brain/schemas.py
nova_backend/tests/second_brain/test_schemas.py
```

## Responsibilities

```text
load knowledge_entry.schema.json
load knowledge_relationship.schema.json
load knowledge_event.schema.json
validate frontmatter objects
validate embedded relationships
validate event envelopes
return structured validation errors
```

## Must Not Do

```text
read arbitrary vault files
mutate notes
invoke Executor
invoke OpenClaw
infer approval
```

## Required Tests

```text
valid knowledge entry passes
missing non_authorizing fails
non_authorizing false fails
promoted without review metadata fails
candidate with reviewed_at "" passes
promoted with reviewed_at "" fails
authorizes relationship type fails
proves relationship without source_ref or ledger_ref fails
entry event without entity_id fails
index/search/snapshot event without scope_id fails
```
