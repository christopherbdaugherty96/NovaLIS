# Slice 8 - Living Dashboard Graph

Status: future implementation blueprint / not runtime truth.

## Goal

Render the second brain as a living graph after real graph snapshots and event replay exist.

## Suggested Runtime Files

```text
nova_backend/static/second_brain/*
Nova-Frontend-Dashboard/*
nova_backend/tests/*dashboard*
```

## Visual Stack

```text
vanilla JavaScript
3d-force-graph
Three.js ShaderMaterial or Points
selective bloom pipeline
lightweight edge pulse trails
```

## Alive Effects

```text
idle breathing glow
electric search pulses
new knowledge flash
review / promotion glow
reasoning cascade
conflict warning pulse
stale dimming
critical health warning pulse
```

## Performance Requirements

```text
instanced rendering or THREE.Points
single shader/material family where possible
per-node and per-edge cooldowns
animation budget
frustum/visibility culling
large-graph sampling
snapshot_required for stale clients
```

## Governance Requirements

```text
dashboard does not mutate vault
dashboard does not imply approval
dashboard does not imply execution permission
dashboard does not imply certification or lock status
visual prominence is not status
```
