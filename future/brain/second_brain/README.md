# Future Second Brain Schemas

Status: future planning / not runtime truth.

This folder contains implementation-ready schema and contract drafts for the future Nova second brain.

These files do not add runtime behavior. They are here so a future reviewed implementation branch can build from stable contracts instead of re-inventing field names in code.

---

## Files

- `knowledge_entry.schema.json` - frontmatter contract for second-brain Markdown notes.
- `knowledge_relationship.schema.json` - typed relationship object embedded in entries and index rows.
- `knowledge_event.schema.json` - idempotent event contract for knowledge operations and future dashboard replay.
- `index_projection_contract.md` - rebuildable SQLite / DuckDB projection contract.
- `event_replay_contract.md` - reconnect, replay, and snapshot rules.
- `api_contract.md` - future read-only and proposal-only API/MCP surface.
- `health_check_contract.md` - lint / health checks required before runtime promotion.
- `living_dashboard_visual_contract.md` - visualization contract for the future Three.js living brain surface.
- `governance_threat_model.md` - authority drift, prompt injection, stale knowledge, and dashboard risk model.
- `implementation_backlog.md` - ordered future implementation slices.
- `implementation_blueprint/` - module-by-module future implementation handoff specs.
- `templates/` - draft Markdown frontmatter templates.
- `OBSIDIAN_VAULT_END_TO_END.md` - end-to-end vault scaffold guide.
- `obsidian_vault/` - complete future Obsidian vault template.
- `acceptance_test_plan.md` - future implementation test matrix.

The vault template includes a manifest and runbooks:

```text
obsidian_vault/VAULT_MANIFEST.md
obsidian_vault/RUNBOOK_CAPTURE_REVIEW_PROMOTE.md
obsidian_vault/RUNBOOK_HEALTH_LINT.md
obsidian_vault/RUNBOOK_LIVING_GRAPH.md
```

The implementation blueprint starts at:

```text
implementation_blueprint/README.md
```

---

## Boundary

```text
Knowledge is context.
Knowledge is not authority.
Visualization is visibility.
Visualization is not authority.
```

The current authoritative planning document is:

```text
future/brain/SECOND_BRAIN_FOUNDATION.md
```
