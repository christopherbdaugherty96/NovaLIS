# Nova Canonical Truth — Index

Last assembled: 2026-07-08.

This folder is a thin **navigation and reconciliation layer**. It does not hold new facts.
Each file summarizes one kind of truth and links to the real source docs, generated runtime
files, or tests that back it. When a canonical file and its source disagree, **the source
wins** — these files can go stale; the generated runtime docs and the code cannot.

## Authority order (highest first)

1. Running code and tests in `nova_backend/`.
2. Generated runtime truth: [`../current_runtime/CURRENT_RUNTIME_STATE.md`](../current_runtime/CURRENT_RUNTIME_STATE.md)
   (marked "Manual edits: NOT PERMITTED").
3. Canonical + hand-maintained truth docs (this folder and the sources it points to).
4. Design, planning, and archive material (intent and history, never runtime authority).

## The seven truths

| # | File | Question it answers |
| --- | --- | --- |
| 01 | [01_PROJECT_TRUTH.md](01_PROJECT_TRUTH.md) | What is Nova *intended* to be? |
| 02 | [02_RUNTIME_TRUTH.md](02_RUNTIME_TRUTH.md) | What works *now*? |
| 03 | [03_GOVERNANCE_TRUTH.md](03_GOVERNANCE_TRUTH.md) | What is *enforced in code*? |
| 04 | [04_CAPABILITY_TRUTH.md](04_CAPABILITY_TRUTH.md) | Which capabilities exist, their state and maturity? |
| 05 | [05_FRONTEND_BACKEND_TRUTH.md](05_FRONTEND_BACKEND_TRUTH.md) | How is the code laid out, front and back? |
| 06 | [06_TEST_AND_PROOF_TRUTH.md](06_TEST_AND_PROOF_TRUTH.md) | What evidence exists, and how current is it? |
| 07 | [07_ROADMAP_TRUTH.md](07_ROADMAP_TRUTH.md) | What is next, and what gates it? |
| 08 | [08_ARCHIVE_POLICY.md](08_ARCHIVE_POLICY.md) | What counts as historical, and how it is treated. |

## Label vocabulary used across these files

- **runtime-backed** — asserted by generated runtime truth or a passing test.
- **current** — hand-maintained and reviewed recently; treat as living but not generated.
- **unverified** — claimed but not yet proven by observed evidence or a test.
- **superseded** — replaced by a newer doc; kept for history.
- **historical** — a record of a past state; never a statement about today.

## Relationship to existing entry points

This folder does not replace the existing navigation docs — it sits above them:

- [`../INDEX.md`](../INDEX.md) — goal-based router into the full docs set.
- [`../../REPO_MAP.md`](../../REPO_MAP.md) — engineer navigation for code and docs.
- [`../FULL_DOCUMENTATION_MAP.md`](../FULL_DOCUMENTATION_MAP.md) — deep discoverability map.
