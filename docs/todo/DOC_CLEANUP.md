# Doc Cleanup — Nova

**Updated:** 2026-08-20  
**Purpose:** documentation maintenance only; not runtime implementation work.

## Current open cleanup

### Remaining legacy-doc hygiene

These are still valid maintenance candidates, but none is an active product/runtime lane:

- add or verify roadmap pointers in broad navigation surfaces where still missing;
- deprecate/banner `docs/design/ui_backend_contract.md` if it remains boilerplate example content rather than the real contract;
- banner or otherwise clearly classify `docs/Audit BackLog(active)/New-Audit-and-Issues.md` as stale audit input while preserving any still-valid robustness findings;
- refresh product/reference docs that still name obsolete top-level UI pages instead of the current Settings / Advanced relationships;
- add cross-links among `PROOFS/`, `demo_proof/`, and `capability_verification/` without merging those distinct evidence genres;
- keep old archive/future trees clearly non-authoritative rather than mass-moving them and breaking references.

### Unresolved / deferred reference work

The following items remain unresolved. Wave A1 preserves them without attempting the underlying documentation expansion.

#### `NOVA_JOB_WORKFLOW_PLAN` roadmap/reference citations

```text
Status: unresolved
Destination: target current documentation set
Deferred: not part of Wave A1
```

Retain the need to connect the job-workflow plan to the appropriate current roadmap/reference surfaces where it remains relevant.

#### Connector-security references

```text
Status: unresolved
Destination: target current documentation set
Deferred: not part of Wave A1
```

Retain the need to connect current connector/security guidance to the appropriate governance, integration, and security documentation without treating future connector plans as implemented behavior.

#### Conversation response contract

```text
Status: unresolved
Destination: target current documentation set
Deferred: not part of Wave A1
```

Retain the need to surface/reference `docs/nova-conversation-response-contract.md` from the appropriate current product/behavior documentation.

#### Approval / simulation evidence

```text
Status: unresolved
Destination: target current documentation set
Deferred: not part of Wave A1
```

Retain the need to connect existing approval/simulation proof or design evidence to the appropriate current proof/governance documentation without upgrading design evidence into runtime proof.

#### B / H / D substrate citations

```text
Status: unresolved
Destination: target current documentation set
Deferred: not part of Wave A1
```

Retain the need to connect the relevant engineering-robustness, horizon, and product-coherence substrate/reference documents to the current roadmap/reference set where those citations are still missing.

### Human-only repository hygiene

`branches_safe_to_delete.txt`, if still present and still stale, remains a separate repository-root cleanup decision. Do not delete it merely from a docs truth-sync.

Physical consolidation of legacy archive directories also remains optional/human-directed because existing cross-references may depend on their locations.

## Resolved / superseded in Wave A1

### SECURITY.md PGP placeholder — RESOLVED

The old cleanup item claimed `SECURITY.md` still contained `PGP-PUBKEY-PLACEHOLDER`. Current repository search no longer finds that placeholder in `SECURITY.md`; the stale claim itself was the remaining occurrence in this tracker (plus historical audit text).

Do not keep this as an open maintenance task.

### `NovaLIS-Governance/STATUS.md` current-status conflict — RESOLVED BY RETIREMENT

The April governance snapshot had diverged from generated/current truth. Wave A1 now marks it **SUPERSEDED AS A CURRENT-STATUS SURFACE** and points readers to generated runtime truth plus current canonical/status documents.

This is safer than maintaining another duplicated phase/capability/current-priority snapshot.

### Cap 65 lock-status conflict — RESOLVED

Mechanical certification truth established Cap 65's bounded read-only lock state. Older documents that predated the lock are historical, not competing current truth.

### Canonical reading order — RESOLVED

`docs/CANONICAL/00_INDEX.md` remains the canonical navigation/reconciliation entry point and has been updated in Wave A1 to qualify generated evidence to what its machinery actually measures.

### Archive folder headers — RESOLVED

Existing archive banners/policies remain the chosen solution. Do not add per-file banners across every historical document unless a specific ambiguity is discovered.

### `docs/integrations/` / `docs/architecture/` empty-folder premise — SUPERSEDED

Prior review established that these are not empty disposable folders. Do not fold/delete them based on the old premise.

### Proof-system merge idea — REJECTED / SUPERSEDED

Keep `PROOFS/`, `demo_proof/`, and `capability_verification/` separate because they represent different evidence genres.

### Trust page vs Trust Panel naming — RECONCILED

Historical trust-page MVP proof and a broader incomplete Trust Panel concept are different scopes. Preserve that distinction rather than forcing one boolean status.

## Cleanup rules

1. Current operational truth belongs in the current canonical/status surfaces, not duplicated across many snapshots.
2. Historical docs stay historical; do not silently rewrite them into present-tense truth unless they are still used as current entry points.
3. Generated artifacts are authoritative only for the properties their generators actually inspect.
4. Do not delete or relocate non-doc repository artifacts as a side effect of documentation cleanup.
5. Documentation cleanup does not authorize runtime, capability, authority, connector, memory, provider, OAuth, OpenClaw, or external-write changes.
6. Unresolved cleanup work must remain recorded until it is explicitly completed, rejected, or superseded; Wave A1 must not erase it merely to simplify the tracker.

## Current priority relationship

Wave A1 is the active truth-synchronization lane. This cleanup file should not independently select implementation work.

Current ordering is maintained by:

- `docs/status/DAILY_COMMAND_CENTER.md`;
- `.agent_context/current_priority.md`;
- `docs/CANONICAL/07_ROADMAP_TRUTH.md`;
- `docs/future/NOVA_MASTER_ROADMAP_2026-07-05.md`;
- Issue #343.
