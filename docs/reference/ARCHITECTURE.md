# Nova Architecture

Technical overview of Nova's runtime. Companion to
[`INTRODUCTION.md`](INTRODUCTION.md) (non-technical) and
[`docs/current_runtime/CURRENT_RUNTIME_STATE.md`](current_runtime/CURRENT_RUNTIME_STATE.md)
(generated, authoritative).

---

## High-level shape

Nova is a FastAPI application (`nova_backend/src/brain_server.py`)
serving a small set of HTTP and WebSocket endpoints to a local web UI.
All actions that touch the outside world — or even the local machine in
non-trivial ways — flow through a single governance spine.

```
User → UI → Session handler → Request router
                                      │
      ┌───────────────────────────────┼─────────────────────────┐
      ▼                               ▼                         ▼
Explanation path       Governed action path           Review / memory paths
(chat, summaries)      GovernorMediator               second-opinion lane,
                         → CapabilityRegistry         memory CRUD, etc.
                         → ExecuteBoundary
                         → NetworkMediator
                         → LedgerWriter
```

The explanation path never acts. Only the governed path can execute a
capability, and only after passing through every mediator in sequence.

## Governance spine

Five components, in order, gate every real action:

1. **`GovernorMediator`** — receives the intent and decides whether it
   is permitted in the current build phase / policy context.
2. **`CapabilityRegistry`** — maps the intent to one of the 26
   registered capabilities. An unregistered intent cannot execute.
3. **`ExecuteBoundary`** — enforces the shape of the capability call:
   argument schema, confirmation state, resource envelope.
4. **`NetworkMediator`** — if (and only if) the capability requires
   network access, this mediator records the outbound request and can
   refuse based on policy.
5. **`LedgerWriter`** — appends an immutable event to
   the active runtime-state ledger describing what happened.

**Everything interesting in Nova is implemented as a capability that
must pass through this spine.** There is no back door.

## Capability inventory (today)

Nova ships **26 live capabilities** (as of April 2026):

- **16 read-only** (9 local + 7 network): chat, research, news,
  weather and calendar snapshots, memory review, second-opinion review,
  screen analysis, and more.
- **6 local-device controls**: open website, speak text, set volume,
  next/previous media, set brightness, open file/folder.
- **1 governed external write**: email drafting (cap 64). Nova opens a mailto: draft
  in the system mail client — the user always sends. Nova cannot send autonomously.
  Requires explicit confirmation. No calendar write, no file content writes, no
  API-key-based mutation of any third-party service.

The canonical inventory is regenerated from the code by
`scripts/generate_runtime_docs.py`; see
`docs/current_runtime/GOVERNANCE_MATRIX.md` for the authoritative list.

## Memory layer

Memory in Nova is **user-controlled**:

- A **confirmation prompt** appears before Nova stores a new memory.
- Memories are stored in a local database (not a remote vector service).
- You can list, edit, and delete memories from the Trust page.
- Memory retrieval is visible — when Nova uses a memory to answer, the
  context is shown.

There is no implicit learning from your messages. Nova remembers only
what you explicitly tell it to remember.

## Ledger

The ledger is an **append-only** record of every governed action:

- Event type, timestamp, capability name, input arguments (redacted if
  sensitive), output summary, and the policy decisions that allowed it.
- Stored locally at the active runtime root under `data/ledger.jsonl`.
- Exposed in the Trust page UI.
- Never rewritten. Corrections are new entries, not edits.

## Runtime state and installed-code separation

Nova treats installed code and changing runtime state as separate concerns.
This is especially important on Windows, where `C:\Program Files` is protected.

Mutable runtime state is resolved through `src.utils.persistent_state`:

- If Nova runs from a writable checkout, such as `C:\Nova-Project`, runtime
  state can stay with that checkout.
- If Nova runs from a protected install path, such as `C:\Program Files\Nova`,
  runtime state falls back to `%LOCALAPPDATA%\Nova`.
- `NOVA_RUNTIME_DIR` can override the runtime root for tests or controlled
  deployments.

The runtime-state surface includes the ledger, model version lock, settings,
memory, usage tracking, profiles, policies, OpenClaw runtime state,
notifications, and captures. Installer validation should prove that these files
are not written into the protected install directory.

## Runtime-doc drift check

A common failure in governed systems is **docs drift from code**. Nova
prevents this with `scripts/generate_runtime_docs.py`, which regenerates
a fixed set of canonical documents from the live code:

- `CURRENT_RUNTIME_STATE.md`
- `GOVERNANCE_MATRIX.md`
- `GOVERNANCE_MATRIX_TREE.md`
- `SKILL_SURFACE_MAP.md`
- `BYPASS_SURFACES.md`
- `RUNTIME_FINGERPRINT.md`

A CI job fails the build if a PR changes code without regenerating
these docs. Claims in the README / architecture docs may go stale;
claims in the generated docs cannot.

## Process & deployment

- **Single process** — one `uvicorn` serving the FastAPI app.
- **Local-first** — default bind is `127.0.0.1:8000`, no external
  exposure.
- **Models** via [Ollama](https://ollama.com), running on the same
  machine.
- **No database server required** — state is on the local filesystem.

## Development workflow

```bash
# Install editable
pip install -e ".[dev]"

# Run locally
nova-start                   # or: cd nova_backend && python -m uvicorn src.brain_server:app

# Tests
pytest nova_backend/tests

# Regenerate runtime docs (run before committing code changes)
python scripts/generate_runtime_docs.py
```

## Capability verification

Nova ships a 6-phase capability verification system and shared lock
infrastructure for all 26 governed capabilities. In the current
repository state, that framework is live for every capability, but only
capability 64 (`send_email_draft`) has progressed through automated
certification so far; the others still show pending phases in
`capability_locks.json`. No capability is locked yet.

```
python scripts/certify_capability.py status        # overview of all 26 caps
python scripts/certify_capability.py advance 64 p4_api
python scripts/certify_capability.py live-signoff 64
python scripts/certify_capability.py lock 64
```

Lock state lives in `nova_backend/src/config/capability_locks.json`.
The regression guard at `nova_backend/tests/certification/test_lock_regression_guard.py`
runs automatically on every `pytest` invocation and blocks if a locked capability's
governance fields have silently changed.

See [`33_CAPABILITY_VERIFICATION_GUIDE.md`](reference/HUMAN_GUIDES/33_CAPABILITY_VERIFICATION_GUIDE.md)
for the full plain-language explanation.

## Known hot-path files

Two files are larger than they should be and are scheduled for a Tier 3
refactor:

- `nova_backend/src/brain_server.py` — ~3,600 lines
- `nova_backend/src/websocket/session_handler.py` — ~3,800 lines

The refactor is deliberately deferred until after Tier 1 (installer)
and Tier 2 (first external-write capability) ship, to avoid mixing
structural churn with user-visible progress.

## Pointers

- [`CURRENT_RUNTIME_STATE.md`](current_runtime/CURRENT_RUNTIME_STATE.md) — generated truth
- [`GOVERNANCE_MATRIX.md`](current_runtime/GOVERNANCE_MATRIX.md) — capability list
- [`MasterRoadMap.md`](../4-15-26%20NEW%20ROADMAP/MasterRoadMap.md) — plan
- [`DEEP_CODE_AUDIT.md`](../4-15-26%20NEW%20ROADMAP/DEEP_CODE_AUDIT.md) — tactical hotspot map
