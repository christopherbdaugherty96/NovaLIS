# Nova Docs Code Alignment Audit
Date: 2026-04-02
Status: Docs/code grounding note
Scope: Check whether the main documentation layers still match the actual repository state after the recent docs reorg and UI/runtime changes

## 2026-04-10 Remediation Update

This packet remains useful as a time-stamped audit snapshot, but one important item changed after the original 2026-04-02 pass:
- the frontend mirror drift identified here was remediated
- the maintained mirror is back in sync with `nova_backend/static/`
- the sync check now covers the split frontend files as well as the original shell files

Current interpretation rule:
- keep reading this document as an audit snapshot of what was true on 2026-04-02
- prefer the newer Phase 6 audit packets and the human frontend guide for current source-of-truth details

## What Was Checked

This pass checked:
- repo root docs
- docs root and human guides
- current runtime truth docs
- proof and design references that still function as current orientation material
- the repo's own drift tooling

Key checks run:
- `python scripts/check_runtime_doc_drift.py`
- `python scripts/check_frontend_mirror_sync.py`

## Grounded Result

### 1. Runtime truth docs match the current code
The runtime-generated authority layer is aligned with the live codebase.

Confirmed:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`

Result:
- `check_runtime_doc_drift.py` passed

This means the highest-authority current-runtime docs are still trustworthy.

### 2. Human-facing orientation docs mostly matched the code
The main explanatory docs were checked against real files, routes, and runtime surfaces.

Confirmed examples:
- startup scripts exist
- optional wake-word requirements file exists
- landing preview route exists
- Agent page/OpenClaw API files exist
- Settings permissions and bridge/home-agent runtime controls exist
- Intro / Trust / Workspace / Settings / Agent frontend surfaces exist in the current UI

### 3. One real repo-truth mismatch was found at the time of this audit
On 2026-04-02, the frontend mirror check failed:
- `nova_backend/static/index.html` != `Nova-Frontend-Dashboard/index.html`
- `nova_backend/static/dashboard.js` != `Nova-Frontend-Dashboard/dashboard.js`
- `nova_backend/static/style.phase1.css` != `Nova-Frontend-Dashboard/style.phase1.css`

Interpretation:
- the runtime-served frontend in `nova_backend/static/` is the real current UI
- `Nova-Frontend-Dashboard/` was a drifting mirror copy during that pass, not a trustworthy canonical source

Current note:
- that drift has since been corrected
- the maintained mirror is synced again
- the sync guard now also covers `dashboard-config.js`, `dashboard-workspace.js`, `dashboard-control-center.js`, `dashboard-chat-news.js`, and `dashboard-surfaces.css`

### 4. Docs were updated to reflect that truth
Current orientation docs now treat:
- `nova_backend/static/` as the canonical frontend
- `Nova-Frontend-Dashboard/` as a maintained mirror that must stay synced to remain trustworthy

This keeps the docs honest without rewriting runtime code.

## Missing Or Deferred Items

This audit did not find evidence that the main docs are missing a whole current runtime subsystem.

The main remaining repo-truth gap is not missing documentation of live code.
After remediation, it is mostly older active docs that still describe the mirror-copy drift as current.

## Recommended Interpretation Rule

When reviewing the repo today:

1. trust `docs/current_runtime/` for live runtime truth
2. trust `nova_backend/static/` for the real frontend
3. treat `Nova-Frontend-Dashboard/` as a maintained mirror and verify it with the mirror sync check
4. treat historical reports as time-stamped snapshots, not automatic truth for the current checkout

## Short Version

The docs now match the current codebase much more closely.

The main live mismatch left in the repo is no longer frontend mirror drift itself.

The main remaining mismatch class is:
- stale active docs that still describe the earlier drift as current

Not:
- runtime truth drift
- missing documentation of a major live runtime slice
