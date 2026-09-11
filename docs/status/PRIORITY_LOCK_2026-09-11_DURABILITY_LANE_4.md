# Priority Lock — Durability Lane 4

Date: 2026-09-11
Status: OWNER AUTHORIZED / ACTIVE
Authorized base: `main@38dd95fd06d200c450e71b56679a48a9cc774f68`

## Authorized contract

Durability Lane 4 is limited to versioned snapshot staging and manifest validation:

- capture the recovery-included canonical registry set while Lane 3 maintenance
  owns the mutation boundary;
- represent every logical store in the manifest as included, absent, or explicitly
  excluded by registry policy;
- stage included bytes under `control/staging/<snapshot-id>` using canonical,
  path-independent logical-store identities;
- derive inventory, classification, provenance, byte counts, schema information,
  and hashes from the staged copy;
- write the completion marker last and bind it to the manifest hash;
- reject incomplete, missing, extra, malformed, structurally invalid, or tampered
  staged state without modifying live state;
- preserve the same contract under the default Windows root and
  `NOVA_RUNTIME_DIR`.

The manifest describes the staged snapshot. Later validation does not consult the
live filesystem or reinterpret changed live state as captured evidence.

## Source boundary

Before generation activation exists, snapshot capture may resolve the single
current owner from the registry's legacy runtime or repository source. Multiple
current owners fail closed. When an explicit canonical generation is supplied,
only that generation is captured. Snapshot staging never moves, rewrites, or
activates a source.

## Explicit exclusions

This lane does not implement migration, generation activation or switching,
encryption, external or portable backup, restore, rollback, SQLite or storage
redesign, provider expansion, Continuity, capabilities, voice, broader UI, or new
execution authority.

## Exit gate

One bounded PR must prove complete registry coverage, deterministic staged bytes,
integrity and inventory rejection, incomplete-staging rejection, corruption-safe
failure, maintenance ownership, source-conflict refusal, root parity, and no live
state damage. One exact-head review follows. Migration and generation activation
remain separately owner-gated after Lane 4 closes.
