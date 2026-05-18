# Vault Manifest

Status: future scaffold manifest / not runtime truth.

This manifest records what is intentionally present in this Obsidian vault scaffold.

---

## Scaffold Mode

This vault is a template and fixture set.

Some example notes use schema-valid fixture hashes such as:

```text
sha256:1111111111111111111111111111111111111111111111111111111111111111
```

Those hashes are not production content hashes. A future health command should allow them only in scaffold/test mode and flag them outside scaffold mode.

Templates intentionally use:

```text
kb_REPLACE_ID
REPLACE_TITLE
REPLACE_WITH_SHA256_HASH
```

Those placeholders are allowed in `templates/` and should fail health checks if copied into non-template notes.

---

## Required Top-Level Files

```text
README.md
00_START_HERE.md
VAULT_MANIFEST.md
```

---

## Required Maps

```text
_MOCs/HOME.md
_MOCs/REVIEW_QUEUE.md
_MOCs/GRAPH_HEALTH.md
_MOCs/LIVING_GRAPH.md
_MOCs/AUTHORITY_BOUNDARIES.md
```

---

## Required Namespaces

```text
raw/
knowledge/
entities/
concepts/
synthesis/
proposals/
logs/
templates/
indexes/
```

---

## Required Template Coverage

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
tombstone_review
```

---

## Required Example Coverage

```text
promoted research example
promoted decision example
promoted concept example
promoted capability boundary example
candidate synthesis example
candidate living graph proposal
living graph mock snapshot
living graph mock event stream
living graph visual intention mapping
living graph canvas
mock health report
mock search results
mock export snapshot
schema validation slice proposal
health/index slice proposal
```

---

## Implementation Handoff Coverage

The build-ready future implementation handoff lives outside the vault at:

```text
future/brain/second_brain/implementation_blueprint/
```

It covers:

```text
schema loader
markdown parser and health report
deterministic index projection
read-only query surface
context bridge
append-only event feed
proposal-only writes
living dashboard graph
acceptance gate
test fixture matrix
```

---

## Link Conventions

Use both:

```text
Obsidian wikilinks for human navigation
schema relationship target IDs for machine graph edges
```

Example:

```text
See [[knowledge/decisions/kb_decision_file_first_event_first_foundation]]

relationships:
  - type: supports
    target: kb_decision_file_first_event_first_foundation
```

Do not treat wikilinks alone as typed relationships. The indexer may parse them as weak links, but typed relationships live in frontmatter.
