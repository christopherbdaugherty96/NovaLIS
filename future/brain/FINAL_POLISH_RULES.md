# Final Polish Rules

This document captures the final hardening rules for the future Brain architecture.

It is planning only. It does not change runtime behavior, active capabilities, generated runtime truth, or current Brain implementation.

---

## Core System Shape

Future Brain systems should reduce to four core objects:

```text
Signal
Plan / Envelope
Run
Record
```

If a future feature cannot be mapped to one of these objects, it should be questioned before implementation.

---

## System Loop

```text
Signal
→ Context
→ Plan
→ Trust
→ Approval
→ Run
→ Receipt
→ Memory
→ Learning
→ Back to Context
```

This loop must remain bounded, visible, and auditable.

---

## Master Rule

> If behavior cannot be explained in a receipt, it should not happen.

NovaLIS should not perform hidden actions, hidden learning, hidden memory promotion, hidden authority changes, or hidden retries.

---

## Signal Rules

Every signal must answer:

- why did this trigger?
- what is allowed next?
- what is blocked?
- what is the maximum effect?

A signal may start awareness or planning. A signal does not automatically grant execution authority.

---

## Context Rules

Context assembly must include:

- size limits
- freshness checks
- source/conflict notes
- explicit exclusion of unrelated material

If context conflicts, NovaLIS must surface uncertainty instead of silently choosing a convenient interpretation.

---

## Plan / Envelope Rules

No plan means no execution.

Every executable plan must define:

- goal
- scope
- allowed actions
- blocked actions
- stop conditions
- expected receipt

---

## Trust Rules

The trust surface must answer:

- what will happen?
- what will not happen?
- what could go wrong?
- is approval required?
- how does the user stop it?

---

## Run Rules

A run must have:

- visible start
- bounded middle
- explicit end
- stop condition
- receipt

A run must be killable in one step.

---

## Receipt Rules

Every non-trivial run receipt should include:

- what was requested
- what was approved
- what was attempted
- what was blocked
- what actually happened
- why it stopped
- whether memory/learning is suggested

---

## Memory Rules

Memory should use clear tiers:

```text
Transient
Session
Persistent
LearningRecord
```

Persistent memory requires explicit approval unless a future implemented policy says otherwise.

No silent promotion to persistent memory.

---

## Learning Rules

Learning may improve:

- clarity
- filtering
- signal quality
- explanations
- repeated failure detection

Learning may not increase:

- frequency
- risk
- scope
- authority
- permission
- account access
- execution rights

Learning suggests. The user approves. The system updates only through governed paths.

---

## Universal Hard Blocks

These actions are blocked by default across all domains unless a future explicit high-risk policy, implementation, and approval path exists:

- autonomous purchases
- autonomous publishing
- credential entry
- money movement
- account changes
- real broker/trading execution
- sending messages without approval
- deleting files without approval

Repeated success does not remove these blocks.

---

## Retry Rule

Retry is allowed only when:

- same goal
- same scope
- same risk
- known failure cause
- retry count under limit
- no blocked action occurred

Otherwise, NovaLIS must stop and ask the user.

---

## Paper Wallet Realism Rule

Any future paper-wallet simulation should be conservative by default.

Use pessimistic assumptions when uncertain:

- worse fills
- slippage included
- spread considered
- failed fills logged
- no guaranteed real-world transfer of simulated performance

---

## Final Boundary

Future Brain may plan, learn, summarize, and recommend.

Future Brain may not grant itself authority.
