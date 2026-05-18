# Second Brain Foundation Planning Packet - 2026-05-18

Status: planning packet complete / not active runtime work.

This packet records the completed documentation and contract pass for a future Nova second-brain foundation.

It does not activate the workstream.

The active priority remains governed by:

```text
.agent_context/current_priority.md
docs/status/ACTIVE_PRIORITY_LOCK_2026-05-15_APPROVAL_GATE_WIRING.md
```

---

## Completed Planning Artifacts

Research and implementation plan:

```text
docs/future/NOVA_SECOND_BRAIN_OBSIDIAN_RESEARCH_AND_IMPLEMENTATION_PLAN_2026-05-18.md
```

Future foundation:

```text
future/brain/SECOND_BRAIN_FOUNDATION.md
```

Proposed priority lock:

```text
docs/status/PROPOSED_PRIORITY_LOCK_2026-05-18_SECOND_BRAIN_FOUNDATION.md
```

Schema and contract folder:

```text
future/brain/second_brain/
```

Included contracts:

```text
knowledge_entry.schema.json
knowledge_relationship.schema.json
knowledge_event.schema.json
index_projection_contract.md
event_replay_contract.md
api_contract.md
health_check_contract.md
living_dashboard_visual_contract.md
governance_threat_model.md
implementation_backlog.md
implementation_blueprint/
acceptance_test_plan.md
OBSIDIAN_VAULT_END_TO_END.md
obsidian_vault/
obsidian_vault/VAULT_MANIFEST.md
obsidian_vault/RUNBOOK_CAPTURE_REVIEW_PROMOTE.md
obsidian_vault/RUNBOOK_HEALTH_LINT.md
obsidian_vault/RUNBOOK_LIVING_GRAPH.md
templates/
```

---

## Research Summary

The research pass reviewed current GitHub patterns around:

```text
LLM Wiki
Obsidian second brains
local-first Markdown knowledge bases
MCP vault access
SQLite / DuckDB graph and search projections
AI-assisted vault maintenance
living graph / semantic graph surfaces
```

The strongest reusable pattern for Nova is:

```text
raw sources
-> reviewed Markdown knowledge
-> rebuildable local index
-> read-only query APIs
-> proposal-only writes
-> append-only event replay
-> dashboard visualization
```

---

## Boundary Summary

The planning packet preserves:

```text
knowledge is not authority
memory is not permission
ledger remains proof authority
generated runtime docs remain runtime truth
events are append-only history, not disposable projections
proposals fail closed on stale version/hash
visualization is visibility only
all writes start as proposal/review-gated
dashboard comes after data/events
```

---

## Completion Definition

This planning pass is complete when:

```text
[x] research findings are documented
[x] Nova-specific architecture plan exists
[x] proposed priority lock exists
[x] schema drafts exist
[x] health/lint contract exists
[x] index projection contract exists
[x] event replay contract exists
[x] living dashboard visual contract exists
[x] governance threat model exists
[x] implementation backlog exists
[x] implementation blueprint exists
[x] acceptance test plan exists
[x] end-to-end Obsidian vault scaffold exists
[x] vault manifest and operator runbooks exist
[x] future docs point to the packet
```

---

## Next Correct Step

Do not implement runtime behavior from this packet until a reviewed priority lock is active.

When active, start with:

```text
Slice 1 - Schema Validation
Slice 2 - Markdown Parser / Health Report
Slice 3 - Deterministic Index
```

Only after those should Nova add read APIs, event replay, proposal writes, or the living dashboard graph.
