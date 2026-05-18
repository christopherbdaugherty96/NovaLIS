# Slice 7 - Proposal-Only Writes

Status: future implementation blueprint / not runtime truth.

## Goal

Support reviewed candidate changes without autonomous mutation of promoted knowledge.

## Suggested Runtime Files

```text
nova_backend/src/second_brain/proposals.py
nova_backend/tests/second_brain/test_proposals.py
```

## Operations

```text
knowledge.propose_entry
knowledge.propose_relationship
knowledge.propose_promotion
knowledge.propose_tombstone
```

## Required Guards

```text
proposal artifacts write only to proposals/ or review queue
promotion requires approved review metadata
promotion requires expected entity version
promotion requires expected content hash
stale review target fails closed
review lease conflict fails closed
proposal writes do not invoke execution
proposal writes emit append-only knowledge events
```

## Boundary

Proposal writes may change future knowledge state after review. They cannot approve actions, enable capabilities, or write to external systems.
