# Start Here

Last reviewed: 2026-10-03

This is the shortest human path through NovaLIS.

Nova is a local-first personal AI that keeps your context and your authority on your own
machine. It reasons, recommends, and uses a small set of governed capabilities; it does not
pursue goals on its own or expand its own authority.

Nova is an alpha build for technical users. It is not a finished consumer product.

## Where things stand

- **Current milestone:** Alpha 0, a limited first build for one external technical Windows
  tester. No installer is published yet.
- **Current ordering and boundaries:** [`.agent_context/current_priority.md`](.agent_context/current_priority.md)
  (the top Alpha 0 block governs; older blocks are historical where they conflict).
- **What runs today:** the generated [Current Runtime State](docs/current_runtime/CURRENT_RUNTIME_STATE.md).
- **What has been verified, and how:** [Capability Inventory](docs/capability_verification/CAPABILITY_INVENTORY.md).

## The fast path

1. Read the [README](README.md).
2. Follow the [Quickstart](QUICKSTART.md) and run Nova locally (loopback only).
3. Try the commands below.
4. Read [Known Limitations](docs/product/KNOWN_LIMITATIONS.md).
5. Read the [Conversation and Memory Model](docs/product/CONVERSATION_AND_MEMORY_MODEL.md).

## Good first commands

1. `What works today?`
2. `What capabilities are active?`
3. `Summarize today's news.`
4. `remember: My preferred tone is concise.`
5. `review memories`
6. `Draft an email to test@example.com about tomorrow.`
7. `Plan my week`

Notes:
- Memory commands are explicit and receipted; ordinary chat does not become durable memory.
- Plan My Week produces a proposal and records your decisions; it does not act on its own.
- An email draft opens in your own mail client. Nova does not send email.
- Opening a folder and creating an email draft ask for confirmation first.

## What to look for

Do not judge Nova by feature count. Judge whether it makes these things clear:

- what you asked for, and what Nova thinks it means
- whether a real action is involved, and which capability would act
- whether that action needs your approval, and whether the approval was used once, for that exact action
- what actually happened: completed, failed, completed with a missing receipt, or unknown

```text
Awareness -> Decision -> Authority -> Execution -> Outcome
```

Capability describes what the runtime can technically do; it does not grant permission.

## What Nova is not yet

- not an autonomous agent or workflow automation system
- not supported for remote access: Nova is meant to be local-only, but a token-gated remote
  bridge route still exists in code and is being disabled for Alpha 0; do not expose Nova to a
  network
- not a Google Workspace or email-reading assistant
- not a recovery/restore product for end users
- not a polished daily-use product

Do not infer permission from capability, a roadmap, memory, prior approval, OAuth scope,
connection state, or a future issue or PR.

## For contributors and AI agents

- [AGENTS.md](AGENTS.md): binding rules for agents working in this repo
- [Repo Map](REPO_MAP.md): where things live
- [Canonical Truth Index](docs/CANONICAL/00_INDEX.md): how to resolve conflicting documents
- [Governance Matrix](docs/current_runtime/GOVERNANCE_MATRIX.md): generated authority map

## Operational truth record (machine-checked)

Kept verbatim because `scripts/check_operational_truth_consistency.py` validates it. It records
the beta-readiness ledger that preceded the Alpha 0 decision; for current ordering use
`.agent_context/current_priority.md`.

<details>
<summary>Beta-readiness ledger</summary>

### Beta-readiness ledger (post-#405, 2026-09-20)

```text
BETA_READINESS_SEQUENCE_V1: ACTIVE
verified main after Lane 5A rollback/restore proof: 868de9d92c701834f1c4fba422ab9c47a01ea33f
#397 through #405: COMPLETE / MERGED
COMPLETE: #406 governed-memory ID collision correctness (PR #411; main `ca66a06d`)
COMPLETE: #408 durability/state-ownership decision (PR #412; main `2592ad91`)
COMPLETE: durability implementation lane 1 - canonical state registry/migration detection (PR #413; main `e74fdca0`)
COMPLETE: durability implementation lane 2 - corruption-safe readers (PR #416; main `80e1c86f`)
COMPLETE: durability implementation lane 3 - maintenance locking + mutation quiescence (PR #419; main `2bfe202e`)
COMPLETE: durability implementation lane 4 - versioned snapshot + manifest (PR #421; main `4e32b501`)
FRESH-MAIN CLOSEOUT: PASS (314 focused durability/operational-truth tests passed; 1 expected Windows POSIX-FIFO skip; runtime structural smoke PASS)
COMPLETE: #409 release integrity / repository control (PR #423; main `aa39515f`)
COMPLETE: #410 private-beta freeze criteria (PR #410; main `3ad3f544`)
AUTHORIZED / ACTIVE: Lane 5A recovery construction (owner authorization; base main `3ad3f544`)
COMPLETE: Lane 5A step 1 - inactive recovery candidate migration (PR #424; main `298b7731`)
MIGRATION PROOF: PASS (173 durability tests passed; 1 expected Windows POSIX-FIFO skip)
COMPLETE: Lane 5A step 2 - recovery candidate validation (PR #426; main `9de640cd`)
VALIDATION PROOF: PASS (184 durability tests passed; 1 expected Windows POSIX-FIFO skip)
COMPLETE: Lane 5A step 3 - controlled recovery activation (PR #427; main `678dda6c`)
ACTIVATION PROOF: PASS (192 durability tests passed; 1 expected Windows POSIX-FIFO skip)
COMPLETE: Lane 5A authority-foundation correction (PR #428; main `3a3e9d33`)
AUTHORITY FOUNDATION PROOF: PASS (201 durability tests passed; 1 expected Windows POSIX-FIFO skip)
RECOVERY AUTHORITY MODEL: dual-slot highest-valid-generation selection
COMPLETE: Lane 5A step 4 - rollback/restore proof (PR #430; main `868de9d9`)
ROLLBACK/RESTORE PROOF: PASS (208 durability tests passed; 1 expected Windows POSIX-FIFO skip; runtime structural smoke PASS)
COMPLETE: beta user-facing truth pass (PR #433; main `ad64048e`)
COMPLETE: rollback/restore operational-truth checker contract (PR #436; main `0003a2e`)
FRESH-MAIN PROOF: PASS (39 focused checker-contract tests; Ruff; operational-truth consistency; runtime structural smoke)
COMPLETE: first Synthetic Beta Cohort v1 (PR #438; test-only evidence, not product acceptance)
COMPLETE: connected-user cohort test-spec correction (PR #439; main `486ad3dddc3f75412085b968c28561ab57e25686`)
CONFIRMED P1 BEFORE BETA ACCEPTANCE: the local-only boundary is unsafe if `NOVA_HOST` accepts a non-loopback bind; repair and fresh proof are required before any Windows acceptance run.
NEXT REQUIRED ENGINEERING: bounded local-boundary P1 repair (no remote mode or authority expansion)
THEN: fresh-main security and truth proof
THEN: installer supply-chain and privacy/Data-Out/secrets audit
THEN: build a new exact Windows candidate artifact; the prior artifact is historical only
THEN: clean Windows operator proof against that exact artifact
THEN: freeze exact candidate identity
THEN: rerun #434 and remaining acceptance checks against that frozen candidate
THEN: owner acceptance/distribution decision
THEN: 3 real non-developer users
```

Google/provider expansion remains paused. Operational Continuity implementation remains paused.
New capabilities remain paused. Voice expansion remains paused. Broader UI work remains paused.
Other feature expansion remains paused. This current order supersedes older ordering language below and
grants no new capability or authority.

</details>
