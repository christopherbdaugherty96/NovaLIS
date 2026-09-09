# Issue #406: memory identity and existing-duplicate decision

Recorded before implementation from main e5fdecae76e9dcfaf42531afc43ba5ac857023fd.
Owner scope: reproduce/correct #406, local proof, exact-head review; no merge or later lane.

## Decision

New governed-memory IDs retain MEM-YYYYMMDD-HHMMSS and use a full 32-hex UUID candidate. Allocate inside the shared-path read/modify/write lock for save and supersede. Compare against every retained record ID (including deleted/superseded history); resolve collisions deterministically by incrementing the 128-bit suffix until unused, without retrying randomness. Legacy four-hex IDs remain valid; command parsing must accept both complete formats without truncation.

Detect existing duplicates on every ID-addressed lookup before deletion/visibility filtering. Multiple records normalizing to the requested ID cause an explicit ambiguity error and no write: get/show, lock, defer, confirmed unlock/delete/supersede all refuse. A deleted duplicate remains ambiguous. Never automatically rename, merge, delete or rewrite ambiguous records or their links.

Enumeration/export remain available with identities intact. No automatic recovery: an ID cannot identify which duplicate a historical reference meant. Recovery requires a separate reviewed operation using preserved/exported evidence. Unambiguous records remain usable. This is safe refusal, not a recovery UI or migration.

## Proof and limits

Force repeated timestamps and UUID candidates. Cover rapid saves, multiple same-path instances/threads, restart, supersession, deleted-history reservation and current-item filtering. Deliberately persist duplicates and prove all ID-based operations refuse without altering file bytes/links; distinct IDs must still target exactly their own record. Verify old/new command parsing and governed execution.

Concurrency guarantee: existing single-process shared-path lock contract. Cross-process access, corrupt-file recovery, backup/restore and storage architecture belong to #408. Schemas, confirmation rules, authority and other memory stores remain unchanged.
