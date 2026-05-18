# Living Graph

Status: future visualization map / not runtime truth.

The living graph should make the second brain look alive without implying authority.

## Visual Model

```text
knowledge entry -> glowing neuron node
relationship -> synaptic edge
knowledge event -> visual intention
event seq -> replay checkpoint
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

## Boundary

Visual intensity, centrality, glow, and pulse frequency do not mean approved, certified, locked, executable, or true.

## Scaffold Artifacts

- [[_MOCs/LIVING_GRAPH.canvas]]
- [[indexes/living_graph_mock_snapshot.json]]
- [[logs/living_graph_event_stream_example.json]]
- [[indexes/living_graph_visual_intentions.json]]

## Color Mapping

```text
research -> blue pulses
decision -> gold pulses
pattern -> green pulses
conversation -> purple pulses
reference -> white pulses
capability_log -> red/orange pulses
proposal / synthesis -> purple candidate glow
```

## Implementation Boundary

Use these artifacts as mock inputs for a future Three.js / 3d-force-graph implementation only after the data layer, graph snapshot endpoint, and append-only event feed exist in runtime code.
