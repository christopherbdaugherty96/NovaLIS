# Priority Lock — Durability Lane 3

Date: 2026-09-10
Status: OWNER AUTHORIZED / ACTIVE
Authorized base: `main@1be759a504391aa04d235b6666cdcd0f922c0b6b`

## Authorized contract

Durability Lane 3 is limited to maintenance locking and mutation quiescence:

- one stable OS-visible interprocess maintenance owner at
  `control/maintenance.lock`;
- shared OS-visible writer leases acquired before authoritative mutation begins;
- process-local admission closes before maintenance waits for admitted writers;
- admitted writers finish while retaining their leases, then maintenance obtains
  exclusive OS ownership;
- foreground, direct-store, scheduler/background, and OpenClaw/runtime mutations
  fail closed while maintenance owns the boundary;
- clean release, failed maintenance, abnormal termination, and stale diagnostic
  metadata cannot leave Nova permanently blocked;
- the Windows default root and `NOVA_RUNTIME_DIR` use the same control contract.

The OS lock is ownership truth. File contents are diagnostic metadata and never
justify deleting or overriding a live lock.

## Mutation-entry inventory

| Class | Authoritative entry points | Narrow admission boundary |
|---|---|---|
| Foreground / Governor | Governed capability invocation and its receipt/ledger effects | `Governor.handle_governed_invocation` |
| Direct stores | Governed/user/self memory, quick corrections, policies, schedules, settings, usage, profiles, goals, connections/credentials, story tracking, model lock | Public read-modify-write methods; common JSON writer remains defense in depth |
| Scheduler / background | Notification delivery and scheduled OpenClaw claims/runs | Schedule-store mutation methods and `OpenClawAgentScheduler.tick` |
| OpenClaw / runtime | Envelope lifecycle, active/recent run state, delivery state, execution memory | Public lifecycle/runtime mutation methods |
| Audit / receipts | Append-only ledger events consumed by receipt views | `LedgerWriter.log_event`, preserving its same-path `RLock` |

Derived caches may be refused by the common writer during maintenance, but they
do not expand the authoritative inventory. Reads remain available except where a
governed invocation necessarily creates audit/receipt state.

## Explicit exclusions

This lane does not implement snapshots, manifests, migration, generation
activation, backup, encryption, restore, rollback, SQLite, provider expansion,
Continuity, voice, UI expansion, or new execution authority.

## Exit gate

One bounded PR must prove cross-process contention, foreground and background
refusal, admitted-writer drain, exclusive acquisition, clean and failed release,
abnormal termination, stale metadata safety, root parity, corruption fail-closed
preservation, and the #418 ledger serialization contract. One exact-head review
follows. Snapshot/manifest work remains separately authorized after Lane 3 closes.
