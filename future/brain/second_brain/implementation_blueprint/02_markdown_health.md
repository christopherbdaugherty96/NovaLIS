# Slice 2 - Markdown Parser And Health

Status: future implementation blueprint / not runtime truth.

## Goal

Parse the Obsidian vault safely and report health without mutating files.

## Suggested Runtime Files

```text
nova_backend/src/second_brain/markdown_parser.py
nova_backend/src/second_brain/health.py
nova_backend/tests/second_brain/test_markdown_parser.py
nova_backend/tests/second_brain/test_health.py
```

## Responsibilities

```text
walk configured vault roots
parse YAML frontmatter
extract Markdown body
extract Obsidian wikilinks
extract template placeholders
validate note schema
detect duplicate IDs
detect broken wikilinks
detect missing relationship targets
detect fixture hashes outside scaffold mode
detect sensitive-data findings
emit health report
```

## Health Modes

```text
scaffold: examples allowed with warnings
strict: placeholders and fixture hashes fail outside templates
runtime: critical findings block retrieval/export/embedding
```

## Must Not Do

```text
repair files automatically
delete notes
create embeddings
send note text to cloud services
authorize execution
```
