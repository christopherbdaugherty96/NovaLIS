# Test Fixture Matrix

Status: future fixture matrix / not runtime truth.

## Fixtures

```text
valid promoted note
valid candidate note
candidate synthesis
capability log with safe status language
note missing frontmatter
note with duplicate ID
note with placeholder hash outside templates
note with fixture hash outside scaffold mode
note with broken wikilink
relationship with missing target
proves relationship without evidence
promoted note without review metadata
promoted note without source_refs or ledger_refs
event with duplicate idempotency_key
event with sequence gap
index event missing scope_id
entry event missing entity_id
proposal promotion with stale content hash
secret-like raw note
env-file raw note
large graph snapshot
slow event consumer
```

## Fixture Location

Future implementation should keep executable test fixtures under:

```text
nova_backend/tests/fixtures/second_brain/
```

The current Obsidian vault scaffold is documentation/test inspiration only.
