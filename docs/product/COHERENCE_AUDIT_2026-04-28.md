# Nova Coherence Audit — 2026-04-28

**Scope:** Full repo — docs, design plans, future-vision files, memory/conversation model,
architecture docs, governance model, first-time user path, active code, and runtime state.

**Goal:** Establish whether Nova is internally coherent, truthful, and easy to continue —
not to identify new features.

**Result:** Nova is coherent at the governance and execution layers. The primary incoherence
is in documentation density: too many layers, some stale, with no obvious reading order.
The audit resolved all high-priority contradictions. Open items are doc hygiene and two
human-gated live signoffs.

---

## Phase 1 — Document Truth Audit

### Authoritative document hierarchy (in priority order)

| File | Role | Status |
|---|---|---|
| `docs/current_runtime/CURRENT_RUNTIME_STATE.md` | Auto-generated truth | Accurate, regenerated |
| `4-15-26 NEW ROADMAP/Now.md` | Active sprint | Current as of 2026-04-26 |
| `NovaLIS-Governance/STATUS.md` | Governance-facing status | Consistent with runtime |
| `4-15-26 NEW ROADMAP/MasterRoadMap.md` | Strategic baseline | Frozen 2026-04-15, valid |
| `4-15-26 NEW ROADMAP/BackLog.md` | Deferred work | Actively maintained |

### Contradictions found and resolved

| Issue | Severity | Fix applied |
|---|---|---|
| `README.md` claimed "25 live capabilities"; runtime shows 27 | HIGH | Fixed in prior session |
| `TODO.md` described installer and cap work as future; both done | HIGH | Replaced with pointer |
| Trust card docs described the surface as entirely unbuilt | MEDIUM | Both files updated with implementation note (2026-04-28) |
| `SECURITY.md` contained `PGP-PUBKEY-PLACEHOLDER` | LOW | Deferred (no PGP key held) |

### Remaining doc-truth issues (deferred)

- `SECURITY.md`: placeholder not filled — no PGP key available; remove or fill when ready
- Phase 4.5 in `NovaLIS-Governance/STATUS.md` shows ACTIVE; runtime shows PARTIAL — both
  are defensible framings of the same state; not a contradiction requiring a fix

---

## Phase 2 — Design Plan Coherence

Reviewed all design plans in `docs/product/`, `docs/Future/`, and phase folders (4–11).

**Active and accurate:**
- `docs/product/CONVERSATION_AND_MEMORY_MODEL.md` (new, 2026-04-28)
- `docs/product/TRUST_REVIEW_CARD_SPEC.md` and `TRUST_REVIEW_CARD_PLAN.md` (updated)
- `docs/product/CAPABILITY_SIGNOFF_MATRIX.md` (created prior session)
- `docs/product/PROOF_CAPTURE_CHECKLIST.md` (created prior session)
- `docs/capability_verification/live_checklists/cap_64_send_email_draft.md` (updated)

**Stale but clearly marked:**
- `docs/archive/` — 39 files; not linked from active navigation
- Phase folders 4–11 contain 128 design docs that are historical, not operational

**Finding:** Design plans are coherent with current code. No plan describes a feature that
was implemented differently than specified, with one exception: the Trust Review Card — the
plan described a future full card; the initial Action Receipts delivery is a subset. Both
docs now acknowledge this explicitly.

---

## Phase 3 — Conversation Coherence

Verified the full conversation/memory/context pipeline against source:

| Layer | Source | Authority | Status |
|---|---|---|---|
| Current message | `session_handler.py` | None | Accurate |
| Session state | `session_handler.py` (session_state dict) | None | Accurate |
| Tone/mode | `intent_patterns.py` TONE_SET_RE, ToneProfile | None | Accurate |
| Project threads | `project_threads.py`, ProjectThreadStore | None | Accurate |
| Explicit memory | `governed_memory_store.py`, `user_memory_store.py` | None | Accurate |
| Topic memory + story tracker | session_state, caps 52/53 | None | Accurate |
| Governed action boundary | GovernorMediator → CapabilityRegistry → ExecuteBoundary | YES | Accurate |
| Ledger + receipts | LedgerWriter, `/api/trust/receipts` | None (record only) | Accurate |
| Runtime truth | `docs/current_runtime/` (generated) | None | Accurate |

**Key invariant confirmed:** No memory layer can authorize a governed action. The principle
"Intelligence is not authority" holds structurally — it is not just a claim in docs.

**PAUSED_SCOPE_RE bug fixed:** `brain_server.py` was not exporting `PAUSED_SCOPE_RE` to
`session_handler.py`. This meant the paused-scope guard was silently missing from live
websocket sessions. Fixed in the prior session (commit `93be5ff` area).

---

## Phase 4 — Memory Coherence

Memory is used in two senses in this codebase: conversational memory (user-saved facts) and
the Python memory of the runtime. Neither conflates with authority.

**Conversational memory stores:**
- `GovernedMemoryStore`: explicit user-requested saves, governed
- `UserMemoryStore`: user profile and preference data
- `NovaMemoryStore`: general persistent context

All three are injected as context only. None can route to an executor.

**Session memory (non-persistent):**
- `session_state` dict in `session_handler.py` — cleared on session close
- `topic_memory_map` — session-only topic clusters
- Pending confirmation state — cleared after resolution

**Background scheduler:**
`OpenClawAgentScheduler` runs a background polling loop but requires:
1. `home_agent_enabled` permission (explicit user setting)
2. `home_agent_scheduler_enabled` permission (second explicit user setting)
3. Feature flag environment variable
4. Daily run cap (default 8)

This is not a governance bypass. It is a constrained background executor behind four
independent gates. The scheduler does not have access to memory stores; it uses a separate
task queue.

**Finding:** Memory coherence is sound. The documentation now fully reflects this
(`CONVERSATION_AND_MEMORY_MODEL.md`).

---

## Phase 5 — Governance Coherence

Verified the governance path end-to-end:

```
User message
  → build_request_understanding() [classifies, does NOT authorize]
  → GovernorMediator.check()
  → CapabilityRegistry.can_execute()
  → SingleActionQueue
  → ExecuteBoundary.execute()
  → Executor (e.g. send_email_draft_executor.py)
  → LedgerWriter.write()
```

**Every real action passes through this path.** Confirmed by:
- 1638 automated tests, 0 failures
- `docs/current_runtime/BYPASS_SURFACES.md` — no bypass surfaces found in current runtime
- Cap 64 executor: `webbrowser.open()` only; no SMTP imports; `test_executor_module_does_not_import_smtplib` confirms this at the AST level
- Cap 65 executor docstring: "No write operations in this executor"

**Confirmation gate:** Session handler sets `pending_governed_confirm` state for caps
requiring confirmation. The gate was broken for cap 64 prior to commit `93be5ff` — fixed.

**OpenClaw governance hardening:** Steps 1–7 complete (prior sessions). No new gaps found.

**Finding:** Governance is coherent and structurally enforced. The core claim — that
conversation context cannot authorize execution — is true in code, not just in documentation.

---

## Phase 6 — First-Time User Path

Traced the path a new user follows:

1. `README.md` — clear quickstart, links to `FIRST_RUN.md`
2. `FIRST_RUN.md` — step-by-step setup; Next Reading section has accurate links
3. `START_HERE.md` — honest capabilities overview; trust card description updated
4. `docs/product/WHAT_WORKS_TODAY.md` — accurate; Action Receipts card listed as live
5. Chat → Trust Center → Action Receipts — working path

**Gaps in first-time path:**
- No canonical "read these 5 docs in this order" landing page
- `docs/INDEX.md` has 31 entries vs. 534 files — index is useful but not exhaustive
- Archive docs not marked "ARCHIVED — do not use" at file level (only at folder level)
- Formspree waitlist not activated — users cannot join from the landing page (external blocker)

**`FIRST_RUN.md` fix applied:** Next Reading section previously linked `TRUST_REVIEW_CARD_SPEC.md`
as a next step for new users; that link was removed (spec is a developer reference, not a
user doc).

---

## Phase 7 — Duplication and Drift

**Duplication inventory:**

| Category | Count | Risk |
|---|---|---|
| Active operational docs | ~10 | Low |
| Design phase docs (4–11) | 128 | Low — historical, not linked from active paths |
| Future-vision docs | 43 | Medium — no "chosen direction" designated |
| Archive docs | 39 | Low — archived |
| Proof/certification packets | 159 | Low — structured reference |

**Key drift risk:** 43 future-vision docs describe competing directions (voice-first, solo
business assistant, Auralis, everyday mode, Google connector). None has a "this is the chosen
path" designator. `MasterRoadMap.md` names Solo Business Assistant as the Tier 2+ shell
direction, but this is not reflected back in the Future docs.

**Deferred:** Consolidating the 128 phase docs and 43 future docs is Tier 3 work per
`MasterRoadMap.md`. Not actionable in this audit pass.

---

## Phase 8 — Runtime vs. Documentation Consistency

Ran `scripts/check_runtime_doc_drift.py` — **no drift detected.**

Runtime fingerprint regenerated: hashes updated in `docs/current_runtime/` to reflect
code changes from this audit pass (PAUSED_SCOPE_RE fix, JS receipt card cleanup, new
executor boundary tests).

Capability count consistent across:
- `CURRENT_RUNTIME_STATE.md`: 27 active capabilities
- `README.md`: 27 (updated prior session)
- `CAPABILITY_SIGNOFF_MATRIX.md`: 27 rows

---

## Phase 9 — What Needs Human Action

These items cannot be completed from the repo side:

| Item | Blocker | What to do |
|---|---|---|
| Cap 64 P5 live signoff | Requires human + mail client | Follow `docs/capability_verification/live_checklists/cap_64_send_email_draft.md` |
| Cap 65 P5 live signoff | Requires Shopify env vars | Set `NOVA_SHOPIFY_SHOP_DOMAIN` + `NOVA_SHOPIFY_ACCESS_TOKEN`, run checklist |
| Formspree waitlist | External activation | Activate Formspree endpoint for landing page |
| GitHub Actions CI | Billing unlock | Unlock billing; CI workflow is already written |
| `SECURITY.md` PGP | Key required | Fill key or replace with contact-only policy |

---

## Summary

**Coherent and trustworthy:**
- Governance spine (GovernorMediator → LedgerWriter) is structurally sound
- All 1638 automated tests pass
- Memory cannot authorize execution — confirmed in code, not just in docs
- Cap 64 is ready for P5 human live signoff (89 tests pass)
- Cap 65 is ready for P5 pending Shopify env vars
- Trust card docs now accurately reflect what is built vs. what is planned

**Cleaned up in this audit pass:**
- `PAUSED_SCOPE_RE` export bug fixed (was causing silent paused-scope bypass in websocket sessions)
- `EMAIL_DRAFT_OPENED` dead event code removed from receipt card JS
- Trust Review Card spec and plan updated with accurate current state
- `CONVERSATION_AND_MEMORY_MODEL.md` created — first complete doc of all 9 context layers
- Runtime fingerprints regenerated and committed

**Deferred (not blockers):**
- Doc consolidation (128 phase docs, 43 future docs)
- `docs/CANONICAL.md` reading-order guide
- Archive warning headers in individual archived files
- Designating a chosen next product direction in Future docs

The system is ready to present to technical early adopters. The primary gap before broader
demo is Cap 64 P5 live signoff — a 15-minute human run.
