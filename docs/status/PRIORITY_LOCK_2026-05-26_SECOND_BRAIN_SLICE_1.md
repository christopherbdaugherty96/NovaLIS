# Priority Lock - 2026-05-26 Second Brain Slice 1

Status: proposed / ready for review.

This lock authorizes review of the first Second Brain implementation slice only.
It does not authorize implementation until this lock is reviewed and accepted.

---

## 1. Current Truth

Current repo truth:

```text
main == origin/main
latest continuity sync: 5aeb7d9 docs: post-PR #233 continuity sync
UI simplification lane is closed.
Goal Card persistence is complete end-to-end through Phase 3.
Goal Cards remain display-only and non-executing.
No execution authority has expanded.
```

Current Second Brain truth:

```text
Second Brain / Obsidian work is future planning only.
Existing future docs define a broad long-term direction.
Existing Obsidian overlay generation is navigation-only and does not mutate source files.
No Second Brain runtime feature is currently authorized by this lock.
```

This lock narrows the existing future direction into an implementation-safe first
slice. It does not override generated runtime truth, code, tests, or capability
locks.

Reference context:

```text
docs/status/PROPOSED_PRIORITY_LOCK_2026-05-18_SECOND_BRAIN_FOUNDATION.md
docs/future/NOVA_SECOND_BRAIN_OBSIDIAN_RESEARCH_AND_IMPLEMENTATION_PLAN_2026-05-18.md
future/brain/second_brain/OBSIDIAN_VAULT_END_TO_END.md
scripts/generate_obsidian_overlay.py
_MOCs/HOME.md
```

---

## 2. Problem

Nova now has a clearer governed product surface, but its durable local knowledge
substrate remains future planning. The repo needs a small, reviewable first
slice that makes Markdown/Obsidian knowledge parseable and lintable without
turning notes into memory authority, auto-learning, hidden execution, or a
runtime write path.

The risk to avoid:

```text
knowledge source -> memory authority
notes -> permission
lint -> repair/mutation
index -> runtime truth
graph visuals -> implied approval
```

The first slice must prove that Nova can understand local knowledge files while
keeping execution authority unchanged.

---

## 3. Goal

Define and later implement Second Brain Slice 1 as:

```text
schema
frontmatter parser
wikilink extraction
vault health/lint report
read-only, file-derived, rebuildable knowledge indexing scaffold if needed
no-mutation guarantees
non-authorizing tests
```

The goal is to let Nova inspect and structure local knowledge safely.

The goal is not to make Nova learn silently, edit the vault, promote memory,
query a vector database, expose MCP tools, visualize a living graph, or connect
knowledge to execution.

---

## 4. Authorized Scope

Future implementation under this lock may include only:

```text
KnowledgeEntry schema
Relationship schema
KnowledgeEvent schema
frontmatter parser
wikilink extraction
vault health/lint report
read-only knowledge indexing scaffold if strictly file-derived and rebuildable
tests proving no mutation
tests proving knowledge cannot authorize execution
tests proving notes are context, not permission
documentation of the implemented boundaries
```

Read-only knowledge indexing scaffold means:

```text
derived from files
deterministically rebuildable
safe to delete and regenerate
not a vector database
not a persistent authority store
not an event feed
not a runtime permission source
not exposed through API or MCP in Slice 1
```

The implementation may inspect Markdown and frontmatter. It may report health
findings. It must not repair, rewrite, normalize, promote, or edit vault files.

---

## 5. Explicit Non-Goals

Slice 1 must not include:

```text
no vector database
no MCP tool
no REST/API query surface
no dashboard living graph
no graph visualization runtime
no auto-learning
no memory promotion
no proposal writes
no Obsidian auto-editing
no autonomous vault mutation
no vault repair mode
no generated synthesis promotion
no append-only event store runtime
no ContextPack integration
no GovernorMediator changes
no CapabilityRegistry changes
no ExecuteBoundary changes
no execution integration
no scheduler
no background watcher
no OpenClaw integration
no browser/computer-use expansion
no external writes
no capability_locks.json changes
no generated runtime-doc claim before code/tests exist
```

Later slices may revisit some read/query/proposal/dashboard ideas only through
separate reviewed priority locks and design docs.

---

## 6. Authority Boundary

Required boundary language:

```text
Obsidian can help Nova understand.
Obsidian cannot authorize Nova to act.
Knowledge is context, not permission.
Notes are a knowledge source, not execution proof.
Read-only parsing is allowed.
Silent learning is prohibited.
Vault mutation is prohibited in Slice 1.
Any future write/proposal layer requires a separate priority lock and design doc.
```

Additional invariants:

```text
Memory cannot authorize execution.
Receipts prove events; notes do not.
The ledger remains proof authority.
Generated runtime docs remain runtime truth authority.
Execution still requires GovernorMediator, Governor, CapabilityRegistry,
ExecuteBoundary, and receipts where applicable.
```

The Second Brain may improve context assembly later. It must never become a
parallel permission system.

---

## 7. Files Allowed To Change In The Future Implementation PR

Future implementation PRs under this lock may modify only a narrow file set.

Allowed implementation areas:

```text
nova_backend/src/brain/second_brain/
nova_backend/tests/brain/second_brain/
docs/status/SECOND_BRAIN_SLICE_1_CLOSEOUT_*.md
docs/PROOFS/Second-Brain/
docs/future/NOVA_SECOND_BRAIN_OBSIDIAN_RESEARCH_AND_IMPLEMENTATION_PLAN_2026-05-18.md
future/brain/second_brain/
```

Allowed support files only if strictly necessary:

```text
pyproject.toml
requirements*.txt
scripts/check_second_brain_*.py
```

Only these existing runtime/governance files may be touched, and only for
negative tests or import guards, not integration:

```text
nova_backend/tests/governance/
nova_backend/tests/adversarial/
```

Explicitly disallowed in the Slice 1 implementation PR:

```text
nova_backend/src/governor/
nova_backend/src/governance/
nova_backend/src/executor/
nova_backend/src/openclaw/
nova_backend/src/capabilities/
capability_locks.json
nova_backend/static/
Nova-Frontend-Dashboard/
docs/current_runtime/
```

Generated runtime docs may be updated only after implementation exists and a
runtime-doc generation path explicitly requires it. This lock itself does not
authorize generated runtime-doc edits.

---

## 8. Required Tests

Future implementation must include tests proving:

```text
KnowledgeEntry schema requires non-authorizing posture.
Relationship schema cannot express authorization.
KnowledgeEvent schema cannot become an execution receipt or ledger substitute.
Frontmatter parser reads Markdown without modifying files.
Wikilink extraction reads links without modifying files.
Vault health/lint reports findings without repairing files.
No Slice 1 code imports GovernorMediator.
No Slice 1 code imports CapabilityRegistry.
No Slice 1 code imports ExecuteBoundary or executors.
No Slice 1 code imports OpenClaw runtime modules.
No Slice 1 code writes to vault Markdown files.
No Slice 1 code opens network connections.
No Slice 1 code schedules background work.
No Slice 1 code exposes MCP, REST, WebSocket, or dashboard surfaces.
Notes are context, not permission.
Obsidian cannot authorize Nova to act.
Knowledge entries cannot satisfy approval, confirmation, capability lock,
ledger, or receipt requirements.
```

Test fixtures should include:

```text
valid knowledge entry
missing frontmatter
duplicate IDs
broken wikilinks
relationship to missing target
note claiming to authorize an action
note claiming to prove execution without ledger reference
generated/candidate note that must remain non-authorizing
```

The test suite should include at least one no-mutation assertion that records
file hashes or mtimes before and after parser/lint execution.

---

## 9. Exit Criteria

This priority lock can close only after a reviewed implementation PR proves:

```text
schemas exist for KnowledgeEntry, Relationship, and KnowledgeEvent
parser extracts frontmatter and wikilinks
health/lint report is read-only and no-mutation
optional index scaffold, if included, is file-derived and rebuildable
tests pass
tests prove knowledge cannot authorize execution
tests prove notes are context, not permission
tests prove no GovernorMediator / CapabilityRegistry / ExecuteBoundary /
  OpenClaw integration
docs distinguish implemented behavior from future plans
no generated runtime truth is claimed before implementation and tests exist
```

Out of scope for closing this lock:

```text
vector search
MCP tools
proposal writes
vault mutation
dashboard graph
runtime execution integration
```

---

## 10. Final Verdict

Second Brain Slice 1 is approved for review as a lock-first, code-second
workstream.

Authorized next action:

```text
review this priority lock
```

Not authorized by this branch:

```text
implement Slice 1 code
add runtime integrations
add write paths
add APIs or MCP tools
add dashboard visualization
expand execution authority
```

The intended implementation direction is:

```text
less hidden memory
more inspectable local knowledge
zero new authority
```

This preserves Nova's core rule:

```text
Intelligence is not authority.
Knowledge is context, not permission.
```
