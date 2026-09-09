# Priority Lock — Durability Implementation Lane 1

Status: COMPLETE / MERGED AS PR #413
Authorized from: accepted #408 decision on `main@2592ad913b7da4c998425b7b2ee8432a8c032ba8`
Merged head: `6078e03cb3c945247aee1bbcf8c830ff5521aeb2`
Main merge: `e74fdca094295f587a50b4a3d82df45958937f3d`

## Objective

Create the smallest runtime foundation needed to make Nova's accepted state-ownership contract concrete:

1. resolve the canonical stable user-data container without creating it during inspection;
2. define one typed logical-store registry for the accepted state inventory;
3. detect legacy, canonical, absent, and conflicting state ownership without moving or rewriting data.

## Authorized changes

- a durability layout/registry module;
- read-only migration-source detection;
- focused tests;
- the mechanical current-priority reconciliation and its validator;
- mechanically generated runtime documentation only if required by the normal proof process.

## Required behavior

- Default installed root: `%LOCALAPPDATA%\Nova`.
- `NOVA_RUNTIME_DIR` remains an explicit override of the stable container.
- Canonical state paths distinguish generation-owned data from container-scoped cache, logs, and captures.
- Repository-relative goals and story-tracker state are detected as legacy ownership.
- Existing direct-runtime-root state is detected as legacy ownership.
- More than one meaningful source, or a canonical source plus a legacy source, reports a conflict.
- Detection is read-only and never creates, moves, merges, deletes, or rewrites state.
- Unsafe generation identifiers cannot escape the canonical generation directory.

## Explicitly not authorized

- migrating or copying any state;
- changing existing store writers or runtime path binding;
- corruption-reader changes;
- maintenance mode, activation slots, snapshot, manifest, encryption, backup, restore, or rollback;
- SQLite;
- provider, Continuity, capability, OpenClaw, voice, or UI expansion.

## Exit gate

Focused proof and one exact-head review must pass before merge. Merge completes this lane only. Corruption-safe readers remain a separate owner-authorization decision.
