# Slice 5 - Context Bridge

Status: future implementation blueprint / not runtime truth.

## Goal

Convert second-brain retrieval results into planning-only context items.

## Suggested Runtime Files

```text
nova_backend/src/second_brain/context_bridge.py
nova_backend/tests/second_brain/test_context_bridge.py
```

## Context Item Requirements

```text
source_label: second_brain
authority_label preserved
status preserved
review_state preserved
why_selected included
warnings included
non_authorizing true
```

## Ranking Bias

```text
runtime_truth_reference above promoted knowledge
promoted above reviewed
reviewed above candidate
candidate above raw source
stale/conflicted entries visibly warned
```

## Boundary

Context helps planning. It does not authorize execution.
