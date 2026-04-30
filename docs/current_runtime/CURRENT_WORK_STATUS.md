# Nova Current Work Status

Last reviewed: 2026-04-30

This document captures human-readable project status for the current work session.

For generated runtime truth, use [`CURRENT_RUNTIME_STATE.md`](CURRENT_RUNTIME_STATE.md). Generated runtime docs remain the authority for exact runtime fingerprint, capability count, active capabilities, and generated invariants.

This file is not generated. It exists to prevent recent session work from being overstated or lost.

---

## Current Remote Main Truth

Remote `main` is currently grounded at commit:

```text
c8193bdc4b1fc213952d888430d8381aec1779b8
brain: add static capability contracts
```

That commit added the static Brain capability contract catalog and aligned Brain docs around the current truth.

Implemented on remote `main`:

- `nova_backend/src/brain/capability_contracts.py`
- `nova_backend/tests/brain/test_capability_contracts.py`
- Brain docs now state that static contracts exist for Cap 16, Cap 63, Cap 64, and Cap 65.
- Docs also state that runtime/live contract lookup is not wired into the full Task Environment Router or Governor path yet.

Current generated runtime truth still reports:

- 27 enabled capabilities.
- Phase 3.5 complete.
- Phase 4 complete.
- Phase 4.2 complete.
- Phase 4.5 partial.
- Phase 5 complete.
- Phase 6 complete.
- Phase 7 complete.
- Phase 8 active.
- Phase 9 active.
- No broad autonomy.
- All actions must pass GovernorMediator.
- All outbound HTTP must pass NetworkMediator.
- Execution must be logged to the ledger.

---

## Static Capability Contracts Status

Status: committed to remote `main`.

Current static contracts:

| Capability | Status | Boundary |
|---|---|---|
| Cap 16 `governed_web_search` | Static contract exists | Network-read only; cannot bypass NetworkMediator or treat stale memory as current proof. |
| Cap 63 `openclaw_execute` | Static contract exists | Governed OpenClaw environment; confirmation required; cannot bypass Governor or silently use a personal browser session. |
| Cap 64 `send_email_draft` | Static contract exists | Confirmation-bound local `mailto:` draft only; cannot send/read/Gmail/SMTP/archive/delete/label. |
| Cap 65 `shopify_intelligence_report` | Static contract exists | Read-only Shopify reporting; requires env vars; cannot write/mutate/update/refund/fulfill. |

Important boundary:

Static contracts are planning/review vocabulary. They do not authorize, route, or execute anything by themselves.

Still not wired:

- Full Task Environment Router contract lookup.
- Governor use of live contract lookup.
- Dry Run / Plan Preview contract consultation.
- Brain Trace UI rendering of contract decisions.

---

## Search Synthesis Status

Status: local in-progress / not confirmed on remote `main` as of this review.

A recent Codex session began a Search Synthesis slice after the static contracts commit. The session log reported:

- `nova_backend/src/brain/search_synthesis.py` was created locally.
- `nova_backend/src/executors/web_search_executor.py` was edited locally.
- Search Synthesis tests were created locally.
- Targeted Search Synthesis tests were reportedly green.
- Brain docs were being edited to mark the module as implemented.
- The session stopped before final drift/targeted checks and before a confirmed commit/push.

Because that work is not visible on remote `main`, repository docs should not claim Search Synthesis as a committed or live runtime feature until the local changes are committed and verified.

Correct wording until committed:

```text
Search Synthesis is the next/in-progress Cap 16 reliability slice. It should remain deterministic, non-authorizing, and limited to structuring evidence already collected by the governed web-search executor.
```

Incorrect wording until committed:

```text
Search Synthesis is live in runtime.
Search Synthesis is wired into Governor.
Search Synthesis creates a new search path.
Search Synthesis authorizes browsing or tool use.
```

---

## Active P1

Current P1 remains Cap 16 current-information reliability.

Immediate best next step:

1. Recover the local Search Synthesis working tree.
2. Confirm whether the local files still exist.
3. Re-run targeted checks:

```bash
python scripts/check_runtime_doc_drift.py
python -m py_compile nova_backend/src/brain/search_synthesis.py
python -m pytest nova_backend/tests/brain/test_search_synthesis.py nova_backend/tests/executors/test_web_search_evidence.py -q
python -m pytest nova_backend/tests/executors/test_web_search_executor.py -q
python -m pytest nova_backend/tests/brain -q
python -m pytest nova_backend/tests/test_registry_fail_closed.py nova_backend/tests/governance -q
```

4. Commit only the Search Synthesis files and directly related docs if the checks pass.
5. Keep `scripts/pids/nova_backend.pid` and `Auralis-Digital/` untouched.

---

## Do Not Overstate

Do not claim these are finished unless verified against code/runtime truth:

- Full Task Environment Router.
- Governor-driven live contract lookup.
- Dry Run / Plan Preview API.
- Brain Trace UI.
- Search Synthesis on remote `main`.
- Google OAuth/Gmail/Calendar runtime connectors.
- Gmail send/write authority.
- Shopify write authority.
- Broad autonomous execution.
- One-click consumer installer.

---

## Recommended Continuation Order

1. Finish and commit Search Synthesis as a narrow Cap 16 evidence-structuring module.
2. Keep it non-authorizing and attached only to the existing governed web-search output path.
3. Re-run drift and targeted governance checks.
4. Then revisit docs and mark Search Synthesis implemented only after the source file and tests are committed.
5. After that, continue with Context Assembler / Intention Parser scaffolds only if Cap 16 reliability is stable enough to support them.
