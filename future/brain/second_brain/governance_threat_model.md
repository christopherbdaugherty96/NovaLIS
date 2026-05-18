# Second Brain Governance Threat Model

Status: future planning / not runtime truth.

This document records specific failure modes that a Nova second brain must avoid.

---

## Core Asset

The protected asset is Nova's authority boundary:

```text
Knowledge must never become permission.
```

---

## Threats

### T1 - Memory As Authorization

Risk:

```text
A note says "user approved X", and runtime treats the note as approval.
```

Required control:

```text
Only approval-gate / ledger state may satisfy execution approval.
Second-brain notes may cite approval receipts but cannot replace them.
```

### T2 - Candidate Knowledge Treated As Truth

Risk:

```text
Generated synthesis is included in planning as confirmed fact.
```

Required control:

```text
Every context item carries authority_label.
Candidate knowledge must be visibly labeled and lower-ranked.
```

### T3 - Autonomous Vault Mutation

Risk:

```text
An agent rewrites promoted knowledge without review.
```

Required control:

```text
All writes start as proposals.
Promotion requires explicit review state.
Health checks flag generated synthesis marked as promoted.
```

### T4 - Ledger Replacement

Risk:

```text
Obsidian notes become treated as execution proof.
```

Required control:

```text
Ledger remains proof authority.
Knowledge entries may carry ledger_refs only as references.
```

### T5 - Dashboard Authority Drift

Risk:

```text
Living graph UI makes a capability look certified/approved because it glows or appears central.
```

Required control:

```text
Dashboard labels must distinguish discussed / implemented / active / certified / locked.
Visual prominence is not status.
```

### T6 - Prompt Injection Through Notes

Risk:

```text
Raw clipped content contains instructions to the agent.
```

Required control:

```text
Raw sources are untrusted.
Context renderer labels raw/candidate content.
Future prompt assembly must quote source content as data, not instructions.
```

### T7 - Stale Knowledge

Risk:

```text
Old roadmap or status notes override generated runtime truth.
```

Required control:

```text
Runtime truth references rank higher than second-brain notes.
Stale entries surface warnings.
Generated runtime docs remain authoritative.
```

### T8 - Silent Sensitive Data Spread

Risk:

```text
Credentials, personal data, or private business data become indexed, embedded, exported, or sent to a cloud model.
```

Required control:

```text
Sensitive data scanner before indexing/export.
Local embeddings by default.
Cloud model routing requires future explicit privacy policy.
Health checks flag possible secrets, private keys, credential-like values, and env files.
```

### T9 - Event Replay Double Effects

Risk:

```text
Frontend reconnect replays events and doubles visual animations, making activity look larger than it was.
```

Required control:

```text
Frontend tracks event_id/idempotency_key.
Duplicate events update state but do not replay animation.
```

### T10 - Index Drift

Risk:

```text
SQLite/vector index disagrees with Markdown source.
```

Required control:

```text
Health check detects drift.
Rebuild index from Markdown.
Markdown source wins.
```

---

## Required Governance Tests

Future implementation must prove:

```text
note cannot approve execution
candidate cannot override runtime truth
promoted knowledge requires review metadata
health check flags authority drift
retrieval cannot call Executor
retrieval cannot call OpenClaw
dashboard cannot mutate vault
event replay is idempotent
raw source prompt injection is labeled as data
sensitive data findings block export/cloud routing
```
