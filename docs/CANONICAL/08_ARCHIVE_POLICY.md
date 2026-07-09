# 08 — Archive Policy (what is historical)

**Status: current.** This is the policy for how historical material is treated across the docs
tree.

## Principle

Preserve history; never let it masquerade as current truth. Old docs are moved, labelled, and
kept — not deleted and not rewritten to look cleaner than the past actually was.

## What belongs in `docs/archive/`

- Superseded truth/canonical documents (older "Nova Truth" and blueprint versions).
- Closed-phase working docs (phase 1 / 2 / 3 / 3.5 / 4 design and status material).
- Old audits and one-off reviews that a newer doc has replaced.
- Orphaned drafts and specifications for capabilities that have since shipped.

See [`../archive/README.md`](../archive/README.md) for the folder's own non-authority statement.

## What must NOT be archived

- Generated runtime truth (`docs/current_runtime/`).
- The live product-definition, capability-inventory, roadmap, and status sources cited by the
  canonical files in this folder.
- **Evidence artifacts** — proof packets, demo captures, and live-verification records stay in
  place. They are dated history, not stale docs; archiving them would break the audit trail.
  See [06_TEST_AND_PROOF_TRUTH.md](06_TEST_AND_PROOF_TRUTH.md).

## Rules

- **Move, do not delete.** Deletion is reserved for content that is provably a duplicate and
  safe to drop.
- **Label in place.** Historical docs should carry, or live under a README that carries, a clear
  "not runtime authority" statement.
- **Update inbound links** when a file moves, so navigation docs do not rot.
- **Do not rewrite history** to improve appearances.
- **Do not run a mass archival sweep while runtime code is being edited on the same branch.**
  Docs cleanup and runtime work belong on separate branches, merged deliberately.

## Applied in this pass (2026-07-08)

Moved to archive (documented intent: `docs/todo/DOC_CLEANUP.md`):

- `docs/AUDIT_ACTION_PLAN_2026-04-28.md` → `docs/archive/audits-2026-04/`
- `docs/SANITY_AUDIT_2026-04-28.md` → `docs/archive/audits-2026-04/`
- `docs/SECOND_PASS_OVERVIEW_2026-04-28.md` → `docs/archive/audits-2026-04/`
- `docs/Governed Web Intelligence (Capability 16 + 48 Integration).txt` → `docs/archive/`
- `docs/Governed Webpage Launch Capability Specification.txt` → `docs/archive/`

Remaining archival candidates are listed as the next cleanup pass in `docs/todo/DOC_CLEANUP.md`.
