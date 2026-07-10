# Governor Bypass — Evidence Map

**Status:** MAP ONLY — this document classifies existing evidence. It moves, renames, and deletes
nothing. Any consolidation is a separate, human-approved decision.
**Date:** 2026-07-09
**Why this exists:** four files in `docs/PROOFS/` carry "Governor Bypass" names with four different
content hashes. Before any dedup, this map records what each one actually is, so no evidence is
destroyed by a false-duplicate assumption (see the UNLOCK false-positive lesson: hash before
concluding).

## The finding

**These are not four copies of one proof.** Three are successive generations of a real
governor-bypass proof, tracking the runtime as it grew. One is a misfiled implementation
document that has nothing to do with bypass proofs.

## File-by-file

| # | File | SHA256 (12) | Size | Committed | What it actually is |
|---|---|---|---|---|---|
| 1 | `phase 3.5-4/GOVERNOR_BYPASS_PROOF.md` | `EE92591CE349` | 3.7 KB | 2026-02-16 | **Gen 1 — Phase 3.5 structural proof.** Claims no execution path exists outside the Master Governor; execution modules present but inactive. Flow: brain_server → GovernorMediator → SkillRegistry → read-only tools. |
| 2 | `Governor Bypass Proof Document.txt` (PROOFS root) | `258483BC6C27` | 2.9 KB | 2026-04-20 (content dated 2026-02-17) | **Gen 2 — inbound-path enumeration.** Proves all governed-action paths converge at `governor.handle_governed_invocation()`; skill-registry and LLM paths shown non-executing. Committed to the PROOFS root ~2 months after its content date. |
| 3 | `Phase-4/GOVERNOR_BYPASS_PROOF.md` | `728725BBC026` | 9.1 KB | 2026-02-27 → 2026-03-03 | **Gen 3 — Phase-4 v2.0, the most complete bypass proof.** `NOVA-GOV-BYPASS-PROOF-v2.0`, status VERIFIED, all 9 executor branches (caps 16–22, 32, 48), adds the NetworkMediator claim (no outbound network outside it), explicit non-authorizing language. |
| 4 | `Phase-4/Governor Bypass Proof Document.txt` | `84C83F0F8EFF` | 12 KB | 2026-02-27 | **MISFILED — not a bypass proof.** Content is an implementation write-up of the constitutional model version lock (`llm_manager.py`, `inference_wrapper.py`, composite hash, `confirm_model_update()`). Wearing a bypass-proof filename it does not match. |

## Authority ordering

1. **Live truth about bypass surfaces is NOT any of these files.** It is:
   - `docs/current_runtime/BYPASS_SURFACES.md` (generated),
   - `python scripts/prove_runtime_truth.py` (mechanical: Governor blocks unconfirmed cap 64 and
     unknown capabilities — asserted on every merge since PR #284).
2. **Most authoritative historical proof:** file 3 (Phase-4 v2.0) — widest scope, latest
   substantive revision, explicit verification status.
3. **Files 1 and 2** are earlier generations: valid historical evidence of what was proven at
   Phase 3.5, superseded in scope by file 3. Keep as history; never cite as current.
4. **File 4** is evidence for a *different* claim (model version lock — the same lock that fired
   and was owner-cleared on 2026-07-07). Its content is real; only its name/location is wrong.

## Needs human decision (deliberately not done here)

1. **File 4 rename/move:** it belongs with model-lock evidence, not bypass proofs. Options:
   rename in place with a correct name, or move to a model-lock evidence location. Either changes
   history layout — owner call.
2. **Files 1–2 labeling:** optionally add a superseded-by-Gen-3 header line to each. Low value,
   zero urgency.
3. **Nothing is a candidate for deletion.** All four have distinct evidentiary content.

Related: `docs/PROOFS/README.md` (packet index), `docs/CANONICAL/06_TEST_AND_PROOF_TRUTH.md`
(how proof truth is read), `docs/current_runtime/BYPASS_SURFACES.md` (generated live surface).
