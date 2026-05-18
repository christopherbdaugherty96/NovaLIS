# Slice 6 - Append-Only Event Feed

Status: future implementation blueprint / not runtime truth.

## Goal

Store and replay idempotent knowledge events for sync and future dashboard visualization.

## Suggested Runtime Files

```text
nova_backend/src/second_brain/events.py
nova_backend/tests/second_brain/test_events.py
```

## Required Behavior

```text
atomic monotonic seq allocation
idempotency_key uniqueness
event_id uniqueness
append-only history
replay from last_seq
snapshot_required on replay gap
slow-consumer handling
burst coalescing for WebSocket delivery
no animation instructions in backend events
```

## Subject Model

```text
entry / relationship -> entity_id + entity_version
index / search / graph_snapshot / vault -> scope_id
```

## Dashboard Boundary

The event feed emits domain events. The frontend maps those events to visual intentions.
