# Second Brain Acceptance Gate

Status: future implementation gate / not runtime truth.

The future Second Brain workstream should not claim runtime completion until all gates below pass.

---

## Required Proof

```text
schema tests pass
health/lint tests pass
deterministic index rebuild tests pass
read-only query tests pass
context bridge non-authorizing tests pass
append-only event replay tests pass
proposal-only write tests pass
dashboard contract tests pass if dashboard slice exists
generated runtime docs updated only after code exists
```

---

## Required Negative Proof

```text
second-brain note cannot grant approval
second-brain note cannot satisfy approval gate
second-brain note cannot enable capability
retrieval cannot call Executor
retrieval cannot call OpenClaw
proposal writes cannot call external systems
dashboard cannot mutate vault
dashboard cannot certify capability status
```

---

## Required Artifacts

```text
health report sample
index rebuild proof
query response samples
event replay proof
proposal stale-write proof
dashboard screenshot / browser proof if visual slice exists
```
