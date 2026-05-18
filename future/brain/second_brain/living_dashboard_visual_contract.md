# Living Dashboard Visual Contract

Status: future planning / not runtime truth.

This document defines the future living-brain dashboard visualization contract.

It does not authorize dashboard implementation. It exists to prevent the visual layer from drifting away from the data, event, and governance model.

---

## Principle

```text
The graph visualizes knowledge.
It does not create knowledge.
It does not authorize action.
```

The intended visual effect is a living neural graph:

```text
knowledge entries look like softly glowing neuron nodes
relationships look like synaptic connections
knowledge activity appears as electric pulses moving along edges
the graph breathes subtly when idle
searches, saves, reviews, and conflicts create bounded visible activity
```

The "alive" look is presentation only. It must never imply approval, execution, certification, or runtime truth.

---

## Data Inputs

The visual layer may consume:

```text
graph_snapshot
knowledge_event
health_summary
search_result_trace
```

It must not directly read or mutate vault files.

---

## Graph Snapshot Shape

```json
{
  "schema_version": 1,
  "snapshot_id": "kgshot_...",
  "created_at": "2026-05-18T00:00:00Z",
  "projection_version": "kgproj_...",
  "max_seq": 1,
  "truncated": false,
  "omitted_node_count": 0,
  "omitted_edge_count": 0,
  "sampling_strategy": "none",
  "redaction_applied": false,
  "health_state": "ok",
  "nodes": [
    {
      "id": "kb_...",
      "label": "Approval Gate Decision",
      "entry_type": "decision",
      "status": "promoted",
      "authority_label": "promoted_knowledge",
      "health": "ok"
    }
  ],
  "edges": [
    {
      "source": "kb_...",
      "target": "kb_...",
      "type": "supports",
      "confidence": "high"
    }
  ]
}
```

---

## WebSocket Replay Contract

Required future behavior:

```text
client opens knowledge graph stream
client sends last_seq
server sends missed events or snapshot_required
client applies events idempotently
duplicate event_id does not replay animation twice
gap in seq triggers snapshot refresh
```

---

## Visual Intention Queue

Raw events map to visual intentions.

Examples:

```text
idle heartbeat -> ambient_breathing_glow
knowledge.search_performed -> search_pulse
knowledge.proposed -> candidate_node_flash
knowledge.promoted -> promotion_glow
knowledge.rejected -> fade_candidate
knowledge.superseded -> dim_old_node
health finding critical -> warning_pulse
```

Each intention should carry:

```text
intention_id
source_event_id
priority
created_at
ttl_ms
node_ids
edge_ids
effect_type
```

Visual intentions should support:

```text
edge pulse direction
pulse color by entry type
glow intensity
arc intensity
decay curve
cooldown key
budget cost
```

Alive-state requirements:

```text
idle: low-intensity breathing glow plus occasional sparse pulses
search: pulses radiate from query or matched nodes to ranked results
new knowledge: node flash plus electric edge pulses to linked entries
review/promotion: warmer sustained glow that decays into normal state
reasoning/cascade: rapid but budgeted pulses across the active subgraph
conflict: contained warning pulse between contradicting nodes
stale/superseded: dimmed node with low-frequency cool pulse
critical health: warning state that is visible but not alarm-spammy
```

---

## Performance Budget

Future implementation should enforce:

```text
instanced rendering or THREE.Points for nodes
single shader/material family where possible
per-instance category color and pulse attributes
edge pulse uniforms or lightweight particle trails
animation budget for high-cost effects
per-node effect cooldown
per-edge effect cooldown
visibility/frustum culling for particles and arcs
snapshot downsampling for very large graphs
selective bloom only for event highlights
no double-glow pipeline
```

---

## Governance Boundary

The dashboard may display:

```text
knowledge status
review state
health findings
source refs
ledger refs
candidate vs promoted distinction
```

The dashboard must not imply:

```text
approval
execution permission
capability certification
runtime truth
ledger proof replacement
```

If the graph shows capability logs, the UI must preserve the distinction between:

```text
capability discussed
capability implemented
capability active
capability certified
capability locked
```
