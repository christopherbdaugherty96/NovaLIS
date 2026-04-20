# Verified Repository And Active-Doc Review

**Status:** Verified repository truth only  
**Date:** 2026-04-20  
**Authority:** Local repo state, current runtime docs, current roadmap docs

---

## Scope

This document contains only claims that are directly supported by the current Nova repository and active project documentation.

It does **not** include:

- market comparison
- product strategy opinion
- future architecture recommendations
- time-sensitive ecosystem claims

Companion documents:

- `docs/design/IDEAS/NOVA_STRATEGIC_POSITIONING_MEMO_2026-04-20.md`
- `docs/future/EXTERNAL_LANDSCAPE_NOTES_2026-04-20.md`

---

## Directly Verified From Repo And Active Docs

### Identity

- Project repo: `christopherbdaugherty96/NovaLIS`
- Product name used in docs: Nova
- License: `BUSL-1.1`
- Change date to Apache 2.0: `2030-04-18`

### Runtime

- Active capabilities: `26`
- Current runtime authority model:

```text
User -> GovernorMediator -> Governor -> CapabilityRegistry -> SingleActionQueue -> LedgerWriter -> ExecuteBoundary -> Executor
```

- Governed outbound HTTP control exists through `NetworkMediator`
- Runtime docs currently report no runtime-truth discrepancies

### Current roadmap truth

Per the active roadmap:

- Tier 1 is still in validation
- Tier 2 is implemented, awaiting live sign-off and lock
- Immediate priority is installer validation, cap 64 signoff, waitlist activation, and demo-ready README assets

### Installed / published work reported by current project docs

- Windows installer is built and published
- Capability 64 (`send_email_draft`) is implemented but not fully closed
- A memory continuity candidate design note exists in:
  - `docs/design/IDEAS/NOVA_MEMORY_CONTINUITY_UPGRADE_CANDIDATE_2026-04-20.md`

### Models

- Default Ollama model: `gemma4:e4b`

### Documentation

- Current human-guide count in `docs/reference/HUMAN_GUIDES/`: `34`

---

## Verified Gaps

These gaps are directly supported by current project docs:

- Clean Windows VM installer validation is still open
- Cap 64 live checklist, signoff, and lock are still open
- GitHub Actions is blocked by billing lock
- Formspree waitlist activation is still pending

---

## Verified Constraints

- Nova does not autonomously send email; it opens a local draft in the system mail client
- Nova's memory-continuity work is currently a candidate design note, not active roadmap authority
- The repo treats runtime docs and `Now.md` as stronger truth surfaces than informal review documents

---

## Source Surfaces

This review is derived from:

- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `4-15-26 NEW ROADMAP/Now.md`
- `README.md`
- `LICENSE`
- current repo files

---

*End of Document*
