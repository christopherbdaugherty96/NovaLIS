# Doc Cleanup — Nova

**Updated:** 2026-04-28
**Purpose:** Documentation maintenance tasks. Not implementation work.

---

## Open

### SECURITY.md — fill PGP placeholder
`SECURITY.md` contains `PGP-PUBKEY-PLACEHOLDER` and no response SLA.
Fix: fill in PGP key or remove placeholder; add "We aim to respond within 14 days."

### Phase 4.5 status conflict
- `NovaLIS-Governance/STATUS.md` shows Phase 4.5 = **ACTIVE**
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md` shows Phase 4.5 = **PARTIAL**

Verify which is correct; update the stale doc.

### Archive folder headers
Docs in `docs/archive/` are not clearly marked as non-authoritative.
Fix: add `> ARCHIVED — do not use for implementation decisions.` header to each.

### Canonical reading-order doc
No root-level pointer tells new readers which 5 docs to read first.
Fix: create `docs/CANONICAL.md` — 10 lines listing the 5 authoritative sources with one-line descriptions.

---

## Resolved

| Item | Resolved |
|------|---------|
| README.md capability count | Updated to 27 — 2026-04-21 |
| TODO.md stale content | Replaced with pointer to Now.md — 2026-04-27 |
| docs/INDEX.md scope vs. actual file count | Known gap; not blocking |
