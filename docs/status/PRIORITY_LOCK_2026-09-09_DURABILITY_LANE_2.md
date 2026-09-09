# Priority Lock — Durability Implementation Lane 2

Status: COMPLETE / MERGED
Authorized from: lane 1 closeout on `main@2a3ccbd7cf4e13a1770d68c579ab8fce108059f3`
Merged: PR #416 at `main@80e1c86f4ff9a735f5b390248f73dd3fafc1008d`

## Objective

Make corruption distinguishable from genuinely absent state for the authoritative
and portable stores accepted by #408. Preserve the original evidence and prevent
dependent mutation when persisted state cannot be trusted.

## Authorized work

- inventory readers that translate read, parse, or schema failure into empty or default state;
- introduce one shared corruption result/error contract where it reduces ambiguity;
- preserve the original file bytes by leaving the corrupt file untouched;
- fail dependent mutation closed;
- focused malformed, truncated, and invalid-shape regressions;
- mechanical current-priority reconciliation and generated runtime docs when required.

## Explicitly excluded

- repair, quarantine moves, migration, backup, restore, rollback, generation activation;
- maintenance or interprocess locking;
- SQLite or storage-format redesign;
- provider, Continuity, capability, OpenClaw, voice, or UI expansion.

## Merge boundary

One exact-head review. Only a reproduced violation of this contract or a material
trust/runtime failure blocks merge. Cosmetic cleanup and unrelated debt do not.

## Evidence inventory

| Store | Current silent behavior | Required lane-2 behavior |
| --- | --- | --- |
| Governed, user, and Nova-self memory | broad read fallback to empty/default | explicit corruption; mutation refused |
| Quick corrections | malformed lines skipped or broad empty fallback | explicit corruption; consumption rewrite refused |
| User and tone profiles | broad default fallback | explicit corruption; mutation refused |
| Runtime settings and atomic policies | broad default fallback | explicit corruption; mutation refused |
| Notification schedules | load failures become absent/default | explicit corruption; schedule mutation refused |
| Pattern-review queue | broad empty fallback | explicit corruption; mutation refused |
| Goals | already raises a store corruption error | retain and verify evidence preservation |
| Story tracker | broad caller-supplied default fallback | explicit corruption; writes refused |
| OpenClaw envelope/runtime/execution stores | broad empty/default fallback | explicit corruption; lifecycle mutation refused |
| Ledger/receipts | malformed records can be skipped or flattened | explicit unavailable/corrupt truth; append policy verified |
| Provider usage | broad default fallback | explicit corruption; accounting mutation refused |

Missing files remain valid absent/initial state. Cache, capture, log, model-provider,
and unrelated parsing failures are outside this reader lane unless they directly
control an accepted authoritative mutation.
