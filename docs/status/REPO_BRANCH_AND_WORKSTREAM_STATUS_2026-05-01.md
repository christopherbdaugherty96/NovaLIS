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
| PR #68 Daily Brief MVP | `nova_backend/src/brief/daily_brief.py` (662 lines), `tests/brief/test_daily_brief.py` (76 tests), `general_chat_runtime.py` helpers | Deterministic on-demand session brief, 11 sections. Non-authorizing frozen dataclass. Live weather via WeatherService, calendar via CalendarSkill local ICS, email placeholder. No new capability, no LLM calls, no Governor path. |
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
| Brain planning preview | PR #64 merged; Task Understanding, Task Envelope, Simple Task Mode, RunManager, Run Preview are planning-only scaffolds | Scaffold |
| Daily Brief MVP | PR #68 merged; on-demand deterministic brief; 11 sections; live weather + calendar; no new capability | Implemented |
| Search Evidence Synthesis | Merged via PR #66 as deterministic Cap 16 evidence metadata | Implemented |
| Memory loop (Stage 3) | PR #82 merged 2026-05-02; remember/review/update/forget/why-used with receipts; MEMORY_LOOP_PROOF.md PASS | Implemented |
| Context Pack (Stage 4) | PR #83 merged 2026-05-02; live-wired into general_chat_runtime.py; CONTEXT_PACK_PROOF.md PASS | Implemented |
| Brain discipline / trace (Stage 5) | PRs #85/#87/#88/#89 merged 2026-05-02; 7 mode contracts, classify_mode(), BrainTrace, Context Pack wired; BRAIN_MODE_PROOF.md PASS | Implemented |
| RoutineGraph v0 (Stage 6) | PR #93 merged 2026-05-03; RoutineBlock/RoutineGraph/RoutineRun/RoutineReceipt; DAILY_BRIEF_GRAPH; 60 tests | Implemented |
| Plan My Week routine (Stage 6) | PR #98 merged 2026-05-03; WeeklyPlan/PlanMyWeekProposal/PlanApprovalRecord; two-phase runner; 52 tests | Implemented |
| Cost posture metadata | PR #99 merged 2026-05-03; cost_posture field on all 27 caps; registry validation; governance matrix column; 24 tests; metadata only | Implemented |
| Google connector | Future read/context connector direction; no Google OAuth/Gmail/Calendar/Drive runtime connector | Planning |
| Free-first cost governance | Design docs merged; cost posture metadata implemented (step 1 of N); no runtime enforcement yet | Step 1 done |
| Auralis website coworker | Future business workflow / production discipline layer | Planning |
| YouTubeLIS | Planning-only tool folder and docs/templates | Planning |
| E-commerce / operator planning | Future planning only unless runtime truth proves otherwise | Not started |
| OpenClaw | Governed/constrained execution surface; hardening audit exists; expansion frozen until envelope/guard/receipt gaps closed | Scaffold / constrained |
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

## Next Work Order (as of 2026-05-03)

Items 1–4 from the original 2026-05-01 list are complete. Current priority order:

1. Doc/status cleanup — fix stale wording where planning-as-runtime or local-only language remains.
2. Plan Google read-only connector foundation — design-only planning doc after connector governance
   is clear; no runtime connector, no OAuth, no Gmail API access.
3. Keep OpenClaw expansion frozen until envelope issuance, real approval decisions, centralized
   execution guard, boundary detection, and receipts exist.
4. Do not start new write/action capabilities in this sprint.
