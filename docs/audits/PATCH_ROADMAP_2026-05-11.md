# Audit Patch Roadmap

Status update after PR #158 and 2026-05-12 runtime-doc confirmation:

```text
P1-GOV — COMPLETE. Addressed by PR #153 and PR #154.
P1-CI  — COMPLETE. Runtime docs confirmed current 2026-05-12 (generator run on
         branch claude/review-repo-status-f2E7Q; merged into main).
This roadmap is now fully historical. Active direction: see
docs/status/FIVE_PASS_STABILITY_AND_OPERATIONAL_ROADMAP_2026-05-12.md and
docs/status/REPO_SYNC_AND_ROADMAP_UPDATE_2026-05-12.md.
```

**Date:** 2026-05-11
**Source:** PASS1_RUNTIME_AND_OPENCLAW_AUDIT_2026-05-11.md + PASS3_FULL_ALIGNMENT_AUDIT_2026-05-11.md
**Historical branch targeted by this roadmap:** audit/full-repo-doc-code-alignment

Each item below was a proposed narrow patch at the time of the audit. None are authorized to begin without a separate
reviewed priority lock unless the item is docs-only and explicitly scoped below.

---

## P1-GOV — OpenClaw freeform goal governance inspection (HIGHEST GOVERNANCE PRIORITY AT TIME OF AUDIT)

Historical outcome:

```text
PASS4 inspection merged in PR #153.
PATCH A-D hardening merged in PR #154.
```

Original audit scope retained below for historical traceability.

**Type:** governance inspection → likely fix
**Branch:** `audit/openclaw-freeform-goal-inspection`
**Source:** `PASS1_RUNTIME_AND_OPENCLAW_AUDIT_2026-05-11.md`
**Scope:** Direct inspection of the freeform goal execution path. Read and document:

1. `OpenClawAgentRunner.run_goal()` — does it filter tools against an allowlist, or does
   ThinkingLoop have unrestricted access to the full tool registry?
2. `ExecutorSkillAdapter.execute()` — does it traverse `GovernorMediator`, `Governor`,
   `CapabilityRegistry`, `SingleActionQueue`, `ExecuteBoundary`? Or does it call
   `executor.execute(request)` directly, bypassing the governed path?
3. `/api/openclaw/approve-action` — is `approval_state = auto_allowed` constrained to a
   safe subset of actions, or can it approve mutation-capable/external-write actions
   without human review?
4. Mutation-capable tool registry — confirm which tools in the ThinkingLoop registry can
   mutate state (`volume`, `brightness`, `media`, `open_webpage`, `screen_capture`, etc.)
   and verify they are blocked or properly mediated.
5. Scheduler reachability — can the freeform goal path reach the Nova scheduler and
   create/trigger recurring jobs without explicit user approval?
6. Remote bridge reachability — can the freeform goal path trigger external network calls
   beyond governed NetworkMediator scope?

**Required test artifacts (if inspection reveals live execution path):**
- Tests that attempt to call mutation-capable tools through the freeform goal path
- Assert each is rejected, or confirm which governance layer mediates it
- Document the exact traversal path with line references

**Merge gate at time of audit:** Either (a) inspection confirms path is already hard-blocked with evidence,
or (b) a hard-block patch is implemented and tested.

---

## P1-CI — Runtime docs regeneration (COMPLETE)

**Type:** generator/docs
**Historical branch in original roadmap:** `docs/regenerate-runtime-docs`
**Current status:** COMPLETE — runtime docs confirmed current 2026-05-12. Generator run on
branch `claude/review-repo-status-f2E7Q`. `CURRENT_RUNTIME_STATE.md` was already current
from PR #154. MOC artifacts refreshed (993 docs indexed). Drift check: 3 pre-existing
README warnings; no regressions. No open regeneration PR needed.

---

## P2 — Cap 16 `authority_scope` field in registry.json

**Type:** registry metadata (docs-equivalent)
**Branch:** `fix/cap16-authority-scope-registry`
**Scope:** Add explicit `"authority_scope": "suggest"` to Cap 16 entry in
`nova_backend/src/config/registry.json`. No routing change. No behavior change.
Makes the implicit dataclass default explicit.
**Files:** `nova_backend/src/config/registry.json` (Cap 16 entry, ~line 71)
**Merge gate:** Existing registry tests pass. Capability count unchanged.

---

## P2 — OpenClaw deprecated direct-run path inspection

**Type:** governance inspection → possible fix
**Branch:** `fix/openclaw-deprecated-direct-run-hardblock` (only if hard-block needed)
**Scope:** Read `nova_backend/src/api/openclaw_agent_api.py` lines 20–80. Determine
whether the `OPENCLAW_DEPRECATED_DIRECT_RUN` flag-off branch truly prevents execution or
only logs. If execution can still occur: add a hard-block `raise` or `return` before any
execution path. If already blocked: add a comment confirming it.
**Files:** `nova_backend/src/api/openclaw_agent_api.py` lines 24, 45
**Merge gate:** Inspection confirms no execution possible when flag is off.
**Note:** This is an inspection first. A patch branch is only needed if the inspection
reveals a live execution path.

---

## P3 — Stale status doc labels

**Type:** docs-only
**Branch:** `docs/stale-status-doc-labels`
**Scope:** Two targeted edits only:

1. `docs/status/TRUST_REVIEW_CARD_MVP_STATUS_2026-05-07.md` — update status line to
   reflect that the MVP closeout review exists and the workstream is closed. Add:
   `Status: CLOSED — see TRUST_REVIEW_CARD_MVP_CLOSEOUT_REVIEW_2026-05-07.md`

2. `docs/status/WORKFLOW_STAGE_ROADMAP_2026-05-02.md` — add at the top of the file:
   `Superseded by: docs/status/OPENCLAW_PRIORITY_LOCK_CLOSEOUT_2026-05-06.md and
   subsequent closeout docs. This is a historical snapshot dated 2026-05-02.`

**Files:** The two docs above only.
**Merge gate:** No new content added. No claims changed. Labels only.

---

## P4 — Google connector future docs labeling pass

**Type:** docs-only
**Branch:** `docs/google-connector-planning-labels`
**Scope:** Read the ~6 Google connector future docs that were not individually verified:

- `docs/future/GOOGLE_CONNECTOR_IMPLEMENTATION_ROADMAP.md`
- `docs/future/NOVA_GOOGLE_ACCOUNT_AND_CONNECTOR_ONBOARDING_PLAN.md`
- `docs/future/NOVA_GOOGLE_CONNECTOR_DIRECTION_FINAL_LOCK_2026-04-26.md`
- `docs/future/NOVA_MCP_GOVERNED_CONNECTOR_PLAN_2026-04-27.md`

For each: verify a planning-only status line is present in the first 5 lines. If missing,
add: `Status: planning only — no runtime Google connector exists.`

Special case: `NOVA_GOOGLE_CONNECTOR_DIRECTION_FINAL_LOCK_2026-04-26.md` — the word "Lock"
in the filename could be confused with a priority lock. Add a clarifying note to line 1–3
if not already present: `This is a planning direction record, not a governance priority lock.`

**Files:** The docs listed above only.
**Merge gate:** No capability expansion. No runtime claims added.

---

## P5 — Full websocket+conversation test suite run (verification, not a patch)

**Type:** verification
**Branch:** none needed — run on main or next implementation branch
**Scope:** Run `python -m pytest tests/websocket/ tests/conversation/ -q` from
`nova_backend/`. Verify the count is at or above 536 (the count cited in the Everyday UX
closeout doc). Document the result.
**Note:** This is a sanity check before the next implementation PR, not a blocker for the
audit branch itself.

---

## Historical ordering recommendation

```text
1. P1-GOV (openclaw freeform goal inspection)
2. P1-CI (docs/regenerate-runtime-docs)
3. P3 (docs/stale-status-doc-labels)
4. P2a (fix/cap16-authority-scope-registry)
5. P4 (docs/google-connector-planning-labels)
6. P5 (test verification)
```

P1-GOV is historically complete via PR #153/#154. P1-CI is complete as of 2026-05-12. This
roadmap is now fully historical.

---

## What This Roadmap Does Not Authorize

- No runtime capability changes
- No new capabilities
- No OpenClaw expansion
- No browser/computer-use expansion
- No external writes
- No autonomous workflows
- No Cap 64 P5
- No Google connector runtime implementation
- No UI simplification implementation
- No Personality Layer MVP implementation

Each implementation patch (beyond the docs/registry items above) requires its own reviewed
priority lock before work begins.
