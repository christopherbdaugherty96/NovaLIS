# Nova Architecture

Technical overview of Nova's runtime. Companion to [INTRODUCTION.md](INTRODUCTION.md) and the generated runtime truth in [docs/current_runtime/CURRENT_RUNTIME_STATE.md](../current_runtime/CURRENT_RUNTIME_STATE.md).

---

## High-Level Shape

Nova is a FastAPI application served from `nova_backend/src/brain_server.py` with a local web UI and WebSocket session handling.

Every real action flows through a governance spine. The conversation path can explain, summarize, and present. The governed capability path is the only path that can execute real actions.

```text
User -> UI -> Session handler -> Request router
                                      |
      +-------------------------------+-------------------------+
      v                               v                         v
Explanation path       Governed action path           Review / memory paths
(chat, summaries)      GovernorMediator               second-opinion lane,
                         -> CapabilityRegistry        memory CRUD, etc.
                         -> ExecuteBoundary
                         -> NetworkMediator
                         -> LedgerWriter
```

---

## Governance Spine

Five components, in order, gate real actions:

1. **GovernorMediator** - receives the intent and checks policy context.
2. **CapabilityRegistry** - maps the intent to a registered, enabled capability.
3. **ExecuteBoundary** - enforces argument shape, confirmation state, and resource limits.
4. **NetworkMediator** - gates outbound network access when a capability requires it.
5. **LedgerWriter** - appends an event describing what happened and why.

An unregistered intent cannot execute. There is no action back door around the governed capability path.

---

## Capability Inventory

Nova's exact active capability inventory is generated from the codebase. Use these files for current counts, IDs, and runtime state:

- [CURRENT_RUNTIME_STATE.md](../current_runtime/CURRENT_RUNTIME_STATE.md)
- [GOVERNANCE_MATRIX.md](../current_runtime/GOVERNANCE_MATRIX.md)
- [RUNTIME_FINGERPRINT.md](../current_runtime/RUNTIME_FINGERPRINT.md)

The capability set includes read-only research and status surfaces, local-device controls, governed memory operations, OpenClaw execution surfaces, connector-backed intelligence, and confirmation-backed draft workflows such as email drafting. Nova can open a draft in the system mail client; the user reviews and sends manually.

---

## Conversation, Memory, And Authority

Conversation context and memory can improve understanding and continuity. They do not authorize execution.

Use [Conversation and Memory Model](../product/CONVERSATION_AND_MEMORY_MODEL.md) for the human-facing explanation of:

- current message
- session context
- mode and tone
- memory and continuity
- ledger and Action Receipts
- generated runtime truth
- future plans versus current authority

Memory must not bypass capability registration, confirmation requirements, execution boundaries, or ledger/receipt recording.

---

## Memory Layer

Memory in Nova is user-controlled:

- confirmation appears before Nova stores new memory
- memories are stored locally
- memory can be listed, searched, edited, exported, locked, deferred, and deleted through governed surfaces
- memory use should remain visible and inspectable

Memory is not an execution authority. Stored preferences or plans must not silently trigger actions.

---

## Ledger

The ledger is an append-only record of governed actions. Entries include event type, timestamp, capability name, redacted arguments when needed, output summary, and policy decisions. Corrections are new entries, not rewrites.

---

## Runtime State And Installed-Code Separation

Nova treats installed code and mutable runtime state as separate concerns, especially on Windows where `C:\Program Files` is protected.

Mutable state is resolved through `src.utils.persistent_state`:

- writable checkout: runtime state can stay with the checkout
- protected install path: runtime state falls back to `%LOCALAPPDATA%\Nova`
- `NOVA_RUNTIME_DIR` can override the runtime root for tests or controlled deployments

Runtime state includes ledger data, model version lock, settings, memory, usage tracking, profiles, policies, OpenClaw state, notifications, and captures.

---

## Trust Receipt API And Action Receipts

Nova exposes a read-only action receipt surface that reads the append-only ledger and returns recent governed-action events:

- `GET /api/trust/receipts?limit=N` — last N receipt-worthy events (default 20, max 100), newest first
- `GET /api/trust/receipts/summary` — quick summary for dashboard badges

Receipt-worthy events include: `ACTION_COMPLETED`, `ACTION_ATTEMPTED`, `EMAIL_DRAFT_CREATED`, `OPENCLAW_ACTION_APPROVED`/`DENIED`, `SCREEN_CAPTURE_COMPLETED`, `MEMORY_ITEM_SAVED`, and related completion events.

Action Receipts and the Trust Receipt API are current proof surfaces. A fuller Trust Review Card / Trust Panel experience remains future work, especially richer blocked-reason drill-down, confirmation-state preview, proof browsing, and a polished demo flow.

---

## Runtime Docs And Drift Checks

Nova prevents docs drift with generated runtime docs:

- `CURRENT_RUNTIME_STATE.md`
- `GOVERNANCE_MATRIX.md`
- `GOVERNANCE_MATRIX_TREE.md`
- `SKILL_SURFACE_MAP.md`
- `BYPASS_SURFACES.md`
- `RUNTIME_FINGERPRINT.md`

Run:

```bash
python scripts/generate_runtime_docs.py
python scripts/check_runtime_doc_drift.py
```

Public and architecture docs should link to generated runtime docs instead of copying exact counts or hashes.

---

## Development Workflow

```bash
pip install -e ".[dev]"
nova-start
pytest nova_backend/tests
python scripts/generate_runtime_docs.py
```

---

## Capability Verification

Nova has a capability verification and lock discipline for governed capabilities. Check `nova_backend/src/config/capability_locks.json` and the generated runtime docs for current certification and lock state.

```bash
python scripts/certify_capability.py status
python scripts/certify_capability.py advance 64 p4_api
python scripts/certify_capability.py live-signoff 64
python scripts/certify_capability.py lock 64
```

See [33_CAPABILITY_VERIFICATION_GUIDE.md](HUMAN_GUIDES/33_CAPABILITY_VERIFICATION_GUIDE.md) for the plain-language explanation. See also [Capability Signoff Matrix](../product/CAPABILITY_SIGNOFF_MATRIX.md) and [Proof Capture Checklist](../product/PROOF_CAPTURE_CHECKLIST.md) for current human-facing proof guidance.

---

## Known Hot-Path Files

Two runtime files are known refactor candidates:

- `nova_backend/src/brain_server.py`
- `nova_backend/src/websocket/session_handler.py`

They should be refactored carefully, with focused tests and no unrelated behavioral churn.

---

## Pointers

- [Current runtime state](../current_runtime/CURRENT_RUNTIME_STATE.md)
- [Governance matrix](../current_runtime/GOVERNANCE_MATRIX.md)
- [Conversation and Memory Model](../product/CONVERSATION_AND_MEMORY_MODEL.md)
- [Capability Signoff Matrix](../product/CAPABILITY_SIGNOFF_MATRIX.md)
- [Master roadmap](../../4-15-26%20NEW%20ROADMAP/MasterRoadMap.md)
- [Deep code audit](../../4-15-26%20NEW%20ROADMAP/DEEP_CODE_AUDIT.md)
