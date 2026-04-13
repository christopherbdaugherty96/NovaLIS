# Nova System Audit And Productization Gaps
Date: 2026-04-10
Status: Active design audit
Scope:
- current repository state
- codebase usability and maintainability gaps
- docs truth vs contributor experience
- productization blockers before broader UX widening

Authority note:
- this is a design audit and remediation-shaping packet
- live runtime truth still belongs to `docs/current_runtime/`

## Purpose

This packet records a corrected system audit of Nova as it exists in the repository on 2026-04-10.

The goal is not to re-argue Nova's core value.

The goal is to answer a narrower question:

`What currently weakens trust, contributor clarity, and everyday usability even when the core runtime is meaningfully real?`

This audit intentionally corrects older notes that mixed:
- true structural problems
- stale claims
- repo-state assumptions that are no longer accurate

## What Was Actually Verified

The following grounded checks were run during this audit:
- runtime-doc drift check passed
- runtime-auditor tests passed
- runtime governance docs tests passed
- Phase 4 runtime-active test passed
- landing page test passed
- workspace API tests passed
- OpenClaw bridge API tests passed
- OpenClaw agent API tests passed
- runtime settings API tests passed
- Phase 8 runtime contract tests passed

Immediate remediation already applied during this audit pass:
- self-awareness now refreshes volatile runtime truth each call instead of caching the full block for 60 seconds
- calendar capability metadata in the connection registry was corrected from `56` to `57`
- root-level pytest execution was hardened so repo-root test runs can resolve `src`
- OpenClaw execution memory was moved into the existing `nova_backend/src/data/nova_state/openclaw/` runtime-state tree
- `.gitignore` was widened for common untitled canvas/base artifacts
- placeholder root/OpenClaw agent files were converted into explicit legacy stubs instead of misleading one-line debris
- mojibake in high-visibility files such as `brain_server.py` and `session_handler.py` comments was cleaned
- the frontend mirror was resynced and the sync check was extended to cover the new split JS/CSS files
- the runtime frontend was split beyond `dashboard.js` into smaller served modules and a separate surface stylesheet
- dashboard-focused tests now read the live modular frontend bundle through a shared helper instead of stale single-file assumptions
- navigation smoke now also validates required script-tag presence and modular bundle load order

This means Nova is not in a "nothing is real" state.

The deeper issue is different:
- the live system is meaningfully real
- but the repository still has clarity, workflow, and productization gaps that will slow trust and adoption

## Corrected Grounded Findings

### 1. The backend and governance spine are materially real

The repo has a substantial active backend under:
- `nova_backend/src/`
- `nova_backend/tests/`

This is not a shell project.

Key grounded strengths:
- FastAPI runtime is active through `src.brain_server:app`
- governance and runtime-truth systems are real
- runtime-doc generation and drift checking are real
- Phase 8 operator surfaces are real enough to have dedicated runtime tests
- the current runtime docs and current tests are more aligned than older audit notes implied

### 2. The repo still has contributor-trust hazards

The strongest problems found in this audit are not "the runtime is fake."

They are:
- canonical-path confusion
- residual local workflow rough edges
- legacy placeholder/stub visibility
- active-doc drift about the frontend split and mirror model
- noisy working-tree hygiene when generated artifacts are not ignored quickly

These do not fully break Nova.

They do make it harder to:
- onboard contributors
- review changes confidently
- keep the frontend coherent
- make the product feel strong instead of improvised

## Highest-Value Current Gaps

### 1. Frontend canonical-vs-mirror clarity is improved, but docs must keep pace

The repo currently documents:
- `nova_backend/static/` as the runtime-served canonical frontend
- `Nova-Frontend-Dashboard/` as a maintained mirror copy

That is a valid model only if the relationship is kept legible.

The mirror drift found earlier in this audit cycle has now been remediated.

The current sync guard covers:
- `index.html`
- `dashboard.js`
- `dashboard-config.js`
- `dashboard-workspace.js`
- `dashboard-control-center.js`
- `dashboard-chat-news.js`
- `style.phase1.css`
- `dashboard-surfaces.css`

Current remaining risk:
- older audit/design packets still describe the mirror as drifting or the frontend as mostly single-file
- contributors can still get mixed signals if they read stale design notes before the human guides
- future contributors can still regress toward single-file assumptions if new tests/docs are written without using the modular bundle contract

This is one of the biggest current productization gaps because it creates a practical contributor failure mode:
- someone edits the wrong frontend surface
- the live UI changes do not match what they expected
- the repo begins to carry two frontend stories at once

This is still a source-of-truth problem when docs lag behind reality, even though the code-level drift is currently closed.

Current correction:
- active human-guide and top-level docs now describe the modular frontend as the maintained runtime architecture
- the remaining doc debt is mostly in older historical packets, not in the main active guidance path

### 2. Root-level test execution is improved, but verification ergonomics still need to stay explicit

Nova tests import `src.*` directly.

Earlier in the audit cycle this caused repo-root failures.
That immediate problem was addressed by adding a root `conftest.py` so repo-root pytest execution can resolve `src`.

This is a real usability gap for:
- new contributors
- CI maintenance
- repeatable local verification

The current result is:
- there is a large real test suite
- and the execution ergonomics are now materially better
- but top-level contributor docs still need to keep the supported commands obvious

### 3. Legacy placeholder modules are now labeled more honestly, but still worth eventual quarantine

The repo still contains legacy placeholder files in places that look authoritative, including:
- top-level root files named after agent/openclaw components
- some `nova_backend/src/openclaw/agent_*` files

At the same time, real OpenClaw logic exists in neighboring files such as:
- `agent_runner.py`
- `agent_runtime_store.py`
- `thinking_loop.py`
- `tool_registry.py`

That mixed state creates a navigation problem:
- the codebase looks more implemented than some files really are
- and more unfinished than other files really are

This pass improved that state by converting these files into explicit legacy stubs with clear intent.

Remaining gap:
- decide whether to archive/delete them entirely or keep them as compatibility markers with stronger contributor notes

### 4. Working-tree hygiene is better, but should keep tightening around generated artifacts

The audit found:
- untracked canvas/base artifacts in the repo root
- `.gitignore` patterns that do not fully cover the file names actually being generated

This matters more than it sounds like.

A dirty tree full of low-signal artifacts makes it harder to:
- spot real changes
- review edits safely
- keep a calm contributor workflow

This pass widened `.gitignore`, which reduces the immediate noise.

Remaining gap:
- watch for new generated artifact names and keep the ignore patterns aligned with reality

### 5. Text encoding damage was real; the remaining task is preventing recurrence

Core files such as `nova_backend/src/brain_server.py` previously contained mojibake in comments/docstrings.

This likely does not break runtime behavior.

But it does hurt:
- readability
- perceived code quality
- trust in the primary orientation file the docs tell people to read first

This pass cleaned the most visible corruption.

Remaining gap:
- prevent future copy/paste or editor-encoding regressions in newly edited docs and comments

## Corrected Audit Notes Versus Older Claims

This audit intentionally corrects a few stale or inaccurate claims found in older notes.

### Corrected item: `.env.example` exists

Nova does already include:
- `nova_backend/.env.example`

So the problem is not "missing environment example."

The real issue is:
- environment setup still needs clearer top-level contributor guidance
- and the provider-routing story should stay aligned with the actual runtime posture

### Corrected item: `.github/workflows/` exists

Nova already has GitHub workflow files in:
- `.github/workflows/`

So the current gap is not "no CI exists."

The real question is:
- whether the CI coverage matches the repo's actual highest-friction failure modes
- especially frontend-source-of-truth drift and root-level test ergonomics

### Corrected item: `nova_backend/src/requirements.txt` is a compatibility shim

There is a second `requirements.txt` under `nova_backend/src/`, but it is a compatibility shim pointing back to the canonical file:
- `-r ../requirements.txt`

That is not currently a duplication bug.

### Corrected item: the frontend does not currently have a package-managed build system

The older complaint about "no package.json" is directionally true for the historical dashboard copy:
- `Nova-Frontend-Dashboard/` does not have a `package.json`

But the more important truth is not just absence of npm tooling.

It is:
- the runtime frontend is currently shipped as static assets
- and the stronger immediate problem is frontend coherence and maintainability, not simply lack of bundling for its own sake

## Product Diagnosis

The strongest current system-level bottleneck is:

`repo coherence, doc freshness, and frontend maintainability are now lagging behind the real backend/runtime maturity`

Nova already has:
- meaningful runtime depth
- governance structure
- proof-oriented checks
- active operator/product surfaces

What is now limiting it is more productization-shaped:
- one obvious place to edit frontend truth
- cleaner contributor workflow
- less legacy debris and stale audit language
- stronger maintainability for the main UI layer

## Immediate Remediation Order

### P0
- keep the frontend source-of-truth model explicit and stop active docs from reintroducing mirror confusion
- keep root-level test execution reliable and explicit in contributor docs and CI
- decide whether legacy placeholder modules should be archived, deleted, or retained as clearly quarantined compatibility stubs
- keep the modular frontend bundle contract explicit in tests and smoke checks so future cleanup does not regress back into hidden single-file assumptions

### P1
- keep tightening `.gitignore` and local-artifact handling as new artifact names appear
- prevent new encoding damage in high-visibility files
- improve top-level contributor instructions for how to run, test, and review the project

### P2
- continue reducing the frontend monolith through a clearer internal structure
- improve frontend testability and UI-surface validation
- continue product polish around run clarity and everyday usefulness

## Relationship To Other Docs

Read this packet alongside:
- `docs/design/Phase 6/NOVA_CORRECTED_REPO_AUDIT_AND_REMEDIATION_2026-03-26.md`
- `docs/design/Phase 6/NOVA_DOCS_CODE_ALIGNMENT_AUDIT_2026-04-02.md`
- `docs/design/Phase 8/NOVA_PHASE_8_USER_OPERABILITY_AND_RUN_SYSTEM_AUDIT_2026-04-05.md`
- `docs/reference/HUMAN_GUIDES/14_FRONTEND_AND_UI_GUIDE.md`

Interpretation:
- the older Phase 6 audits establish the repo-truth lane
- the Phase 8 audit establishes run-operability and user-control gaps
- this packet updates the current repo/productization picture after those earlier corrections

## What This Means Right Now

Nova is not mainly blocked by missing conceptual architecture.

Nova is currently blocked by a simpler but more important class of work:

- make the codebase easier to trust
- make the frontend easier to change safely
- make local development and review easier to repeat
- then continue broadening product usability from a stronger foundation

## Short Version

The blunt current truth is:

- the backend and governance spine are more real than some older audit notes suggested
- the frontend and contributor workflow are less coherent than the backend maturity now deserves

That makes the next best move:

`productize the repo surface and frontend editing model before trying to widen Nova much further`
