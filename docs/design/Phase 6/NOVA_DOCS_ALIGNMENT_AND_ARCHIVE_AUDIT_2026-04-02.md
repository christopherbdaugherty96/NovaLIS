# Nova Docs Alignment And Archive Audit
Date: 2026-04-02
Status: Docs audit note
Scope: Record the current alignment state of the docs tree after the design-folder reorg, including archive review and the remaining cleanup class

## What Was Reviewed

This audit reviewed the docs tree across:
- runtime truth
- docs root readmes
- design phase folders
- proof packet indexes
- design archive folders

The review goal was:
- check whether the current docs layers still align with each other
- check whether stale references from the old flat `docs/design/` layout remain
- check whether anything important appears to have been accidentally moved into archive folders

## Grounded Result

### 1. The core active docs layers are aligned
The main entry surfaces now point in the same direction:
- `README.md`
- `docs/README.md`
- `docs/design/README.md`
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`

They consistently describe Nova as:
- a governed personal intelligence workspace
- trust-first
- stronger on governed intelligence than broad autonomy
- still missing broader connector and execution breadth

### 2. The design reorg is structurally sound
The `docs/design/` root is now much cleaner.

The phase-folder layout is coherent and now includes:
- Phase 3.5
- Phase 4
- Phase 4.2
- Phase 4.5
- Phase 5
- Phase 6
- Phase 7
- Phase 8
- Phase 8.5
- Phase 9
- Phase 10
- Phase 11

This is a meaningful improvement over the earlier flat-file sprawl.

### 3. No strong evidence was found that active roadmap docs were accidentally buried in archive
The archive review found:
- `docs/design/archive/` contains a preserved older full Phase 4.2 roadmap plus an archive readme
- `docs/design/archive(phase 4)/` contains clearly historical Phase 4 and pre-Phase-4 material

The strongest check here is practical:
- current active design maps do not rely on archive files
- current phase folders contain the active roadmap packets
- the one duplicate Phase 4.2 roadmap case is explainable:
  - the archive holds an older full text
  - the active Phase 4.2 folder contains the current deprecation/correction path and runtime-alignment note

Conclusion:
- the archive folders look historical, not like a mistaken dump of current roadmap authority

### 4. The remaining broken references are mostly historical, not structural
The audit found a non-trivial number of stale doc references still present across the wider docs tree.

But the remaining class is mostly:
- archive docs
- old proof documents
- older theory/reference texts in phase folders
- pre-reorg legacy path references

The most important current navigation docs and phase maps were cleaned first.

## Current Alignment Assessment

### Aligned enough for active use
These are now in a good enough state to navigate the project coherently:
- docs root
- repo root readme
- design root
- main phase maps
- grounded current-status roadmap packet

### Not fully cleaned yet
Remaining cleanup still exists in:
- archive-era historical documents
- older proof packets
- older theory/reference texts inside active phase folders
- some path strings inside preserved raw-source notes

These are mostly documentation-hygiene issues, not evidence of roadmap corruption.

## Archive Judgment

Archive judgment as of this audit:

- `docs/design/archive/` is appropriate to keep
- `docs/design/archive(phase 4)/` is appropriate to keep
- no high-confidence active roadmap packet was found that clearly needs to be moved back out of archive right now

To reduce confusion, the archive surface should remain clearly labeled as:
- historical
- superseded
- non-authoritative for current roadmap use

## Remaining Cleanup Classes

The remaining docs cleanup work now falls into three buckets:

### Bucket 1 - High-value stale-link cleanup
Still worth doing:
- fix remaining stale internal references in older non-archive phase docs
- continue patching proof indexes that still point to pre-reorg design paths

### Bucket 2 - Historical-text labeling
Still worth doing:
- add clearer archive/deprecation banners to older preserved files where the text could confuse readers

### Bucket 3 - Deep historical consistency cleanup
Optional unless you want a museum-quality docs set:
- repair or annotate dead references inside old archived texts
- normalize older casing and path aliases
- clean up older references to document systems that no longer exist

## Recommended Interpretation Rule

When there is tension between docs layers, use this order:

1. `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
2. current root readmes and phase maps
3. current corrected phase packets
4. proofs
5. historical or archived texts

That order gives the clearest picture of Nova as it exists now.

## Short Version

The docs tree is now much better structured and the active roadmap layer is aligned.

The remaining mess is mostly:
- legacy references
- historical theory text
- archive-era residue

Not:
- evidence that the live Nova roadmap was accidentally archived.
