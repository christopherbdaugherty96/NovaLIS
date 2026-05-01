# Repo Branch and Workstream Status - 2026-05-01

Status: human-maintained alignment snapshot.

This is not generated runtime truth. Code, tests, generated runtime docs, and proof artifacts win if they conflict with this note.

No remote branches were deleted during this pass.

---

## Branch Matrix

Observed after `git fetch --all --prune`, before merge commits from this pass were pushed.

| Branch | Ahead / behind vs observed `origin/main` | Category | Recommendation |
|---|---:|---|---|
| `main` | source of truth | canonical | Keep as source of truth. |
| `reconcile/search-evidence-synthesis` | ahead 4 / behind 17 | active code PR | Merged in this pass after review and validation. Safe-delete candidate after remote merge is confirmed; do not delete automatically. |
| `docs/free-first-integration-policy` | ahead 5 / behind 2 | docs-only candidate | Merged in this pass as design-layer docs. Safe-delete candidate after remote merge is confirmed; do not delete automatically. |
| `docs/auralis-website-coworker-workflow` | ahead 8 / behind 134 | already integrated / redundant | Intended paths match `main` after prior manual integration. Safe-delete candidate after user approval. |
| `integrate-youtubelis-folder` | ahead 10 / behind 318 | already merged / redundant | Intended paths match `main` after PR #65 / manual integration. Safe-delete candidate after user approval. |
| `docs/nova-agent-google-coordination-plan` | ahead 0 / behind 15 | stale / behind-only | Cleanup candidate after user approval. |
| `backup/main-before-local-sync-2026-04-30` | ahead 0 / behind 17 | backup/archive | Retain unless user explicitly approves deletion. |
| `local/wip-before-main-sync-2026-04-30` | ahead 2 / behind 86 | do-not-merge raw | Contains older Brain/Search Synthesis files plus generated docs and PID noise. Inspect only; do not merge raw. |
| `auralis/mock-lead-runner-mvp` | local branch, behind-only vs this pass | local worktree / redundant | Behind current alignment state; cleanup candidate only after user approval. |
| `claude/adoring-ramanujan-2c80f6` | local worktree branch, behind-only vs this pass | local worktree artifact | Do not delete automatically; classify as cleanup candidate if user confirms no unique local work is needed. |
| `claude/elegant-mendel-da6069` | local worktree branch at observed `origin/main` | local worktree artifact | Behind after this pass; cleanup candidate only after user approval. |

---

## Merged In This Pass

| Item | Files / scope | Runtime claim |
|---|---|---|
| PR #66 Search Evidence Synthesis | `nova_backend/src/brain/search_synthesis.py`, `nova_backend/src/executors/web_search_executor.py`, focused tests | Implemented as deterministic Cap 16 evidence structuring. No new capability, no authorization, no Governor bypass, no new external action path. |
| Free-first integration policy docs | `docs/design/DESIGN_AUTHORITY.md`, Phase 6 cost-governance docs | Design policy only. Runtime enforcement does not exist until registry metadata, generator output, tests, and UI/proof paths exist. |
| Human status alignment | status, todo, roadmap, Brain, product, Google, and index docs | Documentation alignment only. No generated runtime docs were manually edited. |

---

## Open / Retained

| Item | Status |
|---|---|
| Backup branch | Retained unless user approves deletion. |
| Redundant Auralis / YouTubeLIS branches | Marked safe-delete candidates only; no deletion executed. |
| Local WIP branch | Do-not-merge raw. Its valuable Brain/Search Synthesis/Cap 64 content appears represented by PR #64, PR #66, and prior Cap 64 test work; ignore PID/generated-doc noise. |

---

## Workstream Status

| Workstream | Status | Label |
|---|---|---|
| Runtime / governance | Governor-mediated runtime with 27-capability generated truth as the authoritative source | Implemented |
| Brain planning preview | PR #64 merged; Task Understanding, Task Envelope, Simple Task Mode, RunManager, and Run Preview are planning-only | Scaffold |
| Search Evidence Synthesis | Merged in this pass as deterministic Cap 16 evidence metadata | Implemented |
| Google connector | Future read/context connector direction; no Google OAuth/Gmail/Calendar/Drive runtime connector | Planning |
| Free-first cost governance | Design docs merged; metadata and visibility planned | Planning |
| Auralis website coworker | Future business workflow / production discipline layer | Planning |
| YouTubeLIS | Planning-only tool folder and docs/templates | Planning |
| E-commerce / operator planning | Future planning only unless runtime truth proves otherwise | Not started |
| OpenClaw | Governed/constrained execution surface; not broad autonomy | Scaffold / constrained |
| Personality / agent model | Design discussion and docs | Planning |
| Active screen command layer | Design discussion and docs | Planning |

---

## Do Not Overstate

- Search Evidence Synthesis structures evidence already collected by governed web search. It does not search, browse, authorize, or add a capability.
- Brain Planning Preview is planning-only. It does not execute, authorize, route through Governor, or call OpenClaw.
- Google docs describe a future read/context connector. Cap 64 remains local `mailto:` draft only and must never call Gmail API.
- Free-first is not runtime-enforced until registry metadata, generator output, tests, and UI/proof surfaces prove it.
- Auralis is not an autonomous website builder and has no publish/deploy/domain/DNS/client-send authority.
- YouTubeLIS has no upload/publish/account automation.
- OpenClaw future expansion must require Run, Task Envelope, Governor, capability checks, ExecuteBoundary, and receipts.

---

## Next Merge / Work Order

1. Push this alignment branch to `main` after validation.
2. Re-run conversation/search proof against the Search Evidence Synthesis baseline.
3. Review branch cleanup candidates and delete only with explicit user approval.
4. Plan cost posture metadata as the next free-first runtime-visible step.
5. Plan Google read-only connector foundation only after connector governance and cost posture boundaries are clear.
6. Do not start write/action capabilities from this cleanup pass.
