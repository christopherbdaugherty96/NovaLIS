# Second Brain Event Replay Contract

Status: future planning / not runtime truth.

This contract defines the future sequence-numbered event model for second-brain sync and living dashboard replay.

---

## Goals

```text
idempotent event application
safe reconnect after disconnect
deterministic graph snapshot recovery
clear separation between domain events and visual effects
```

---

## Event Sequence

Each event has:

```text
seq
event_id
idempotency_key
subject_type
entity_id
entity_version
scope_id
payload_hash
```

Rules:

```text
seq is monotonic
event_id is globally unique
idempotency_key prevents duplicate application
payload_hash detects accidental mutation
entity_version increments per knowledge entity when subject_type is entry or relationship
scope_id identifies vault/index/search/snapshot scope for global events
```

Sequence allocation must be atomic. A future implementation should allocate `seq` inside the append-only event-store transaction under a single-writer lock.

---

## Reconnect Flow

```text
client connects
client sends last_seq
server compares last_seq to replay buffer
if replay is available:
  server sends missed events
else:
  server sends snapshot_required
  client requests graph snapshot
client resumes from snapshot.max_seq
```

---

## Domain Events vs Visual Intentions

Backend emits domain events:

```text
knowledge.proposed
knowledge.promoted
knowledge.rejected
knowledge.tombstoned
knowledge.search_performed
knowledge.index_rebuilt
```

Frontend maps them to visual intentions:

```text
candidate_node_flash
promotion_glow
fade_candidate
search_pulse
index_refresh_wave
```

Backend must not emit animation instructions.

---

## Duplicate Handling

Frontend must track applied event IDs:

```text
if event_id already applied:
  update state if needed
  do not replay animation
```

This prevents reconnect replay from double-firing visual effects.

---

## Gap Handling

If the client sees a sequence gap:

```text
pause event animation
request snapshot
replace graph state
resume from snapshot.max_seq
record non-authorizing warning
```

Do not infer missing events.

---

## Retention

Future implementation should define:

```text
event replay buffer size
maximum replay age
snapshot cadence
event compaction rules
privacy handling for search/read events
maximum events per second
slow-consumer disconnect behavior
burst coalescing rules
snapshot_required threshold
```

Search/read events may be disabled or summarized if privacy requires it.

Suggested first-budget defaults:

```text
coalesce search/read events by query/session where possible
prefer one snapshot_required message over long replay for stale clients
summarize event payloads; do not include note body text
drop visual-only replay hints before dropping domain events
keep append-only event history more durable than the WebSocket replay buffer
```

---

## Append-Only History

Knowledge events are operation history, not a rebuildable index.

Index rebuilds may emit a new `knowledge.index_rebuilt` event, but they must not erase, regenerate, or resequence historical events.

Tombstone events preserve deletion history. They should carry the prior content hash and subject metadata in the hashed payload, but they must not become execution receipts.
