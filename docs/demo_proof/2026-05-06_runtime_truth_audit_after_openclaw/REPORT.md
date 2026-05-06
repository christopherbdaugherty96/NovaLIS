# Runtime Truth Audit After OpenClaw Proof Chain - 2026-05-06

Status: draft / review required

## Purpose

This audit executes the active runtime-truth priority lock after the completed OpenClaw proof chain.

It verifies whether generated runtime truth and human-maintained docs remain aligned after:

- PR #103 planning-task preview runtime handoff proof
- PR #104 RequestUnderstanding review-card payload contract
- PR #105 local capability signoff matrix
- PR #106 OpenClawMediator skeleton
- PR #107 first read-only OpenClaw workflow proof
- PR #108 OpenClaw priority-lock closeout

## Commands

```powershell
python scripts/generate_runtime_docs.py
python -m pytest nova_backend/tests/openclaw/test_openclaw_mediator.py nova_backend/tests/openclaw/test_first_read_only_workflow_proof.py nova_backend/tests/phase45/test_obsidian_overlay_generator.py -q
```

## Generator Result

The runtime docs generator completed successfully:

```text
Generated runtime docs: C:\Nova-Project\docs\current_runtime\CURRENT_RUNTIME_STATE.md
Indexed 914 docs and 730 code files. MOCs -> C:\Nova-Project\_MOCs; config -> C:\Nova-Project\.obsidian.
```

## Runtime Truth Diff

Generated runtime docs changed only fingerprint/hash values:

- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`

No generated capability count, capability list, authority text, runtime discrepancy text, or OpenClaw approval wording changed.

`RUNTIME_CAPABILITY_REFERENCE.md` did not change. This is correct for this pass because OpenClawMediator and the first read-only workflow proof are proof/supporting artifacts without a new capability ID or runtime route.

## Overlay Diff

The generator also refreshed the Obsidian overlay through `refresh_obsidian_overlay()`.

The initial audit surfaced proof-artifact over-indexing into runtime/reference MOCs: files under `docs/demo_proof/**/raw/*` and `docs/demo_proof/**/screenshots/*` were being indexed as ordinary docs/code/assets.

The overlay generator now excludes those raw proof evidence and screenshot folders from topical/runtime aggregation while keeping proof `PROOF_INDEX.md` and `REPORT.md` files browsable. The regenerated `_MOCs` still index the real OpenClaw mediator/workflow proof modules and proof summary docs, but raw JSON payloads, focused pytest text, and screenshot notes no longer pollute operational topic surfaces.

These are generated navigation/index updates, not runtime authority changes.

## Focused Verification

Focused mediator/workflow and overlay-generator verification passed:

```text
46 passed
```

## Acceptance Gate Answers

1. Do generated runtime docs need regeneration after PRs #103-#108?
   - Yes, for runtime fingerprint/hash alignment.

2. If regenerated, are changes generator-consistent and code-grounded?
   - Yes. Changes came from `scripts/generate_runtime_docs.py`. Runtime truth changes are limited to fingerprint/hash values; overlay changes are generated indexing output after a narrow proof-artifact exclusion patch.

3. Do runtime docs distinguish active runtime surfaces from proof-only/supporting artifacts?
   - Yes after cleanup. No new capability or active runtime surface was added for the proof-only OpenClawMediator/read-only workflow proof modules. Generated runtime capability docs do not inflate them into authority, and generated MOCs no longer index raw proof evidence as operational runtime/reference material.

4. Do OpenClawMediator and the first read-only workflow proof remain non-authorizing/non-executing in docs?
   - Yes. The proof packages and closeout docs preserve no OpenClaw execution, no Governor/capability calls, no Cap 63 shortcut, no filesystem/browser/network actions, no external/account actions, and no workflow automation expansion.

5. Are discrepancies recorded instead of manually patched?
   - Yes. The audit recorded proof-artifact over-indexing as an indexing-policy discrepancy and corrected it in the generator before regenerating. The generated `Runtime Truth Discrepancies` section remains `None`.

## Boundaries Preserved

- no broad OpenClaw automation
- no browser/computer-use expansion
- no external writes
- no email/calendar/Shopify/account actions
- no direct Cap 63 shortcut use
- no autonomous workflow execution
- no Google connector expansion
- no capability registry expansion
- no workflow automation expansion
- no claim that OpenClaw has full governed hands
